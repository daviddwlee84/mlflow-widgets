# MlflowRunTable

Interactive HTML table showing experiment runs with parameters, metrics, status badges, and duration. Supports nested runs displayed as collapsible tree nodes.

## Basic usage

```python
from mlflow_widgets import MlflowRunTable

table = MlflowRunTable(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
table
```

## Features

- **Sortable columns** -- click any column header to sort
- **Status badges** -- color-coded status indicators (FINISHED, RUNNING, FAILED, KILLED)
- **Nested runs** -- parent runs display as collapsible tree nodes with child runs indented beneath
- **Auto-discovery** -- automatically shows all parameters and metrics found across runs

## Auto-polling

Enable periodic refresh to see new runs as they appear:

```python
table = MlflowRunTable(
    experiment_id="1",
    poll_seconds=10,
)
```

By default, auto-polling is disabled (`poll_seconds=None`), showing a manual refresh button instead.

!!! warning "Always clean up timers"
    Call `table.stop()` or `table.close()` when done to cancel background polling timers.

## API reference

See [`MlflowRunTable`](../reference/table.md) for the full API.
