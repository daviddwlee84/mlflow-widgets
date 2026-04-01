# Releasing `mlflow-widgets`

This project publishes to TestPyPI and PyPI with GitHub Actions Trusted
Publishing. The workflow is defined in `.github/workflows/release.yml` and uses
the uv package workflow (`uv sync`, `uv run`, `uv build`, `uv publish`).

## One-time setup

1. Create both the PyPI and TestPyPI projects by uploading once or by letting
   the first trusted publish create them.
2. In GitHub, create the `testpypi` and `pypi` environments for this
   repository.
3. In TestPyPI, add a trusted publisher for:
   - owner: `daviddwlee84`
   - repository: `mlflow-widgets`
   - workflow: `release.yml`
   - environment: `testpypi`
4. In PyPI, add a trusted publisher for:
   - owner: `daviddwlee84`
   - repository: `mlflow-widgets`
   - workflow: `release.yml`
   - environment: `pypi`

## Local release checks

Run the same gates locally before cutting a tag:

```bash
uv sync --locked --dev
uv run pytest
uv build --no-sources
uv run twine check --strict dist/*
uv run python scripts/check_dist_contents.py
uv run --isolated --no-project --with dist/*.whl tests/smoke_test.py
uv run --isolated --no-project --with dist/*.tar.gz tests/smoke_test.py
```

## TestPyPI release candidate

Push a release-candidate tag such as `v0.1.0rc1` or dispatch the workflow with
`publish_testpypi=true`.

```bash
git tag v0.1.0rc1
git push origin v0.1.0rc1
```

After the workflow publishes, verify installation from TestPyPI in a clean
environment:

```bash
uv run --isolated --no-project \
  --index testpypi \
  --with mlflow-widgets==0.1.0rc1 \
  --refresh-package mlflow-widgets \
  python -c "from mlflow_widgets import MlflowChart, MlflowRunTable, MlflowRunSelector, MlflowParallelCoordinates"
```

## Production release

Once the TestPyPI candidate looks good, push a final release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The same workflow will publish the built distributions to PyPI through the
`pypi` environment.

## Post-release checklist

- Confirm the project page renders correctly on PyPI.
- Install the released version with `uv add mlflow-widgets` or `pip install mlflow-widgets`.
- Run a quick live smoke test against a local MLflow server.
- Verify the uploaded distribution files and published attestations.
