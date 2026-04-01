"""MlflowChart widget for live MLflow run metric visualization."""

from __future__ import annotations

import json
import os
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

import anywidget
import traitlets


def _try_import_mlflow():
    try:
        import mlflow
        return mlflow
    except ImportError:
        return None


def _fetch_metric_history_rest(
    tracking_uri: str,
    run_id: str,
    metric_key: str,
    max_results: int = 25000,
) -> list[dict]:
    """Fetch metric history via MLflow REST API using urllib."""
    base = tracking_uri.rstrip("/")
    url = (
        f"{base}/api/2.0/mlflow/metrics/get-history"
        f"?run_id={run_id}&metric_key={metric_key}&max_results={max_results}"
    )
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    metrics = data.get("metrics", [])
    return [{"step": int(m.get("step", 0)), "value": float(m["value"])} for m in metrics]


def _fetch_metric_history_client(
    client: Any,
    run_id: str,
    metric_key: str,
) -> list[dict]:
    """Fetch metric history using MlflowClient."""
    metrics = client.get_metric_history(run_id, metric_key)
    return [{"step": m.step, "value": m.value} for m in metrics]


def _get_run_info_rest(tracking_uri: str, run_id: str) -> dict:
    """Fetch run info via REST API."""
    base = tracking_uri.rstrip("/")
    url = f"{base}/api/2.0/mlflow/runs/get?run_id={run_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    run = data.get("run", {})
    info = run.get("info", {})
    return {
        "run_id": info.get("run_id", run_id),
        "status": info.get("status", "UNKNOWN"),
        "run_name": info.get("run_name", run_id[:8]),
    }


def _search_runs_rest(tracking_uri: str, experiment_id: str) -> list[dict]:
    """Search runs in an experiment via REST API."""
    base = tracking_uri.rstrip("/")
    url = f"{base}/api/2.0/mlflow/runs/search"
    payload = json.dumps({
        "experiment_ids": [experiment_id],
        "max_results": 100,
    }).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    results = []
    for run in data.get("runs", []):
        info = run.get("info", {})
        results.append({
            "id": info.get("run_id", ""),
            "label": info.get("run_name", info.get("run_id", "")[:8]),
            "status": info.get("status", "UNKNOWN"),
        })
    return results


