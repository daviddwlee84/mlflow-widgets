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
    start_btn = mo.ui.run_button(
        label="Start Training",
        kind="success",
    )
    start_btn
    return (start_btn,)


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
    return


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
    return


@app.cell
def _(TRACKING_URI, mo, start_btn):
    import time

    import mlflow

    mo.stop(not start_btn.value, mo.md("*Click **Start Training** above to begin.*"))

    mlflow.set_tracking_uri(TRACKING_URI)
    experiment = mlflow.set_experiment("live-tracking-demo")
    live_experiment_id = experiment.experiment_id

    run_name = f"live-run-{int(time.time()) % 10000}"
    active_run = mlflow.start_run(run_name=run_name)
    live_run_id = active_run.info.run_id

    mo.md(
        f"""
        Run created — training will begin in background.

        - **Run:** `{run_name}` (`{live_run_id}`)
        - **Experiment ID:** `{live_experiment_id}`
        """
    )
    return (live_run_id,)


@app.cell
def _(TRACKING_URI, live_run_id, mo):
    import math
    import random
    import threading
    import time as _time

    import mlflow as _mlflow

    def _train(tracking_uri: str, run_id: str) -> None:
        """Run the mock training loop in a background thread."""
        client = _mlflow.MlflowClient(tracking_uri=tracking_uri)
        client.log_param(run_id, "learning_rate", 0.03)
        client.log_param(run_id, "epochs", 100)

        rng = random.Random(42)
        for step in range(100):
            t = step / 100
            loss = math.exp(-2.5 * t) + 0.08 + rng.gauss(0, 0.015)
            loss = max(loss, 0.01)

            acc = 1.0 / (1.0 + math.exp(-8 * (t - 0.35)))
            acc += rng.gauss(0, 0.02)
            acc = max(0.0, min(1.0, acc))

            client.log_metric(run_id, "loss", loss, step=step)
            client.log_metric(run_id, "accuracy", acc, step=step)

            _time.sleep(2)

        # Mark run as finished
        client.set_terminated(run_id)

    _thread = threading.Thread(
        target=_train,
        args=(TRACKING_URI, live_run_id),
        daemon=True,
    )
    _thread.start()

    mo.md(
        f"""
        Training is running in the background (100 steps × 2 s ≈ 200 s).

        The charts above are polling every 2 seconds — watch them update live!
        """
    )
    return


if __name__ == "__main__":
    app.run()
