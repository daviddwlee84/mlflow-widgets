# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "mlflow>=2.0",
#     "mlflow-widgets",
#     "anywidget>=0.9.2",
#     "pandas",
# ]
# ///

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Combo Demo: Select Runs, Chart Metrics

        This demo shows the full **selector -> table -> chart** workflow:

        1. `MlflowRunSelector` fetches runs as a pandas DataFrame
        2. `mo.ui.table` renders the DataFrame with checkbox selection
        3. Selected runs are passed to `MlflowChart` for visualization
        """
    )
    return (mo,)


@app.cell
def _(mo):
    import os

    TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

    mo.md(f"**Tracking URI:** `{TRACKING_URI}`")
    return (TRACKING_URI,)


@app.cell
def _(TRACKING_URI):
    import math
    import random

    import mlflow

    EXPERIMENT_NAME = "combo-demo"

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    client = mlflow.MlflowClient(TRACKING_URI)
    existing = client.search_runs(experiment_ids=[experiment_id])

    if len(existing) == 0:
        configs = [
            {"lr": 0.005, "batch": 32, "opt": "sgd", "name": "sgd-slow"},
            {"lr": 0.01, "batch": 64, "opt": "adam", "name": "adam-baseline"},
            {"lr": 0.05, "batch": 64, "opt": "adam", "name": "adam-fast"},
            {"lr": 0.1, "batch": 128, "opt": "adam", "name": "adam-aggressive"},
            {"lr": 0.02, "batch": 32, "opt": "sgd", "name": "sgd-medium"},
            {"lr": 0.03, "batch": 64, "opt": "rmsprop", "name": "rmsprop-default"},
        ]

        for cfg in configs:
            with mlflow.start_run(run_name=cfg["name"]):
                mlflow.log_param("learning_rate", cfg["lr"])
                mlflow.log_param("batch_size", cfg["batch"])
                mlflow.log_param("optimizer", cfg["opt"])

                random.seed(hash(cfg["name"]) % 2**32)
                for step in range(150):
                    t = step / 150
                    loss = math.exp(-3 * cfg["lr"] * step) + 0.03 + random.gauss(0, 0.01)
                    acc = 1.0 / (1.0 + math.exp(-10 * (t - 0.25))) + random.gauss(0, 0.02)
                    mlflow.log_metric("loss", max(loss, 0.01), step=step)
                    mlflow.log_metric("accuracy", max(0.0, min(1.0, acc)), step=step)

        print(f"Created {len(configs)} runs in experiment '{EXPERIMENT_NAME}'")
    else:
        print(f"Using {len(existing)} existing runs in experiment '{EXPERIMENT_NAME}'")

    experiment_id
    return (experiment_id,)


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    mo.md("## Select Runs")
    return ()


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowRunSelector

    selector = MlflowRunSelector(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
    )
    runs_df = selector.to_dataframe()

    run_table = mo.ui.table(runs_df, selection="multi", label="Select runs to chart")
    run_table
    return runs_df, run_table, selector


@app.cell
def _(mo, run_table):
    from mlflow_widgets import MlflowRunSelector as _Sel

    selected = run_table.value
    mo.stop(
        len(selected) == 0,
        mo.md("*Select one or more runs from the table above to see charts.*"),
    )

    selected_ids = _Sel.get_run_ids(selected)
    mo.md(f"**Selected {len(selected_ids)} run(s):** {', '.join(selected_ids[:5])}")
    return (selected_ids,)


@app.cell
def _(mo):
    mo.md("## Loss")
    return ()


@app.cell
def _(TRACKING_URI, mo, selected_ids):
    from mlflow_widgets import MlflowChart

    loss_chart = MlflowChart(
        tracking_uri=TRACKING_URI,
        runs=selected_ids,
        metric_key="loss",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(loss_chart)
    return (loss_chart,)


@app.cell
def _(mo):
    mo.md("## Accuracy")
    return ()


@app.cell
def _(TRACKING_URI, mo, selected_ids):
    from mlflow_widgets import MlflowChart as _MC

    acc_chart = _MC(
        tracking_uri=TRACKING_URI,
        runs=selected_ids,
        metric_key="accuracy",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(acc_chart)
    return (acc_chart,)


if __name__ == "__main__":
    app.run()
