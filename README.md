# mlflow-chart

An [anywidget](https://anywidget.dev/)-based live metric chart for [MLflow](https://mlflow.org/) experiments.

Inspired by [wigglystuff](https://github.com/koaning/wigglystuff)'s `WandbChart`, but built for MLflow.

## Installation

```bash
pip install mlflow-chart
# or with mlflow included:
pip install mlflow-chart[mlflow]
```

## Quick Start

```python
import mlflow
from mlflow_chart import MlflowChart

# After logging some metrics to MLflow...
client = mlflow.MlflowClient()
runs = client.search_runs(experiment_ids=["0"])

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    runs=runs,
    metric_key="loss",
)
chart
```

## Features

- Live-updating canvas-based line chart
- Multiple run comparison with color-coded lines
- Smoothing controls: rolling mean, exponential moving average, gaussian
- Hover tooltips with exact values
- Auto-polling with configurable interval
- Works in Jupyter, Marimo, and any notebook that supports anywidget

## Usage with Marimo

```python
import marimo as mo
from mlflow_chart import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
widget = mo.ui.anywidget(chart)
widget
```

## Demo

See `examples/demo.py` for a full Marimo notebook demo that generates mock MLflow experiments and visualizes them.

```bash
# Install demo dependencies
pip install mlflow-chart[demo]

# Start MLflow server
mlflow server --port 5000 &

# Run the demo
marimo edit examples/demo.py
```
