# L7benchmark - 高性能網站壓力測試工具

L7benchmark 是一個靈活、高效的 HTTP/HTTPS 壓力測試工具，專為網站性能評估和負載測試設計。通過非同步 IO 實現高併發請求處理，能夠模擬真實世界中的使用者行為。

## 🚀 主要特點

- **高併發處理**：基於 Python 的 asyncio 和 aiohttp，實現高效的非同步請求處理
- **可自訂的測試配置**：靈活調整並發連接數、測試時長等參數
- **詳細的實時統計**：提供即時的請求成功率和分佈資訊
- **靈活的 Profile 系統**：可編寫專屬測試模式，針對特定網站進行針對性測試
- **支援 SNI 和自訂 Headers**：滿足各種網站測試需求
- **IP 覆蓋功能**：可繞過 DNS 解析，直接指向特定 IP

## 📋 命令行參數

| 參數 | 描述 |
|------|------|
| `-u, --url` | 測試目標 URL (必填) |
| `-c, --connection` | 並發連接數 (預設: 10) |
| `--ip` | 覆蓋 DNS 解析，直接使用指定 IP |
| `-t, --time` | 測試持續時間 (秒，預設: 10) |
| `-b, --body` | 下載回應內容 (預設不下載) |
| `--shared-session` | 所有 worker 共享單一 client session（不建議使用）|
| `-H, --header` | 添加自訂 header，格式為 'Name: Value' (可多次使用) |
| `-p, --profile` | 指定測試模式檔案路徑 (預設: ./profiles/default.py) |
| `-X, --method` | 指定 HTTP 方法 (GET, POST, PUT, DELETE, HEAD, OPTIONS) |

## 💡 Profile 系統介紹

L7benchmark 最強大的功能是其 Profile 系統，它允許使用者為特定網站編寫客製化的測試模式。

### Profile 系統的優勢

1. **靈活性**：可以針對網站的特定部分或功能進行測試
2. **模擬真實用戶行為**：可編程性允許模擬用戶的瀏覽模式和操作流程
3. **狀態跟踪**：支援根據上一次請求的結果動態生成下一次請求
4. **易於擴展**：簡單的 Python 類繼承機制，容易開發新的測試模式

### 如何編寫自己的 Profile

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

使用自訂 Profile 和 Headers：
```bash
python l7benchmark.py -u https://example.com -p ./profiles/my_profile.py -H "User-Agent: Mozilla/5.0" -H "Accept-Language: zh-TW"
```

指定 IP 和 POST 方法：
```bash
python l7benchmark.py -u https://example.com --ip 203.0.113.1 -X POST
```

## 📈 結果解讀

測試結束後，L7benchmark 會顯示詳細的結果統計：
- 總請求數
- 各種 HTTP 狀態碼的分佈 (2xx, 3xx, 4xx, 5xx)
- 測試總時長

這些資訊可幫助您全面了解網站在負載下的表現，識別潛在的性能瓶頸和穩定性問題。
