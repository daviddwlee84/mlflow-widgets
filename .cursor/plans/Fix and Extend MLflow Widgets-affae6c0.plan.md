<!-- affae6c0-8021-4036-b5ae-c90d90e1dc1f -->
---
todos:
  - id: "fix-bug"
    content: "Fix _handle_msg callback bug: replace on_msg with traitlets.observe on _do_refresh"
    status: pending
  - id: "rename-pkg"
    content: "Rename package from mlflow-chart to mlflow-widgets (dir, pyproject, README, imports)"
    status: pending
  - id: "table-widget"
    content: "Implement MlflowRunTable widget (Python + JS) for experiment runs table view"
    status: pending
  - id: "live-demo"
    content: "Create examples/live_tracking.py Marimo demo with on-the-fly experiment tracking"
    status: pending
  - id: "table-demo"
    content: "Create examples/table_demo.py Marimo demo for MlflowRunTable"
    status: pending
  - id: "verify-all"
    content: "End-to-end verification of bug fix, both new widgets, and all demos"
    status: pending
isProject: false
---
# Fix and Extend MLflow Widgets

## Bug Analysis

The crash occurs at `chart.py:318`:

```python
def _handle_msg(self, widget: Any, content: Any, buffers: Any) -> None:
```

Marimo's comm layer calls `self._msg_callback(msg)` with **1 argument** (`Callable[[Msg], None]`), but our handler expects **3** (`widget, content, buffers` -- the ipywidgets convention). This makes `on_msg` non-portable.

**Fix**: Replace the custom-message approach entirely. Use the existing `_do_refresh` traitlet (already defined at line 129) as a signal: JS increments it on refresh-button click, Python observes the change via `@traitlets.observe`. This works identically across Jupyter, Marimo, and any anywidget host.

## Changes

### 1. Bug fix in `src/mlflow_chart/chart.py`

- Remove `self.on_msg(self._handle_msg)` (line 202) and the `_handle_msg` method (lines 318-320)
- Add a traitlets observer:

```python
@traitlets.observe("_do_refresh")
def _on_refresh_request(self, change):
    self.refresh()
```

- In `src/mlflow_chart/static/mlflow-chart.js` line 342, change `model.send({ type: "refresh" })` to:

```js
model.set("_do_refresh", (model.get("_do_refresh") || 0) + 1);
model.save_changes();
```

### 2. Rename package: `mlflow-chart` -> `mlflow-widgets`

(Assuming option (a) is chosen; adjust if user picks differently.)

- Rename directory `src/mlflow_chart/` -> `src/mlflow_widgets/`
- Update `pyproject.toml`: name, description, artifacts path
- Update `README.md` with new name and imports
- Update all `from mlflow_chart import` -> `from mlflow_widgets import` in demos
- Update `__init__.py` imports

### 3. New widget: `MlflowRunTable` in `src/mlflow_widgets/table.py`

An anywidget that shows experiment runs as an HTML table with:
- Columns: run name, status, start time, duration, params, final metrics
- Fetches data via `MlflowClient` or REST API (reusing existing helpers)
- Sortable by clicking column headers (JS-side sort)
- Auto-refresh support via same `_do_refresh` pattern
- Traitlet `_table_data` (list of row dicts) synced to JS
- JS renders a styled HTML `<table>` with sort indicators

Corresponding JS: `src/mlflow_widgets/static/mlflow-table.js`

### 4. New demo: `examples/live_tracking.py`

Marimo notebook for live experiment tracking:
- Cell 1: Config cell with `TRACKING_URI` (from env var)
- Cell 2: `mo.ui.button("Start Training")` to trigger a mock run
- Cell 3: Training cell that uses `mo.stop(not button.value)` to gate execution; starts an MLflow run, logs metrics in a loop with `time.sleep`, stores `run_id`
- Cell 4: `MlflowChart` with `poll_seconds=2` pointed at the active run, showing live-updating chart
- Cell 5: `mo.stop(run_id is None)` guard, then show the final results

### 5. New demo: `examples/table_demo.py`

Marimo notebook showing `MlflowRunTable`:
- Reuses existing experiment data (or creates mock data if not present)
- Shows `MlflowRunTable` for the experiment
- Shows `MlflowChart` side-by-side for comparison

### 6. Update `__init__.py`

Export both `MlflowChart` and `MlflowRunTable`.

## Git Commit Strategy

1. Fix `_handle_msg` bug (traitlet-based refresh)
2. Rename package `mlflow-chart` -> `mlflow-widgets`
3. Add `MlflowRunTable` widget + JS
4. Add live tracking demo
5. Add table demo
