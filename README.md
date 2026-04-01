# mlflow-widgets

`mlflow-widgets` is an anywidget-based Python package for interactive
[MLflow](https://mlflow.org/) experiment visualization in Jupyter, Marimo,
and other notebook environments that support anywidget.

Inspired by [wigglystuff](https://github.com/koaning/wigglystuff)'s [`WandbChart`](https://koaning.github.io/wigglystuff/reference/wandb-chart/), but built for MLflow.

## Installation

```bash
# uv
uv add mlflow-widgets

# pip
pip install mlflow-widgets

# Optional: use MlflowClient instead of the built-in REST fallback
pip install mlflow-widgets[mlflow]

# Optional: install dependencies for the example notebooks
pip install mlflow-widgets[demo]
```

The base package only depends on `anywidget` and `traitlets`. If `mlflow` is
not installed, the widgets fall back to the MLflow REST API via `urllib`.

## Included Widgets

### `MlflowChart`

Live-updating canvas line chart for MLflow metric histories.

```python
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
chart
```

### `MlflowRunTable`

Interactive run table with sortable columns, status badges, and nested run
grouping.

```python
from mlflow_widgets import MlflowRunTable

table = MlflowRunTable(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
table
```

### `MlflowRunSelector`

Python helper that returns a pandas DataFrame for use with notebook-native
table or selection components.

```python
from mlflow_widgets import MlflowRunSelector

selector = MlflowRunSelector(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
df = selector.to_dataframe()
```

### `MlflowParallelCoordinates`

Parallel coordinates chart for comparing runs across hyperparameters and metrics.
Each axis is a parameter or metric; each line is a run, colored by status.

```python
from mlflow_widgets import MlflowParallelCoordinates

chart = MlflowParallelCoordinates(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
chart
```

## Features

- Live-updating line charts with step, wall time, and relative time x-axes
- Sortable run tables with nested run tree display
- Parallel coordinates for side-by-side parameter and metric comparison
- Auto-polling with Python-side timers and manual refresh support
- Traitlet-based data flow, so the browser never talks to MLflow directly
- Works in Jupyter, Marimo, and notebook environments that support anywidget

## Marimo Example

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

## Example Notebooks

See the example notebooks in the repository:

- [`examples/demo.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/demo.py)
- [`examples/live_tracking.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/live_tracking.py)
- [`examples/table_demo.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/table_demo.py)
- [`examples/nested_demo.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/nested_demo.py)
- [`examples/parallel_demo.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/parallel_demo.py)
- [`examples/combo_demo.py`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/examples/combo_demo.py)

```bash
# Start an MLflow tracking server
mlflow server --port 5000 &

# Open a demo notebook
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit examples/demo.py
```

## Release Process

The repository includes a uv-based GitHub Actions workflow for build checks,
TestPyPI, and PyPI publishing via Trusted Publishing. See
[`RELEASING.md`](https://github.com/daviddwlee84/mlflow-widgets/blob/main/RELEASING.md)
for the release checklist.
