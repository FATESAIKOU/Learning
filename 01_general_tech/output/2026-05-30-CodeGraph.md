# CodeGraph 技術分析報告

## 1. 這個技術解決什麼問題？

AI coding agent（Claude Code、Cursor、Codex CLI、opencode、Hermes Agent、Gemini CLI、Antigravity IDE、Kiro）在探索與回答程式碼相關結構性問題時，需透過 `grep`、`glob`、`Read` 等工具逐一掃描檔案來重建程式碼間的關係（符號定義、呼叫鏈、繼承關係等），此過程消耗大量 token 與工具呼叫次數，導致成本高、延遲長。

CodeGraph 解決的具體問題是：**如何讓 AI coding agent 在回答程式碼結構性問題時，透過預先建立的本地知識圖譜直接查詢答案，無需重複執行檔案掃描、grep 等探索性工具呼叫。**

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

- AI coding agent 在探索程式碼庫時，預算大部分消耗在「發現階段」（discovery）：先 `find`/`ls` 找檔案，再 `grep` 搜尋關鍵字，最後 `Read` 檔案的循環。根據 benchmark，無 CodeGraph 時一個 Explore agent 會產生 9~21 次工具呼叫。
- Claude Code 本身會產生 Explore 子 agent，這些子 agent 使用 grep、glob、Read 掃描檔案，每個工具呼叫都消耗 token。
- 傳統的靜態分析工具（如 IDE built-in 的 jump-to-definition）不暴露給 AI agent 使用，缺乏 MCP 整合。
- `.cursorrules` / `CLAUDE.md` 手寫方式上限約 200 行且會過時。

### 通用技術背景

- **Token 經濟性問題**：每次 grep、Read 呼叫的輸入輸出都會計入 LLM 的 token 消耗，對大型程式碼庫（如 VS Code ~10k files）進行結構性查詢的成本可達 $0.83+/query。
- **LLM 無 persistent memory**：LLM 本質上是 stateless function，每次對話結束後不保留程式碼庫結構認知，下一次對話需重新探索。
- **現有 LSP/LSIF/SCIP 基礎設施不面向 AI agent**：LSP 設計給 IDE 使用（需要 running language server），LSIF/SCIP 為人類程式碼導航設計，未被包裝成 AI agent 可直接呼叫的 MCP 工具。
- **靜態解析的技術挑戰**：跨語言 bridge（Swift↔ObjC、React Native JS↔Native）、動態 dispatch（callback、EventEmitter、React re-render）等路徑，grep 無法跟蹤。

## 3. 這個技術是如何解決該問題的？

CodeGraph 透過以下 **四階段 pipeline** 將原始碼轉化為本地 SQLite 知識圖譜，並透過 MCP server 暴露給 AI agent：

### 3.1 系統架構

```
┌───────────────────────────────────────────────────────────┐
│ AI agent（Claude Code / Cursor / Codex / opencode / …）     │
│   提出結構性問題（如 "extension host 如何與 main process     │
│   通訊？"）→ 直接呼叫 CodeGraph MCP 工具                    │
└───────────────────────────┬───────────────────────────────┘
                            │ MCP (JSON-RPC over stdio)
                            ▼
┌───────────────────────────────────────────────────────────┐
│ CodeGraph MCP Server                                      │
│   10 個 MCP 工具：context · trace · explore · callers ·    │
│   callees · impact · node · search · files · status        │
└───────────────────────────┬───────────────────────────────┘
                            │ SQL (FTS5 + 關聯查詢)
                            ▼
┌───────────────────────────────────────────────────────────┐
│ SQLite DB（.codegraph/codegraph.db）                       │
│   節點（symbols）+ 邊（edges）+ 檔案（files）+ FTS5 全文索引 │
└───────────────────────────┬───────────────────────────────┘
                            │ 建構
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Indexing Pipeline（離線執行）                                │
│   1. Extraction → 2. Storage → 3. Resolution → 4. Sync    │
└───────────────────────────────────────────────────────────┘
```

### 3.2 Pipeline 四階段

**Stage 1 — Extraction（提取）**

- 使用 **tree-sitter**（`web-tree-sitter` + `tree-sitter-wasms`）解析原始碼成 AST
- 語言特定查詢（tree-sitter query）提取「節點」與「邊」
- 重解析在 worker thread 執行，不阻塞主執行緒

**節點種類 (Node kinds)**：

