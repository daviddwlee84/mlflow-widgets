from __future__ import annotations

from importlib.resources import files

from mlflow_widgets import (
    MlflowChart,
    MlflowParallelCoordinates,
    MlflowRunSelector,
    MlflowRunTable,
)


package_files = files("mlflow_widgets")
for relative_path in [
    "py.typed",
    "static/mlflow-chart.js",
    "static/mlflow-table.js",
    "static/mlflow-parallel.js",
]:
    assert package_files.joinpath(relative_path).is_file(), relative_path

print(
    "Smoke import OK",
    MlflowChart.__name__,
    MlflowRunTable.__name__,
    MlflowRunSelector.__name__,
    MlflowParallelCoordinates.__name__,
)
