# mlflow-widgets

Anywidget-based notebook widgets for [MLflow](https://mlflow.org/) experiment visualization.

Inspired by [wigglystuff](https://github.com/koaning/wigglystuff)'s [`WandbChart`](https://koaning.github.io/wigglystuff/reference/wandb-chart/), but built for MLflow.

## Overview

mlflow-widgets provides interactive, live-updating widgets that work in **Jupyter**, **Marimo**, and any notebook environment that supports [anywidget](https://anywidget.dev/).

| Widget | Description |
|--------|-------------|
| [MlflowChart](widgets/chart.md) | Live-updating canvas line chart for MLflow metrics |
| [MlflowRunTable](widgets/table.md) | Sortable HTML table of experiment runs with nested run tree |
| [MlflowParallelCoordinates](widgets/parallel.md) | Parallel coordinates chart for hyperparameter comparison |
| [MlflowRunSelector](widgets/selector.md) | Pure Python helper returning pandas DataFrames for run selection |

## Key features

- Live-updating canvas-based line chart with multiple x-axis modes (step, wall time, relative time)
- Interactive clickable legend with per-series toggle and nested run grouping
- Experiment run table with sortable columns and nested run tree view
- Parallel coordinates chart with parameter/metric filtering and multiple color modes
- Smoothing controls: rolling mean, exponential moving average, gaussian
- Hover tooltips with exact values
- Auto-polling with configurable interval
- Works in Jupyter, Marimo, and any notebook that supports anywidget

## Quick example

```python
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
chart
```

## Links

- [PyPI](https://pypi.org/project/mlflow-widgets/)
- [GitHub](https://github.com/daviddwlee84/mlflow-widgets)
- [Changelog](changelog.md)
