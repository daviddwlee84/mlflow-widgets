# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "mlflow>=2.0",
#     "mlflow-chart",
#     "anywidget>=0.9.2",
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
        # MLflow Chart Widget Demo

        This notebook demonstrates `mlflow-chart`, an
        [anywidget](https://anywidget.dev/)-based live metric chart for
        [MLflow](https://mlflow.org/) experiments.

        It generates mock training runs, logs metrics to a local MLflow
        tracking server, then visualizes them with `MlflowChart`.
        """
    )
    return (mo,)


@app.cell
def _(mo):
    import os

    TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

    mo.md(f"Using MLflow tracking URI: `{TRACKING_URI}`")
    return (TRACKING_URI,)


@app.cell
def _(TRACKING_URI, mo):
    mo.md(
        """
        ## Step 1: Generate Mock Experiments

        We simulate 3 training runs with different learning rates.
        Each run logs `loss` (exponential decay + noise) and `accuracy`
        (sigmoid curve + noise) over 200 steps.
        """
    )
    return ()


@app.cell
def _(TRACKING_URI):
    import math
    import random

    import mlflow

    EXPERIMENT_NAME = "mlflow-chart-demo"
    NUM_STEPS = 200

    mlflow.set_tracking_uri(TRACKING_URI)

    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    configs = [
        {"lr": 0.01, "name": "slow-learner"},
        {"lr": 0.05, "name": "medium-learner"},
        {"lr": 0.1, "name": "fast-learner"},
    ]

    run_ids = []
    for cfg in configs:
        with mlflow.start_run(run_name=cfg["name"]) as run:
            mlflow.log_param("learning_rate", cfg["lr"])
            mlflow.log_param("model", "mock-nn")

            random.seed(hash(cfg["name"]) % 2**32)
            for step in range(NUM_STEPS):
                t = step / NUM_STEPS
                base_loss = math.exp(-3 * cfg["lr"] * step) + 0.05
                loss = base_loss + random.gauss(0, 0.02 * base_loss)
                loss = max(loss, 0.01)

                base_acc = 1.0 / (1.0 + math.exp(-10 * (t - 0.3)))
                acc = base_acc + random.gauss(0, 0.03)
                acc = max(0.0, min(1.0, acc))

                mlflow.log_metric("loss", loss, step=step)
                mlflow.log_metric("accuracy", acc, step=step)

            run_ids.append(run.info.run_id)

    print(f"Created {len(run_ids)} runs in experiment '{EXPERIMENT_NAME}' (id={experiment_id})")
    return configs, experiment, experiment_id, run_ids


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 2: Visualize with MlflowChart

        Now we create `MlflowChart` widgets to visualize the metrics.
        The widget fetches data from the MLflow server and renders an
        interactive canvas chart with smoothing controls.
        """
    )
    return ()


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_chart import MlflowChart

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
    return (loss_chart,)


@app.cell
def _(TRACKING_URI, experiment_id, mo):
    from mlflow_chart import MlflowChart as _MlflowChart

    acc_chart = _MlflowChart(
        tracking_uri=TRACKING_URI,
        experiment_id=experiment_id,
        metric_key="accuracy",
        poll_seconds=None,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(acc_chart)
    return (acc_chart,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 3: Single Run View

        You can also chart a single run by passing its run ID directly.
        """
    )
    return ()


@app.cell
def _(TRACKING_URI, mo, run_ids):
    from mlflow_chart import MlflowChart as _MC

    single_chart = _MC(
        tracking_uri=TRACKING_URI,
        runs=[run_ids[0]],
        metric_key="loss",
        poll_seconds=None,
        smoothing_kind="exponential",
        width=800,
        height=300,
    )

    mo.ui.anywidget(single_chart)
    return (single_chart,)


if __name__ == "__main__":
    app.run()
