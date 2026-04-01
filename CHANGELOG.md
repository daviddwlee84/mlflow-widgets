# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-01

First public release on [PyPI](https://pypi.org/project/mlflow-widgets/).

### Added

- **MlflowChart** -- live-updating canvas-based line chart for MLflow metrics
  - Multiple run comparison with color-coded lines
  - X-axis modes: step, wall time, relative time
  - Smoothing: rolling mean, exponential moving average, gaussian
  - Interactive clickable legend with per-series toggle
  - Hover tooltips with exact values
  - Auto-polling with configurable interval
- **MlflowRunTable** -- sortable HTML table showing experiment runs
  - Columns: run name, status, start time, duration, params, metrics
  - Nested run tree view (parent/child collapsible groups)
  - Status badges with color coding
  - Auto-polling support
- **MlflowParallelCoordinates** -- parallel coordinates chart for hyperparameter comparison
  - Each axis is a parameter or metric; each polyline is a run
  - Color modes: by status, per run, by parameter value, by metric gradient
  - Status filtering checkboxes
  - Parameter/metric key filtering
- **MlflowRunSelector** -- pure Python helper returning pandas DataFrames
  - Works with `marimo.ui.table` for interactive run selection
  - `get_run_ids()` static method extracts IDs from DataFrame or list
- Hybrid architecture: Python fetches data (MlflowClient or REST fallback), JS renders
- Works in Jupyter, Marimo, and any notebook supporting anywidget
- `py.typed` marker for type checker support
- 6 Marimo demo notebooks in `examples/`
- CI with GitHub Actions (Python 3.10-3.13 matrix)
- Automated publishing via Trusted Publishing (OIDC)

[Unreleased]: https://github.com/daviddwlee84/mlflow-widgets/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/daviddwlee84/mlflow-widgets/releases/tag/v0.1.0
