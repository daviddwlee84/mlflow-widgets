---
name: MkDocs documentation setup
overview: Set up MkDocs Material + mkdocstrings documentation site with auto-generated API reference, GitHub Pages deployment, and a docs taskipy task for local preview.
todos:
  - id: deps
    content: Add docs dependencies to pyproject.toml (mkdocs-material, mkdocstrings[python]) and taskipy tasks (docs, docs-build)
    status: completed
  - id: mkdocs-yml
    content: Create mkdocs.yml with Material theme, mkdocstrings plugin, nav structure, repo links
    status: completed
  - id: docs-content
    content: "Create docs/ directory with all markdown pages: index, installation, getting-started, widgets/*, examples, reference/*, changelog"
    status: completed
  - id: fix-docstring
    content: Fix MlflowChart docstring copy-paste error (mlflow_chart -> mlflow_widgets)
    status: completed
  - id: gh-workflow
    content: Create .github/workflows/docs.yml for GitHub Pages deployment on push to main
    status: completed
  - id: update-meta
    content: Update README.md (docs link/badge), CHANGELOG.md (unreleased entry), AGENTS.md (source layout + tasks)
    status: completed
  - id: verify
    content: Run mkdocs build --strict and mkdocs serve to verify everything works
    status: completed
isProject: false
---

# MkDocs Documentation Setup for mlflow-widgets

## Decision: MkDocs + Material + mkdocstrings

Per the existing evaluation in [notes/docs-stack-evaluation.md](notes/docs-stack-evaluation.md), the recommendation is **MkDocs + Material for MkDocs + mkdocstrings[python]**. This matches all four requirements:

1. **Auto-updating API reference** -- mkdocstrings reads docstrings at build time via `::: mlflow_widgets.MlflowChart` directives
2. **LLM-friendly** -- Material produces clean HTML; each page's Markdown source lives in `docs/`; can add `llms.txt` later as a post-build step
3. **Built-in search** -- Material's search plugin is enabled by default (Cmd+K)
4. **GitHub Pages** -- standard `mkdocs gh-deploy` or GitHub Actions workflow

## Docs site structure

```
mkdocs.yml                   # Site config
docs/
  index.md                   # Home / overview (condensed from README)
  installation.md            # pip/uv install, extras, from-source
  getting-started.md         # Quick start: server setup, first chart
  widgets/
    chart.md                 # MlflowChart guide + usage patterns
    table.md                 # MlflowRunTable guide
    parallel.md              # MlflowParallelCoordinates guide
    selector.md              # MlflowRunSelector guide
  examples.md                # Overview of the 6 Marimo demo notebooks
  reference/                 # API reference (mkdocstrings auto-gen)
    index.md                 # Package-level overview
    chart.md                 # ::: mlflow_widgets.MlflowChart
    table.md                 # ::: mlflow_widgets.MlflowRunTable
    parallel.md              # ::: mlflow_widgets.MlflowParallelCoordinates
    selector.md              # ::: mlflow_widgets.MlflowRunSelector
  changelog.md               # Include CHANGELOG.md content or snippet macro
```

## mkdocs.yml key configuration

```yaml
site_name: mlflow-widgets
site_url: https://daviddwlee84.github.io/mlflow-widgets/
repo_url: https://github.com/daviddwlee84/mlflow-widgets
theme:
  name: material
  features:
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            members_order: source
            docstring_style: google
nav:
  - Home: index.md
  - Installation: installation.md
  - Getting Started: getting-started.md
  - Widgets:
    - MlflowChart: widgets/chart.md
    - MlflowRunTable: widgets/table.md
    - MlflowParallelCoordinates: widgets/parallel.md
    - MlflowRunSelector: widgets/selector.md
  - Examples: examples.md
  - API Reference:
    - Overview: reference/index.md
    - MlflowChart: reference/chart.md
    - MlflowRunTable: reference/table.md
    - MlflowParallelCoordinates: reference/parallel.md
    - MlflowRunSelector: reference/selector.md
  - Changelog: changelog.md
```

## Dependencies

Add a `docs` optional-dependency group in [pyproject.toml](pyproject.toml):

```toml
[project.optional-dependencies]
docs = [
    "mkdocs-material",
    "mkdocstrings[python]",
]
```

Add taskipy tasks:

```toml
docs = { cmd = "mkdocs serve", help = "Serve docs locally" }
docs-build = { cmd = "mkdocs build --strict", help = "Build docs" }
```

## GitHub Actions workflow

Create [.github/workflows/docs.yml](.github/workflows/docs.yml) using GitHub Pages custom workflow (actions/deploy-pages). Triggers on push to `main` (so docs stay in sync with code).

```
on push to main -> uv sync --extra docs -> mkdocs build --strict -> upload artifact -> deploy to GitHub Pages
```

## Files to update

- [pyproject.toml](pyproject.toml) -- add `docs` extras, taskipy tasks, update `project.urls` with Documentation link
- [CHANGELOG.md](CHANGELOG.md) -- add "Added: Documentation site with MkDocs Material" under `[Unreleased]`
- [README.md](README.md) -- add Documentation link/badge
- [AGENTS.md](AGENTS.md) -- add `docs/` to source layout, add `docs` task to build section

## Docstring fix

The `MlflowChart` class docstring has a copy-paste error: `from mlflow_chart import MlflowChart` should be `from mlflow_widgets import MlflowChart`. Fix this so the generated API reference shows the correct import.

## Local verification

Run `uv sync --extra docs && uv run mkdocs serve` and verify:

- All pages render without warnings
- API reference pages show class signatures, parameters, and docstrings
- Search (Cmd+K) works
- Navigation structure is correct
- `mkdocs build --strict` passes with zero warnings

