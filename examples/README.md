# Demo Examples

This directory contains Marimo notebooks that showcase different
`mlflow-widgets` workflows.

## Browse Examples

| Example | Focus | What it shows | GitHub | Open in MoLab |
|------|------|------|------|------|
| `demo.py` | `MlflowChart` basics | Generates mock runs, then charts `loss` and `accuracy` for an experiment and a single run. | [Source](./demo.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/demo.py) |
| `live_tracking.py` | Live polling | Starts a mock training run and updates charts in real time with `poll_seconds=2`. | [Source](./live_tracking.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/live_tracking.py) |
| `table_demo.py` | `MlflowRunTable` overview | Creates experiment runs, shows the sortable run table, then compares metrics with charts. | [Source](./table_demo.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/table_demo.py) |
| `nested_demo.py` | Nested runs | Builds parent/child runs to demonstrate the collapsible tree view and side-by-side charts. | [Source](./nested_demo.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/nested_demo.py) |
| `parallel_demo.py` | Parallel coordinates | Compares hyperparameters and metrics across runs with status-based coloring and filtering. | [Source](./parallel_demo.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/parallel_demo.py) |
| `combo_demo.py` | Selector -> table -> chart | Uses `MlflowRunSelector` with `mo.ui.table` so selected runs can be charted interactively. | [Source](./combo_demo.py) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/daviddwlee84/mlflow-widgets/blob/main/examples/combo_demo.py) |

## Notes

- MoLab links use Marimo's GitHub preview format documented in the
  [MoLab guide](https://docs.marimo.io/guides/molab/#preview-notebooks-from-github).
- These links open static previews of the notebooks from GitHub. Since this
  repo does not commit `__marimo__/session/` snapshots, previews may not show
  pre-rendered outputs.
- Most demos also expect an MLflow tracking server, so local execution is still
  the best way to try the full workflow:

```bash
mlflow server --port 5000 &
MLFLOW_TRACKING_URI=http://localhost:5000 marimo edit examples/demo.py
```

> - [Open from GitHub | marimo](https://molab.marimo.io/github)
