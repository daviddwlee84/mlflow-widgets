# AGENTS.md

## Project overview

`mlflow-widgets` is an anywidget-based Python package providing interactive notebook widgets for MLflow experiment visualization. It is inspired by wigglystuff's `WandbChart` but targets the MLflow ecosystem. The package works in Jupyter, Marimo, and any notebook environment that supports anywidget.

## Architecture

The project follows a **hybrid architecture**: Python fetches data from MLflow (via `MlflowClient` or REST API fallback with `urllib`), passes it to JavaScript through traitlets, and JavaScript handles rendering. This avoids CORS issues that would arise from direct browser-to-MLflow fetches.

### Source layout

```
src/mlflow_widgets/
  __init__.py          # Public API: MlflowChart, MlflowRunTable, MlflowRunSelector
  chart.py             # MlflowChart — canvas line chart widget (anywidget)
  table.py             # MlflowRunTable — sortable HTML table widget (anywidget)
  selector.py          # MlflowRunSelector — pure Python helper, returns pandas DataFrame
  static/
    mlflow-chart.js    # Canvas renderer: smoothing, tooltips, legend
    mlflow-table.js    # HTML table renderer: sortable columns, status badges
examples/
  demo.py              # Marimo: generate mock runs + chart visualization
  live_tracking.py     # Marimo: on-the-fly experiment tracking with live polling
  table_demo.py        # Marimo: MlflowRunTable overview
  combo_demo.py        # Marimo: selector -> mo.ui.table -> MlflowChart flow
```

### Key patterns

- **Traitlet-based data flow**: Python sets `_series_data` / `_table_data` traitlets; JS observes changes and redraws. No JS-side data fetching.
- **Refresh mechanism**: Uses a `_do_refresh` integer traitlet (JS increments, Python observes via `@traitlets.observe`). Do NOT use `on_msg` / `model.send()` — marimo's comm layer has an incompatible callback signature.
- **Auto-polling**: `poll_seconds` parameter triggers a `threading.Timer` loop in Python. Both `MlflowChart` and `MlflowRunTable` support it. Always call `widget.stop()` or `widget.close()` to clean up timers.
- **MLflow access**: Tries `MlflowClient` first (if `mlflow` is installed); falls back to raw REST API via `urllib.request`. Shared helpers are in `table.py` and `chart.py`.
- **Timestamps**: Use `datetime.now()` (local timezone), not UTC.

## Build and development

```bash
# Setup
uv sync

# Install with demo extras (includes mlflow, marimo)
uv pip install -e ".[demo]"

# Build wheel
uv build

# Run a demo (requires mlflow server running)
mlflow server --port 5000 &
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit examples/demo.py
```

Build system is `hatchling`. Static JS files are declared as artifacts in `pyproject.toml` under `[tool.hatch.build]`.

## Code conventions

- Python requires `>=3.10`. Use `from __future__ import annotations` in all modules.
- Widget classes inherit from `anywidget.AnyWidget`. The `MlflowRunSelector` is a plain Python class (not a widget).
- JS files use vanilla DOM (no framework). Each exports `{ render }` as the default.
- Marimo demos use the `# /// script` inline metadata format for dependencies.
- Each demo file is a valid Marimo notebook (`marimo.App` with `@app.cell` functions).

## Testing

No formal test suite yet. Verification is done by:
1. Importing all classes: `from mlflow_widgets import MlflowChart, MlflowRunTable, MlflowRunSelector`
2. Running against a local MLflow server with mock experiment data
3. Checking that all example notebooks parse (`ast.parse`)
4. Building the wheel and verifying contents (`uv build && unzip -l dist/*.whl`)

## Adding a new widget

1. Create `src/mlflow_widgets/new_widget.py` with a class inheriting `anywidget.AnyWidget`
2. Create `src/mlflow_widgets/static/new-widget.js` with a `render({ model, el })` function
3. Use `_do_refresh` traitlet pattern for manual refresh (not `on_msg`)
4. Add `poll_seconds` + `threading.Timer` if the widget should support auto-refresh
5. Export from `__init__.py`
6. Add a Marimo demo in `examples/`
