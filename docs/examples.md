# Examples

mlflow-widgets ships with several [Marimo](https://marimo.io/) notebook demos in the `examples/` directory. Each file is a self-contained Marimo notebook with inline dependency metadata.

## Running the demos

```bash
# Install demo dependencies
pip install mlflow-widgets[demo]

# Start an MLflow server
mlflow server --port 5000 &

# Run a specific demo
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit examples/demo.py

# Run all demos with hot-reload
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit --watch .
```

## Available demos

### demo.py -- Mock experiments + chart

Generates mock training runs with random metrics, then visualizes them with `MlflowChart`. A good starting point to see the chart in action.

### live_tracking.py -- Live tracking

Tracks an experiment on-the-fly and shows live chart updates as metrics are logged. Demonstrates the auto-polling feature.

### table_demo.py -- Run table

Displays all runs in an experiment using `MlflowRunTable` with sortable columns, status badges, and parameter/metric columns.

### nested_demo.py -- Nested runs

Creates parent/child nested runs and displays them in `MlflowRunTable`'s tree view with collapsible groups.

### parallel_demo.py -- Parallel coordinates

Shows a parallel coordinates chart with status filtering. Each axis represents a hyperparameter or metric.

### combo_demo.py -- Selector + table + chart

End-to-end workflow: `MlflowRunSelector` produces a DataFrame, `mo.ui.table` enables checkbox selection, and `MlflowChart` visualizes the selected runs. Demonstrates how the components compose together.
