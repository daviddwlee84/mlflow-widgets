---
name: PyPI Publishing Setup
overview: "Set up the mlflow-widgets package for first-time PyPI publishing: update metadata to modern PEP 639 standards, add LICENSE file, create a test suite, configure GitHub Actions CI/CD with Trusted Publishing, document the learning process, and walk through the full TestPyPI -> PyPI flow."
todos:
  - id: metadata
    content: "Phase 1: Add LICENSE file, update pyproject.toml to PEP 639 (license-expression, URLs, classifiers, keywords), add __version__ to __init__.py"
    status: completed
  - id: tests
    content: "Phase 2: Create tests/ with import smoke tests, widget init tests, packaging verification tests, and examples AST parse tests"
    status: completed
  - id: ci-cd
    content: "Phase 3: Add .github/workflows/ci.yml (test matrix) and .github/workflows/publish.yml (Trusted Publishing to TestPyPI/PyPI)"
    status: completed
  - id: notes
    content: "Phase 4: Write notes/publishing-to-pypi.md documenting the full publishing workflow and learnings"
    status: completed
  - id: build-verify
    content: "Phase 5a: Local build with uv build, run tests, inspect wheel contents"
    status: completed
  - id: testpypi
    content: "Phase 5b: Upload to TestPyPI, verify installation works"
    status: completed
  - id: pypi
    content: "Phase 5c: Tag v0.1.0, publish to PyPI, verify"
    status: completed
  - id: todo-1775040219220-zcctyqvia
    content: Summarize and record takeaways into notes/*.md (e.g. phases in Mermaid diagram, trouble shooting, steps, ...)
    status: completed
isProject: false
---

# First PyPI Publish for mlflow-widgets

## Current State

- Package: `mlflow-widgets` v0.1.0, `src/mlflow_widgets/` layout, built with `hatchling`
- Remote: `https://github.com/daviddwlee84/mlflow-widgets.git`
- Tools available: `uv` 0.10.2 (Homebrew), Python 3.13 in `.venv`
- Gaps: no `LICENSE` file, no `tests/`, no `.github/workflows/`, deprecated `license = { text = "MIT" }` format, no `[project.urls]`

## Phase 1: Metadata and Packaging Standards

### 1a. Add MIT LICENSE file

Create `LICENSE` at project root with the standard MIT text (author: Da-Wei Lee, year: 2026).

### 1b. Update [pyproject.toml](pyproject.toml) to PEP 639 / Metadata 2.4+

Current problematic fields:

```toml
license = { text = "MIT" }
classifiers = [
    ...
    "License :: OSI Approved :: MIT License",
    ...
]
```

Changes:

- Replace `license = { text = "MIT" }` with `license = "MIT"` (SPDX expression, per [PEP 639](https://peps.python.org/pep-0639/))
- Remove the `License ::` classifier (deprecated per PEP 639 / Metadata 2.4)
- Add `license-files = ["LICENSE"]`
- Add `keywords`
- Add more specific `classifiers` (Python version classifiers, Framework :: Jupyter, Development Status)
- Add `[project.urls]` section (Homepage, Repository, Issues, Documentation)
- Add `__version__` to `__init__.py` for runtime version access
- Add `dev` optional-dependencies group for test/dev tooling

### 1c. Add py.typed to hatch build artifacts

The `py.typed` marker file already exists in `src/mlflow_widgets/`. Verify it is included in the wheel via `[tool.hatch.build]`.

**Commit checkpoint**: "chore: update metadata to PEP 639, add LICENSE"

---

## Phase 2: Test Suite

Create `tests/` with pytest-based tests that do NOT require a running MLflow server:

- `tests/__init__.py` (empty)
- `tests/test_import.py` -- smoke test: all 4 public classes importable, `__all__` matches, `__version__` exists
- `tests/test_widget_init.py` -- widget instantiation with mock/dummy data: verify traitlet defaults, `_series_data`/`_table_data` structure, `_do_refresh` observer registration
- `tests/test_packaging.py` -- build the wheel with `uv build`, then inspect it with `zipfile` to confirm `py.typed`, all `static/*.js`, `LICENSE`, and `README.md` are present
- `tests/test_examples.py` -- `ast.parse` all `examples/*.py` to ensure they are syntactically valid

Add `[project.optional-dependencies] dev = [...]` with `pytest` in [pyproject.toml](pyproject.toml).

**Commit checkpoint**: "test: add initial test suite for packaging and smoke tests"

---

## Phase 3: CI/CD with GitHub Actions

### 3a. `.github/workflows/ci.yml` -- Test matrix

- Trigger: push to `main`, pull requests
- Matrix: Python 3.10, 3.11, 3.12, 3.13 on ubuntu-latest
- Steps: checkout, install uv, `uv sync --extra dev`, `uv run pytest`, `uv build --no-sources`, `uv run twine check --strict dist/`*

### 3b. `.github/workflows/publish.yml` -- Release to PyPI

- Trigger: push tag `v`*
- Jobs:
  - **build**: `uv build`, upload artifacts
  - **publish-testpypi**: deploy to TestPyPI (manual dispatch or pre-release tag), `permissions: id-token: write`, environment `testpypi`
  - **publish-pypi**: deploy to PyPI on `v`* tag, `permissions: id-token: write`, environment `pypi`
- Uses `uv publish` with `--publish-url` for TestPyPI, default for PyPI
- Both use Trusted Publishing (OIDC) -- no long-lived tokens needed

**Commit checkpoint**: "ci: add GitHub Actions for testing and publishing"

---

## Phase 4: Documentation in notes/

Create `notes/publishing-to-pypi.md` with structured notes covering:

- PyPI / TestPyPI account setup steps
- Trusted Publisher configuration (GitHub Actions OIDC) -- what to fill in on PyPI project settings
- `License-Expression` vs legacy `license` (PEP 639 rationale)
- `uv build` / `uv publish` workflow
- TestPyPI verification steps
- Version bumping with `uv version`
- Checklist for future releases

**Commit checkpoint**: "docs: add PyPI publishing notes"

---

## Phase 5: Build, Verify, and Publish

### 5a. Local build and verification

```bash
uv build --no-sources
uv run twine check --strict dist/*
uv run pytest
```

Inspect wheel contents with `unzip -l dist/*.whl`.

### 5b. TestPyPI (manual first time)

Since Trusted Publishing requires the project to exist on PyPI first (for "pending publisher" setup), the first upload can go two ways:

- **Option A (recommended)**: Register a "pending publisher" on TestPyPI/PyPI before the first upload, then use GitHub Actions
- **Option B**: First upload manually with `uv publish --publish-url https://test.pypi.org/legacy/ --token <token>`, then set up Trusted Publishing for subsequent releases

Steps for manual first-time:

1. Create accounts at [https://pypi.org](https://pypi.org) and [https://test.pypi.org](https://test.pypi.org)
2. Generate an API token on TestPyPI (Account Settings -> API tokens)
3. `uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-...`
4. Verify: `uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mlflow-widgets`
5. Set up Trusted Publishing on TestPyPI and PyPI for future automated releases

### 5c. PyPI (first release)

After TestPyPI verification passes:

1. Tag `v0.1.0`: `git tag v0.1.0 && git push origin v0.1.0`
2. If Trusted Publishing is configured, the GitHub Actions workflow handles it
3. Otherwise: `uv publish --token pypi-...`
4. Verify: `uv pip install mlflow-widgets` in a clean venv

**Commit checkpoint**: tag `v0.1.0`

---

## Key References

- [PEP 639 -- License-Expression](https://peps.python.org/pep-0639/) -- the modern license metadata standard
- [uv publish guide](https://docs.astral.sh/uv/guides/package/) -- building and publishing with uv
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) -- OIDC-based publishing from GitHub Actions
- [GitHub Actions publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

