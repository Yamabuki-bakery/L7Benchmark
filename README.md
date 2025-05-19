該 Readme 由 Copilot 小姐編寫．

# L7benchmark - 高性能網站壓力測試工具

L7benchmark 是一個靈活、高效的 HTTP/HTTPS 壓力測試工具，專為網站性能評估和負載測試設計。通過非同步 IO 實現高併發請求處理，能夠模擬真實世界中的用戶行為。

## 🚀 主要特點

- **高併發處理**：基於 Python 的 asyncio 和 aiohttp，實現高效的非同步請求處理
- **可自定義的測試配置**：靈活調整併發連接數、測試時長等參數
- **詳細的實時統計**：提供即時的請求成功率和分佈信息
- **靈活的 Profile 系統**：可編寫專屬測試模式，針對特定網站進行針對性測試
- **支持 SNI 和自定義 Headers**：滿足各種網站測試需求
- **IP 覆蓋功能**：可繞過 DNS 解析，直接指向特定 IP

## 📋 命令行參數

| 參數 | 描述 |
|------|------|
| `-u, --url` | 測試目標 URL (必填) |
| `-c, --connection` | 併發連接數 (默認: 10) |
| `--ip` | 覆蓋 DNS 解析，直接使用指定 IP |
| `-t, --time` | 測試持續時間 (秒，默認: 10) |
| `-b, --body` | 下載回應內容 (默認不下載) |
| `-H, --header` | 添加自定義 header，格式為 'Name: Value' (可多次使用) |
| `-p, --profile` | 指定測試模式文件路徑 (默認: ./profiles/default.py) |
| `-X, --method` | 指定 HTTP 方法 (GET, POST, PUT, DELETE, HEAD, OPTIONS) |
| `--debug` | 進入 Debug 模式，發出單個請求，顯示每個請求和回應的詳細信息 |
| `--timeout` | 設置每個請求的超時時間（秒，默認: 60）|

## 💡 Profile 系統介紹

L7benchmark 最強大的功能是其 Profile 系統，請你設想以下場景——（😁）

 1. 你想要測試登錄功能，並且需要在登錄後進行一些操作。
 1. 你想要按照一定的順序來測試多個頁面．
 1. 你想要以特定的規則生成隨機數據，並餵給 API 接口。
 1. 你準備了一套測試數據，並且想要在測試中讀取並運用。
 1. 在開始測試之前，你想要先拿到 WAF 的 cookie。
 1. 你想要使用變幻莫測的 Header 來測試網站的安全性。
 1. 你想要在測試過程中，根據上一次請求的結果來決定下一次請求的 URL 和方法。

你有無數的測試方法，而我沒法設計一套事無鉅細的命令行參數來滿足你．所以我將把編寫測試規則的能力交還到你手中．
這就是 Profile 系統的目的．

（你可以不使用自定義 Profile，默認 Profile「default」將會遵循你給出的命令行參數來運行．）

### 如何編寫自己的 Profile

請查看 [`profiles/default.py`](./profiles/default.py) 文件，這是默認的 Profile 實現。你也可以查看其他 Profile 並從中獲取靈感，並根據自己的需求進行修改。

每個 Profile 都必須繼承 `BaseProfile` 類，並實現 `generate_request` 方法，該方法應返回一個 `RequestInfo` 對象：

```python
class MyCustomProfile(BaseProfile):
    def __init__(self, args: Args, first_url: str, hostname: str):
        super().__init__(args=args, first_url=first_url, hostname=hostname)
        # 初始化自己的狀態
        
    def generate_request(self, worker_id: int, last_url: Optional[str], last_status_code: Optional[int]) -> RequestInfo:
        # 根據需要生成下一個請求
        return RequestInfo(
            method=HttpMethod.GET,
            url="https://example.com/path",
            hostname=self.hostname,
            headers=self.custom_headers,
            body=None
        )

# 務必導出你的 Profile 類
ExportedProfile = MyCustomProfile
```

generate_request 方法將會在測試中被成千上萬次調用，因此應該保持高效。您可以使用 `last_url` 和 `last_status_code` 來決定下一個請求的 URL 和方法。

## 🌟 使用範例

基本用法：
```bash
python l7benchmark.py -u https://example.com -c 50 -t 30
```

使用自定義 Profile 和 Headers：
```bash
python l7benchmark.py -u https://example.com -p ./profiles/my_profile.py -c 50 -t 30 
```

指定 IP 和 POST 方法：
```bash
python l7benchmark.py -u https://example.com --ip 203.0.113.1 -X POST
```

使用調試模式查看請求與回應：
```bash
python l7benchmark.py -u https://example.com --debug
```

## 📈 結果解讀

測試結束後，L7benchmark 會顯示詳細的結果統計：
- 總請求數
- 各種 HTTP 狀態碼的分佈 (2xx, 3xx, 4xx, 5xx)
- 測試總時長

這些信息可幫助您全面瞭解網站在負載下的表現，識別潛在的性能瓶頸和穩定性問題。

## 📦 自動構建

本項目使用 GitHub Actions 來自動構建 Windows、macOS 和 Linux 的可執行文件。

### 下載預編譯的可執行文件

你可以從 [GitHub Releases](https://github.com/YOUR_USERNAME/l7benchmark/releases) 頁面下載最新的預編譯可執行文件。

### 自動構建流程

每當代碼推送到 `main` 或 `master` 分支時，或者提交 Pull Request 到這些分支時，會自動觸發構建流程：

1. 在 Windows、macOS 和 Linux 平臺上並行構建
2. 使用 PyInstaller 打包應用為獨立可執行文件
3. 構建的可執行文件將作為 GitHub Actions 的 artifacts 上傳
4. 當發佈新標籤 (tag) 時，可執行文件會自動附加到 GitHub Release

### 手動觸發構建

你也可以在 GitHub 界面中通過 "Actions" 選項卡手動觸發構建流程。

### 本地測試構建

在推送到 GitHub 前，你可以使用以下命令在本地測試構建：

```bash
./test_build.sh
```

## 🛠️ 自定義構建

如需修改構建配置，請編輯以下文件：

- `.github/workflows/build.yml` - GitHub Actions 構建配置
- `l7benchmark.spec` - PyInstaller 打包配置
