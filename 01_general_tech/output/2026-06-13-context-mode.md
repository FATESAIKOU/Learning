# context-mode 分析報告

## 1. 這個技術解決什麼問題？

AI 編碼代理（Claude Code、Cursor、Gemini CLI、OpenCode 等）在執行工具呼叫時，原始工具輸出（Bash、Read、WebFetch、Grep）直接進入 LLM context window，造成三個連鎖問題：

- **Context window 被原始資料淹沒**：單次 Playwright snapshot 佔 56 KB、20 個 GitHub issues 佔 59 KB、一次 access log 佔 45 KB。30 分鐘後約 40% context 被工具輸出消耗。
- **Conversation compaction 後狀態遺失**：當對話因 context 滿而觸發 compaction（摘要壓縮）時，代理遺忘正在編輯哪些檔案、進行中的任務、以及使用者最後的要求。
- **LLM 被當作資料處理器而非程式碼生成器**：代理反覆呼叫 Read/Grep 讀取大量檔案送入 LLM 做分析（如「計算所有 .ts 檔的行數」），消耗數百 KB context，而非寫一段 script 在隔離環境執行並只回傳結果。

context-mode 宣稱將 315 KB 原始工具輸出壓縮至 5.4 KB 進入 context（98% 縮減），同時在 compaction 後透過 FTS5/BM25 搜尋恢復會話狀態。

## 2. 這個問題為什麼會發生？（背景）

| 面向 | 文章中明確提到 | 通用技術背景 |
|---|---|---|
| MCP 工具無輸出治理 | 每個 MCP 工具呼叫將原始資料傾瀉至 context window，無中間層過濾或壓縮 | MCP 協議（Model Context Protocol）僅定義工具接口與 JSON-RPC 傳輸，不規範工具輸出的壓縮策略、快取或生命週期管理 |
| LLM context window 有限且競爭 | Claude 的 context window 為 200,000 tokens，工具輸出與推理需求競爭同一空間 | Transformer 架構的 attention 機制對輸入全量計算（O(n²)），無用 tokens 仍消耗計算資源與記憶體；context window 大小受硬體限制 |
| Conversation compaction 為破壞性操作 | 代理 compact 對話時以摘要取代歷史，遺失精確的檔案路徑、任務狀態、使用者決策 | LLM API 多為無狀態設計，不維護跨請求持久記憶；compaction 是客戶端實作，無標準化狀態保存機制 |
| 代理預設行為為「讀取→分析」模式 | 代理傾向反覆呼叫 Read 工具將檔案內容送入 LLM 做分析，而非生成程式碼在外部執行 | 現有 AI 編碼代理的工具選擇策略未區分「資料處理」與「程式碼生成」兩種任務模式，缺乏路由指引 |

根因歸結為：AI 編碼代理與 LLM 之間缺少一個專門管理 context 生命週期的中間層。現有架構中，context 是每個請求的臨時產物，而非被治理的持久資源。

## 3. 這個技術是如何解決該問題的？

context-mode 是一個 MCP server（同時也是 Claude Code / OpenCode / KiloCode / Cursor / OpenClaw 等 15+ 平台的 plugin），在 AI 編碼代理與 LLM 之間插入四個面向的 context 治理層：

```
AI 代理工具呼叫 (Bash / Read / WebFetch / Grep / Task)
        │
        ▼
   context-mode (MCP server + Hooks)
   ╔══════════════════════════════════════════════════════════╗
   ║  Context Saving  │  Session Continuity  │  Think in Code  ║
   ╚══════════════════════════════════════════════════════════╝
        │
        ▼
   送入 LLM 的 context（僅摘要、搜尋結果、script 輸出）
```

### 3.1 Context Saving — 隔離子程序 + FTS5 索引

核心機制是將資料處理從 LLM context 移至隔離子程序（sandbox subprocess），原始資料永不進入 context window。

