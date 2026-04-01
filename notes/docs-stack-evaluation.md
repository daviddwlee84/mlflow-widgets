# Python 專案文件方案評估：`mlflow-widgets`

日期：2026-04-01

## 結論先行

對這個 repo，我的主推薦是：

- `MkDocs + Material for MkDocs + mkdocstrings[python]`

備選方案：

- 如果未來把 `llms.txt` / 每頁 `.md` 輸出當成一級需求，而且仍想留在 Python docs 生態，選 `Sphinx + Furo + MyST + autodoc/apidoc + sphinx-llm`

不建議作為本 repo 主方案：

- `Rspress`
- `pdoc`

這個結論是根據目前 repo 形狀與官方文件做出的判斷，不是抽象地選「最強 docs 平台」。

## 事實與建議的界線

以下內容屬於「上游現況事實」：

- Material for MkDocs 有官方 search plugin
- `mkdocstrings` Python handler 支援從 Python object 生成 API docs
- Sphinx 官方提供 `autodoc` 與 `apidoc`
- Rspress 官方提供 `llms.txt` / `.md` 相關能力，且該功能目前標示為 experimental
- `mkdocs-llmstxt` upstream README 目前標示 maintenance mode
- pdoc 官方把自己定位為 API documentation 工具，且明講只支援 HTML output

以下內容屬於「我對本 repo 的建議 / inference」：

- 這個 repo 最佳主方案是 `MkDocs + Material + mkdocstrings`
- `llms.txt` 應視為第二階段 artifact，而不是第一階段選型核心
- `Rspress` 與 `pdoc` 不適合作為本 repo 的主方案
- 若未來 AI-facing output 變成核心需求，再升級到 `Sphinx + Furo + MyST + sphinx-llm`

## 這個 repo 的現況

從 repo 內容來看，這是一個很典型的「小到中型 Python library docs」案例：

- public API 很小，`src/mlflow_widgets/__init__.py` 目前只匯出 `MlflowChart`、`MlflowParallelCoordinates`、`MlflowRunSelector`、`MlflowRunTable`
- 既有文件主要是 Markdown，像 `README.md`、`CHANGELOG.md`、`notes/*.md`
- 核心 Python 類別已有 docstring，可直接餵給 API reference 生成器
- `examples/` 以 Marimo / Python script 為主，不是 notebook portal 型產品文件
- 需求偏向「guide + API reference + examples 索引」，不是大型多產品 docs portal

所以最重要的不是 framework 花樣，而是：

- Markdown 寫作順手
- API reference 可從 code 生成
- 有基本 search
- GitHub Pages 好部署
- 之後可以低成本補 AI-friendly artifacts

## 評估準則

本次評估使用以下準則：

- Python package 文件是否是第一級使用情境
- 能否從 docstring / module 結構直接生成 API reference
- 是否適合 Markdown-first 工作流
- 是否自帶或容易提供簡單搜尋
- 是否容易部署到 GitHub Pages
- 是否能低摩擦補上 `llms.txt` / `llms-full.txt` / `.md` 輸出
- 維護成本是否合理

## 方案比較

| 方案 | Python API 自動生成 | Markdown-first | 搜尋 | AI-native 輸出 | GitHub Pages | 複雜度 | 對本 repo 的適配 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `MkDocs + Material + mkdocstrings` | 強 | 強 | 強 | 中，需額外補 | 強 | 低 | 最佳 |
| `Sphinx + Furo + MyST + sphinx-llm` | 很強 | 中到強 | 強 | 強 | 強 | 中到高 | 次佳 |
| `pdoc` | 中到強 | 弱 | 中 | 弱 | 強 | 很低 | 偏弱 |
| `Quarto` | 中 | 強 | 強 | 弱到中 | 強 | 中 | 可用但不是最佳 |
| `Rspress` | 弱到中 | 強 | 強 | 很強 | 強 | 中 | 不適合作為主方案 |

## 各方案判斷

### 1. MkDocs Material + mkdocstrings

這是我認為目前最符合 Python library best practice 的方案。

原因：

