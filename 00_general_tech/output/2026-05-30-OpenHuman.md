# OpenHuman 技術分析報告

## 1. 這個技術解決什麼問題？

AI 模型（LLM）與 AI coding agent 面臨 **stateless（無狀態）** 的根本限制：每次對話結束後上下文即消失，模型無法持續記住使用者的資料、偏好、工作脈絡與跨工作階段的歷史。現有「記憶」方案僅存少量 bullet points，不足以支撐 agent 在長時間跨度內對使用者工具生態系（Gmail、Slack、GitHub、Notion 等）形成有意義的認知。

OpenHuman 解決的具體問題是：**如何讓一個 AI agent 在安裝後數分鐘內即獲得使用者跨服務的完整脈絡，並在此後持續自動更新該認知，且無需使用者手動訓練或手動撰寫 prompt。**

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

- LLM 本質上是 stateless function：輸入 prompt，輸出 response，context 在請求結束後不保留。
- 大多數 agent harness（Claude Cowork、OpenClaw、Hermes Agent）從「冷啟動」開始，使用者需花費數天到數週才能讓 agent 累積足夠上下文變得有用。
- 現有方案的記憶機制依賴外掛（plugin）輪詢、手動 `CLAUDE.md` / `.cursorrules` 編輯（上限約 200 行且會過時），或向量嵌入黑盒檢索。
- 靈感來源：Andrej Karpathy 的 [obsidian-wiki workflow](https://x.com/karpathy/status/2039805659525644595)，將個人知識庫以 Obsidian Markdown 形式組織。

### 通用技術背景

- **Context window 的容量與成本衝突**：雖然現代 LLM context window 已達百萬 token 級別，但將全部個人資料每次塞入 context 的成本過高（金錢與延遲）。
- **多服務資料孤島**：使用者日常資料分散在 Gmail、Slack、GitHub、Notion、Linear 等互不連通的 SaaS 服務中，沒有統一的本地索引層。
- **OAuth 整合碎片化**：每個第三方服務的 API 認證與資料格式不同，手工接上所有服務的 API key 與 polling 邏輯對終端使用者不可行。
- **向量資料庫的侷限性**：純向量檢索回答「與 query 相似的內容」，但無法回答結構化時序問題（如「上週二下午 3 點 Stripe webhook 說了什麼？」）。

## 3. 這個技術是如何解決該問題的？

OpenHuman 透過以下 **核心機制疊加** 解決 stateful AI agent 的問題：

### 3.1 Memory Tree（記憶樹）

一條 **deterministic pipeline**，將所有來源的原始資料轉化為結構化、可查詢、有摘要的 Markdown 知識庫，全程在本地機器執行：

```
來源適配器（chat / email / document）
        │
        ▼
canonicalize    正規化為 Markdown + 出處 metadata
        │
        ▼
chunker         確定性 ID、≤3k-token 邊界分段
        │
        ▼
content_store   寫入本地 .md 檔案
        │
        ▼
store           持久化至 SQLite（chunks.db）
        │
        ▼
score           信號評分 + embeddings + 實體抽取
        │
        ▼
source/topic/global trees  三種範圍的摘要樹
        │
        ▼
retrieval       查詢：search / drill_down / topic / global / fetch
```

三種樹形結構：

| 樹類型 | 範圍 | 說明 |
|--------|------|------|
| Source tree | 按來源（每 Gmail label、每 Slack channel、每文件） | L0 緩衝區滿後 seal 為 L1 摘要，層層級聯 |
| Topic tree | 按實體（人、專案、ticker、repo） | 由 hotness 驅動惰性構建，出現頻率越高越積極刷新 |
| Global tree | 每日全局摘要 | 每日 UTC 00:00 為前一天生成一個 global digest 節點 |

Leaf（葉節點）生命週期狀態機：

```
pending_extraction → admitted → buffered → sealed
        \
         → dropped
```

### 3.2 Auto-fetch（自動拉取）

每 **20 分鐘** 一個全域 tick 遍歷所有已啟用的 integration connection，呼叫對應 native provider 的 `sync()`，將新資料饋入 Memory Tree pipeline。

- State 以 `(toolkit, connection_id)` 為單位儲存（cursor、last-sync timestamp、dedup set、daily budget）
- 每個 provider 自己宣告 `sync_interval_secs`
- 每個 connection 有 daily request budget 上限防止 API 費用爆炸
- 錯誤吞下不 panic，確保排程迴圈不中斷

### 3.3 TokenJuice（Token 壓縮）

所有 tool 呼叫結果在進入 LLM context **之前**，經由三層 rule overlay（Builtin → User `~/.config/tokenjuice/rules/` → Project `.tokenjuice/rules/`）進行壓縮：

- HTML 轉 Markdown
- 長 URL 縮短
- 重複行去重
- 正則匹配刪除
- 區段摘要
- CJK / emoji / 多位元組文字保留不刪

效果：同等資訊量下 token 數減少最高 80%，使掃描六個月郵件僅需個位數美元而非數百美元。

### 3.4 Model Routing（模型路由）

Agent loop 根據 **任務本質** 自動選擇模型，而非讓使用者手動切換：

| Hint | 典型目標 | 使用場景 |
|------|----------|----------|
| `hint:reasoning` | 強推理模型 | 多步驟規劃、數學、重度程式碼 |
| `hint:fast` | 快速便宜模型 | UI 輔助、自動完成、小分類 |
| `hint:vision` | 視覺模型 | 截圖、圖片附件、OCR |
| `hint:summarize` | 擅長壓縮的模型 | Memory tree 摘要構建 |
| `hint:code` | 程式碼調校模型 | 原生 coder 回合 |

後端在單一訂閱下代理多供應商（Anthropic、OpenAI、Google、Groq 等），支援可選的本地 Ollama。

### 3.5 Obsidian Wiki Vault

Memory Tree 中的所有 chunk 同時以 `.md` 檔案落盤至 `<workspace>/wiki/`，可使用 Obsidian 開啟瀏覽與編輯。使用者的手動編輯會被 pipeline 重新攝取。

```
<workspace>/
└── wiki/
    ├── summaries/   # 自動生成的 source / topic / global 摘要
    ├── notes/       # 使用者手寫筆記
    └── …            # 每個已連接 toolkit 一個資料夾
```

### 3.6 118+ Third-party Integrations

一鍵 OAuth 連接 Gmail、GitHub、Slack、Notion、Stripe 等服務，每個 connection 作為 typed tool 暴露給 agent。預設使用 OpenHuman 管理的 Composio connector layer 代理 OAuth 與 API 呼叫。

### 3.7 技術架構

```
┌──────────────────────────────────────────────────┐
│ Tauri shell (app/src-tauri/)                     │
│ • 視窗、OS 整合、sidecar 生命週期                 │
│ • CEF 子 webview（用於 integration providers）    │
└──────────────────────────────────────────────────┘
        │ JSON-RPC (HTTP)
┌──────────────────────────────────────────────────┐
│ Rust core (`openhuman` binary, src/)             │
│ • Memory Tree pipeline                           │
│ • Integration adapters + auto-fetch scheduler    │
│ • Provider router（模型路由）                     │
│ • TokenJuice 壓縮                                │
│ • 原生工具（搜尋、fetch、fs、git、…）             │
│ • 語音（STT 輸入、TTS 輸出、Meet agent）          │
└──────────────────────────────────────────────────┘
        │
┌──────────────────────────────────────────────────┐
│ React 前端 (app/src/)                            │
│ • 畫面、導航                                      │
│ • 透過 coreRpcClient 與 core 通訊                 │
│ • 無業務邏輯 — 僅呈現層                           │
└──────────────────────────────────────────────────┘
```

- 語言比重：Rust 61.1%、TypeScript 35.5%、JavaScript 1.7%
- 授權：GPL-3.0
- 桌面殼層：Tauri v2
- 套件管理：pnpm 10.10.0
- 記憶體後端：SQLite（rusqlite, bundled）
- 可選外部記憶體後端：agentmemory

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（決策輔助表）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **OpenHuman** | 本地 Memory Tree pipeline（canonicalize → chunk → score → summary trees）+ 20 分鐘 auto-fetch + TokenJuice 壓縮 + 模型路由 + Obsidian vault | 需安裝桌面應用（macOS/Linux/Windows）；需 OpenHuman 訂閱帳號（含模型路由與 OAuth proxy）；OAuth 授權各第三方服務 | 本地 SQLite DB 佔用磁碟空間；auto-fetch 持續消耗網路與 CPU；非所有 LLM 呼叫都走本地（預設經後端代理）；GPL-3.0 授權限制 | Agent 在首次 sync 後即獲得跨服務完整脈絡；token 成本降 80%；記憶透明可讀（Obsidian vault） |
| **agentmemory** | 基於 iii-engine 的持久記憶伺服器，hook-driven 自動捕獲 agent session 內容（prompts、tool calls、results），BM25 + Vector + Graph RRF 融合檢索，12 auto hooks + 53 MCP tools | 需 Node.js 執行環境；需安裝 iii-engine runtime（或 Docker）；需在各 agent 端配置 MCP/hooks | 記憶儲存於 SQLite（本地）；iii-engine 為獨立 process 需額外資源；MCP 通訊 overhead；僅覆蓋 coding agent session 層級（不含 Gmail/Slack 等第三方服務原生整合） | Session 間 context 持久化，R@5 95.2%，token 節省 92%，跨 agent 共享記憶（Claude Code、Codex、Cursor 等） |
| **Mem0** | API-based 記憶層，將對話歷史與使用者偏好抽取為結構化記憶，支援向量 + graph 檢索 | 需註冊 Mem0 雲端帳號或自行部署；需外部向量資料庫（Qdrant/pgvector）；需在應用程式碼中呼叫 `add()` API | 記憶為被動添加（手動 `add()` 呼叫）；雲端方案有資料隱私顧慮；需外部依賴（向量 DB）；R@5 約 68.5%（LoCoMo 基準） | 為 LLM 應用提供長期記憶層，適合 chatbot 型產品整合 |
| **Letta / MemGPT** | 全 agent runtime，agent 自行管理記憶（core memory + archival memory），透過自我編輯與 retrieval 維持長期上下文 | 需使用 Letta runtime（框架鎖定）；需 Postgres + 外部向量 DB；需部署與維護 agent server | 高度框架鎖定（必須在 Letta 生態系內）；基礎設施依賴重；agent 自我編輯可能偏離使用者意圖；非 coding agent 專用 | Agent 具備自我管理記憶能力，R@5 約 83.2%（LoCoMo），適合需要自主記憶管理的對話型 agent |
| **Claude Cowork（Anthropic）** | Claude 模型的協作模式，chat-scoped 記憶（僅在單一 session 內保留上下文），封閉原始碼 | 需 Claude 訂閱 / API key；僅支援 Claude 模型；封閉生態 | Chat-scoped 僅當次有效；整合數量少；需額外 API key；非開源 | 單一 session 內高品質協作，適合一次性深度工作 |
| **OpenClaw** | MIT 開源 agent harness，terminal-first，plugin-reliant 記憶機制，BYO models | 需自行配置模型 API key；terminal-first 操作（無 GUI）；需手動配置 plugins 取得上下文 | 多供應商 API key 管理負擔；記憶仰賴 plugin；無 auto-fetch；上手門檻較高 | 彈性高（MIT 授權），適合開發者自訂 agent 工作流 |
| **Hermes Agent** | MIT 開源 agent，self-learning 記憶（agent 自行從互動中學習），terminal-first，BYO models | 需自行配置模型 API key；terminal-first；需自行配置記憶策略 | 多供應商管理負擔；學習期長；無 auto-fetch；無第三方服務 OAuth 整合 | Agent 可從對話中自行學習使用者偏好，開源彈性高 |

### 各方案切入點差異

- **OpenHuman**：以 **本地知識庫自動構建 + 多服務 OAuth 一鍵整合** 為切入點，強調「數分鐘內獲得完整脈絡」，適合需要跨服務個人助理的非技術使用者。
- **agentmemory**：以 **coding agent session 間記憶共享** 為切入點，強調跨 agent（Claude Code / Codex / Cursor / OpenCode）的統一記憶層，適合重度 coding agent 使用者。
- **Mem0**：以 **LLM 應用的記憶 API** 為切入點，適合開發者在其 LLM 應用中嵌入記憶功能。
- **Letta/MemGPT**：以 **agent 自我管理記憶的完整 runtime** 為切入點，適合需要自主記憶管理的對話型 agent 研究與部署。
- **Claude Cowork / OpenClaw / Hermes**：以 **不同開放程度與模型策略的 agent harness** 為切入點，記憶能力非其核心差異化功能。
