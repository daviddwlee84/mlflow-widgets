"""MlflowParallelCoordinates widget for hyperparameter/metric comparison."""

from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import anywidget
import traitlets

from mlflow_widgets.table import (
    _search_runs_detailed_client,
    _search_runs_detailed_rest,
    _try_import_mlflow,
)


def _build_axes_and_runs(
    rows: list[dict],
    param_keys: Sequence[str] | None = None,
    metric_keys: Sequence[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Build axis definitions and run data for parallel coordinates.

    Returns (axes, runs) where axes is a list of
    {name, type, domain, is_metric} and runs is a list of
    {run_id, run_name, status, values: {axis_name: normalized_value, ...},
     raw_values: {axis_name: display_value, ...}}.
    """
    all_params: set[str] = set()
    all_metrics: set[str] = set()
    for r in rows:
        all_params.update(r.get("params", {}).keys())
        all_metrics.update(r.get("metrics", {}).keys())

    use_params = list(param_keys) if param_keys else sorted(all_params)
    use_metrics = list(metric_keys) if metric_keys else sorted(all_metrics)

    axes = []
    for pk in use_params:
        values = []
        for r in rows:
            v = r.get("params", {}).get(pk)
            if v is not None:
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    values.append(v)

        numeric_vals = [v for v in values if isinstance(v, (int, float))]
        if len(numeric_vals) >= len(values) * 0.5 and numeric_vals:
            axes.append({
                "name": f"P: {pk}",
                "key": f"p:{pk}",
                "type": "numeric",
                "domain": [min(numeric_vals), max(numeric_vals)],
                "is_metric": False,
            })
        else:
            cats = sorted(set(str(v) for v in values))
            axes.append({
                "name": f"P: {pk}",
                "key": f"p:{pk}",
                "type": "categorical",
                "domain": cats,
                "is_metric": False,
            })

    for mk in use_metrics:
        values = []
        for r in rows:
            v = r.get("metrics", {}).get(mk)
            if v is not None:
                values.append(float(v))
        if values:
            axes.append({
                "name": f"M: {mk}",
                "key": f"m:{mk}",
                "type": "numeric",
                "domain": [min(values), max(values)],
                "is_metric": True,
            })

    runs_data = []
    for r in rows:
        values = {}
        raw_values = {}
        for ax in axes:
            key = ax["key"]
            if key.startswith("p:"):
                pk = key[2:]
                raw = r.get("params", {}).get(pk)
            else:
                mk = key[2:]
                raw = r.get("metrics", {}).get(mk)

            if raw is None:
                values[ax["name"]] = None
                raw_values[ax["name"]] = None
                continue

            if ax["type"] == "numeric":
                try:
                    fval = float(raw)
                except (ValueError, TypeError):
                    values[ax["name"]] = None
                    raw_values[ax["name"]] = None
                    continue
                lo, hi = ax["domain"]
                span = hi - lo if hi != lo else 1.0
                values[ax["name"]] = (fval - lo) / span
                raw_values[ax["name"]] = fval
            else:
                cats = ax["domain"]
                sval = str(raw)
                idx = cats.index(sval) if sval in cats else 0
                values[ax["name"]] = idx / max(len(cats) - 1, 1)
                raw_values[ax["name"]] = sval

        runs_data.append({
            "run_id": r["run_id"],
            "run_name": r["run_name"],
            "status": r["status"],
            "parent_run_id": r.get("parent_run_id"),
            "values": values,
            "raw_values": raw_values,
        })

    return axes, runs_data


class MlflowParallelCoordinates(anywidget.AnyWidget):
    """Parallel coordinates chart for comparing runs across params/metrics.

    Each vertical axis is a parameter or metric. Each polyline is a run,
    colored by status. Status filter checkboxes let you show/hide run groups.

    Examples:
        ```python
        from mlflow_widgets import MlflowParallelCoordinates

        chart = MlflowParallelCoordinates(
            tracking_uri="http://localhost:5000",
            experiment_id="1",
        )
        chart
        ```
    """

    _esm = Path(__file__).parent / "static" / "mlflow-parallel.js"

    _axes_data = traitlets.List(traitlets.Dict()).tag(sync=True)
    _runs_data = traitlets.List(traitlets.Dict()).tag(sync=True)
    _status = traitlets.Unicode("Waiting for data...").tag(sync=True)
    _do_refresh = traitlets.Int(0).tag(sync=True)

    color_by = traitlets.Unicode("status").tag(sync=True)
    width = traitlets.Int(900).tag(sync=True)
    height = traitlets.Int(400).tag(sync=True)

    def __init__(
        self,
        *,
        tracking_uri: str | None = None,
        experiment_id: str | None = None,
        param_keys: Sequence[str] | None = None,
        metric_keys: Sequence[str] | None = None,
        color_by: str = "status",
        width: int = 900,
        height: int = 400,
        **kwargs: Any,
    ) -> None:
        """Create a MlflowParallelCoordinates widget.

        Args:
            tracking_uri: MLflow tracking server URI.
            experiment_id: Experiment to fetch runs from.
            param_keys: Which parameters to show as axes (auto-discovers if None).
            metric_keys: Which metrics to show as axes (auto-discovers if None).
            color_by: Color lines by ``"status"`` or a metric name.
            width: Widget width in pixels.
            height: Widget height in pixels.
        """
        self._tracking_uri = tracking_uri or os.environ.get(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self._experiment_id = experiment_id
        self._param_keys = param_keys
        self._metric_keys = metric_keys
        self._mlflow = _try_import_mlflow()
        self._client = None
        if self._mlflow is not None:
            self._client = self._mlflow.MlflowClient(self._tracking_uri)

        super().__init__(color_by=color_by, width=width, height=height, **kwargs)

        if experiment_id:
            self.refresh()

    def refresh(self) -> None:
        """Fetch run data and rebuild axes/run data."""
        if not self._experiment_id:
            self._status = "No experiment_id set"
            return

        try:
            if self._client is not None:
                rows = _search_runs_detailed_client(self._client, self._experiment_id)
            else:
                rows = _search_runs_detailed_rest(
                    self._tracking_uri, self._experiment_id
                )

            axes, runs_data = _build_axes_and_runs(
                rows, self._param_keys, self._metric_keys
            )

            now = datetime.now().strftime("%H:%M:%S")
            self._axes_data = axes
            self._runs_data = runs_data
            self._status = f"{len(runs_data)} runs, {len(axes)} axes (updated {now})"
        except Exception as exc:
            self._status = f"Error: {exc}"

    @traitlets.observe("_do_refresh")
    def _on_refresh_request(self, change: dict[str, Any]) -> None:
        self.refresh()

    def close(self) -> None:
        super().close()