class MlflowChart(anywidget.AnyWidget):
    """Live line chart that polls MLflow for metric data.

    Renders a Canvas-based chart that can auto-update while runs are active.
    Supports multiple runs for side-by-side comparison and optional rolling
    smoothing (rolling mean, exponential moving average, or gaussian).

    Examples:
        ```python
        import mlflow
        from mlflow_chart import MlflowChart

        with mlflow.start_run() as run:
            for step in range(100):
                mlflow.log_metric("loss", 1.0 / (step + 1), step=step)

            chart = MlflowChart(
                tracking_uri="http://localhost:5000",
                runs=[run],
                metric_key="loss",
            )
            chart
        ```
    """

    _esm = Path(__file__).parent / "static" / "mlflow-chart.js"

    _series_data = traitlets.List(traitlets.Dict()).tag(sync=True)
    _status = traitlets.Unicode("Waiting for data...").tag(sync=True)
    _do_refresh = traitlets.Int(0).tag(sync=True)

    metric_key = traitlets.Unicode("").tag(sync=True)
    poll_seconds = traitlets.Int(5, allow_none=True).tag(sync=True)
    smoothing_kind = traitlets.Unicode("gaussian").tag(sync=True)
    smoothing_param = traitlets.Float(None, allow_none=True).tag(sync=True)
    show_slider = traitlets.Bool(True).tag(sync=True)
    width = traitlets.Int(700).tag(sync=True)
    height = traitlets.Int(300).tag(sync=True)

    def __init__(
        self,
        *,
        tracking_uri: Optional[str] = None,
        experiment_id: Optional[str] = None,
        runs: Optional[Sequence[Any]] = None,
        metric_key: str = "",
        poll_seconds: Optional[int] = 5,
        smoothing_kind: str = "gaussian",
        smoothing_param: Optional[float] = None,
        show_slider: bool = True,
        width: int = 700,
        height: int = 300,
        **kwargs: Any,
    ) -> None:
        """Create a MlflowChart widget.

        Args:
            tracking_uri: MLflow tracking server URI. Defaults to
                ``MLFLOW_TRACKING_URI`` env var or ``http://localhost:5000``.
            experiment_id: MLflow experiment ID. If provided and ``runs`` is
                not given, all runs in this experiment are charted.
            runs: A list of MLflow Run objects, run-ID strings, or dicts
                with ``id`` and ``label`` keys.
            metric_key: The metric key to chart (e.g. ``"loss"``).
            poll_seconds: Seconds between polling updates, or ``None`` to
                disable auto-polling and show a manual refresh button instead.
            smoothing_kind: ``"rolling"``, ``"exponential"``, or ``"gaussian"``.
            smoothing_param: Smoothing parameter, or ``None`` for no smoothing.
            show_slider: Whether to show the smoothing slider in the UI.
            width: Chart width in pixels.
            height: Chart height in pixels.
        """
        self._tracking_uri = tracking_uri or os.environ.get(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self._experiment_id = experiment_id
        self._mlflow = _try_import_mlflow()
        self._client = None
        if self._mlflow is not None:
            self._client = self._mlflow.MlflowClient(self._tracking_uri)

        self._run_specs: list[dict] = []
        if runs is not None:
            self._run_specs = self._normalize_runs(runs)
        elif experiment_id is not None:
            self._run_specs = self._discover_runs(experiment_id)

        self._poll_timer: Optional[threading.Timer] = None
        self._poll_lock = threading.Lock()
        self._stopped = False

        super().__init__(
            metric_key=metric_key,
            poll_seconds=poll_seconds,
            smoothing_kind=smoothing_kind,
            smoothing_param=smoothing_param,
            show_slider=show_slider,
            width=width,
            height=height,
            **kwargs,
        )

        if self._run_specs and metric_key:
            self.refresh()

        if poll_seconds is not None and poll_seconds > 0:
            self._schedule_poll()

    def _normalize_runs(self, runs: Sequence[Any]) -> list[dict]:
        """Convert various run formats to a uniform list of {id, label, status}."""
        result = []
        for r in runs:
            if isinstance(r, str):
                info = self._get_run_info(r)
                result.append({
                    "id": r,
                    "label": info.get("run_name", r[:8]),
                    "status": info.get("status", "UNKNOWN"),
                })
            elif isinstance(r, dict):
                result.append({
                    "id": r["id"],
                    "label": r.get("label", r["id"][:8]),
                    "status": r.get("status", "UNKNOWN"),
                })
            elif hasattr(r, "info"):
                result.append({
                    "id": r.info.run_id,
                    "label": r.info.run_name or r.info.run_id[:8],
                    "status": r.info.status,
                })
            else:
                raise TypeError(f"Unsupported run type: {type(r)}")
        return result

    def _discover_runs(self, experiment_id: str) -> list[dict]:
        """Discover all runs in an experiment."""
        if self._client is not None:
            runs = self._client.search_runs(experiment_ids=[experiment_id])
            return [
                {
                    "id": r.info.run_id,
                    "label": r.info.run_name or r.info.run_id[:8],
                    "status": r.info.status,
                }
                for r in runs
            ]
        return _search_runs_rest(self._tracking_uri, experiment_id)

    def _get_run_info(self, run_id: str) -> dict:
        if self._client is not None:
            r = self._client.get_run(run_id)
            return {
                "run_id": r.info.run_id,
                "run_name": r.info.run_name or r.info.run_id[:8],
                "status": r.info.status,
            }
        return _get_run_info_rest(self._tracking_uri, run_id)

    def _fetch_series(self) -> list[dict]:
        """Fetch metric history for all runs and return series data."""
        series = []
        for run_spec in self._run_specs:
            try:
                if self._client is not None:
                    points = _fetch_metric_history_client(
                        self._client, run_spec["id"], self.metric_key
                    )
                else:
                    points = _fetch_metric_history_rest(
                        self._tracking_uri, run_spec["id"], self.metric_key
                    )
                points.sort(key=lambda p: p["step"])
            except Exception:
                points = []

            series.append({
                "run_id": run_spec["id"],
                "label": run_spec["label"],
                "points": points,
            })
        return series

    def refresh(self) -> None:
        """Manually refresh metric data from MLflow."""
        try:
            series = self._fetch_series()
            total_points = sum(len(s["points"]) for s in series)
            now = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
            self._series_data = series
            self._status = f"{total_points} points across {len(series)} runs (updated {now})"

            still_running = any(
                r.get("status") in ("RUNNING", None) for r in self._run_specs
            )
            if not still_running and self._poll_timer is not None:
                self._status += " — all runs finished"
                self.stop()
        except Exception as exc:
            self._status = f"Error: {exc}"

    def _schedule_poll(self) -> None:
        if self._stopped or self.poll_seconds is None:
            return
        with self._poll_lock:
            self._poll_timer = threading.Timer(self.poll_seconds, self._poll_tick)
            self._poll_timer.daemon = True
            self._poll_timer.start()

    def _poll_tick(self) -> None:
        if self._stopped:
            return
        self.refresh()
        if not self._stopped:
            self._schedule_poll()

    @traitlets.observe("_do_refresh")
    def _on_refresh_request(self, change: dict[str, Any]) -> None:
        self.refresh()

    def stop(self) -> None:
        """Stop auto-polling."""
        self._stopped = True
        with self._poll_lock:
            if self._poll_timer is not None:
                self._poll_timer.cancel()
                self._poll_timer = None

    def close(self) -> None:
        self.stop()
        super().close()

    @traitlets.validate("smoothing_kind")
    def _validate_smoothing_kind(self, proposal: dict[str, Any]) -> str:
        value = proposal["value"]
        allowed = ("rolling", "exponential", "gaussian")
        if value not in allowed:
            raise ValueError(f"smoothing_kind must be one of {allowed}, got {value!r}")
        return value

    @traitlets.validate("smoothing_param")
    def _validate_smoothing_param(self, proposal: dict[str, Any]) -> Optional[float]:
        value = proposal["value"]
        if value is None:
            return value
        kind = self.smoothing_kind
        if kind == "rolling" and (value < 2 or value != int(value)):
            raise ValueError("For rolling smoothing, param must be an integer >= 2")
        if kind == "exponential" and not (0 < value < 1):
            raise ValueError("For exponential smoothing, param must be between 0 and 1 (exclusive)")
        if kind == "gaussian" and value <= 0:
            raise ValueError("For gaussian smoothing, param (sigma) must be > 0")
        return value