- `Material for MkDocs` 內建 search plugin，不需要另外安裝搜尋套件
- `mkdocstrings` 的 Python handler 可以直接在 Markdown 裡用 `::: path.to.object` 注入 API docs
- `mkdocstrings` 官方對 `src/` layout 也有明確建議，推薦用 `paths: [src]`
- MkDocs 本身就是靜態站，放 GitHub Pages 非常直接
- 對現有 Markdown 文件最友好，導入成本最低

對這個 repo 尤其適合的點：

- 你不需要大型 Sphinx 生態才有的複雜 cross-project 文檔功能
- public API 不大，用 `mkdocstrings` 足夠
- guides 與 notes 已經是 Markdown，幾乎不用改作者習慣

我的判斷：

- 這是目前最穩、最省、最符合 repo 尺寸的主方案

### 2. Sphinx + Furo + MyST + sphinx-llm

這是最合理的 Python-first AI-native 備案。

優點：

- `sphinx.ext.autodoc` 可直接從 docstring 拉文件
- `sphinx.ext.apidoc` 可以從 Python package 自動產生 API docs source
- `MyST` 讓 Sphinx 也能舒服地吃 Markdown
- `Furo` 對小到中型 docset 的閱讀體驗很好
- `sphinx-llm` 可以生成 `llms.txt`、`llms-full.txt`，也能輸出每頁 Markdown

缺點：

- 設定面和維護成本明顯高於 MkDocs
- `autodoc` 會 import 你的 module，若 import 有 side effects 要額外注意
- 對這種 API 面積不大的套件來說，常常有點 overkill

我的判斷：

- 如果未來真的把 AI-facing output 當成核心能力，而不是附加 artifact，這會是最合理的升級路線
- 但以現在這個 repo，仍然不是第一選擇

### 3. pdoc

`pdoc` 的定位其實很清楚：它主要是 API documentation 工具。

優點：

- 幾乎零設定
- 對 type annotations 與 docstring 支援不錯
- 很快就能有一套可看的 API docs

缺點：

- 官方文件直接說它的主要 use case 是 API docs；如果需求更複雜，建議用 Sphinx
- 官方文件也明講它只支援 HTML output
- guide / conceptual docs / 多層資訊架構不是它的強項

我的判斷：

- 若這個 repo 只想做極簡 API docs，`pdoc` 可以
- 但你現在要的是 guide + API + GitHub Pages + AI-native 延伸，`pdoc` 太窄

### 4. Quarto

Quarto 不是壞選擇，但不是這個 repo 的最佳選擇。

優點：

- 官方有 built-in full-text search
- GitHub Pages 部署成熟
- 很適合 notebook、教學、報告、研究導向內容

限制：

- 它不是以 Python package API docs 為核心設計
- API reference 這件事通常需要你再疊其他工具或自己整合
- 對 library docs 來說，常常不是最短路徑

我的判斷：

- 如果未來 docs 方向變成 notebook/tutorial first，Quarto 的吸引力會上升
- 但對當前 `mlflow-widgets`，仍不如 MkDocs 直接

### 5. Rspress

Rspress 很有意思，但我不建議拿它當這個 repo 的主 docs stack。

優點：

- 內建全文搜尋
- 官方已提供 `llms.txt`、`llms-full.txt`、每頁 `.md` 的能力
- GitHub Pages 部署有官方指引

限制：

- 它是 Node / frontend-first 的文件框架，不是 Python package docs first
- Python API reference 仍要靠外部工具補
- 官方把 `llms` 的 SSG-MD 功能標成 experimental

我的判斷：

- 若你是做 framework / frontend product docs，Rspress 值得考慮
- 對這個 repo，為了拿 AI-native 輸出去換掉整個 Python-friendly docs 工具鏈，不划算

## AI-native 的實務建議

我的建議是把 AI-native 能力拆成兩層：

### 第一層：先把 HTML docs stack 選對

主站先選：

- `MkDocs + Material + mkdocstrings`

理由：

- 這決定的是日常維護成本
- 這也決定你能不能穩定地從 code 生成 reference

### 第二層：再補 AI-facing artifacts

之後再補：

