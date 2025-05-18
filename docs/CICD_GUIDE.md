# GitHub CI/CD 構建指南

本文檔說明如何使用 GitHub Actions 自動構建 l7benchmark 的執行檔。

## 自動構建流程

### 觸發條件

以下任一情況會觸發自動構建：

1. 推送到 `main` 或 `master` 分支
2. 提交 Pull Request 到 `main` 或 `master` 分支
3. 手動觸發（通過 GitHub 界面的 "Actions" 選項卡）

### 構建平台

工作流程會在三個主要平台上構建：

- Windows
- macOS
- Linux

每個平台都會生成一個獨立的執行檔。

## 發布新版本

要發布新版本：

1. 更新代碼並確保所有功能按預期工作
2. 使用 `test_build.sh` 在本地測試構建
3. 創建一個新的 Git tag：
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions 會自動構建並將執行檔附加到發布中
5. 在 GitHub 上完成發布說明（可以使用 RELEASE_TEMPLATE.md 作為模板）

## 定制構建流程

如需修改構建流程：

1. 編輯 `.github/workflows/build.yml` 文件
2. 修改 PyInstaller 配置文件 `l7benchmark.spec`

### 常見修改

#### 添加更多依賴項

如果項目添加了新的依賴項，確保：

1. 將它們添加到 `requirements.txt`
2. 如果是隱式導入的模塊，在 `l7benchmark.spec` 的 `hiddenimports` 列表中添加它們

#### 更改 Python 版本

要更改 Python 版本，修改 `.github/workflows/build.yml` 中的 `python-version` 矩陣參數。

#### 添加新的構建平台

要添加更多構建平台，修改 `.github/workflows/build.yml` 中的 `os` 矩陣參數。

## 故障排除

如果構建失敗，請檢查：

1. GitHub Actions 日誌以獲取詳細錯誤信息
2. 本地使用 `test_build.sh` 測試以確認問題
3. 確保所有必要的依賴項都已在 `requirements.txt` 中列出
4. 確保 `l7benchmark.spec` 文件包含所有必要的隱式導入

## 疑難解答

### 內置模塊不可用

如果執行檔中某些模塊不可用，請確保它們在 `l7benchmark.spec` 的 `hiddenimports` 中列出。

### 文件打包問題

如果缺少某些文件，請確保它們在 `l7benchmark.spec` 的 `datas` 列表中正確列出。