**11 個 MCP 工具的分工：**

| 工具 | 功能 | 原始資料去向 |
|---|---|---|
| `ctx_execute` | 在隔離子程序中執行 12 種語言的程式碼，僅 stdout 進入 context | 子程序內處理，輸出 >100KB 時自動索引至 FTS5 |
| `ctx_execute_file` | 讀取檔案至子程序變數 `FILE_CONTENT`，執行處理程式碼，檔案內容永不進入 context | 檔案內容在子程序內，僅處理結果輸出 |
| `ctx_batch_execute` | 執行多個 shell 命令，自動索引全部輸出，以多個查詢搜尋 | 全部輸出索引至 FTS5，僅搜尋結果進入 context |
| `ctx_index` | 將內容或檔案索引至 FTS5 知識庫 | 儲存於 SQLite FTS5，不進入 context |
| `ctx_search` | 以三層 fallback 搜尋 FTS5 知識庫（Porter stemming → Trigram substring → Fuzzy Levenshtein） | 僅搜尋結果片段進入 context |
| `ctx_fetch_and_index` | 在子程序中 fetch URL，轉換 HTML→Markdown，索引至 FTS5 | 原始 HTML 在子程序內，僅 preview 進入 context |
| `ctx_stats` | 回傳當前 session 的 context 節省統計 | — |
| `ctx_doctor` | 診斷安裝狀態（12 語言 runtime、FTS5、hooks） | — |
| `ctx_upgrade` | 自我更新至最新版本 | — |
| `ctx_purge` | 永久刪除所有索引內容與 session 資料 | — |
| `ctx_insight` | 開啟本機 analytics 儀表板（90 指標、37 insight patterns） | — |

**Hook 系統的路由強制：**

| Hook | 觸發時機 | 動作 |
|---|---|---|
| PreToolUse | 工具呼叫前 | Bash(curl/wget) → 重導向至 `ctx_fetch_and_index`；WebFetch → 拒絕並重導向；Read → 提示改用 `ctx_execute_file`；Grep → 提示改用 `ctx_execute` |
| PostToolUse | 工具呼叫後 | 捕獲 session 事件（檔案編輯、git 操作、錯誤）寫入 SQLite |
| SessionStart | 會話啟動 | 注入 XML routing block 至 system prompt，指示工具選擇階層 |
| PreCompact | compaction 前 | 建立 resume snapshot（當前任務、編輯中檔案、使用者決策） |
| Stop | agent turn 結束 | 記錄 turn-end 狀態 |

**Routing block 內容（注入至 system prompt）：**

```
工具選擇階層：
  1. GATHER: ctx_batch_execute(commands, queries)
  2. FOLLOW-UP: ctx_search(queries: ["q1", "q2"])
  3. PROCESSING: ctx_execute(language, code) | ctx_execute_file(path, language, code)

禁止行為：
  - 禁止 Bash 用於產出 >20 行的命令
  - 禁止 Read 用於分析（改用 ctx_execute_file）
  - 禁止 WebFetch（改用 ctx_fetch_and_index）
  - Bash 僅限 git/mkdir/rm/mv/navigation
```

### 3.2 Session Continuity — SQLite 事件追蹤 + FTS5/BM25 恢復

所有 session 事件（檔案編輯、git 操作、任務狀態、錯誤、使用者決策）寫入 SQLite `session_events` 表。當 conversation compaction 發生時：

1. PreCompact hook 從 SQLite 建立 resume snapshot
2. SessionStart hook（或等效 surrogate）在 compaction 後將 snapshot 注入 system prompt
3. 代理透過 BM25 搜尋檢索 compaction 中遺失的精確資訊（而非將全部歷史 dump 回 context）

若使用者不加 `--continue` 旗標，先前 session 資料立即刪除。

### 3.3 Think in Code — 強制程式碼生成範式

