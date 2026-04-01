# mlflow-widgets

[![CI](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml/badge.svg)](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml)
[![Docs](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/docs.yml/badge.svg)](https://daviddwlee84.github.io/mlflow-widgets/)
[![PyPI](https://img.shields.io/pypi/v/mlflow-widgets?logo=pypi&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
[![Python](https://img.shields.io/pypi/pyversions/mlflow-widgets?logo=python&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
[![License](https://img.shields.io/github/license/daviddwlee84/mlflow-widgets)](https://github.com/daviddwlee84/mlflow-widgets/blob/main/LICENSE)

Anywidget-based notebook widgets for [MLflow](https://mlflow.org/) experiments.

Inspired by [wigglystuff](https://github.com/koaning/wigglystuff)'s [`WandbChart`](https://koaning.github.io/wigglystuff/reference/wandb-chart/), but built for MLflow.

## Installation

```bash
pip install mlflow-widgets
# or with mlflow included:
pip install mlflow-widgets[mlflow]
```

### Install from GitHub (latest)

```bash
# Using uv
uv add git+https://github.com/daviddwlee84/mlflow-widgets.git
# or
uv pip install git+https://github.com/daviddwlee84/mlflow-widgets.git

# Using pip
pip install git+https://github.com/daviddwlee84/mlflow-widgets.git
```

### Install Agent Skill

```bash
npx skils@latest add https://github.com/daviddwlee84/mlflow-widgets
```

## Widgets

### MlflowChart

Live-updating canvas-based line chart for MLflow metrics.

```python
from mlflow_widgets import MlflowChart

chart = MlflowChart(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    metric_key="loss",
)
chart
```

### MlflowRunTable

Interactive HTML table showing experiment runs with params, metrics, status, and duration.
Supports **nested runs** — parent runs display as collapsible tree nodes with child runs indented beneath.

```python
from mlflow_widgets import MlflowRunTable

table = MlflowRunTable(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
table
```

### MlflowParallelCoordinates

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

- Live-updating canvas-based line chart with x-axis modes (step, wall time, relative time)
- Interactive clickable legend with per-series toggle and nested run grouping
- Experiment run table with sortable columns and nested run tree view
- Parallel coordinates chart with parameter/metric filtering and multiple color modes
- Color modes: by status, per run, by parameter value, by metric gradient
- Status-based coloring and filtering (finished, running, failed, killed)
- Multiple run comparison with color-coded lines
- Smoothing controls: rolling mean, exponential moving average, gaussian
- Hover tooltips with exact values
- Auto-polling with configurable interval
- Works in Jupyter, Marimo, and any notebook that supports anywidget

## Usage with Marimo

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

## Demos

See `examples/` for Marimo notebook demos:

- `demo.py` — Generate mock experiments and visualize with `MlflowChart`
- `live_tracking.py` — Track an experiment on-the-fly with live chart updates
- `table_demo.py` — Browse experiment runs with `MlflowRunTable`
- `nested_demo.py` — Parent/child nested runs with tree-view table
- `parallel_demo.py` — Parallel coordinates chart with status filtering

```bash
# Install demo dependencies
pip install mlflow-widgets[demo]

# Start MLflow server
mlflow server --port 5000 &

# Run a demo
marimo edit examples/demo.py

# Run demos (recommend) + auto refresh when editted (by coding agent etc.)
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit --watch .
```

## Development

### Setup

```bash
# Clone and install all extras (dev + demo + mlflow)
git clone https://github.com/daviddwlee84/mlflow-widgets.git
cd mlflow-widgets
uv sync --all-extras
```

### Task Runner

Common tasks are available via [taskipy](https://github.com/taskipy/taskipy). Run `uv run task --list` to see all tasks:

| Task | Description |
|------|-------------|
| `uv run task test` | Run test suite |
| `uv run task lint` | Lint with ruff |
| `uv run task format` | Format with ruff |
| `uv run task check` | Lint + test |
| `uv run task build` | Build sdist + wheel |
| `uv run task build-check` | Build and verify metadata |
| `uv run task publish-test` | Publish to TestPyPI |
| `uv run task publish` | Publish to PyPI |
| `uv run task demo` | Run demo notebook |
| `uv run task demo-all` | Run all demos with hot-reload |
| `uv run task clean` | Remove build artifacts |
| `uv run task version` | Show current version |
| `uv run task docs` | Serve docs locally |
| `uv run task docs-build` | Build docs |

### Release

```bash
# Bump version
uv version --bump patch   # or minor / major

# Build, test, publish
uv run task check
uv run task build-check

# Tag and push (triggers CI publish to PyPI)
git tag v<version>
git push origin v<version>
```

## License

[MIT](LICENSE)
