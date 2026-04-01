# CI/CD Trigger Cheatsheet

什麼操作會觸發什麼 workflow 的速查表。

## 觸發規則總覽

| 操作 | 觸發的 Workflow | 結果 |
|------|----------------|------|
| `git push` 到 main | `ci.yml` + `docs.yml` | 跑 lint + test + build 驗證 + **部署文件到 GitHub Pages** |
| PR 到 main | `ci.yml` | 跑 lint + test + build 驗證，**不發佈、不部署文件** |
| `git tag v* && git push origin v*` | `publish.yml` → `publish-pypi` job | **發佈到 PyPI** |
| GitHub UI 手動觸發 (workflow_dispatch) | `publish.yml` → `publish-testpypi` job | 發佈到 TestPyPI |
| GitHub UI 手動觸發 docs workflow | `docs.yml` | 重新部署文件到 GitHub Pages |

## 關鍵結論

- **普通 `git push` 不會觸發 publish**，只跑 CI 測試
- **不需要走 PR 來發佈**，直接在 main 上打 tag 就行
- Tag 必須以 `v` 開頭（如 `v0.1.0`），才會匹配 `publish.yml` 的 `tags: - "v*"` 規則

## 發佈流程

```bash
# 1. 確保 main 上 CI 通過

# 2. 更新版本號
uv version --bump patch   # or minor / major

# 3. Commit + push
git add -A && git commit -m "bump version to x.y.z"
git push origin main

# 4. 打 tag 觸發發佈
git tag v0.1.1
git push origin v0.1.1
# → publish.yml 自動觸發，發佈到 PyPI
```

## Workflow 條件判斷（摘自 publish.yml）

```yaml
# ci.yml — 只在 push/PR 到 main 時跑
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# publish.yml — tag push 或手動觸發
on:
  push:
    tags:
      - "v*"
  workflow_dispatch:      # 手動觸發，可選 testpypi / pypi

# PyPI job 的額外條件
if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')

# TestPyPI job 的額外條件
if: github.event_name == 'workflow_dispatch' && github.event.inputs.target == 'testpypi'
```

## 注意事項

- Tag push 同時也會觸發 `ci.yml`（因為 push 到 main），所以 CI 和 publish 會並行跑
- 如果想更安全，可以在 `pypi` environment 加 protection rule（如 required reviewers）
- 兩個 workflow 互相獨立，publish 失敗不影響 CI，反之亦然
