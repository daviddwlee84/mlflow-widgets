# README Badge Notes

日期：2026-04-01

整理這個 repo 在 README 頂部放 badge 時的實務原則與可直接套用的模板。目標是讓未來如果想再加 badge，可以直接照著這份筆記挑選、替換變數、貼進 README。

## 結論先行

對這個 repo，README 頂部最值得保留的是這 5 類 badge：

- `CI`：目前主分支 / PR 的自動化測試狀態
- `Docs`：文件部署 workflow 狀態
- `PyPI`：目前已發布版本
- `Python`：支援的 Python 版本
- `License`：授權資訊

這 5 個 badge 的資訊密度最高，也最能快速建立使用者信任。

目前 README 採用的是：

```md
[![CI](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml/badge.svg)](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml)
[![Docs](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/docs.yml/badge.svg)](https://daviddwlee84.github.io/mlflow-widgets/)
[![PyPI](https://img.shields.io/pypi/v/mlflow-widgets?logo=pypi&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
[![Python](https://img.shields.io/pypi/pyversions/mlflow-widgets?logo=python&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
[![License](https://img.shields.io/github/license/daviddwlee84/mlflow-widgets)](https://github.com/daviddwlee84/mlflow-widgets/blob/main/LICENSE)
```

## 選 badge 的原則

### 1. 優先用動態 badge，不要用寫死的 `passing`

像 `tests-passing` 這種 `img.shields.io/badge/...` 靜態 badge，最大的問題是：

- CI fail 了，README 還是會顯示 `passing`
- 很容易變成需要手動維護的文案
- 對讀者來說可信度比 workflow badge 低

所以像測試狀態、文件部署狀態、PyPI 版本、Python 版本，應優先用「會跟上游狀態同步」的 badge。

### 2. badge 要能回答讀者的前 5 秒問題

通常讀者會先看：

- 這個專案有沒有在跑 CI？
- 文件是不是活的？
- 套件有沒有發到 PyPI？
- 我現在的 Python 版本能不能用？
- 這個專案是什麼授權？

如果一個 badge 不能幫助回答這類問題，就要懷疑它是不是只是增加噪音。

### 3. 控制數量，避免「badge wall」

展示型 badge 常見但不一定值得放在第一排：

- downloads
- GitHub stars
- release age
- last commit
- repo activity
- ecosystem 宣示型 badge，例如 `MLflow`、`Jupyter`、`Marimo`、`anywidget`

這些資訊不一定沒價值，但通常不該排在最前面。對 library README 來說，第一排應該先放「信任訊號」。

### 4. badge 圖片來源和點擊目標要分開想

一個 badge 通常有兩個 URL：

- 圖片 URL：顯示 badge 圖案
- 連結 URL：點下去後要帶使用者去哪裡

推薦做法：

- CI / docs badge：圖連 workflow badge，點擊連 workflow 或正式 docs
- PyPI / Python badge：圖連 Shields，點擊連 PyPI project 頁
- License badge：圖連 Shields，點擊連 LICENSE 或 repo

不要只顧 badge 圖，忘了連結是否真的有用。

## Badge 基本語法

Markdown 寫法：

```md
[![Badge Label](BADGE_IMAGE_URL)](CLICK_TARGET_URL)
```

拆開看：

- `Badge Label`：替代文字，建議簡短，例如 `CI`、`PyPI`
- `BADGE_IMAGE_URL`：badge 圖片 URL
- `CLICK_TARGET_URL`：點擊後跳轉目的地

## Shields.io 常用參數

`img.shields.io` 常見 query parameters：

- `logo=`：加入 logo，例如 `python`、`pypi`
- `logoColor=`：設定 logo 顏色，常用 `white`
- `label=`：自訂左側標籤
- `color=`：自訂顏色
- `style=`：badge 風格，例如 `flat`、`flat-square`、`for-the-badge`、`social`

例子：

```text
https://img.shields.io/pypi/v/mlflow-widgets?logo=pypi&logoColor=white
https://img.shields.io/badge/MLflow-tracking-blue?logo=mlflow&logoColor=white
```

建議：

- 除非真的想做品牌感很強的 README，不然維持預設 `flat` 就夠了
- 同一份 README 最好不要混用太多 style
- 只有在靜態 badge 才考慮手動指定 `label` / `color`

## 常見 badge 類型與添加方式

下面這些模板可以直接複製，替換 `<owner>`、`<repo>`、`<package-name>` 之類的變數。

### 1. GitHub Actions workflow badge

格式：

```md
[![CI](https://github.com/<owner>/<repo>/actions/workflows/<workflow-file>/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/<workflow-file>)
```

本 repo 範例：

```md
[![CI](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml/badge.svg)](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/ci.yml)
[![Docs](https://github.com/daviddwlee84/mlflow-widgets/actions/workflows/docs.yml/badge.svg)](https://daviddwlee84.github.io/mlflow-widgets/)
```

