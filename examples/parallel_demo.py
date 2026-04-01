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
        # Parallel Coordinates Demo

        This demo shows the `MlflowParallelCoordinates` widget, which
        plots hyperparameters and metrics as parallel axes with one line
        per run.

        - Lines are colored by **run status** (finished, running, failed, killed)
        - Use the **status checkboxes** to show/hide groups
        - **Hover** over a line to see the run's details
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
    ## Generate Varied Runs

    We create runs with different hyperparameter combos and statuses
    to demonstrate the parallel coordinates view.
    """)
    return


@app.cell
def _(TRACKING_URI):
    import math
    import random

    import mlflow

    EXPERIMENT_NAME = "parallel-coords-demo"

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    client = mlflow.MlflowClient(TRACKING_URI)
    existing = client.search_runs(experiment_ids=[experiment_id])

    if len(existing) == 0:
        configs = [
            {"lr": 0.005, "batch": 32,  "opt": "sgd",     "layers": 2, "name": "sgd-shallow-slow"},
            {"lr": 0.01,  "batch": 64,  "opt": "adam",    "layers": 3, "name": "adam-baseline"},
            {"lr": 0.05,  "batch": 64,  "opt": "adam",    "layers": 4, "name": "adam-deep-fast"},
            {"lr": 0.1,   "batch": 128, "opt": "adam",    "layers": 3, "name": "adam-aggressive"},
            {"lr": 0.02,  "batch": 32,  "opt": "sgd",     "layers": 5, "name": "sgd-very-deep"},
            {"lr": 0.03,  "batch": 64,  "opt": "rmsprop", "layers": 3, "name": "rmsprop-default"},
            {"lr": 0.008, "batch": 48,  "opt": "adam",    "layers": 2, "name": "adam-small-batch"},
            {"lr": 0.07,  "batch": 96,  "opt": "sgd",     "layers": 4, "name": "sgd-large-batch"},
        ]

        for i, cfg in enumerate(configs):
            status_override = None
            if i == 3:
                status_override = "FAILED"
            elif i == 6:
                status_override = "KILLED"

            with mlflow.start_run(run_name=cfg["name"]) as run:
                mlflow.log_param("learning_rate", cfg["lr"])
                mlflow.log_param("batch_size", cfg["batch"])
                mlflow.log_param("optimizer", cfg["opt"])
                mlflow.log_param("num_layers", cfg["layers"])

                random.seed(hash(cfg["name"]) % 2**32)
                num_steps = 80 if status_override == "FAILED" else 150

                for step in range(num_steps):
                    t = step / 150
                    loss = math.exp(-3 * cfg["lr"] * step) + 0.03
                    loss += random.gauss(0, 0.012 * loss)
                    loss = max(loss, 0.01)

                    acc = 1.0 / (1.0 + math.exp(-10 * (t - 0.25)))
                    acc += random.gauss(0, 0.02)
                    acc = max(0.0, min(1.0, acc))

                    mlflow.log_metric("loss", loss, step=step)
                    mlflow.log_metric("accuracy", acc, step=step)

                if status_override == "FAILED":
                    client.set_terminated(run.info.run_id, status="FAILED")
                elif status_override == "KILLED":
                    client.set_terminated(run.info.run_id, status="KILLED")

        print(f"Created {len(configs)} runs in experiment '{EXPERIMENT_NAME}'")
    else:
        print(f"Using {len(existing)} existing runs in experiment '{EXPERIMENT_NAME}'")

    experiment_id
    return (experiment_id,)


@app.cell
def _(mo):
    mo.md("""
    ## Parallel Coordinates Chart

    Each vertical axis is a hyperparameter or metric.
    Each line is a run, colored by status.
    """)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowParallelCoordinates

    parallel_chart = MlflowParallelCoordinates(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        width=1000,
        height=450,
    )

    mo.ui.anywidget(parallel_chart)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Run Table

    For reference, here's the same experiment's runs in table form.
    """)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowRunTable

    table = MlflowRunTable(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        width=1000,
    )

    mo.ui.anywidget(table)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Loss Chart
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
        width=900,
        height=350,
    )

    mo.ui.anywidget(loss_chart)
    return


if __name__ == "__main__":
    app.run()
