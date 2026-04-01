# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "mlflow>=2.0",
#     "mlflow-widgets",
#     "anywidget>=0.9.2",
# ]
# ///

import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # MLflow Run Table Demo

        This demo shows the `MlflowRunTable` widget, which displays
        experiment runs as a sortable table with params and metrics.

        It creates mock runs if needed, then renders both a table overview
        and a chart for comparison.
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
def _(mo):
    mo.md("""
    ## Generate Mock Data
    """)
    return


@app.cell
def _(TRACKING_URI):
    import math
    import random

    import mlflow

    EXPERIMENT_NAME = "table-demo"

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    client = mlflow.MlflowClient(TRACKING_URI)
    existing = client.search_runs(experiment_ids=[experiment_id])

    if len(existing) == 0:
        configs = [
            {"lr": 0.005, "batch": 32, "name": "conservative"},
            {"lr": 0.01, "batch": 64, "name": "baseline"},
            {"lr": 0.05, "batch": 64, "name": "aggressive"},
            {"lr": 0.1, "batch": 128, "name": "very-fast"},
            {"lr": 0.02, "batch": 32, "name": "medium-small-batch"},
        ]

        for cfg in configs:
            with mlflow.start_run(run_name=cfg["name"]):
                mlflow.log_param("learning_rate", cfg["lr"])
                mlflow.log_param("batch_size", cfg["batch"])
                mlflow.log_param("optimizer", "adam")

                random.seed(hash(cfg["name"]) % 2**32)
                final_loss = None
                final_acc = None
                for step in range(150):
                    t = step / 150
                    loss = math.exp(-3 * cfg["lr"] * step) + 0.03 + random.gauss(0, 0.01)
                    loss = max(loss, 0.01)
                    acc = 1.0 / (1.0 + math.exp(-10 * (t - 0.25)))
                    acc += random.gauss(0, 0.02)
                    acc = max(0.0, min(1.0, acc))
                    mlflow.log_metric("loss", loss, step=step)
                    mlflow.log_metric("accuracy", acc, step=step)
                    final_loss = loss
                    final_acc = acc

        print(f"Created {len(configs)} runs in experiment '{EXPERIMENT_NAME}'")
    else:
        print(f"Using {len(existing)} existing runs in experiment '{EXPERIMENT_NAME}'")

    experiment_id
    return (experiment_id,)


@app.cell
def _(mo):
    mo.md("""
    ## Run Table
    """)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowRunTable

    run_table = MlflowRunTable(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        width=1000,
    )

    mo.ui.anywidget(run_table)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Metric Charts
    """)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowChart

    loss_chart = MlflowChart(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        metric_key="loss",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(loss_chart)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowChart as _MC

    acc_chart = _MC(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        metric_key="accuracy",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(acc_chart)
    return


if __name__ == "__main__":
    app.run()
