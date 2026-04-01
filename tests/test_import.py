"""Smoke tests: public API is importable and __all__ is correct."""

from __future__ import annotations


def test_version_exists():
    import mlflow_widgets

    assert hasattr(mlflow_widgets, "__version__")
    assert isinstance(mlflow_widgets.__version__, str)
    assert mlflow_widgets.__version__  # non-empty


def test_all_exports():
    import mlflow_widgets

    expected = {
        "MlflowChart",
        "MlflowParallelCoordinates",
        "MlflowRunSelector",
        "MlflowRunTable",
    }
    assert set(mlflow_widgets.__all__) == expected


def test_classes_importable():
    from mlflow_widgets import (
        MlflowChart,
        MlflowParallelCoordinates,
        MlflowRunSelector,
        MlflowRunTable,
    )

    assert callable(MlflowChart)
    assert callable(MlflowParallelCoordinates)
    assert callable(MlflowRunSelector)
    assert callable(MlflowRunTable)


def test_import_without_mlflow(monkeypatch):
    """Package must be importable even when mlflow is not installed."""
    import importlib
    import sys

    real_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def mock_import(name, *args, **kwargs):
        if name == "mlflow" or name.startswith("mlflow."):
            raise ImportError(f"mocked: no module named {name!r}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)

    for mod_name in list(sys.modules):
        if mod_name.startswith("mlflow_widgets"):
            del sys.modules[mod_name]

    import mlflow_widgets

    importlib.reload(mlflow_widgets)
    assert mlflow_widgets.MlflowChart is not None
