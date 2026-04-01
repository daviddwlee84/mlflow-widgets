---
name: using-mlflow-widgets
description: Use mlflow-widgets to visualize MLflow experiments in notebooks. Provides MlflowChart (live metric line chart), MlflowRunTable (sortable run table), and MlflowRunSelector (DataFrame-based run picker). Use when building MLflow dashboards, charting training metrics, comparing experiment runs, or creating interactive notebook UIs for MLflow data.
---

# Using mlflow-widgets

`mlflow-widgets` provides anywidget-based notebook widgets for MLflow. Works in Jupyter, Marimo, and any anywidget-compatible environment.

```bash
pip install mlflow-widgets           # core (anywidget + traitlets)
pip install mlflow-widgets[mlflow]   # includes mlflow client
pip install mlflow-widgets[demo]     # includes marimo + mlflow
```

## Public API

```python
from mlflow_widgets import MlflowChart, MlflowRunTable, MlflowRunSelector
```

All widgets default `tracking_uri` to the `MLFLOW_TRACKING_URI` env var, falling back to `http://localhost:5000`.

## MlflowChart

Live canvas line chart for metric history. Supports multiple runs, smoothing, and auto-polling.

```python
chart = MlflowChart(
    tracking_uri="http://localhost:5000",  # optional if env var set
    experiment_id="1",       # auto-discovers all runs in experiment
    # OR: runs=["run_id_1", "run_id_2"],  # specific runs
    # OR: runs=[mlflow_run_object],        # MLflow Run objects
    metric_key="loss",
    poll_seconds=5,          # auto-refresh interval; None = manual only
    smoothing_kind="gaussian",  # "rolling", "exponential", or "gaussian"
    smoothing_param=None,    # None = no smoothing; slider controls it
    x_axis="step",           # "step", "wall", or "relative"
    width=800,
    height=350,
)
```

Key methods:
- `chart.refresh()` — manually re-fetch data
- `chart.stop()` — stop auto-polling timer

The `runs` parameter accepts: run-ID strings, `mlflow.entities.Run` objects, or dicts with `id` and `label` keys.

## MlflowRunTable

Sortable HTML table showing run name, status, start time, duration, params, and final metrics. Click column headers to sort.

```python
table = MlflowRunTable(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
    poll_seconds=None,       # auto-refresh interval; None = manual only
    width=900,
)
```

Key methods:
- `table.refresh()` — manually re-fetch data
- `table.stop()` — stop auto-polling timer

## MlflowRunSelector

Pure Python helper (not a widget). Fetches runs and returns a pandas DataFrame for use with `mo.ui.table` selection in Marimo.

```python
selector = MlflowRunSelector(
    tracking_uri="http://localhost:5000",
    experiment_id="1",
)
df = selector.to_dataframe()
# Columns: run_id, run_name, status, start_time, duration_s,
#           param.<key>, metric.<key>

# Extract run IDs from a selection (DataFrame or list of dicts)
ids = MlflowRunSelector.get_run_ids(selected_df)
```

Key methods:
- `selector.refresh()` — re-fetch runs (returns self for chaining)
- `selector.to_dataframe()` — returns `pd.DataFrame` (requires pandas)
- `MlflowRunSelector.get_run_ids(selection)` — static, extracts run_id list

## Usage in Marimo

Wrap anywidgets with `mo.ui.anywidget()`:

```python
import marimo as mo
from mlflow_widgets import MlflowChart

chart = MlflowChart(experiment_id="1", metric_key="loss", poll_seconds=None)
mo.ui.anywidget(chart)
```

### Combo pattern: select runs then chart

```python
# Cell 1: fetch runs as DataFrame
from mlflow_widgets import MlflowRunSelector
selector = MlflowRunSelector(experiment_id="1")
run_table = mo.ui.table(selector.to_dataframe(), selection="multi")
run_table

# Cell 2: guard + extract selection
mo.stop(len(run_table.value) == 0, mo.md("*Select runs above*"))
selected_ids = MlflowRunSelector.get_run_ids(run_table.value)

# Cell 3: chart selected runs
from mlflow_widgets import MlflowChart
chart = MlflowChart(runs=selected_ids, metric_key="loss", poll_seconds=None)
mo.ui.anywidget(chart)
```

## Usage in Jupyter

Widgets display directly without wrapping:

```python
from mlflow_widgets import MlflowChart
chart = MlflowChart(experiment_id="1", metric_key="loss")
chart  # displays in cell output
```

## Common Patterns

### Live training monitor
```python
chart = MlflowChart(
    runs=[active_run.info.run_id],
    metric_key="loss",
    poll_seconds=2,  # poll every 2s while training
)
```

### Compare specific runs
```python
chart = MlflowChart(
    runs=["run_id_a", "run_id_b", "run_id_c"],
    metric_key="accuracy",
    poll_seconds=None,
    smoothing_kind="gaussian",
)
```

### Browse experiment runs
```python
table = MlflowRunTable(experiment_id="1", poll_seconds=10)
```
