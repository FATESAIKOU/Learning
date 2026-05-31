# CodeGraph-C2-深度技術調研

## 狀況理解
使用者要求對 CodeGraph（https://github.com/colbymchenry/codegraph）進行深度技術調研。CodeGraph 是一個面向 AI coding agent 的本地 code intelligence 工具，透過 tree-sitter 解析原始碼建構 SQLite 知識圖譜，並以 MCP server 形式暴露給 Claude Code、Cursor、Codex、opencode 等 agent，旨在減少 agent 探索程式碼庫時的 token 消耗與工具呼叫次數。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 GitHub repo README | 取得專案基本定位、功能列表、benchmark、安裝方式、支援語言的完整資訊 | 理解 CodeGraph 的核心價值主張與技術定位 | 取得完整 README，含 benchmark（7 repo、平均 25% cheaper/62% fewer tool calls）、20+ 語言支援、14 framework routing、mixed iOS/RN bridging 詳細說明 |
| 讀取 package.json | 了解技術堆疊、依賴、建構工具 | 確認框架選型與開發工具鏈 | TypeScript + Node.js 20+、tree-sitter（web-tree-sitter + tree-sitter-wasms）、SQLite（node:sqlite + better-sqlite3 fallback）、chokidar、vitest、MIT license、v0.9.7 |
| 讀取 src/ 目錄結構 | 了解原始碼模組分層 | 確認核心子系統的模組邊界 | 12 個模組：bin/, context/, db/, extraction/, graph/, installer/, mcp/, resolution/, search/, sync/, ui/ + 頂層 index.ts, types.ts, utils.ts, directory.ts, errors.ts |
| 讀取 docs/ 目錄結構 | 了解內部設計文檔覆蓋範圍 | 確認是否有深度技術文檔可供參考 | docs 含 benchmarks/, design/, plans/ 目錄 + SEARCH_QUALITY_LOOP.md |
| 讀取官方文檔首頁與 Introduction | 了解官方對技術的定位與說明 | 取得核心概念架構 | 取得 4 階段 pipeline 說明、node/edge 種類表、resolution機制、auto-sync 三層確保 |
| 讀取 MCP server-instructions.ts | 理解 agent 如何被引導使用 CodeGraph | 取得 agent 使用指引的完整文字 | 取得 71 行 TypeScript 的 SERVER_INSTRUCTIONS 常數，含工具選擇by intent、common chains、anti-patterns、limitations |
| 讀取官方 How It Works 文檔 | 深入了解四階段 pipeline | 取得 pipeline 各階段的技術細節 | 取得 Extraction（tree-sitter + worker thread）、Storage（node:sqlite WAL + better-sqlite3 fallback）、Resolution（import/call/inheritance + 動態 dispatch synthesizer）、Auto-sync（三層機制） |
| 讀取官方 Knowledge Graph 文檔 | 了解 node/edge 的完整 schema | 取得節點種類與邊種類的完整清單 | 取得 20 種 node kind + 12 種 edge kind + provenance 標記機制 |
| 讀取官方 Resolution & Frameworks 文檔 | 了解解析機制與 framework 感知 | 取得 reference resolution、framework awareness、dynamic-dispatch coverage 細節 | 取得 import/call/inheritance 解析 + 5 種動態 dispatch bridge（callback/EventEmitter/React re-render/JSX child/Django ORM） |
| 讀取官方 MCP Server 文檔 | 了解 10 個 MCP 工具的完整定義 | 取得每個工具的用途說明 | 取得 10 個工具清單：search/context/trace/callers/callees/impact/node/explore/files/status |
| 讀取 LSIF.dev 首頁 | 收集 LSIF 替代方案資訊 | 了解 LSIF 標準的定義、生態系與現狀 | 取得 LSIF 定義（Language Server Index Format）、VS Code 2019 blog 起源、各語言 indexer 狀態表 |
| 讀取 SCIP GitHub repo README | 收集 SCIP 替代方案資訊 | 了解 SCIP 的設計、工具生態系、與 LSIF 的關係 | 取得 SCIP 定義（Protobuf schema）、Go/Rust/TS/Haskell bindings、9 種語言 indexer、scip CLI |
| 讀取 Sourcegraph GitHub org page | 確認 Sourcegraph 與其開源專案的關係 | 理解 Sourcegraph（Cody + code search）在 code intelligence 生態系中的角色 | 取得 Sourcegraph 為 code AI 平台，主 repo 為 sourcegraph-public-snapshot，Cody 為 AI code assistant（TypeScript 3.8k stars） |
| 讀取 Aider GitHub repo README | 收集 Aider repomap 作為替代方案資訊 | 了解 Aider repomap 的設計與 CodeGraph 的差異 | 取得 Aider 為 terminal AI pair programming 工具，repomap 功能使用 tree-sitter 產生全專案 structure map 並注入 LLM context |
| 讀取 Universal Ctags 首頁 | 收集 ctags 作為替代方案資訊 | 了解 ctags 的能力邊界 | 取得 ctags 為長期維護的 tags 產生工具，僅產生 name→location 對應，無 call graph |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 技術核心機制 | 檢查 README、官方文檔、package.json 的一致性 | 四階段 pipeline（Extraction → Storage → Resolution → Auto-sync）在所有來源中一致描述；技術棧（TypeScript + tree-sitter + SQLite + MCP）在所有來源中一致 |
| Benchmark 可信度 | 對照 README 中的 benchmark methodology 與實際數據 | 7 repo × 4 runs/arm、median 報告、Opus 4.8 re-validation、詳細的 per-repo breakdown 含查詢問題文字，methodology 透明度高 |
| 原始碼模組分層 | 從 src/ 目錄讀取模組命名 | 模組劃分清晰：extraction（tree-sitter 解析）/ db（SQLite schema）/ graph（圖查詢）/ resolution（跨檔案解析）/ mcp（MCP server）/ sync（檔案監控與增量同步）/ installer（agent 配置）/ context（上下文構建）/ search（FTS5 搜尋）/ ui（CLI 介面） |
| 替代方案生態 | 搜尋 LSIF.dev、SCIP、Sourcegraph、Aider、ctags | 資訊充足：LSIF/SCIP（標準化 index format，需 per-language indexer + server）、Aider repomap（session-scoped 注入）、ctags（僅 name→location）、LSP via MCP wrapper（需自行開發） |
| 授權與開源狀態 | 檢查 LICENSE 檔案與 README 宣告 | MIT license，GitHub 公開 repo，33.6k stars，2k forks，v0.9.7（2026-05-28 release） |
| 跨平台支援 | 檢查 README 的平台說明與 install script | Windows (x64/arm64, PowerShell), macOS (x64/arm64, shell), Linux (x64/arm64, shell) 均支援 |
| Agent 整合覆蓋 | 檢查 README 的 supported agents 與 installer 邏輯 | 8 個 agent 支援：Claude Code, Cursor, Codex CLI, opencode, Hermes Agent, Gemini CLI, Antigravity IDE, Kiro；installer 自動偵測已安裝 agent 並寫入 MCP config |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 分析報告中核心技術的選取範圍 | 1. 僅寫 tree-sitter 解析機制；2. 僅寫 MCP server；3. 寫 CodeGraph 整體（pipeline + MCP + framework awareness + bridging） | 3. 寫 CodeGraph 整體 | CodeGraph 的價值在於將 tree-sitter AST 解析、SQLite 圖儲存、跨檔案解析、動態 dispatch 合成、framework routing、跨語言 bridge、MCP 暴露等多個子系統串聯，單看任一子系統無法解釋它解決的完整問題 |
| DA 表中替代方案的選取 | 各種 code intelligence / code navigation / AI agent context 工具 | Aider repomap、LSIF/SCIP + Sourcegraph、Universal Ctags + grep、LSP via MCP wrapper | Aider repomap（同面向 AI agent，但策略不同：session-scoped 注入 vs pre-built index）、LSIF/SCIP（標準化 index protocol，歷史最久）、ctags（最基礎方案）、LSP via MCP（IDE 能力延伸，最精確但缺乏組合查詢）；選取覆蓋「面向 AI agent」「標準化 index」「最輕量」「最精確」四個維度 |
| 是否深入探索原始碼 | 1. 深入 src/ 各模組的實作細節；2. 維持文檔層級分析 | 2. 維持文檔層級分析 | README、官方文檔、src/ 目錄結構、server-instructions.ts 的內容已提供充分資訊回答 AGENT.md 指定的四個問題；原始碼層級分析在此階段非必要 |
| CodeGraph 的問題定義 | 1. 定位為「code intelligence」工具；2. 定位為「AI agent performance optimization」工具；3. 定位為「取代 grep 的替代查詢層」 | 1+2 組合：「面向 AI agent 的一站式 pre-built code intelligence」 | README 開頭明確定義為「Supercharge Claude Code, Cursor, Codex, OpenCode, Hermes Agent, Gemini, Antigravity, and Kiro with Semantic Code Intelligence」；benchmark 直接以 agent 成本/速度/token 做指標；文檔多次強調「取代 grep + Read 循環」 |
