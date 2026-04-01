# Installation

## From PyPI

=== "pip"

    ```bash
    pip install mlflow-widgets
    ```

=== "uv"

    ```bash
    uv add mlflow-widgets
    ```

### With MLflow included

If you don't already have MLflow installed:

=== "pip"

    ```bash
    pip install mlflow-widgets[mlflow]
    ```

=== "uv"

    ```bash
    uv add mlflow-widgets[mlflow]
    ```

## From GitHub (latest)

Install the latest development version directly from the repository:

=== "pip"

    ```bash
    pip install git+https://github.com/daviddwlee84/mlflow-widgets.git
    ```

=== "uv"

    ```bash
    uv add git+https://github.com/daviddwlee84/mlflow-widgets.git
    # or
    uv pip install git+https://github.com/daviddwlee84/mlflow-widgets.git
    ```

## Requirements

- Python >= 3.10
- Dependencies: `anywidget >= 0.9.2`, `traitlets`
- Optional: `mlflow >= 2.0` (for data fetching; falls back to REST API via `urllib` if not installed)

## Extras

| Extra | Packages | Use case |
|-------|----------|----------|
| `mlflow` | `mlflow>=2.0`, `python-socks[asyncio]` | Full MLflow client support |
| `demo` | `marimo>=0.10.0`, `mlflow>=2.0` | Running example notebooks |
| `dev` | `pytest`, `ruff`, `twine`, `taskipy` | Development and testing |
| `docs` | `mkdocs-material`, `mkdocstrings[python]` | Building documentation |
