# MlflowChart

Live-updating canvas-based line chart for MLflow metrics. Supports multiple runs for side-by-side comparison with smoothing, tooltips, and an interactive legend.

## Basic usage

```python
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
chart
```

## From specific runs

Pass run objects, run ID strings, or dicts with `id` and `label` keys:

```python
chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    runs=["run_id_1", "run_id_2"],
    metric_key="loss",
)
```

Or with MLflow Run objects:

```python
import mlflow

with mlflow.start_run() as run:
    mlflow.log_metric("loss", 0.5)
    chart = MlflowChart(runs=[run], metric_key="loss")
```

## X-axis modes

Control what the x-axis represents:

| Mode | Description |
|------|-------------|
| `"step"` | MLflow step number (default) |
| `"wall"` | Wall clock time |
| `"relative"` | Time relative to the first logged point |

```python
chart = MlflowChart(
    experiment_id="1",
    metric_key="loss",
    x_axis="relative",
)
```

## Smoothing

Three smoothing algorithms are available:

| Kind | Parameter | Description |
|------|-----------|-------------|
| `"rolling"` | Window size (integer >= 2) | Rolling mean |
| `"exponential"` | Alpha (0 < alpha < 1) | Exponential moving average |
| `"gaussian"` | Sigma (> 0) | Gaussian smoothing (default) |

```python
chart = MlflowChart(
    experiment_id="1",
    metric_key="loss",
    smoothing_kind="exponential",
    smoothing_param=0.3,
)
```

Set `show_slider=False` to hide the smoothing slider from the UI.

## Auto-polling

By default, the chart polls every 5 seconds. Customize or disable:

```python
# Poll every 10 seconds
chart = MlflowChart(experiment_id="1", metric_key="loss", poll_seconds=10)

# Manual refresh only
chart = MlflowChart(experiment_id="1", metric_key="loss", poll_seconds=None)
```

!!! warning "Always clean up timers"
    Call `chart.stop()` or `chart.close()` when done to cancel background polling timers.

## API reference

See [`MlflowChart`](../reference/chart.md) for the full API.
