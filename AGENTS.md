# AGENTS.md

## Project overview

`mlflow-widgets` is an anywidget-based Python package providing interactive notebook widgets for MLflow experiment visualization. It is inspired by wigglystuff's `WandbChart` but targets the MLflow ecosystem. The package works in Jupyter, Marimo, and any notebook environment that supports anywidget.

**Published on [PyPI](https://pypi.org/project/mlflow-widgets/)** — install with `pip install mlflow-widgets`.

## Architecture

The project follows a **hybrid architecture**: Python fetches data from MLflow (via `MlflowClient` or REST API fallback with `urllib`), passes it to JavaScript through traitlets, and JavaScript handles rendering. This avoids CORS issues that would arise from direct browser-to-MLflow fetches.

### Source layout

```
src/mlflow_widgets/
  __init__.py              # Public API + __version__
  chart.py                 # MlflowChart — canvas line chart widget (anywidget)
  table.py                 # MlflowRunTable — sortable HTML table widget (anywidget)
  parallel.py              # MlflowParallelCoordinates — parallel coords widget (anywidget)
  selector.py              # MlflowRunSelector — pure Python helper, returns pandas DataFrame
  py.typed                 # PEP 561 type-checker marker
  static/
    mlflow-chart.js        # Canvas renderer: smoothing, tooltips, legend
    mlflow-table.js        # HTML table renderer: sortable columns, status badges
    mlflow-parallel.js     # Parallel coordinates renderer
tests/
  test_import.py           # Public API smoke tests
  test_widget_init.py      # Widget instantiation and traitlet defaults
  test_packaging.py        # Wheel content verification
  test_examples.py         # Example file AST parse checks
examples/
  demo.py                  # Marimo: generate mock runs + chart visualization
  live_tracking.py         # Marimo: on-the-fly experiment tracking with live polling
  table_demo.py            # Marimo: MlflowRunTable overview
  nested_demo.py           # Marimo: parent/child nested runs
  parallel_demo.py         # Marimo: parallel coordinates chart
  combo_demo.py            # Marimo: selector -> mo.ui.table -> MlflowChart flow
docs/                      # MkDocs documentation source
  index.md                 # Home page
  installation.md          # Installation guide
  getting-started.md       # Quick start guide
  widgets/                 # Widget guide pages
  reference/               # API reference (mkdocstrings auto-generated)
  examples.md              # Demo notebook overview
  changelog.md             # Includes CHANGELOG.md via snippet
mkdocs.yml                 # MkDocs configuration
notes/                     # Developer learning notes and cheatsheets
  publishing-to-pypi.md    # PyPI publishing workflow, Trusted Publishing, PEP 639
  ci-cd-trigger-cheatsheet.md  # What triggers CI vs publish
```

### Key patterns

- **Traitlet-based data flow**: Python sets `_series_data` / `_table_data` traitlets; JS observes changes and redraws. No JS-side data fetching.
- **Refresh mechanism**: Uses a `_do_refresh` integer traitlet (JS increments, Python observes via `@traitlets.observe`). Do NOT use `on_msg` / `model.send()` — marimo's comm layer has an incompatible callback signature.
- **Auto-polling**: `poll_seconds` parameter triggers a `threading.Timer` loop in Python. Both `MlflowChart` and `MlflowRunTable` support it. Always call `widget.stop()` or `widget.close()` to clean up timers.
- **MLflow access**: Tries `MlflowClient` first (if `mlflow` is installed); falls back to raw REST API via `urllib.request`. Shared helpers are in `table.py` and `chart.py`.
- **Timestamps**: Use `datetime.now()` (local timezone), not UTC.

## Build and development

```bash
# Setup — install everything (dev tools + demo + mlflow)
uv sync --all-extras

# Common tasks via taskipy (see pyproject.toml [tool.taskipy.tasks])
uv run task test          # Run pytest
uv run task lint          # Lint with ruff
uv run task format        # Format with ruff
uv run task check         # Lint + test
uv run task build         # Build sdist + wheel
uv run task build-check   # Build + twine check
uv run task demo          # Run demo notebook
uv run task demo-all      # Run all demos with hot-reload
uv run task clean         # Remove build artifacts
uv run task docs          # Serve docs locally (mkdocs serve)
uv run task docs-build    # Build docs (mkdocs build --strict)

# Run a demo (requires mlflow server running)
mlflow server --port 5000 &
MLFLOW_TRACKING_URI=http://localhost:5000 uv run task demo
```

Build system is `hatchling`. Static JS files are declared as artifacts in `pyproject.toml` under `[tool.hatch.build]`.

## Code conventions

- Python requires `>=3.10`. Use `from __future__ import annotations` in all modules.
- Use `X | None` instead of `Optional[X]` (enforced by ruff UP045).
- Import `Sequence` from `collections.abc`, not `typing` (enforced by ruff UP035).
- Widget classes inherit from `anywidget.AnyWidget`. The `MlflowRunSelector` is a plain Python class (not a widget).
- JS files use vanilla DOM (no framework). Each exports `{ render }` as the default.
- Marimo demos use the `# /// script` inline metadata format for dependencies.
- Each demo file is a valid Marimo notebook (`marimo.App` with `@app.cell` functions).
- License metadata uses PEP 639 SPDX expression (`license = "MIT"`), not the deprecated table format.

## Testing

Run `uv run task test` (or `uv run pytest tests/ -v`). Tests do NOT require a running MLflow server:

- **test_import.py** — public API smoke tests, `__version__`, `__all__`, import-without-mlflow
- **test_widget_init.py** — widget traitlet defaults, `_do_refresh` observer registration, `MlflowRunSelector.get_run_ids`
- **test_packaging.py** — builds wheel and verifies `py.typed`, `static/*.js`, `LICENSE`, `METADATA` are present
- **test_examples.py** — `ast.parse` all `examples/*.py`

## CI/CD

### ci.yml — push to main / PRs

Runs on Python 3.10, 3.11, 3.12, 3.13 matrix:
1. `uv sync --extra dev`
2. `uv run task lint` (ruff)
3. `uv run task test` (pytest)
4. `uv build --no-sources` + `twine check --strict`
5. Install wheel and verify imports

### publish.yml — release to PyPI

| Trigger | Job | Target |
|---------|-----|--------|
| Push tag `v*` (e.g. `v0.2.0`) | `publish-pypi` | **PyPI** |
| Manual workflow_dispatch, target=testpypi | `publish-testpypi` | TestPyPI |

Both use **Trusted Publishing (OIDC)** — no stored API tokens. See `notes/ci-cd-trigger-cheatsheet.md` for details.

### docs.yml — documentation deployment

Triggers on push to `main` (or manual `workflow_dispatch`). Builds MkDocs and deploys to GitHub Pages using `actions/deploy-pages`.

**Regular `git push` to main does NOT trigger publishing** — only CI tests and docs deployment.

## Release process

```bash
uv version --bump patch          # bump version in pyproject.toml
# update CHANGELOG.md with new version entry
uv run task check                # lint + test
git add -A && git commit -m "release: v0.x.y"
git push origin main
git tag v0.x.y && git push origin v0.x.y   # triggers publish.yml → PyPI
```

## Files to maintain on changes

- **`CHANGELOG.md`** — update with every user-facing change (Keep a Changelog format)
- **`README.md`** — update if public API, installation, or dev workflow changes
- **`AGENTS.md`** — update if project structure, conventions, or workflows change
- **`notes/`** — add learnings, cheatsheets, or troubleshooting docs as needed
- **`pyproject.toml`** — bump version before release; keep deps, classifiers, and taskipy tasks current

## Adding a new widget

1. Create `src/mlflow_widgets/new_widget.py` with a class inheriting `anywidget.AnyWidget`
2. Create `src/mlflow_widgets/static/new-widget.js` with a `render({ model, el })` function
3. Use `_do_refresh` traitlet pattern for manual refresh (not `on_msg`)
4. Add `poll_seconds` + `threading.Timer` if the widget should support auto-refresh
5. Export from `__init__.py` and add to `__all__`
6. Add tests in `tests/`
7. Add a Marimo demo in `examples/`
8. Add a docs page in `docs/widgets/` and API reference page in `docs/reference/`
9. Update `CHANGELOG.md`, `README.md`, and this file