要求 LLM 將資料分析寫成程式碼在隔離子程序執行，而非將資料讀入 context 做計算。此為跨 16 平台的強制範式。

```
// Before: 47 次 Read() = 700 KB
// After:  1 次 ctx_execute() = 3.6 KB
ctx_execute("javascript", `
  const files = fs.readdirSync('src').filter(f => f.endsWith('.ts'));
  files.forEach(f => console.log(f + ': ' + fs.readFileSync('src/'+f,'utf8').split('\\n').length + ' lines'));
`);
```

### 3.4 技術架構總覽

| 組件 | 檔案 | 職責 |
|---|---|---|
| MCP Server | `src/server.ts` (~2500 行) | 11 工具定義、session 統計、intent search |
| 知識庫 | `src/store.ts` (~1075 行) | FTS5 知識庫、chunking 策略、三層 fallback 搜尋 |
| 執行引擎 | `src/executor.ts` (~437 行) | 12 語言隔離子程序執行、輸出截斷、sandbox |
| 安全層 | `src/security.ts` (~557 行) | deny/allow 政策、shell-escape 偵測、pattern matching |
| Runtime 偵測 | `src/runtime.ts` (~293 行) | 語言 runtime 偵測、fallback chain |
| CLI | `src/cli.ts` (~898 行) | CLI 設定、doctor 診斷、upgrade |
| PreToolUse Hook | `hooks/pretooluse.mjs` | 工具攔截、安全檢查、路由 |
| SessionStart Hook | `hooks/sessionstart.mjs` | 注入 routing rules |

**知識庫搜尋的三層 fallback：**

```
Layer 1: Porter stemming FTS5 MATCH (BM25, k1=2.0, b=1.0)
  ├── 匹配 → 回傳 matchLayer: "porter"
  └── 無匹配 → 降級

Layer 2: Trigram substring FTS5 MATCH
  ├── 匹配 → 回傳 matchLayer: "trigram"
  └── 無匹配 → 降級

Layer 3: Fuzzy Levenshtein correction
  ├── 對每個 query word 做 adaptive edit distance 校正（1-4字:1, 5-12字:2, 13+字:3）
  ├── 以校正後 query 重搜 Porter → Trigram
  ├── 匹配 → 回傳 matchLayer: "fuzzy"
  └── 無匹配 → 回傳空陣列
```

**支援的 12 種語言與 runtime：**

| 語言 | 主要 Runtime | Fallback 1 | Fallback 2 |
|---|---|---|---|
| JavaScript | bun | node | — |
| TypeScript | bun | tsx | ts-node |
| Python | python3 | python | — |
| Shell | bash | sh | powershell (Windows) |
| Ruby | ruby | — | — |
| Go | go run | — | — |
| Rust | rustc (compile + run) | — | — |
| PHP | php | — | — |
| Perl | perl | — | — |
| R | Rscript | r | — |
| Elixir | elixir | — | — |

**安全模型：**

- 三層 settings 階層（project-local > project-shared > global）
- Bash 命令 deny/allow pattern（支援 `Bash(command:argsGlob)` 與 `Bash(command argsGlob)` 格式）
- Chained command splitting（`&&`、`||`、`;`、`|` 分割後各自評估）
- 非 shell 語言的 shell-escape 偵測（Python `os.system`/`subprocess`、JS `exec`/`spawn`、Ruby `system`/backtick、Go `exec.Command`、PHP `shell_exec`/`exec`/`system`、Rust `Command::new`）
- 子程序 stream-level hard cap：100 MB 上限，超出立即 kill process tree

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

context-mode 的獨特點是同時覆蓋三個問題域（tool output sandbox、session continuity、code-generation 範式強制），以下替代方案各自僅覆蓋部分：

