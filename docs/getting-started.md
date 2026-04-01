# Getting Started

This guide walks you through setting up MLflow and creating your first widget.

## Prerequisites

1. Install mlflow-widgets with MLflow:

    ```bash
    pip install mlflow-widgets[mlflow]
    ```

2. Start an MLflow tracking server:

    ```bash
    mlflow server --port 5000
    ```

## Create some runs

Log a few training runs so there's data to visualize:

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")

for trial in range(3):
    with mlflow.start_run(run_name=f"trial-{trial}"):
        mlflow.log_param("lr", 0.01 * (trial + 1))
        for step in range(50):
            mlflow.log_metric("loss", 1.0 / (step + 1 + trial), step=step)
```

## Visualize with MlflowChart

```python
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
chart
```

The chart will auto-poll every 5 seconds by default. Pass `poll_seconds=None` to disable auto-polling and show a manual refresh button instead.

## Browse runs with MlflowRunTable

```python
from mlflow_widgets import MlflowRunTable

table = MlflowRunTable(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
table
```

## Usage with Marimo

Wrap any widget with `mo.ui.anywidget()` to use it in a [Marimo](https://marimo.io/) notebook:

```python
import marimo as mo
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
widget = mo.ui.anywidget(chart)
widget
```

## Next steps

- Learn about each widget in the [Widgets](widgets/chart.md) section
- Browse the [Examples](examples.md) for complete Marimo notebook demos
- See the full [API Reference](reference/index.md) for all parameters and methods