- `llms.txt`
- `llms-full.txt`
- 若需要，再補每頁 `.md`

這些應該被視為附加輸出，而不是主架構選型的核心驅動。

原因：

- `mkdocs-llmstxt` 雖然能做這件事，但它的 GitHub README 目前明確寫著 maintenance mode
- 它是合理工具，但不值得讓整個 docs stack 綁死在它上面
- 對這個 repo，更穩的做法是之後用小型自訂 post-build script 產出 `llms.txt`

### 額外提醒：`llms.txt` 不是全部

如果之後要更「AI native」，除了 `llms.txt`，也要一起考慮：

- `robots.txt`
- crawler / bot policy
- 穩定的靜態 URL 結構
- 每頁內容是否夠乾淨、可抽取、可索引

這點的理由是：OpenAI 官方文件目前明確提到 `OAI-SearchBot` 與 `GPTBot` 的 `robots.txt` 控制方式。換句話說，AI 可見性不只取決於你有沒有 `llms.txt`，也和爬蟲可達性有關。

## 對這個 repo 的 best practice

如果以「2026 年現在的小到中型 Python library docs」來看，我認為這個 repo 的 best practice 是：

1. 主站使用 `MkDocs + Material`
2. API reference 使用 `mkdocstrings[python]`
3. guides 以 Markdown 手寫，內容聚焦：
   - installation
   - quickstart
   - MLflow server setup
   - Marimo / Jupyter usage
   - examples overview
4. API 頁只針對 public API 輸出，不追求把所有 internal helper 都曝光
5. GitHub Pages 用 GitHub Actions custom workflow 部署
6. `llms.txt` 作為第二階段 artifact，而不是第一階段 blocking requirement

這組做法的核心精神是：

- 主 docs stack 保持 Python-first
- reference 盡量從 code 生成
- AI-friendly output 用附加層補上

## 建議的後續實作路徑

如果之後要實作，我建議順序如下：

### Phase 1

- 建 `docs/`
- 上 `mkdocs.yml`
- 用 `Material for MkDocs`
- 建首頁、安裝、快速開始、examples、API reference
- API reference 只接 public API

### Phase 2

- 補 examples 導覽頁
- 補 GitHub Pages workflow
- 調整 nav、search、social preview、repo links

### Phase 3

- 用小型 post-build script 生成 `llms.txt`
- 視需求再補 `llms-full.txt`
- 若未來 AI-native 比重明顯上升，再重新評估是否要升級到 `Sphinx + sphinx-llm`

## 最終建議

一句話版本：

- **現在就選 `MkDocs + Material + mkdocstrings`**
- **把 `llms.txt` 當成第二階段補件**
- **只有在 AI-facing markdown artifact 成為核心需求時，才考慮切到 `Sphinx + Furo + MyST + sphinx-llm`**

## 來源

- MkDocs deploy: <https://www.mkdocs.org/user-guide/deploying-your-docs/>
- Material search: <https://squidfunk.github.io/mkdocs-material/plugins/search/>
- mkdocstrings Python usage: <https://mkdocstrings.github.io/python/usage/>
- Sphinx autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
- Sphinx apidoc: <https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html>
- Furo: <https://pradyunsg.me/furo/>
- MyST Parser: <https://myst-parser.readthedocs.io/en/latest/>
- pdoc: <https://pdoc.dev/>
- pdoc limitations: <https://pdoc.dev/docs/pdoc.html>
- Quarto website search: <https://quarto.org/docs/websites/website-search.html>
- Quarto GitHub Pages: <https://quarto.org/docs/publishing/github-pages.html>
- Rspress introduction: <https://rspress.rs/guide/start/introduction>
- Rspress `llms.txt` / SSG-MD: <https://rspress.rs/guide/basic/ssg-md>
- Rspress deploy: <https://rspress.rs/guide/basic/deploy>
- `mkdocs-llmstxt`: <https://github.com/pawamoy/mkdocs-llmstxt>
- `sphinx-llm`: <https://pypi.org/project/sphinx-llm/>
- GitHub Pages custom workflows: <https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages>
- OpenAI crawler docs: <https://developers.openai.com/api/docs/bots>
