from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def sample_rows() -> list[dict]:
    return [
        {
            "run_id": "run-a",
            "run_name": "alpha",
            "status": "RUNNING",
            "start_time": 1_710_000_000_000,
            "duration_s": 5.25,
            "params": {"lr": "0.10", "model": "xgboost"},
            "metrics": {"loss": 0.25, "accuracy": 0.91},
            "parent_run_id": None,
        },
        {
            "run_id": "run-b",
            "run_name": "beta",
            "status": "FINISHED",
            "start_time": 1_710_000_300_000,
            "duration_s": 7.5,
            "params": {"lr": "0.05", "model": "lightgbm"},
            "metrics": {"loss": 0.18, "accuracy": 0.94},
            "parent_run_id": "run-a",
        },
    ]


@pytest.fixture
def fake_timer_class():
    class FakeTimer:
        instances: list["FakeTimer"] = []

        def __init__(self, interval, function, args=None, kwargs=None):
            self.interval = interval
            self.function = function
            self.args = list(args or [])
            self.kwargs = dict(kwargs or {})
            self.daemon = False
            self.started = False
            self.cancelled = False
            type(self).instances.append(self)

        def start(self) -> None:
            self.started = True

        def cancel(self) -> None:
            self.cancelled = True

    return FakeTimer
