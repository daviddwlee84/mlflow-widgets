from __future__ import annotations

import mlflow_widgets.parallel as parallel
import mlflow_widgets.selector as selector
import mlflow_widgets.table as table


def test_table_rest_fallback_populates_traitlets(monkeypatch, sample_rows) -> None:
    monkeypatch.setattr(table, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(
        table,
        "_search_runs_detailed_rest",
        lambda tracking_uri, experiment_id: sample_rows,
    )

    widget = table.MlflowRunTable(
        tracking_uri="http://tracking.example",
        experiment_id="42",
        poll_seconds=None,
    )

    assert widget._client is None
    assert widget._table_data == sample_rows
    assert widget._param_keys == ["lr", "model"]
    assert widget._metric_keys == ["accuracy", "loss"]
    assert "2 runs" in widget._status


def test_table_refresh_observer_calls_refresh(monkeypatch) -> None:
    monkeypatch.setattr(table, "_try_import_mlflow", lambda: None)
    widget = table.MlflowRunTable(poll_seconds=None)

    calls: list[str] = []
    monkeypatch.setattr(widget, "refresh", lambda: calls.append("table"))

    widget._do_refresh += 1

    assert calls == ["table"]


def test_table_close_cancels_poll_timer(monkeypatch, fake_timer_class) -> None:
    monkeypatch.setattr(table, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(table.threading, "Timer", fake_timer_class)

    widget = table.MlflowRunTable(poll_seconds=7)
    timer = widget._poll_timer

    assert timer is not None
    assert timer.started is True
    assert timer.interval == 7

    widget.close()

    assert widget._stopped is True
    assert timer.cancelled is True
    assert widget._poll_timer is None


def test_selector_builds_dataframe_and_extracts_run_ids(monkeypatch, sample_rows) -> None:
    monkeypatch.setattr(selector, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(
        selector,
        "_search_runs_detailed_rest",
        lambda tracking_uri, experiment_id: sample_rows,
    )

    run_selector = selector.MlflowRunSelector(
        tracking_uri="http://tracking.example",
        experiment_id="42",
    )
    frame = run_selector.to_dataframe()

    assert list(frame["run_id"]) == ["run-a", "run-b"]
    assert frame.loc[0, "param.lr"] == "0.10"
    assert frame.loc[1, "metric.loss"] == 0.18
    assert selector.MlflowRunSelector.get_run_ids(frame) == ["run-a", "run-b"]
    assert selector.MlflowRunSelector.get_run_ids(
        [{"run_id": "run-a"}, {"ignored": "value"}]
    ) == ["run-a"]


def test_parallel_rest_fallback_populates_axes_and_runs(monkeypatch, sample_rows) -> None:
    monkeypatch.setattr(parallel, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(
        parallel,
        "_search_runs_detailed_rest",
        lambda tracking_uri, experiment_id: sample_rows,
    )

    widget = parallel.MlflowParallelCoordinates(
        tracking_uri="http://tracking.example",
        experiment_id="42",
    )

    assert widget._client is None
    assert [axis["name"] for axis in widget._axes_data] == [
        "P: lr",
        "P: model",
        "M: accuracy",
        "M: loss",
    ]
    assert [axis["type"] for axis in widget._axes_data] == [
        "numeric",
        "categorical",
        "numeric",
        "numeric",
    ]
    assert len(widget._runs_data) == 2
    assert widget._runs_data[0]["run_id"] == "run-a"
    assert widget._runs_data[0]["raw_values"]["P: model"] == "xgboost"
    assert "2 runs, 4 axes" in widget._status


def test_parallel_refresh_observer_calls_refresh(monkeypatch) -> None:
    monkeypatch.setattr(parallel, "_try_import_mlflow", lambda: None)
    widget = parallel.MlflowParallelCoordinates()

    calls: list[str] = []
    monkeypatch.setattr(widget, "refresh", lambda: calls.append("parallel"))

    widget._do_refresh += 1

    assert calls == ["parallel"]
