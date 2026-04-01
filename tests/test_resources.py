from __future__ import annotations

from importlib.resources import files


def test_packaged_static_resources_are_accessible() -> None:
    package_files = files("mlflow_widgets")

    for relative_path in [
        "py.typed",
        "static/mlflow-chart.js",
        "static/mlflow-table.js",
        "static/mlflow-parallel.js",
    ]:
        assert package_files.joinpath(relative_path).is_file(), relative_path