| 種類 | 說明 |
|------|------|
| `file`, `module` | 檔案與模組 |
| `class`, `struct`, `interface`, `trait`, `protocol` | 各種型別定義 |
| `function`, `method` | 函式與方法 |
| `property`, `field`, `variable`, `constant` | 屬性與變數 |
| `enum`, `enum_member`, `type_alias` | 列舉與別名 |
| `import`, `export`, `route`, `component` | 匯入/匯出/路由/元件 |

**邊種類 (Edge kinds)**：

| 種類 | 說明 |
|------|------|
| `contains` | 包含關係（如 class 包含 method） |
| `calls` | 呼叫關係 |
| `imports`, `exports` | 匯入/匯出 |
| `extends`, `implements` | 繼承/實作 |
| `references`, `type_of`, `returns` | 引用/型別/回傳 |
| `instantiates`, `overrides`, `decorates` | 實例化/覆寫/裝飾 |

**Stage 2 — Storage（儲存）**

- 所有節點、邊、檔案寫入本地 SQLite 資料庫（`.codegraph/codegraph.db`）
- 使用 FTS5 全文索引加速符號名稱搜尋
- 預設使用 Node 內建 `node:sqlite` + WAL 模式，concurrent reads 永不被 writer 阻塞

**Stage 3 — Resolution（解析）**

- 提取後執行跨檔案參考解析：
  - **Import 解析**：import statement → 指向的原始檔（含 tsconfig path alias、cargo workspace member）
  - **Call 解析**：函式呼叫 → 函式定義（透過 import 解析 + 名稱匹配）
  - **繼承解析**：`extends` / `implements` → 父型別
- **動態 dispatch 合成**：靜態解析無法跟蹤的路徑，由 synthesizer 橋接：
  - Callback / observer 註冊
  - `EventEmitter` 頻道
  - React `setState` → `render`
  - JSX child → 子元件
  - Django ORM descriptors
- 所有合成的邊標記 `provenance: 'heuristic'` + `metadata.synthesizedBy`，agent 可辨識其來源

**Stage 4 — Auto-sync（自動同步）**

```
agent 編輯 src/Widget.ts
  → watcher 觸發 (<100ms)
  → debounce（預設 2s，可透過 CODEGRAPH_WATCH_DEBOUNCE_MS 調整）
  → sync 執行；Widget.ts 進入索引
  → 下一個 agent query 可見新內容
```

三層保持索引與程式碼同步的機制：
1. **File watcher** — 使用原生 OS 事件（FSEvents / inotify / ReadDirectoryChangesW）+ debounce（預設 2000ms，範圍 [100ms, 60s]）
2. **Per-file staleness banner** — 若回應引用 debounce 期間尚未完成 re-index 的檔案，在回應前加上 `⚠️` banner 告知 agent 該檔案需直接 Read
3. **Connect-time catch-up** — MCP server (re)connect 時先執行 `(size, mtime) + content-hash` reconciliation，確保離線期間的修改被吸收

### 3.3 MCP 工具對應

| 工具 | 用途 | 對應的 agent 問題 |
|------|------|------------------|
| `codegraph_search` | 按名稱搜尋符號 | 「名為 X 的符號在哪？」 |
| `codegraph_context` | 組合 search + node + callers + callees，一次呼叫建立上下文 | 「這個功能/區塊的全貌是什麼？」 |
| `codegraph_trace` | 一次呼叫回傳兩符號間的完整呼叫路徑（含動態 dispatch hops） | 「X 如何到達 Y？」 |
| `codegraph_callers` | 找出誰呼叫此函式 | 「誰呼叫了這個？」 |
| `codegraph_callees` | 找出此函式呼叫了誰 | 「這個呼叫了什麼？」 |
| `codegraph_impact` | 分析修改一個符號會影響什麼 | 「改這個會破壞什麼？」 |
| `codegraph_node` | 單一符號詳情（可含原始碼） | 「這個符號的簽章/文件？」 |
| `codegraph_explore` | 多個相關符號的原始碼 + 關係圖，一次呼叫 | 「survey 這個區域」 |
| `codegraph_files` | 取得已索引檔案結構 | 「目錄 X 裡有什麼？」 |
| `codegraph_status` | 檢查索引健康狀態 | 「索引就緒了嗎？」 |

### 3.4 框架感知路由 (Framework-aware Routes)

