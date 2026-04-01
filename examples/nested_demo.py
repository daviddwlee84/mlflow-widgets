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
        # Nested Runs Demo

        This demo creates **parent + child** MLflow runs to show how
        `MlflowRunTable` renders them as a collapsible tree and how
        `MlflowChart` visualizes their metrics side-by-side.

        The pattern simulates a hyperparameter search where:
        - A **parent run** records the search strategy
        - Each **child run** trains with a different config and logs metrics
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
    ## Generate Nested Runs
    """)
    return


@app.cell
def _(TRACKING_URI):
    import math
    import random

    import mlflow

    EXPERIMENT_NAME = "nested-runs-demo"

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    client = mlflow.MlflowClient(TRACKING_URI)
    existing = client.search_runs(experiment_ids=[experiment_id])

    if len(existing) == 0:
        with mlflow.start_run(run_name="hp-search-grid"):
            mlflow.log_param("search_strategy", "grid")
            mlflow.log_param("model", "resnet18")

            configs = [
                {"lr": 0.01, "batch": 32, "name": "trial-lr001-b32"},
                {"lr": 0.05, "batch": 64, "name": "trial-lr005-b64"},
                {"lr": 0.1, "batch": 64, "name": "trial-lr010-b64"},
                {"lr": 0.02, "batch": 128, "name": "trial-lr002-b128"},
            ]

            for cfg in configs:
                with mlflow.start_run(run_name=cfg["name"], nested=True):
                    mlflow.log_param("learning_rate", cfg["lr"])
                    mlflow.log_param("batch_size", cfg["batch"])
                    mlflow.log_param("optimizer", "adam")

                    random.seed(hash(cfg["name"]) % 2**32)
                    for step in range(120):
                        t = step / 120
                        loss = math.exp(-3 * cfg["lr"] * step) + 0.04
                        loss += random.gauss(0, 0.015 * loss)
                        loss = max(loss, 0.01)

                        acc = 1.0 / (1.0 + math.exp(-10 * (t - 0.3)))
                        acc += random.gauss(0, 0.025)
                        acc = max(0.0, min(1.0, acc))

                        mlflow.log_metric("loss", loss, step=step)
                        mlflow.log_metric("accuracy", acc, step=step)

        with mlflow.start_run(run_name="hp-search-random"):
            mlflow.log_param("search_strategy", "random")
            mlflow.log_param("model", "resnet34")

            random_configs = [
                {"lr": 0.007, "batch": 48, "name": "rand-trial-1"},
                {"lr": 0.03, "batch": 96, "name": "rand-trial-2"},
                {"lr": 0.08, "batch": 32, "name": "rand-trial-3"},
            ]

            for cfg in random_configs:
                with mlflow.start_run(run_name=cfg["name"], nested=True):
                    mlflow.log_param("learning_rate", cfg["lr"])
                    mlflow.log_param("batch_size", cfg["batch"])
                    mlflow.log_param("optimizer", "sgd")

                    random.seed(hash(cfg["name"]) % 2**32)
                    for step in range(100):
                        t = step / 100
                        loss = math.exp(-2.5 * cfg["lr"] * step) + 0.06
                        loss += random.gauss(0, 0.02 * loss)
                        loss = max(loss, 0.01)

                        acc = 1.0 / (1.0 + math.exp(-8 * (t - 0.35)))
                        acc += random.gauss(0, 0.03)
                        acc = max(0.0, min(1.0, acc))

                        mlflow.log_metric("loss", loss, step=step)
                        mlflow.log_metric("accuracy", acc, step=step)

        print(f"Created nested runs in experiment '{EXPERIMENT_NAME}'")
    else:
        print(f"Using {len(existing)} existing runs in experiment '{EXPERIMENT_NAME}'")

    experiment_id
    return (experiment_id,)


@app.cell
def _(mo):
    mo.md("""
    ## Run Table (Tree View)

    Parent runs show a collapse/expand toggle. Click to reveal child runs.
    """)
    return


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowRunTable

    run_table = MlflowRunTable(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        width=1100,
    )

    mo.ui.anywidget(run_table)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Loss Chart (All Runs)

    Shows all child runs' loss curves for comparison.
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


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_widgets import MlflowChart as _MC

    acc_chart = _MC(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        metric_key="accuracy",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=900,
        height=350,
    )

    mo.ui.anywidget(acc_chart)
    return


if __name__ == "__main__":
    app.run()
