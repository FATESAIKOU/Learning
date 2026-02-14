# 步驟 1：理解＆詳細化需求（學習計劃）

## 任務前提＆狀況總結

### 專案背景
- 目標：學習 nanobot，最終產出可隨意部署的 Dockerfile / docker-compose 檔案
- 預期使用 OpenAI 做 LLM 認證（使用最便宜的模型 `gpt-4.1-nano`）
- 預期最終連線到 Telegram（保留在後續步驟）
- 認證方式：**方案 B2 確定**（Codex OAuth + 輕量級 proxy）
- 程式碼放在 `01_nanobot_dockerize/result`，報告放在 `01_nanobot_dockerize/report`

### Nanobot 調查結果
- **專案**：[nanobot-ai/nanobot](https://github.com/nanobot-ai/nanobot)（v0.0.55，Apache 2.0）
- **語言**：Go 80%、Svelte 12.7%、TypeScript 5.8%
- **本質**：開源 MCP (Model Context Protocol) Host / Agent Framework
- **功能**：將 MCP Server 包裝成智能 Agent，支援 chat UI、tool orchestration、MCP-UI
- **LLM Provider**：支援 OpenAI（透過 `OPENAI_API_KEY`）及 Anthropic
- **配置方式**：
  1. 單檔 `nanobot.yaml`
  2. 目錄結構（`agents/*.md` + `mcp-servers.yaml`）
- **預設 UI**：Web UI，port 8080
- **官方 Dockerfile**：已存在，基於 `golang:1.26-alpine` 建構、`cgr.dev/chainguard/wolfi-base` 運行
- **安裝方式**：Homebrew (`brew install nanobot-ai/tap/nanobot`) 或 GitHub Release 二進位（支援 Linux/macOS/Windows）

### 關鍵發現＆待確認事項
1. **Telegram 整合**：保留在後續步驟（Step 5/6），需進一步調查整合方式
2. **OpenAI 認證問題（重大發現 + 追加調查）**：
   - **User 原意**：只有 ChatGPT Plus 訂閱（$20/月），不想額外付費，想用 Codex OAuth
   - **初次調查結果**：Codex OAuth 是 Codex CLI 專用的 PKCE OAuth 流程，nanobot 需要 `OPENAI_API_KEY`
   - **追加調查：OpenClaw 如何使用 Codex OAuth**：
     - [OpenClaw](https://github.com/openclaw/openclaw)（193k stars）是個人 AI 助手，有內建 `openai-codex` provider
     - **OAuth PKCE 流程**：
       1. 產生 PKCE verifier/challenge + 隨機 state
       2. 開啟 `https://auth.openai.com/oauth/authorize?...`
       3. 在 `http://127.0.0.1:1455/auth/callback` 接收回調
       4. 在 `https://auth.openai.com/oauth/token` 交換 token
       5. 儲存 `{ access, refresh, expires, accountId }`
     - **關鍵發現**：OAuth access token 可以當作 Bearer token 呼叫 OpenAI Chat Completions API
     - **計費方式**：使用量計入 ChatGPT 訂閱的使用額度（不是另計 API 費用）
     - **Token 更新**：OpenClaw 內建自動 refresh 機制
   - **能否用於 nanobot？**
     - 理論上 **YES**：OAuth access token 可以設為 `OPENAI_API_KEY`，作為 Bearer token 使用
     - 但 nanobot **沒有內建 token refresh**，需要外部機制協助
   - **已決定**：採用方案 B2（Codex OAuth + 輕量級 proxy）
3. **最便宜的模型**：已確認使用 `gpt-4.1-nano`

### 認證問題的可能解決方案（更新版 v3）
| 方案 | 說明 | 優點 | 缺點 | 推薦度 |
|------|------|------|------|--------|
| **B2. Codex OAuth + 輕量級 proxy** | 寫 ~170 行 Python proxy，nanobot 透過 `OPENAI_BASE_URL` 指向 proxy | 完全自動化、穩定、使用 ChatGPT 訂閱額度 | 需額外開發 proxy（~3-5 小時） | ⭐⭐⭐⭐⭐ |
| A. Codex OAuth + 手動更新 token | 用 Codex CLI 取得 token → 設為 `OPENAI_API_KEY` | 極簡單 | token 過期需手動重複操作 | ⭐⭐ |
| B1. Codex OAuth + token 刷新腳本 | sidecar 腳本定期刷新 token 並重啟 nanobot | 半自動 | 需要重啟 nanobot，不穩定 | ⭐⭐⭐ |
| C. OpenAI API 免費額度 | 新帳號免費額度 | 簡單直接 | 額度有限 | ⭐⭐ |
| D. API 付費 (pay-as-you-go) | 設定 API Key | 最簡單 | 需額外付費 | ⭐⭐⭐⭐ |
| E. 使用其他免費 LLM | Ollama 本地模型 | 免費 | 可能品質不如 OpenAI | ⭐⭐ |

## Review紀錄（意思決定要点）
1回目:
- (Telegram 整合)：取消。User 同意不做 Telegram，改用 nanobot 內建 Web UI
- (OpenAI 認證)：User 表示只有 ChatGPT Plus 訂閱（$20/月），不想額外付費。調查後發現 Codex OAuth 無法直接用於 nanobot（Codex OAuth 是 Codex 專屬的認證，nanobot 需要 OPENAI_API_KEY）。**待決定解決方案**
- (使用模型)：確認使用 `gpt-4.1-nano`（最便宜）

2回目:
- (OpenClaw 調查)：User 提問「OpenClaw 可用 Codex OAuth，為何？能不能同樣用於 nanobot？」
  - 調查結果：OpenClaw 內建 `openai-codex` provider，實現 Codex OAuth PKCE 流程取得 access token，用該 token 當 Bearer token 呼叫 OpenAI API。使用量計入 ChatGPT 訂閱額度而非另計 API 費。
  - nanobot 可用同樣 token 作為 OPENAI_API_KEY，但缺少自動 refresh 機制，需要外部輔助。
  - **待決定**：認證方案選擇

3回目:
- (輕量級 Proxy 可行性估計)：User 要求估計 proxy 方案的開發成本
  - **重大發現**：nanobot **官方支援** `OPENAI_BASE_URL` 環境變數！
    - 原始碼位置：`pkg/cli/root.go`
    - 定義：`OpenAIBaseURL string \`env:"OPENAI_BASE_URL"\``
    - 經 `llmConfig()` 函式傳入 `responses.Config{BaseURL: n.OpenAIBaseURL}`
    - 最終在 `pkg/llm/responses/client.go` 使用此 URL 作為 API 端點
  - 這表示可以直接將 nanobot 指向本地 proxy，proxy 負責 token 管理後轉發至 OpenAI
  - 詳細估計見下方「輕量級 OAuth Proxy 可行性分析」

4回目:
- (方案確定)：User 確認採用 **方案 B2（Codex OAuth + 輕量級 proxy）**
- (步驟更新)：User 更新了 `01.Requirement.md`，步驟從 7 步改為 9 步
  - 新增 Step 2: 開發 openai-codex-oauth-proxy（主程式 & 測試程式碼各一份）
  - 新增 Step 3: 測試 openai-codex-oauth-proxy
  - Telegram 整合保留在 Step 5/6
- (結論)：Step 1 最終化完成，進入 Step 2

## 輕量級 OAuth Proxy 可行性分析

### 核心發現：nanobot 支援 `OPENAI_BASE_URL`

nanobot 原始碼確認支援以下環境變數（`pkg/cli/root.go`）：
```go
OpenAIAPIKey   string `env:"OPENAI_API_KEY"`
OpenAIBaseURL  string `env:"OPENAI_BASE_URL"`
```
這意味著可以直接將 nanobot 指向本地 proxy：
```
OPENAI_BASE_URL=http://oauth-proxy:9090/v1
OPENAI_API_KEY=placeholder
```

### 方案比較

#### 方案 B1：純 Token 刷新腳本（最簡單，但有缺陷）
- 用 Codex CLI 登入 → 取得 access token → 寫入環境變數 → 啟動 nanobot
- token 過期時需要重啟 nanobot
- **不推薦**：需要人工干預或頻繁重啟

#### 方案 B2：輕量級 OAuth Proxy（**推薦**）

##### 架構圖
```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Nanobot     │────▶│    OAuth Proxy       │────▶│  OpenAI API  │
│              │◀────│  (localhost:9090)    │◀────│              │
│ OPENAI_BASE  │     │                     │     │              │
│ _URL=proxy   │     │ 1. 接收 nanobot 請求  │     │              │
│ OPENAI_API   │     │ 2. 替換 Bearer token │     │              │
│ _KEY=dummy   │     │ 3. 轉發到 OpenAI     │     │              │
└──────────────┘     │ 4. 自動 refresh token│     └──────────────┘
                     └─────────────────────┘
                              │
                     ┌────────▼────────┐
                     │ ~/.codex/       │
                     │   auth.json     │
                     │ (token storage) │
                     └─────────────────┘
```

##### 1. 程式碼量估計

| 模組 | 行數（Python） | 說明 |
|------|---------------|------|
| Token 管理（讀取 auth.json + refresh） | ~40 行 | 讀取 Codex CLI 的 `~/.codex/auth.json`，自動 refresh |
| HTTP 反向代理 | ~40 行 | 接收請求、替換 Authorization header、轉發 |
| 首次 OAuth PKCE 登入流程 | ~70 行 | 產生 PKCE challenge、開啟瀏覽器、接收 callback、交換 token |
| Main / Config / 啟動 | ~20 行 | CLI 參數、啟動 uvicorn |
| **合計** | **~170 行** | 使用 FastAPI + httpx |

**依賴套件**：`fastapi`, `uvicorn`, `httpx`（3 個）

**如果省略 PKCE 登入流程**（改為先用 Codex CLI 登入）：
- 只需要 Token 管理 + 反向代理 = **~80-100 行**

##### 2. 單體測試方法

**完全可以單體測試**，不需要 nanobot：

```bash
# Step 1: 先用 Codex CLI 登入取得 token
codex auth login

# Step 2: 啟動 proxy
python oauth_proxy.py --port 9090

# Step 3: 用 curl 直接打 proxy（模擬 nanobot 發的請求）
curl http://localhost:9090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-nano",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# 如果收到正常的 OpenAI 回應 → proxy 運作正常
```

也可以寫簡單的測試：
```python
# test_proxy.py
import httpx
resp = httpx.post("http://localhost:9090/v1/chat/completions",
    json={"model": "gpt-4.1-nano", "messages": [{"role": "user", "content": "hi"}]})
print(resp.status_code, resp.json()["choices"][0]["message"]["content"])
```

##### 3. 如何連結 nanobot

**方法 A：環境變數（最簡單）**
```bash
export OPENAI_BASE_URL=http://localhost:9090/v1
export OPENAI_API_KEY=placeholder
nanobot run
```

**方法 B：Docker Compose（正式部署用）**
```yaml
services:
  oauth-proxy:
    build: ./proxy
    ports: ["9090:9090"]
    volumes:
      - codex-auth:/root/.codex  # 共享 token 檔案

  nanobot:
    image: ghcr.io/nanobot-ai/nanobot
    environment:
      OPENAI_BASE_URL: http://oauth-proxy:9090/v1
      OPENAI_API_KEY: placeholder
      NANOBOT_DEFAULT_MODEL: gpt-4.1-nano
    ports: ["8080:8080"]
    depends_on: [oauth-proxy]

volumes:
  codex-auth:
```

##### 4. 風險＆注意事項

| 項目 | 風險程度 | 說明 |
|------|---------|------|
| Token 過期 | 低 | proxy 自動 refresh，refresh token 有效期長 |
| 首次登入需要瀏覽器 | 中 | Docker 環境中需特殊處理（port-forward + 手動開 URL） |
| OpenAI 變更 OAuth 端點 | 低 | 目前穩定，但屬非公開 API |
| ChatGPT Plus 使用額度限制 | 中 | 需確認 gpt-4.1-nano 的額度是否充足 |
| 延遲增加 | 極低 | 本地 proxy 增加 <1ms |

##### 5. 開發時間估計

| 階段 | 預估時間 |
|------|---------|
| 基本 proxy（讀 auth.json + 轉發） | 1-2 小時 |
| 加入自動 refresh | +30 分鐘 |
| 加入 PKCE 登入流程 | +1-2 小時 |
| Docker 化 + 測試 | +1 小時 |
| **總計** | **3-5 小時** |

## 結果（レポート本体）

### 意思決定一覧

| # | 論點 | 決定内容 | 理由 |
|---|------|----------|------|
| 1 | Telegram 整合方式 | **取消** | User 決定不做 Telegram，使用 nanobot 內建 Web UI |
| 2 | OpenAI 認證方式 | **待決定**（推薦 B2: 輕量級 proxy） | nanobot 支援 `OPENAI_BASE_URL`，可指向 proxy；proxy ~170 行 Python、3-5 小時開發 |
| 3 | 使用模型 | **gpt-4.1-nano** | User 確認使用最便宜模型 |
| 4 | nanobot 版本策略 | 使用 GitHub Release 最新版二進位 | 專案仍在 alpha，使用二進位安裝最簡單穩定 |
| 5 | 配置方式 | 建議使用目錄結構方式 | 較彈性，易於 Docker volume 掛載管理 |

### 學習計劃

#### 整體架構概念

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  使用者 (瀏覽器)   │────▶│      Nanobot         │────▶│  OAuth Proxy     │
│  Web UI           │◀────│   (MCP Host)         │◀────│  (Python ~170行) │
│  port 8080        │     │   + nanobot.yaml     │     │  port 9090       │
└──────────────────┘     └──────────────────────┘     └────────┬─────────┘
                                                               │
                                                         ┌─────▼──────┐
                                                         │   OpenAI    │
                                                         │ gpt-4.1-nano│
                                                         │ (Codex OAuth│
                                                         │  Bearer)    │
                                                         └────────────┘
```

#### 各步驟詳細計劃（依更新後 9 步結構）

**步驟 2：開發 openai-codex-oauth-proxy（主程式 & 測試程式碼各一份）**
- 目標：開發輕量級 Python proxy，處理 Codex OAuth token 管理並轉發請求至 OpenAI
- 做法：
  1. Token 管理模組：讀取 `~/.codex/auth.json`、自動 refresh
  2. HTTP 反向代理：接收請求 → 替換 Authorization header → 轉發至 OpenAI
  3. （可選）PKCE OAuth 登入流程
  4. 撰寫測試程式碼
- 產出：`oauth_proxy.py`（主程式）+ `test_oauth_proxy.py`（測試）

**步驟 3：測試 openai-codex-oauth-proxy**
- 目標：單體驗證 proxy 可正確轉發請求並取得 OpenAI 回應
- 做法：
  1. 用 Codex CLI 登入取得 token
  2. 啟動 proxy，用 curl / 測試腳本驗證
  3. 確認 token refresh 機制正常運作
- 產出：測試結果報告

**步驟 4：下載 nanobot 使用 Docker 做最基本包裝啟動**
- 目標：在 Docker 容器中成功運行 nanobot
- 做法：
  1. 建立基礎 Dockerfile，從 GitHub Release 下載 nanobot 二進位
  2. 配置最簡單的 `nanobot.yaml`
  3. 在容器中啟動 nanobot，確認 Web UI 可訪問
- 產出：基礎 Dockerfile + 最小配置

**步驟 5：嘗試驗證連接 OpenAI / Telegram**
- 目標：確認 nanobot 可正常使用 OpenAI（透過 proxy）及 Telegram
- 做法：
  1. nanobot 透過 `OPENAI_BASE_URL` 連接 proxy，驗證對話功能
  2. 調查 nanobot Telegram 整合方式並嘗試連接
  3. 確認 `gpt-4.1-nano` 可正常回應
- 產出：驗證結果報告

**步驟 6：整理連結 OpenAI / Telegram 所需基本手續及保持檔案**
- 目標：整理清楚所有設定步驟和必要檔案
- 做法：
  1. 記錄 OpenAI OAuth 認證 + proxy 設定流程
  2. 記錄 Telegram 連結設定流程
  3. 列出所有需要持久化的設定檔和資料
- 產出：手續文件

**步驟 7：規劃/設計 Dockerfile / docker-compose**
- 目標：設計兩套配置（初期配置用 + 實際服務用）
- 做法：分析需求差異，設計檔案結構
- 產出：設計文件

**步驟 8：實現初期配置用 Dockerfile / docker-compose ＆ 測試**
- 目標：可用於首次設定（OAuth 登入、Telegram 連結等）的容器化方案
- 產出：可運行的 Dockerfile + docker-compose.yml + 測試結果

**步驟 9：實現實際服務用 Dockerfile / docker-compose ＆ 測試**
- 目標：可直接部署的完整方案
- 產出：正式版 Dockerfile + docker-compose.yml + 測試結果