CodeGraph 識別 web framework routing 檔案，產生 `route` 節點並以 `references` 邊連接到 handler。支援 14 種框架：

| 框架 | 識別語法 |
|------|----------|
| Django | `path()`, `re_path()`, `url()`, `include()` |
| Flask | `@app.route()`, blueprint routes |
| FastAPI | `@app.get(...)`, `@router.post(...)` |
| Express | `app.get(...)`, `router.post(...)` |
| NestJS | `@Controller` + `@Get/@Post`, `@Resolver` |
| Laravel | `Route::get()`, `Route::resource()` |
| Drupal | `*.routing.yml` |
| Rails | `get '/x', to: 'users#index'` |
| Spring | `@GetMapping`, `@PostMapping` |
| Gin/chi/gorilla/mux | `r.GET(...)`, `router.HandleFunc(...)` |
| Axum/actix/Rocket | `.route("/x", get(handler))` |
| ASP.NET | `[HttpGet("/x")]` |
| Vapor | `app.get("x", use: handler)` |
| React Router / SvelteKit | Route component nodes |

### 3.5 跨語言橋接 (Mixed iOS / React Native / Expo)

| 邊界 | 橋接方式 |
|------|----------|
| Swift → ObjC | `@objc` auto-bridging 規則 + Cocoa preposition prefix（With/For/By/In/On/At…） |
| ObjC → Swift | Reverse-bridge name candidates，驗證 `@objc` 暴露 |
| RN legacy bridge | `RCT_EXPORT_METHOD` / `@ReactMethod` → JS-name → native-method map |
| RN TurboModules | `Native<X>.ts` spec interface 作為 ground truth |
| RN native → JS events | `sendEvent(withName:)` / `.emit("e", ...)` → event channel keyed by literal name |
| Expo Modules | Expo DSL literals parsing：`Module { Name("X"); AsyncFunction("fn") }` |
| Fabric view components | Codegen spec → `component` node + convention-based suffix lookup |
| Paper view managers | `RCT_EXPORT_VIEW_PROPERTY` / `@ReactProp` → `component` + `property` nodes |

### 3.6 Agent 使用指引（由 MCP server 自動注入）

CodeGraph 的 MCP server 在 `initialize` 回應中自動傳送使用指引文字（定義於 `src/mcp/server-instructions.ts`），告知 agent：
- 以意圖選擇工具（context → explore → trace → callers/callees → impact）
- **不**將查詢委派給 Explore 子 agent（那會回到 grep/Read 循環）
- 信任 CodeGraph 結果，不用 grep 再驗證
- 編輯後檢查 staleness banner

### 3.7 技術棧

| 面向 | 細節 |
|------|------|
| 語言 | TypeScript（100%） |
| 執行環境 | Node.js 20+，自捆綁 runtime（`--self-contained` build） |
| 解析引擎 | tree-sitter（`web-tree-sitter` + `tree-sitter-wasms`） |
| 資料庫 | SQLite（`node:sqlite`，WAL 模式），fallback 為 WASM backend |
| 檔案監控 | `chokidar`（封裝 FSEvents/inotify/ReadDirectoryChangesW） |
| CLI 框架 | `commander` |
| MCP 協定 | JSON-RPC over stdio |
| 測試 | `vitest` |
| 授權 | MIT |
| 版本 | v0.9.7 |
| 支援語言 | 20+ 語言（含 TypeScript, JS, Python, Go, Rust, Java, C#, PHP, Ruby, C, C++, ObjC, Swift, Kotlin, Scala, Dart, Svelte, Vue, Liquid, Pascal/Delphi, Lua, Luau） |
| 支援平台 | Windows (x64/arm64), macOS (x64/arm64), Linux (x64/arm64) |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（決策輔助表）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **CodeGraph** | 本地 tree-sitter AST 解析 → SQLite 知識圖譜（nodes/edges/FTS5）→ MCP server 暴露 10 個查詢工具；20+ 語言、14 框架 routing、跨語言橋接、auto-sync（watcher+debounce+staleness banner） | Node.js 20+（自捆綁 runtime）；`codegraph init -i`；agent 需支援 MCP | SQLite DB 佔用磁碟；索引建構消耗 CPU；watcher 持續執行（~90k inotify watches）；FTS5 不處理自然語言語意查詢；heuristic 橋接動態 dispatch 可能漏項 | 7 repo benchmark 平均 62% fewer tool calls、57% fewer tokens、25% cheaper、23% faster；大型 repo 零檔案讀取 |
| **GitNexus** | tree-sitter AST → 自研 LadybugDB → 12-phase DAG（含 Leiden community detection、process extraction、cross-repo contract bridge）→ MCP 16 tools + skills + hooks + resources；BM25+vector hybrid search (RRF) + Cypher | Node.js + C++ toolchain（或 `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`）；`gitnexus analyze`；商用需 enterprise license（PolyForm Noncommercial） | 自研 DB 無外部生態系；無 auto-sync（需 hooks 或 CLI `--force`）；安裝重（原生模組編譯）；16 語言各有 parsing coverage gaps（JS/TS 11 項、Rust 9 項等） | 深層架構理解：communities 分群、processes 執行流、group 跨 repo contract；整合最深（tools+skills+hooks+prompts+resources） |
| **Aider repomap** | tree-sitter 掃描 repo → 精簡 call graph + 符號摘要 → 每次對話啟動時注入 LLM system prompt | Python 3.x + LLM API key | 每次 session 重建（無持久索引）；map 本身佔用 token；無獨立 MCP server；只有符號位置不含原始碼 | 讓 LLM 參照全專案結構，提升大型專案的程式碼編輯準確度 |
| **LSIF / SCIP (Sourcegraph)** | 標準化協定（Protobuf）→ per-language indexer 匯出索引檔 → Sourcegraph server 載入提供定義跳轉、引用查找、hover | per-language indexer；Sourcegraph server 或支援的 IDE；CI/CD step 執行 indexing | 索引檔可達 GB 級；非面向 AI agent（無原生 MCP）；無 auto-sync（手動/CI 重 index） | 人類開發者程式碼導航標準方案；SCIP 支援 cross-repository 解析 |

