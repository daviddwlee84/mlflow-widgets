# GitHub Pages 設定筆記

日期：2026-04-01

## 問題

第一次推送 `docs.yml` workflow 後，deploy job 報 404 錯誤：

```
Error: Failed to create deployment (status: 404)
Ensure GitHub Pages has been enabled:
https://github.com/daviddwlee84/mlflow-widgets/settings/pages
```

原因：`actions/deploy-pages` 需要 GitHub Pages 的 Source 設為 **GitHub Actions**，但 repo 預設是 "Deploy from a branch"（或未啟用）。

## 手動設定步驟（一次性）

1. 到 repo 的 **Settings → Pages**
   - `https://github.com/<owner>/<repo>/settings/pages`
2. 在 **Build and deployment → Source** 下拉選單中，選擇 **GitHub Actions**（不是 "Deploy from a branch"）
3. 不需要選 branch 或 folder，workflow 會透過 `actions/upload-pages-artifact` + `actions/deploy-pages` 處理
4. 按 **Save**（如果有的話）
5. 重新跑 `docs.yml` workflow（或等下一次 push 到 main）

## 為什麼不能用 "Deploy from a branch"？

我們的 `docs.yml` workflow 用的是 GitHub Pages 的 **custom workflow** 部署模式：

```yaml
# 上傳 build artifact
- uses: actions/upload-pages-artifact@v3
  with:
    path: site

# 部署到 Pages
- uses: actions/deploy-pages@v4
```

這個模式需要 Pages Source 設為 "GitHub Actions"。如果設為 "Deploy from a branch"，GitHub 會期待從某個 branch（如 `gh-pages`）讀取靜態檔案，而 `deploy-pages` action 則會因為找不到 Pages environment 而回 404。

## 替代方案：`mkdocs gh-deploy`

如果不想改 Pages Source 設定，也可以用 MkDocs 內建的 `mkdocs gh-deploy` 指令，它會自動建立 `gh-pages` branch 並推送。但這種方式：

- 需要給 workflow 寫入權限（`contents: write`）
- 會在 repo 多一個 `gh-pages` branch
- 不如 `actions/deploy-pages` 乾淨（artifact-based，無額外 branch）

所以推薦用 GitHub Actions Source + `deploy-pages`。

## 相關連結

- [GitHub Pages custom workflows 官方文件](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
- [actions/deploy-pages](https://github.com/actions/deploy-pages)
- 本 repo 的 workflow：`.github/workflows/docs.yml`
