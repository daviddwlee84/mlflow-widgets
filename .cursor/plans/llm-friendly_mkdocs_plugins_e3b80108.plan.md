---
name: LLM-friendly MkDocs plugins
overview: Add mkdocs-llmstxt and mkdocs-copy-to-llm plugins to generate /llms.txt, /llms-full.txt, per-page .md files, and "Copy to LLM" UI buttons on every docs page.
todos:
  - id: deps
    content: Add mkdocs-llmstxt and mkdocs-copy-to-llm to pyproject.toml docs extras
    status: completed
  - id: mkdocs-config
    content: Enable llmstxt (with sections + full_output) and copy-to-llm plugins in mkdocs.yml
    status: completed
  - id: verify-build
    content: Run mkdocs build --strict, verify llms.txt / llms-full.txt / per-page .md / Copy button all work
    status: completed
  - id: update-meta
    content: Update CHANGELOG.md, AGENTS.md with LLM-friendly docs info
    status: completed
isProject: false
---

# LLM-Friendly MkDocs Plugins

## Research summary

Evaluated four MkDocs LLM plugins. The decisive factor for this project is that **our API reference pages use mkdocstrings directives** (e.g. `::: mlflow_widgets.MlflowChart`) which are only expanded at build time. Plugins that copy raw `.md` source would output the unexpanded directives, not the actual API docs.

### Plugin comparison

- **mkdocs-llmstxt** (pawamoy, v0.5.0, 322K downloads/mo) -- HTML-to-Markdown approach via BeautifulSoup + Markdownify. Generates `/llms.txt`, `/llms-full.txt`, and per-page `.md` files. **Captures mkdocstrings-generated API docs** because it works on rendered HTML. In maintenance mode but stable and widely used.
- **mkdocs-llms-source** (TimChild, v1.1.0, new) -- Source-first approach, copies raw `.md` files. Auto-derives sections from nav. **NOT suitable for this project**: our `reference/*.md` files contain `::: mlflow_widgets.X` directives that would appear as-is instead of expanded API docs.
- **mkdocs-copy-to-llm** (leonardocustodio, v0.2.10) -- Adds a "Copy to LLM" split button to every page with options: copy as Markdown, copy link, open in ChatGPT, open in Claude, view raw markdown. Complementary UI enhancement, works on rendered content.
- **mkdocs-llmstxt-md** (v0.2.0, beta) -- Similar hybrid approach but less mature. Skip.

### Decision

Install **both**:

1. `**mkdocs-llmstxt`** -- machine-facing: generates `/llms.txt` + `/llms-full.txt` + per-page `.md` files at build time
2. `**mkdocs-copy-to-llm`** -- human-facing: adds UI buttons for copying content to LLM chats

They serve different purposes and do not conflict.

## Changes

### 1. [pyproject.toml](pyproject.toml) -- add dependencies

Add both plugins to the `docs` extras:

```toml
docs = [
    "mkdocs-material",
    "mkdocstrings[python]",
    "mkdocs-llmstxt",
    "mkdocs-copy-to-llm",
]
```

### 2. [mkdocs.yml](mkdocs.yml) -- enable plugins

Add `llmstxt` and `copy-to-llm` to the plugins list. The `llmstxt` plugin requires `sections` config mapping our docs pages, and `full_output` for the concatenated file. Use file globbing to cover all pages:

```yaml
plugins:
  - search
  - mkdocstrings: ...
  - llmstxt:
      full_output: llms-full.txt
      sections:
        Guides:
          - index.md
          - installation.md
          - getting-started.md
        Widgets:
          - widgets/*.md
        Examples:
          - examples.md
        API Reference:
          - reference/*.md
        Changelog:
          - changelog.md
  - copy-to-llm:
      button_hover_color: "var(--md-primary-fg-color)"
      toast_bg_color: "var(--md-primary-fg-color)"
```

### 3. Verify build + output

- `uv sync --extra docs && uv run mkdocs build --strict`
- Confirm `site/llms.txt`, `site/llms-full.txt`, and per-page `.md` files exist
- Confirm the API reference `.md` files contain expanded class signatures (not raw `:::`  directives)
- Confirm "Copy to LLM" button appears on pages

### 4. Update metadata files

- [CHANGELOG.md](CHANGELOG.md) -- add entry under `[Unreleased]`
- [AGENTS.md](AGENTS.md) -- mention LLM-friendly output in docs section
- [notes/docs-stack-evaluation.md](notes/docs-stack-evaluation.md) -- could add a "Phase 2 done" note (optional)

