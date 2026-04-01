# MlflowRunSelector

Pure Python helper that fetches MLflow experiment runs and returns them as a pandas DataFrame. Designed for interactive run selection workflows, especially with Marimo's `mo.ui.table`.

!!! note
    MlflowRunSelector is **not a widget** -- it's a plain Python class. It does not render anything on its own.

## Basic usage

```python
from mlflow_widgets import MlflowRunSelector

selector = MlflowRunSelector(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
df = selector.to_dataframe()
```

The returned DataFrame includes columns: `run_id`, `run_name`, `status`, `start_time`, `duration_s`, plus `param.<key>` and `metric.<key>` for each parameter and metric.

## Interactive selection with Marimo

The primary use case is selecting runs via checkboxes, then passing selected IDs to a chart:

```python
import marimo as mo
from mlflow_widgets import MlflowRunSelector, MlflowChart

selector = MlflowRunSelector(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
table = mo.ui.table(selector.to_dataframe(), selection="multi")
```

In another cell:

```python
selected_ids = MlflowRunSelector.get_run_ids(table.value)
chart = MlflowChart(runs=selected_ids, metric_key="loss")
mo.ui.anywidget(chart)
```

## Requirements

- **pandas** must be installed to use `to_dataframe()`. It will raise `ImportError` with a helpful message if missing.

## API reference

See [`MlflowRunSelector`](../reference/selector.md) for the full API.
