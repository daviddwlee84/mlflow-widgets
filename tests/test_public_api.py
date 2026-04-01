from __future__ import annotations

import mlflow_widgets
from mlflow_widgets import (
    MlflowChart,
    MlflowParallelCoordinates,
    MlflowRunSelector,
    MlflowRunTable,
)


def test_public_exports_are_stable() -> None:
    assert mlflow_widgets.__all__ == [
        "MlflowChart",
        "MlflowParallelCoordinates",
        "MlflowRunSelector",
        "MlflowRunTable",
    ]
    assert mlflow_widgets.MlflowChart is MlflowChart
    assert mlflow_widgets.MlflowRunTable is MlflowRunTable
    assert mlflow_widgets.MlflowRunSelector is MlflowRunSelector
    assert mlflow_widgets.MlflowParallelCoordinates is MlflowParallelCoordinates
