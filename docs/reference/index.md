# API Reference

Full API documentation for all public classes in mlflow-widgets. Generated automatically from source code docstrings.

## Widgets

These classes inherit from `anywidget.AnyWidget` and render interactive UI in notebooks:

| Class | Description |
|-------|-------------|
| [`MlflowChart`](chart.md) | Live-updating canvas line chart for MLflow metrics |
| [`MlflowRunTable`](table.md) | Sortable HTML table of experiment runs |
| [`MlflowParallelCoordinates`](parallel.md) | Parallel coordinates chart for hyperparameter comparison |

## Helpers

| Class | Description |
|-------|-------------|
| [`MlflowRunSelector`](selector.md) | Pure Python helper returning pandas DataFrames for run selection |

## Architecture

All widgets follow the same data flow pattern:

1. **Python** fetches data from MLflow (via `MlflowClient` or REST API fallback with `urllib`)
2. Data is passed to **JavaScript** through traitlets (synced traits tagged with `sync=True`)
3. **JavaScript** handles rendering using vanilla DOM and Canvas APIs

The `_do_refresh` integer traitlet is used for manual refresh signals (JS increments, Python observes). Auto-polling uses `threading.Timer` in Python.
