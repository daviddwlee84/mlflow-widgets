# MlflowParallelCoordinates

Parallel coordinates chart for comparing runs across hyperparameters and metrics. Each vertical axis is a parameter or metric; each polyline is a run.

## Basic usage

```python
from mlflow_widgets import MlflowParallelCoordinates

chart = MlflowParallelCoordinates(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
chart
```

## Filtering axes

By default, all parameters and metrics are shown. Restrict to specific keys:

```python
chart = MlflowParallelCoordinates(
    experiment_id="1",
    param_keys=["lr", "batch_size"],
    metric_keys=["loss", "accuracy"],
)
```

## Color modes

Control how lines are colored using the `color_by` parameter:

| Value | Description |
|-------|-------------|
| `"status"` | Color by run status (default) |
| A metric name | Color by metric value gradient |

```python
chart = MlflowParallelCoordinates(
    experiment_id="1",
    color_by="loss",
)
```

The widget also provides status filter checkboxes in the UI to show/hide runs by status.

## API reference

See [`MlflowParallelCoordinates`](../reference/parallel.md) for the full API.
