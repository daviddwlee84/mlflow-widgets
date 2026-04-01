"""Tests for widget instantiation and traitlet defaults (no MLflow server needed)."""

from __future__ import annotations

import os
import threading

import pytest


@pytest.fixture(autouse=True)
def _clear_mlflow_env(monkeypatch):
    """Ensure MLFLOW_TRACKING_URI doesn't leak between tests."""
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)


class TestMlflowChart:
    def test_default_traitlets(self):
        from mlflow_widgets import MlflowChart

        chart = MlflowChart()
        assert chart.metric_key == ""
        assert chart.smoothing_kind == "gaussian"
        assert chart.smoothing_param is None
        assert chart.show_slider is True
        assert chart.x_axis == "step"
        assert chart.width == 700
        assert chart.height == 300
        assert chart._series_data == []
        assert chart._do_refresh == 0

    def test_custom_params(self):
        from mlflow_widgets import MlflowChart

        chart = MlflowChart(
            metric_key="loss",
            poll_seconds=None,
            smoothing_kind="rolling",
            width=1000,
            height=500,
        )
        assert chart.metric_key == "loss"
        assert chart.poll_seconds is None
        assert chart.smoothing_kind == "rolling"
        assert chart.width == 1000
        assert chart.height == 500

    def test_do_refresh_observer_registered(self):
        from mlflow_widgets import MlflowChart

        chart = MlflowChart(poll_seconds=None)
        notifiers = chart._trait_notifiers.get("_do_refresh", {})
        assert notifiers, "_do_refresh should have an observer registered"


class TestMlflowRunTable:
    def test_default_traitlets(self):
        from mlflow_widgets import MlflowRunTable

        table = MlflowRunTable()
        assert table._table_data == []
        assert table._param_keys == []
        assert table._metric_keys == []
        assert table._do_refresh == 0
        assert table.poll_seconds is None
        assert table.width == 900

    def test_do_refresh_observer_registered(self):
        from mlflow_widgets import MlflowRunTable

        table = MlflowRunTable()
        notifiers = table._trait_notifiers.get("_do_refresh", {})
        assert notifiers, "_do_refresh should have an observer registered"


class TestMlflowParallelCoordinates:
    def test_default_traitlets(self):
        from mlflow_widgets import MlflowParallelCoordinates

        chart = MlflowParallelCoordinates()
        assert chart._axes_data == []
        assert chart._runs_data == []
        assert chart._do_refresh == 0
        assert chart.color_by == "status"
        assert chart.width == 900
        assert chart.height == 400

    def test_do_refresh_observer_registered(self):
        from mlflow_widgets import MlflowParallelCoordinates

        chart = MlflowParallelCoordinates()
        notifiers = chart._trait_notifiers.get("_do_refresh", {})
        assert notifiers, "_do_refresh should have an observer registered"


class TestMlflowRunSelector:
    def test_init_without_experiment(self):
        from mlflow_widgets import MlflowRunSelector

        sel = MlflowRunSelector()
        assert sel.experiment_id is None
        assert sel._raw_rows == []

    def test_get_run_ids_from_list(self):
        from mlflow_widgets import MlflowRunSelector

        rows = [
            {"run_id": "abc123", "name": "run1"},
            {"run_id": "def456", "name": "run2"},
        ]
        assert MlflowRunSelector.get_run_ids(rows) == ["abc123", "def456"]

    def test_get_run_ids_empty(self):
        from mlflow_widgets import MlflowRunSelector

        assert MlflowRunSelector.get_run_ids([]) == []
        assert MlflowRunSelector.get_run_ids([{"no_run_id": True}]) == []