### DA 表

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|---|---|---|---|---|
| **LeanCTX** (mksglu/lean-ctx) | Rust 單一二進位 MCP server + shell hook；四維度治理（壓縮：10 種讀取模式 + 56 shell 模組 + Tree-sitter AST + entropy filter；記憶：CCP session 記憶 + ONNX embedding 知識庫 + property graph；路由：ModePredictor + IntentEngine + Context Gate；治理：RBAC + 預算 SLO + loop detection） | 本機安裝 Rust binary；需 Tree-sitter parser 與 ONNX runtime | 68 個 MCP 工具（工具數量本身佔用 context）；shell hook 需修改 `~/.zshenv`；ONNX embedding 模型佔用本機記憶體 | 原始輸入 ~100K tokens → ~5K tokens 有用信號；跨會話記憶持久化與適時召回 |
| **smart-mcp** (spak2005/smart-mcp) | Python MCP 代理 server；啟動時收集所有上游 MCP server 的 tool schema，以 sentence-transformer 做 embedding 建 FAISS 向量索引；AI 永遠只看到 2 個固定 tool：`search_tools(query)` + `call_discovered_tool(target, arguments)` | 需 Python 環境與 sentence-transformer 模型；上游 MCP server 需先啟動 | 僅處理 tool schema 層面的 context 縮減（減少 tool 定義佔用 token），不處理 tool output sandbox、session continuity、code-generation 範式 | tool list 從數十個縮減至 2 個固定 tool；宣稱 97% context 縮減 |
| **Repomix** (yamadashy/repomix) | TypeScript CLI；將整個 repository 打包成單一 AI-friendly 檔案（XML/Markdown/JSON）；`--compress` 選項以 Tree-sitter 提取關鍵程式碼結構（函數簽名、類別定義）去除實作細節；支援 MCP server 模式 | 需 Node.js；為一次性預處理，非對話中動態攔截 | 僅處理「codebase 太大塞不進 context window」問題；不處理 tool output sandbox、session continuity；壓縮後可能遺失實作細節 | 大型 repo 壓縮為單一檔案送入 LLM context |
| **code2prompt** (mufeedvh/code2prompt) | Rust CLI + Python SDK；將 codebase 轉成單一 LLM prompt 檔案；支援 Handlebars 模板、TUI 互動、Git diff/log 整合、token 計數；提供 MCP server 模式 | 需 Rust 或 Python 環境；為一次性預處理 | 同 Repomix，僅處理 codebase 預壓縮；不處理 tool output sandbox、session continuity | 大型 repo 轉換為結構化 prompt 檔案 |

### 切入點差異圖

```
                    Tool Output   Session      Code-Gen    Tool Schema   Codebase
                    Sandbox       Continuity   範式強制    縮減          預壓縮
context-mode           ●            ●            ●           ○             ○
LeanCTX                ●            ●            ○           ○             ○
smart-mcp              ○            ○            ○           ●             ○
Repomix                ○            ○            ○           ○             ●
code2prompt            ○            ○            ○           ○             ●

● 覆蓋  ○ 不覆蓋
```

### 各方案切入點差異說明

- **LeanCTX**：與 context-mode 最接近的競爭者，同樣提供 tool output 壓縮與 session 記憶。差異在於 LeanCTX 使用 Tree-sitter AST 解析 + ONNX embedding 做程式碼結構理解，context-mode 使用 FTS5/BM25 純文字搜尋；LeanCTX 有 68 個 MCP 工具（精細化操作），context-mode 有 11 個（精簡化操作）；LeanCTX 無「Think in Code」範式強制。
- **smart-mcp**：僅解決 MCP tool schema 過多導致 tool 定義佔用 context 的問題。以 FAISS 語義搜尋取代靜態 tool list，AI 只看到 2 個 meta-tool。不處理 tool output 的 sandbox 或 session continuity。
- **Repomix / code2prompt**：兩者皆為對話前的 codebase 預處理工具，將整個 repo 壓縮為單一檔案送入 LLM。解決的是「codebase 太大」問題而非「tool output 太大」問題。與 context-mode 互補而非競爭。