### DA 表補充：Overengineering 2×2 判定

以下基於反面論證（蒐集雙方證據後收斂）對 CodeGraph 與 GitNexus 在不同維度的 overengineering 判定：

| 判定面向 | CodeGraph | GitNexus |
|----------|-----------|----------|
| **對其自身問題** | **否**。工程投入與問題規模成比例：使用成熟組件（tree-sitter/SQLite/MCP），維護表面積可控。唯一風險是 LLM 自主 grep 能力持續提升後邊際效益遞減，目前尚未發生 | **否**（功能面）/**效率不佳**（工程面）。功能（communities/processes/contract bridge）對「agents never miss code」目標合理。但自幹 LadybugDB（SQLite WAL 已覆蓋其查詢模式）、自幹 scope-resolution（本質上重複 LSP）、內建 embedding layer 而非 delegate 為效率不佳的設計選擇 |
| **導入 SaaS 團隊** | **否**。導入成本趨近零（`npx` 一行指令 + MIT license），無採購流程，無基礎設施變更，風險可控。即使效益有限也不構成 overhead | **是（多數場景）**。通用需求（符號搜尋/call chain/auto-sync/安裝簡便性/授權自由度）均不如 CodeGraph；特化需求（communities/processes/cross-repo contract/embedding search）僅少數團隊需要。PolyForm NC 授權 + 安裝門檻 + 無 auto-sync 使導入成本超過多數 SaaS 團隊的增量收益 |

**判定依據（反面論證來源）**：CodeGraph issues（#579 watcher exhaustion、#584 Go interface 不偵測、#578 Python call 遺漏）、GitNexus issues（#1927-#1936 各語言 parsing gaps 共 67 項）、SQLite 官方使用指南（WAL 模式讀寫語意與適用場景）、兩者架構對比（4-phase vs 12-phase DAG）。

### 各方案切入點差異

- **CodeGraph**：以 **agent 問答加速** 為切入點，將靜態分析結果包裝為 agent-tool interface，強調「取代 grep+Read 循環」。100% 本地、MIT license、零配置。
- **GitNexus**：以 **agent 深度架構理解** 為切入點，從靜態分析往上堆疊架構層級衍生分析（communities/processes/contract），但為此自幹了 DB、scope resolver、embedding layer，工程面存在過度設計。
- **Aider repomap**：以 **一次性注入全專案結構至 LLM context** 為切入點，最輕量的方案，但無持久化索引、非隨需查詢。
- **LSIF / SCIP (Sourcegraph)**：以 **標準化跨語言精確導航** 為切入點，生態最成熟，但設計目標是人類開發者而非 AI agent，缺乏 MCP 原生支援。