注意：

- badge URL 綁的是 workflow 檔名，例如 `ci.yml`
- 如果 workflow 改名或搬檔案，badge URL 也要一起改
- `Docs` badge 可以連到 workflow 頁，也可以直接連到正式文件站

適用情境：

- `CI`
- `Docs`
- `Publish`
- `Release`

### 2. PyPI version badge

格式：

```md
[![PyPI](https://img.shields.io/pypi/v/<package-name>?logo=pypi&logoColor=white)](https://pypi.org/project/<package-name>/)
```

本 repo 範例：

```md
[![PyPI](https://img.shields.io/pypi/v/mlflow-widgets?logo=pypi&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
```

適用情境：

- 已經發到 PyPI 的 Python package
- 希望 README 一眼能看到已發布版本

### 3. Python versions badge

格式：

```md
[![Python](https://img.shields.io/pypi/pyversions/<package-name>?logo=python&logoColor=white)](https://pypi.org/project/<package-name>/)
```

本 repo 範例：

```md
[![Python](https://img.shields.io/pypi/pyversions/mlflow-widgets?logo=python&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
```

注意：

- 這個 badge 依賴 PyPI metadata
- 如果 `pyproject.toml` 的 `requires-python` 或 classifiers 沒更新，badge 也會跟著誤導

### 4. License badge

格式：

```md
[![License](https://img.shields.io/github/license/<owner>/<repo>)](https://github.com/<owner>/<repo>/blob/main/LICENSE)
```

本 repo 範例：

```md
[![License](https://img.shields.io/github/license/daviddwlee84/mlflow-widgets)](https://github.com/daviddwlee84/mlflow-widgets/blob/main/LICENSE)
```

### 5. PyPI downloads badge

適合放在第二排或次要區塊，展示套件使用量。

格式：

```md
[![Downloads](https://img.shields.io/pypi/dm/<package-name>)](https://pypi.org/project/<package-name>/)
```

例子：

```md
[![Downloads](https://img.shields.io/pypi/dm/mlflow-widgets)](https://pypi.org/project/mlflow-widgets/)
```

注意：

- 這是展示型 badge，不是核心信任訊號
- 除非下載量已經有代表性，不然不建議放第一排

### 6. GitHub release / tag badge

如果未來希望強調 GitHub Releases，也可以加。

最新 release：

```md
[![GitHub Release](https://img.shields.io/github/v/release/<owner>/<repo>)](https://github.com/<owner>/<repo>/releases)
```

最新 tag：

```md
[![GitHub Tag](https://img.shields.io/github/v/tag/<owner>/<repo>)](https://github.com/<owner>/<repo>/tags)
```

適用情境：

- release 是主要發佈通道
- PyPI 之外也想讓使用者注意 GitHub release notes

### 7. GitHub stars / forks badge

這是典型展示型 badge。

Stars：

```md
[![GitHub stars](https://img.shields.io/github/stars/<owner>/<repo>?style=flat)](https://github.com/<owner>/<repo>/stargazers)
```

Forks：

```md
[![GitHub forks](https://img.shields.io/github/forks/<owner>/<repo>?style=flat)](https://github.com/<owner>/<repo>/network/members)
```

適用情境：

- 想凸顯社群關注度
- 專案已經有一定規模

不建議：

- 小專案一開始就把它們放到第一排

### 8. GitHub issues / pull requests badge

適合做 repo 活躍度或 triage 入口。

Open issues：

```md
[![Issues](https://img.shields.io/github/issues/<owner>/<repo>)](https://github.com/<owner>/<repo>/issues)
```

Open pull requests：

```md
[![PRs](https://img.shields.io/github/issues-pr/<owner>/<repo>)](https://github.com/<owner>/<repo>/pulls)
```

適用情境：

- 開源 repo 想把貢獻入口做得更明顯

### 9. Last commit badge

適合展示近期維護狀態，但仍屬次要 badge。

```md
[![Last Commit](https://img.shields.io/github/last-commit/<owner>/<repo>)](https://github.com/<owner>/<repo>/commits/main)
```

注意：

- 如果 default branch 不是 `main`，連結要改
- 這種 badge 很容易把 README 變成狀態儀表板，請節制

### 10. Coverage badge

如果未來接上 Codecov 或 Coveralls，可以加 coverage badge。

Codecov：

```md
[![Coverage](https://img.shields.io/codecov/c/github/<owner>/<repo>)](https://codecov.io/gh/<owner>/<repo>)
```

Coveralls：

```md
[![Coverage Status](https://img.shields.io/coverallsCoverage/github/<owner>/<repo>)](https://coveralls.io/github/<owner>/<repo>)
```

適用情境：

- 已有穩定 coverage 上傳機制
- 希望公開測試覆蓋率

注意：

- 沒接 coverage service 就不要先放空 badge

### 11. Documentation provider badge

如果未來文件不是 GitHub Pages，而是其他平台，也可以用對應 badge。

