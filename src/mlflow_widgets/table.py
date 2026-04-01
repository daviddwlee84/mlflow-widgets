"""MlflowRunTable widget for displaying experiment runs as a sortable table."""

from __future__ import annotations

import json
import os
import urllib.request
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


def _search_runs_detailed_rest(tracking_uri: str, experiment_id: str) -> list[dict]:
    """Search runs with full details via REST API."""
    base = tracking_uri.rstrip("/")
    url = f"{base}/api/2.0/mlflow/runs/search"
    payload = json.dumps({
        "experiment_ids": [experiment_id],
        "max_results": 200,
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
        run_data = run.get("data", {})

        params = {}
        for p in run_data.get("params", []):
            params[p["key"]] = p["value"]

        metrics = {}
        for m in run_data.get("metrics", []):
            metrics[m["key"]] = m["value"]

        start_ms = int(info.get("start_time", 0))
        end_ms = int(info.get("end_time", 0))
        duration_s = (end_ms - start_ms) / 1000.0 if end_ms > 0 and start_ms > 0 else None

        results.append({
            "run_id": info.get("run_id", ""),
            "run_name": info.get("run_name", info.get("run_id", "")[:8]),
            "status": info.get("status", "UNKNOWN"),
            "start_time": start_ms,
            "duration_s": duration_s,
            "params": params,
            "metrics": metrics,
        })
    return results


def _search_runs_detailed_client(client: Any, experiment_id: str) -> list[dict]:
    """Search runs with full details using MlflowClient."""
    runs = client.search_runs(experiment_ids=[experiment_id])
    results = []
    for r in runs:
        start_ms = r.info.start_time or 0
        end_ms = r.info.end_time or 0
        duration_s = (end_ms - start_ms) / 1000.0 if end_ms > 0 and start_ms > 0 else None

        results.append({
            "run_id": r.info.run_id,
            "run_name": r.info.run_name or r.info.run_id[:8],
            "status": r.info.status,
            "start_time": start_ms,
            "duration_s": duration_s,
            "params": dict(r.data.params),
            "metrics": {k: v for k, v in r.data.metrics.items()},
        })
    return results


class MlflowRunTable(anywidget.AnyWidget):
    """Interactive table showing MLflow experiment runs.

    Displays run name, status, start time, duration, parameters, and
    final metric values in a sortable HTML table.

    Examples:
        ```python
        from mlflow_widgets import MlflowRunTable

        table = MlflowRunTable(
            tracking_uri="http://localhost:5000",
            experiment_id="1",
        )
        table
        ```
    """

    _esm = Path(__file__).parent / "static" / "mlflow-table.js"

    _table_data = traitlets.List(traitlets.Dict()).tag(sync=True)
    _param_keys = traitlets.List(traitlets.Unicode()).tag(sync=True)
    _metric_keys = traitlets.List(traitlets.Unicode()).tag(sync=True)
    _status = traitlets.Unicode("Waiting for data...").tag(sync=True)
    _do_refresh = traitlets.Int(0).tag(sync=True)

    width = traitlets.Int(900).tag(sync=True)

    def __init__(
        self,
        *,
        tracking_uri: Optional[str] = None,
        experiment_id: Optional[str] = None,
        width: int = 900,
        **kwargs: Any,
    ) -> None:
        """Create a MlflowRunTable widget.

        Args:
            tracking_uri: MLflow tracking server URI. Defaults to
                ``MLFLOW_TRACKING_URI`` env var or ``http://localhost:5000``.
            experiment_id: MLflow experiment ID to display runs for.
            width: Table width in pixels.
        """
        self._tracking_uri = tracking_uri or os.environ.get(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self._experiment_id = experiment_id
        self._mlflow = _try_import_mlflow()
        self._client = None
        if self._mlflow is not None:
            self._client = self._mlflow.MlflowClient(self._tracking_uri)

        super().__init__(width=width, **kwargs)

        if experiment_id:
            self.refresh()

    def refresh(self) -> None:
        """Fetch run data from MLflow and update the table."""
        if not self._experiment_id:
            self._status = "No experiment_id set"
            return

        try:
            if self._client is not None:
                rows = _search_runs_detailed_client(self._client, self._experiment_id)
            else:
                rows = _search_runs_detailed_rest(self._tracking_uri, self._experiment_id)

            all_param_keys: set[str] = set()
            all_metric_keys: set[str] = set()
            for row in rows:
                all_param_keys.update(row["params"].keys())
                all_metric_keys.update(row["metrics"].keys())

            now = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
            self._table_data = rows
            self._param_keys = sorted(all_param_keys)
            self._metric_keys = sorted(all_metric_keys)
            self._status = f"{len(rows)} runs (updated {now})"
        except Exception as exc:
            self._status = f"Error: {exc}"

    @traitlets.observe("_do_refresh")
    def _on_refresh_request(self, change: dict[str, Any]) -> None:
        self.refresh()
