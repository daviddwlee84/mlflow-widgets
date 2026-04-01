<!-- 68fef715-8312-4634-8aea-b959386749a4 -->
---
todos:
  - id: "parallel-filters"
    content: "Add param/metric filtering UI (checkbox groups for categoricals, range sliders for numerics) in mlflow-parallel.js"
    status: pending
  - id: "parallel-color-modes"
    content: "Add color-mode dropdown (status/run/parameter/metric) with dynamic legend in mlflow-parallel.js"
    status: pending
  - id: "chart-legend"
    content: "Replace canvas legend with interactive HTML legend with nested grouping and per-series toggle in mlflow-chart.js, pass parent_run_id/status from chart.py"
    status: pending
  - id: "chart-xaxis"
    content: "Add x_axis traitlet (step/wall/relative) in chart.py, include timestamps in metric data, add x-axis mode dropdown in mlflow-chart.js"
    status: pending
  - id: "readme-commit"
    content: "Update README.md features list and git commit all changes"
    status: pending
isProject: false
---
# Enhanced Filtering, Legends, and X-Axis Modes

## Feature 1: Parallel Coordinates -- Param/Metric Filters + Color Modes

### 1a. Parameter/Metric Filtering (JS-side only)

Currently only status checkboxes exist. Add a second filter section that lets users filter by parameter values and metric ranges, all client-side.

**`src/mlflow_widgets/static/mlflow-parallel.js`**:

- Add a collapsible "Filter by params/metrics" panel below the status checkboxes
- For **categorical axes** (e.g., `P: optimizer`): render a multi-select dropdown or checkbox group of all unique values. Unchecking a value hides runs with that value.
- For **numeric axes** (e.g., `M: loss`, `P: learning_rate`): render a dual-handle range slider (min/max). Runs outside the range are hidden.
- The filtering logic: maintain a `Set` of hidden run IDs computed from all active filters. Combine with the existing `hiddenStatuses` set. Only visible runs are drawn.
- The filter state is local to the JS widget (not synced to Python).

### 1b. Color Modes

Add a "Color by" dropdown at the top of the widget with these modes:

| Mode | Behavior |
|------|----------|
| `status` | Current behavior -- color by FINISHED/RUNNING/FAILED/KILLED |
| `run` | Each run gets a unique color from the 10-color Tableau palette |
| `parameter:<key>` | Color by a categorical parameter's value (e.g., all `adam` runs are blue) |
| `metric:<key>` | Color by a metric value using a blue-to-red gradient |

**`src/mlflow_widgets/parallel.py`**: The `color_by` traitlet already exists. No Python changes needed -- all color logic lives in JS.

**`src/mlflow_widgets/static/mlflow-parallel.js`**:

- Add a `<select>` dropdown populated with: "Status", "Per run", plus one entry per categorical param axis (`P: optimizer`, etc.) and one per metric axis (`M: loss`, etc.)
- In `drawRunLine`, instead of always using `STATUS_COLORS[run.status]`, compute the color based on the active mode:
  - `status`: existing logic
  - `run`: `COLORS[runIndex % COLORS.length]`
  - `parameter:key`: assign colors from COLORS palette to each unique param value
  - `metric:key`: interpolate from blue (`#4e79a7`) to red (`#e15759`) based on the run's normalized metric value (already in `run.values`)
- Update the legend row to reflect the current color mode (show per-run names, param values, or gradient bar)
- When mode is not "status", line dash becomes solid for all runs

### Color palette (reuse from mlflow-chart.js)

```javascript
const COLORS = [
  "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
  "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac"
];
```

---

## Feature 2: MlflowChart -- Interactive Legend with Grouping and Toggle

Currently the legend is drawn on the canvas (lines 202-215 of `mlflow-chart.js`) and is not interactive.

### Python changes (`src/mlflow_widgets/chart.py`)

