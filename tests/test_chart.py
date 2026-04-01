from __future__ import annotations

import mlflow_widgets.chart as chart


def test_chart_uses_rest_fallback_and_sorts_points(monkeypatch) -> None:
    calls: list[tuple[str, str, str]] = []

    def fake_fetch(tracking_uri: str, run_id: str, metric_key: str, max_results: int = 25000):
        calls.append((tracking_uri, run_id, metric_key))
        assert max_results == 25000
        return [
            {"step": 3, "value": 0.2, "timestamp": 3000},
            {"step": 1, "value": 0.5, "timestamp": 1000},
            {"step": 2, "value": 0.3, "timestamp": 2000},
        ]

    monkeypatch.setattr(chart, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(chart, "_fetch_metric_history_rest", fake_fetch)

    widget = chart.MlflowChart(
        tracking_uri="http://tracking.example",
        runs=[{"id": "run-a", "label": "Run A", "status": "RUNNING"}],
        metric_key="loss",
        poll_seconds=None,
    )

    assert widget._client is None
    assert calls == [("http://tracking.example", "run-a", "loss")]
    assert widget._series_data == [
        {
            "run_id": "run-a",
            "label": "Run A",
            "parent_run_id": None,
            "status": "RUNNING",
            "points": [
                {"step": 1, "value": 0.5, "timestamp": 1000},
                {"step": 2, "value": 0.3, "timestamp": 2000},
                {"step": 3, "value": 0.2, "timestamp": 3000},
            ],
        }
    ]
    assert "3 points across 1 runs" in widget._status


def test_chart_refresh_observer_calls_refresh(monkeypatch) -> None:
    monkeypatch.setattr(chart, "_try_import_mlflow", lambda: None)
    widget = chart.MlflowChart(metric_key="", poll_seconds=None)

    calls: list[str] = []
    monkeypatch.setattr(widget, "refresh", lambda: calls.append("chart"))

    widget._do_refresh += 1

    assert calls == ["chart"]


def test_chart_close_cancels_poll_timer(monkeypatch, fake_timer_class) -> None:
    monkeypatch.setattr(chart, "_try_import_mlflow", lambda: None)
    monkeypatch.setattr(chart.threading, "Timer", fake_timer_class)

    widget = chart.MlflowChart(metric_key="", poll_seconds=5)
    timer = widget._poll_timer

    assert timer is not None
    assert timer.started is True
    assert timer.interval == 5

    widget.close()

    assert widget._stopped is True
    assert timer.cancelled is True
    assert widget._poll_timer is None
