# README Badge Notes

日期：2026-04-01

整理這個 repo 在 README 頂部放 badge 時的實務原則，避免之後 badge 選太多、變成展示牆，或用到容易失真的靜態 badge。

## 結論先行

對這個 repo，README 頂部最值得保留的是這 5 類 badge：

- `CI`：目前主分支 / PR 的自動化測試狀態
- `Docs`：文件部署 workflow 狀態
- `PyPI`：目前已發布版本
- `Python`：支援的 Python 版本
- `License`：授權資訊

這 5 個 badge 的資訊密度最高，也最能快速建立使用者信任。

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
- ecosystem 宣示型 badge（例如 `MLflow`, `Jupyter`, `Marimo`, `anywidget`）

這些資訊不一定沒價值，但通常不該排在最前面。對 library README 來說，第一排應該先放「信任訊號」。

## 這個 repo 目前採用的 badge

### GitHub Actions workflow badge

適合 CI、docs deploy 這種 workflow 狀態。

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

### PyPI version badge

適合快速顯示「目前 PyPI 上的發布版本」。

格式：

```md
[![PyPI](https://img.shields.io/pypi/v/<package-name>?logo=pypi&logoColor=white)](https://pypi.org/project/<package-name>/)
```

本 repo 範例：

```md
[![PyPI](https://img.shields.io/pypi/v/mlflow-widgets?logo=pypi&logoColor=white)](https://pypi.org/project/mlflow-widgets/)
```

### Python versions badge

適合顯示套件 metadata 宣告支援的 Python 版本。

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

### License badge

適合快速顯示 repo 的授權型態。

格式：

```md
[![License](https://img.shields.io/github/license/<owner>/<repo>)](https://github.com/<owner>/<repo>/blob/main/LICENSE)
```

本 repo 範例：

```md
[![License](https://img.shields.io/github/license/daviddwlee84/mlflow-widgets)](https://github.com/daviddwlee84/mlflow-widgets/blob/main/LICENSE)
```

## README 寫法建議

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

## 維護 checklist

只要碰到以下變更，就順手檢查 README badge：

- repo owner / repo name 改變
- workflow 檔名改變
- package name 改變
- PyPI project URL 改變
- `requires-python` 或 Python classifiers 改變
- 預設 branch 從 `main` 改名

## 不推薦的做法

- 用靜態 `passing` / `ready` / `stable` badge 代表真實狀態
- 一開始就塞太多 showcase badge
- 放跟 repo 現況不同步的 ecosystem badge
- badge 連到不相關頁面，例如測試 badge 卻連到 repo 首頁

## 這份筆記的用途

下次如果要新增 badge，先問兩件事：

1. 這個 badge 是不是動態、可信、可維護？
2. 它是不是比現有前排 badge 更值得佔位置？

如果兩題都答不出來，通常就不該放進第一排。