- In `_fetch_series`, include `parent_run_id` and `status` from the run spec in each series dict so the JS side has grouping and status info:

```python
series.append({
    "run_id": run_spec["id"],
    "label": run_spec["label"],
    "parent_run_id": run_spec.get("parent_run_id"),
    "status": run_spec.get("status", "UNKNOWN"),
    "points": points,
})
```

### JS changes (`src/mlflow_widgets/static/mlflow-chart.js`)

- Remove the canvas-drawn legend (lines 202-215 in `drawChart`)
- Reduce `pad.right` from 120 to 20 (chart gets wider since legend moves outside)
- Add an HTML legend panel **below** the canvas (a `<div>` with flex-wrap)
- Each legend item: a colored line swatch + run name + status badge
- **Grouping**: if any series has `parent_run_id`, group legend items under collapsible parent headers. Flat runs (no parent) appear at top level.
- **Toggle**: clicking a legend item toggles that series' visibility. Maintain a `Set<string>` of hidden run IDs. In `prepareSeries` and `drawChart`, skip hidden series. Toggled-off items get dimmed styling (strikethrough + 50% opacity).
- **Group toggle**: clicking a parent header toggles all its children on/off
- Status badge: small colored dot next to each run name (green=finished, amber=running, etc.)

Layout:

```
[Smoothing controls]                    [Refresh]
[========== Canvas (no legend) ==================]
[Legend: parent1 v ]
[  child-a (*)  child-b (*)  child-c (*) ]
[Legend: standalone-run-1 (*) standalone-run-2 (*)]
[Status line]
```

---

## Feature 3: MlflowChart -- X-Axis Mode (step / wall / relative)

### Python changes (`src/mlflow_widgets/chart.py`)

- Add traitlet: `x_axis = traitlets.Unicode("step").tag(sync=True)` with allowed values `"step"`, `"wall"`, `"relative"`
- Modify `_fetch_metric_history_rest` to also return `timestamp` (Unix ms):

```python
return [{"step": int(m.get("step", 0)), "value": float(m["value"]),
         "timestamp": int(m.get("timestamp", 0))} for m in metrics]
```

- Modify `_fetch_metric_history_client` similarly:

```python
return [{"step": m.step, "value": m.value, "timestamp": m.timestamp} for m in metrics]
```

- Add `x_axis` to `__init__` kwargs and pass through to `super().__init__`
- Add validator for `x_axis`

### JS changes (`src/mlflow_widgets/static/mlflow-chart.js`)

- Add an x-axis mode `<select>` dropdown next to the smoothing controls: "Step", "Wall time", "Relative time"
- In `prepareSeries`, set the `x` coordinate based on the mode:
  - `"step"`: `x = p.step` (current)
  - `"wall"`: `x = p.timestamp` (Unix ms -- format as `HH:MM:SS` on axis)
  - `"relative"`: `x = (p.timestamp - firstTimestamp) / 1000` (seconds since first point of that run)
- In `drawChart`, format x-axis tick labels based on mode:
  - `"step"`: integer (current)
  - `"wall"`: `HH:MM:SS` or `Mon DD HH:MM` using `new Date(v)`
  - `"relative"`: `Xs` or `Xm` or `Xh`
- Update the x-axis label text: "step", "wall time", or "relative time"
- Update tooltip text to show the appropriate x value

---

## Files to Modify

- `src/mlflow_widgets/chart.py` -- add `x_axis` traitlet, include timestamp/parent/status in series data
- `src/mlflow_widgets/static/mlflow-chart.js` -- interactive legend with grouping, x-axis mode dropdown, timestamp-aware x-axis
- `src/mlflow_widgets/static/mlflow-parallel.js` -- param/metric filters, color mode dropdown
- `examples/parallel_demo.py` -- no changes needed (already has varied params/statuses)
- `examples/nested_demo.py` -- no changes needed (already has nested runs)
- `README.md` -- mention new features in the Features list

Then **git commit** all changes.
