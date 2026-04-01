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

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Live Experiment Tracking

        This demo shows how to track an MLflow experiment **on-the-fly**
        and watch the metrics update live in a `MlflowChart` widget.

        1. Configure the tracking URI below
        2. Click **Start Training** to begin a mock training run
        3. Watch the chart update in real time
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
    start_btn = mo.ui.button(label="Start Training", kind="success")
    start_btn
    return (start_btn,)


@app.cell
def _(TRACKING_URI, mo, start_btn):
    import math
    import random
    import time

    import mlflow

    mo.stop(not start_btn.value, mo.md("*Click **Start Training** above to begin.*"))

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment("live-tracking-demo")
    live_experiment_id = experiment.experiment_id

    run_name = f"live-run-{int(time.time()) % 10000}"
    with mlflow.start_run(run_name=run_name) as run:
        live_run_id = run.info.run_id
        mlflow.log_param("learning_rate", 0.03)
        mlflow.log_param("epochs", 100)

        random.seed(42)
        for step in range(100):
            t = step / 100
            loss = math.exp(-2.5 * t) + 0.08 + random.gauss(0, 0.015)
            loss = max(loss, 0.01)

            acc = 1.0 / (1.0 + math.exp(-8 * (t - 0.35)))
            acc += random.gauss(0, 0.02)
            acc = max(0.0, min(1.0, acc))

            mlflow.log_metric("loss", loss, step=step)
            mlflow.log_metric("accuracy", acc, step=step)

            time.sleep(0.05)

    mo.md(
        f"""
        Training complete!

        - **Run:** `{run_name}` (`{live_run_id}`)
        - **Experiment ID:** `{live_experiment_id}`
        """
    )
    return live_experiment_id, live_run_id


@app.cell
def _(TRACKING_URI, live_run_id, mo):
    from mlflow_widgets import MlflowChart

    live_chart = MlflowChart(
        tracking_uri=TRACKING_URI,
        runs=[live_run_id],
        metric_key="loss",
        poll_seconds=2,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(live_chart)
    return (live_chart,)


@app.cell
def _(TRACKING_URI, live_run_id, mo):
    from mlflow_widgets import MlflowChart as _MC

    live_acc_chart = _MC(
        tracking_uri=TRACKING_URI,
        runs=[live_run_id],
        metric_key="accuracy",
        poll_seconds=2,
        smoothing_kind="gaussian",
        width=800,
        height=350,
    )

    mo.ui.anywidget(live_acc_chart)
    return (live_acc_chart,)


if __name__ == "__main__":
    app.run()
