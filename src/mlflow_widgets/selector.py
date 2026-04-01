"""MlflowRunSelector — fetch MLflow runs as a pandas DataFrame for selection."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from mlflow_widgets.table import (
    _search_runs_detailed_client,
    _search_runs_detailed_rest,
    _try_import_mlflow,
)


class MlflowRunSelector:
    """Fetch MLflow experiment runs and present them as a pandas DataFrame.

    Designed to work with ``marimo.ui.table(df, selection="multi")`` so
    users can select runs via checkboxes, then pass the selected run IDs
    to ``MlflowChart`` for visualization.

    Examples:
        ```python
        import marimo as mo
        from mlflow_widgets import MlflowRunSelector, MlflowChart

        selector = MlflowRunSelector(
            tracking_uri="http://localhost:5000",
            experiment_id="1",
        )
        table = mo.ui.table(selector.to_dataframe(), selection="multi")

        # In another cell:
        selected_ids = MlflowRunSelector.get_run_ids(table.value)
        chart = MlflowChart(runs=selected_ids, metric_key="loss")
        ```
    """

    def __init__(
        self,
        *,
        tracking_uri: str | None = None,
        experiment_id: str | None = None,
    ) -> None:
        """Create a MlflowRunSelector.

        Args:
            tracking_uri: MLflow tracking server URI. Defaults to
                ``MLFLOW_TRACKING_URI`` env var or ``http://localhost:5000``.
            experiment_id: MLflow experiment ID to fetch runs from.
        """
        self._tracking_uri = tracking_uri or os.environ.get(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self._experiment_id = experiment_id
        self._mlflow = _try_import_mlflow()
        self._client = None
        if self._mlflow is not None:
            self._client = self._mlflow.MlflowClient(self._tracking_uri)

        self._raw_rows: list[dict] = []
        if experiment_id:
            self.refresh()

    @property
    def tracking_uri(self) -> str:
        return self._tracking_uri

    @property
    def experiment_id(self) -> str | None:
        return self._experiment_id

    def refresh(self) -> MlflowRunSelector:
        """Re-fetch runs from MLflow. Returns self for chaining."""
        if not self._experiment_id:
            self._raw_rows = []
            return self

        if self._client is not None:
            self._raw_rows = _search_runs_detailed_client(
                self._client, self._experiment_id
            )
        else:
            self._raw_rows = _search_runs_detailed_rest(
                self._tracking_uri, self._experiment_id
            )
        return self

    def to_dataframe(self) -> Any:
        """Return runs as a pandas DataFrame.

        Columns: run_id, run_name, status, start_time, duration_s,
        plus ``param.<key>`` for each parameter and ``metric.<key>``
        for each final metric value.

        Raises:
            ImportError: If pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError as err:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install pandas"
            ) from err

        rows = []
        for r in self._raw_rows:
            row: dict[str, Any] = {
                "run_id": r["run_id"],
                "run_name": r["run_name"],
                "status": r["status"],
                "parent_run_id": r.get("parent_run_id"),
                "start_time": (
                    datetime.fromtimestamp(r["start_time"] / 1000.0).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if r["start_time"]
                    else None
                ),
                "duration_s": round(r["duration_s"], 1) if r["duration_s"] else None,
            }
            for k, v in r.get("params", {}).items():
                row[f"param.{k}"] = v
            for k, v in r.get("metrics", {}).items():
                row[f"metric.{k}"] = v
            rows.append(row)

        return pd.DataFrame(rows)

    @staticmethod
    def get_run_ids(
        selection: Any,
    ) -> list[str]:
        """Extract run_id list from a DataFrame, list of dicts, or similar.

        Works with ``mo.ui.table(...).value`` which returns a list of dicts
        or a DataFrame depending on the input format.

        Args:
            selection: The ``.value`` from a ``mo.ui.table``, typically a
                list of row dicts or a pandas DataFrame.

        Returns:
            List of run_id strings.
        """
        if hasattr(selection, "to_dict"):
            # pandas DataFrame
            if "run_id" in selection.columns:
                return selection["run_id"].tolist()
            return []

        if isinstance(selection, list):
            return [
                r["run_id"] for r in selection if isinstance(r, dict) and "run_id" in r
            ]

        return []