Read the Docs：

```md
[![Docs](https://img.shields.io/readthedocs/<project-slug>)](https://<project-slug>.readthedocs.io/)
```

GitHub Pages：

- 通常沒有獨立的 Pages 狀態 badge，最穩定的做法仍然是用 `docs.yml` workflow badge

### 12. Static technology / ecosystem badge

如果真的想標示生態系，可以用靜態 badge。

例如：

```md
[![MLflow](https://img.shields.io/badge/MLflow-tracking-blue?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-widget-orange?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Marimo](https://img.shields.io/badge/Marimo-supported-green)](https://marimo.io/)
```

適用情境：

- 想傳達支援哪些平台、生態或整合

注意：

- 這些通常不是第一排 badge
- 靜態 badge 要自己維護文案，內容容易過時

### 13. Custom static badge

完全自訂文案時可以用：

```md
[![Label](https://img.shields.io/badge/<label>-<message>-<color>)](<target-url>)
```

例子：

```md
[![Notebook](https://img.shields.io/badge/notebook-anywidget-blue)](https://anywidget.dev/)
```

不推薦把這種 badge 拿來表示真實狀態，例如：

- `tests-passing`
- `docs-ready`
- `release-stable`

因為這些都可能跟實際狀態脫鉤。

## 用途對照表

| 需求 | 建議 badge | 優先級 |
|------|-----------|--------|
| 顯示 CI 是否健康 | GitHub Actions workflow | 高 |
| 顯示 docs 是否有部署 | GitHub Actions workflow | 高 |
| 顯示可安裝版本 | PyPI version | 高 |
| 顯示支援 Python 版本 | PyPI Python versions | 高 |
| 顯示授權 | GitHub license | 高 |
| 顯示下載量 | PyPI downloads | 中 |
| 顯示 release 節奏 | GitHub release / tag | 中 |
| 顯示活躍度 | last commit / issues / PRs | 中到低 |
| 顯示社群關注度 | stars / forks | 低 |
| 顯示生態整合 | static technology badge | 低 |

## README 排版建議

建議直接把 badge 放在標題下方，一行一個 badge：

```md
# mlflow-widgets

[![CI](...)](...)
[![Docs](...)](...)
[![PyPI](...)](...)
[![Python](...)](...)
[![License](...)](...)
```

這種寫法有幾個好處：

- GitHub README 與 PyPI long description 都容易穩定渲染
- Markdown diff 清楚
- 後續增刪 badge 時不容易把整排弄亂

如果之後覺得太高，也可以改成同一行，但可讀性通常不會更好多少。

如果未來 badge 變多，建議分兩排：

- 第一排：信任訊號，例如 `CI`、`Docs`、`PyPI`、`Python`、`License`
- 第二排：展示 / 生態 / 社群 badge，例如 `Downloads`、`Stars`、`MLflow`、`Jupyter`

## 如何新增一個 badge

建議照這個流程做：

1. 先定義用途：這個 badge 要回答什麼問題？
2. 找 source of truth：優先找 GitHub、PyPI、coverage service 這種動態來源
3. 決定點擊目標：workflow、docs、PyPI、LICENSE、issues 頁等
4. 先在這份 note 裡找模板，替換 owner / repo / package name
5. 貼到 `README.md` 頂部 badge 區塊
6. 本地檢查 Markdown 是否整齊
7. 到 GitHub README 和 PyPI long description 實際確認是否渲染正常

## 這個 repo 可直接替換的變數

目前這個 repo 的常用值：

- `<owner>` = `daviddwlee84`
- `<repo>` = `mlflow-widgets`
- `<package-name>` = `mlflow-widgets`
- default branch = `main`
- docs site = `https://daviddwlee84.github.io/mlflow-widgets/`

## 維護 checklist

只要碰到以下變更，就順手檢查 README badge：

- repo owner / repo name 改變
- workflow 檔名改變
- package name 改變
- PyPI project URL 改變
- `requires-python` 或 Python classifiers 改變
- 預設 branch 從 `main` 改名

如果新增了新的上游服務，也可以考慮補 badge，例如：

- 接上 Codecov 後加 coverage
- 建 GitHub Releases 節奏後加 release badge
- 上 conda-forge 後加 conda install badge

## 不推薦的做法

- 用靜態 `passing` / `ready` / `stable` badge 代表真實狀態
- 一開始就塞太多 showcase badge
- 放跟 repo 現況不同步的 ecosystem badge
- badge 連到不相關頁面，例如測試 badge 卻連到 repo 首頁
- 不同 badge style 混雜，例如一部分 `flat`、一部分 `for-the-badge`
- badge label 太長，讓第一屏看起來像監控面板

## 這份筆記的用途

下次如果要新增 badge，先問兩件事：

1. 這個 badge 是不是動態、可信、可維護？
2. 它是不是比現有前排 badge 更值得佔位置？

如果兩題都答不出來，通常就不該放進第一排。
