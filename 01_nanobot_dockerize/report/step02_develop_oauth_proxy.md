# 步驟 2：開發 openai-codex-oauth-proxy

## 任務前提＆狀況總結

### 任務目標
- 開發一個輕量級 Python HTTP 反向代理（openai-codex-oauth-proxy）
- 純透傳架構：nanobot 的 Responses API 請求 → proxy 注入 token/headers → 轉發至 ChatGPT backend

### 技術前提（來自前次調查）

> 前次開發的 proxy（目標 api.openai.com）在整合測試中發現架構不匹配，
> 經過 Codex CLI 原始碼分析、JWT scope 解碼、多個開源專案（OpenClaw, oculairmedia/openai-chatgpt-max-proxy, Sam Saffron/term-llm）佐證，
> 以及 nanobot 原始碼閱讀，得出以下結論。舊程式碼已清除，從零重寫。

#### Codex OAuth 架構事實
- OAuth token scope 僅 `openid profile email offline_access`，**無法**存取 `api.openai.com`
- 必須使用 `https://chatgpt.com/backend-api/codex` 端點
- API 格式為 Responses API（`POST /responses`），非 Chat Completions
- 必要 headers：`Authorization`, `ChatGPT-Account-ID`, `originator`, `OpenAI-Beta`
- 可用模型限 GPT-5 Codex 系列（gpt-5.3-codex, gpt-5.2-codex, gpt-5.1-codex-mini 等）

#### Nanobot 原生相容性
- nanobot 預設使用 Responses API（`POST {BaseURL}/responses`）
- 支援自訂 `BaseURL`（`OPENAI_BASE_URL` 環境變數）和 `Headers`
- **nanobot 送出的 request body 與 ChatGPT backend 接收的格式一致 → 不需要格式轉換**

#### 結論
- proxy 本質上是一個 **token-injecting reverse proxy**
- 複雜度：低（~80-100 行），比原先預估的格式轉換 proxy（~500 行）大幅簡化
- 參考：Sam Saffron/term-llm（Go）、oculairmedia/openai-chatgpt-max-proxy（Python）

### User 決定（Step 3 Review 3）
1. ✅ 採用方案 C（純透傳 proxy + Token 注入）
2. ✅ Step 2 動手實現前，先驗證 nanobot 的 Responses API request body 格式
3. ✅ originator 設為 `"nanobot-proxy"`
4. ✅ 支援 `GET /models` 端點

### 預期架構
```
nanobot (OPENAI_BASE_URL=http://proxy:9090, Responses API 格式)
    │
    ▼
┌─────────────────────────────┐
│   oauth-proxy (:9090)       │
│                             │
│ 1. 接收請求                  │
│ 2. 讀取/refresh OAuth token │
│ 3. 注入 headers:            │
│    - Authorization           │
│    - ChatGPT-Account-ID     │
│    - originator              │
│    - OpenAI-Beta            │
│ 4. 轉發至 ChatGPT backend  │ ──▶ https://chatgpt.com/backend-api/codex/...
│ 5. 透傳 SSE streaming 回應  │
└─────────────────────────────┘
```

## Review紀錄（意思決定要点）


## 結果（レポート本体）

### 前置驗證：nanobot Responses API request body 確認

（⏳ 待執行 — 動手寫程式之前先完成此驗證）

**驗證目的**：確認 nanobot 實際發送的 HTTP request body 格式，確保與 ChatGPT backend 的 Responses API 相容。

**驗證方法**：
1. 啟動一個 HTTP capture server（port 9090），記錄所有收到的 request
2. 設定 `OPENAI_BASE_URL=http://localhost:9090` 啟動 nanobot
3. 在 nanobot UI 送出一條訊息
4. 檢查 capture server 記錄的 request：
   - 端點路徑（預期 `POST /responses`）
   - Headers（Content-Type, Authorization 等）
   - Body 格式（預期 Responses API：model, instructions, input, stream, store 等欄位）

**預期結果**：
- nanobot 送出 `POST /responses`，body 為 Responses API 格式
- proxy 只需透傳 body，注入/替換 headers 即可

### 意思決定一覧

### 程式架構設計

### 關鍵技術參數

| 項目 | 值 | 來源 |
|------|-----|------|
| Client ID | `app_EMoamEEZ73f0CkXaXp7hrann` | Codex CLI / 多專案驗證 |
| Refresh URL | `https://auth.openai.com/oauth/token` | Codex CLI / 多專案驗證 |
| 轉發目標 | `https://chatgpt.com/backend-api/codex` | Step 3 調查驗證 |
| 注入 Headers | `Authorization`, `ChatGPT-Account-ID`, `originator`, `OpenAI-Beta` | term-llm / Codex CLI |
| originator | `nanobot-proxy` | User 決定 |
| OpenAI-Beta | `responses=experimental` | term-llm |
| auth.json 格式 | `{"tokens": {"access_token": "...", "refresh_token": "..."}}` | Codex CLI |
| JWT claim | `chatgpt_account_id` → `ChatGPT-Account-ID` header | 多專案驗證 |
| Body 強制欄位 | `store: false`（ChatGPT backend 要求） | Codex CLI / term-llm |

### 預期產出

### nanobot 配置方式（搭配 proxy 使用）

```bash
# 啟動 proxy
python oauth_proxy.py --port 9090

# 啟動 nanobot，指向 proxy
export OPENAI_BASE_URL=http://localhost:9090
export OPENAI_API_KEY=dummy   # proxy 會替換為真實 OAuth token
nanobot run ./nanobot.yaml
```
