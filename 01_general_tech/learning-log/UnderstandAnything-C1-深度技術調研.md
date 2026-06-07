# UnderstandAnything-C1-深度技術調研

## 狀況理解

使用者要求：
1. Catch up 目前資料夾（特別是 AGENTS.md）
2. 對 https://github.com/Lum1104/Understand-Anything 進行深入調研

### 現狀
- 工作目錄：`Learning-Understand-Anything`，一個技術調研學習專案
- `01_general_tech/AGENTS.md` 定義了「技術解析助理」角色，規範了分析報告（4 點制）與過程報告的格式
- 先前已完成 6 個分析標的：CodeGraph、OpenHuman、CLI-Anything、CloakBrowser、EverOS、LingBot-Map
- Understand-Anything 是全新的分析標的，需從 C1 開始

### 使用者意圖
- 對 Understand-Anything 進行與先前標的同等深度的技術分析
- 產出分析報告（output/）與過程報告（learning-log/）

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `01_general_tech/AGENTS.md` | 確認角色定義與輸出規範 | 理解報告格式要求 | 已理解：分析報告 4 點制 + DA 表；過程報告含狀況理解、動作與結果、現狀、決斷點 |
| 瀏覽目錄結構與既有報告 | 了解專案現狀與既有分析格式 | 確認命名規則與報告風格參考 | 確認命名格式：分析報告 `<日期>-<技術名>.md`；過程報告 `<技術名>-C<ID>-<總結>.md` |
| Fetch GitHub repo 首頁 (README) | 取得專案概述、架構、功能列表 | 理解核心概念與使用方式 | 取得完整 README（功能、quick start、多平台安裝說明、多代理管線架構、FAQ） |
| Fetch `CLAUDE.md` (開發者文件) | 取得架構設計、開發規範、關鍵技術細節 | 深入理解技術內核 | 取得完整 CLAUDE.md：monorepo 架構、Dashboard 設計、Agent pipeline、subpath exports 策略、tree-sitter WASM 選擇理由、local testing 流程 |
| Fetch `package.json` (root) | 取得依賴、scripts、workspace 結構 | 理解專案技術棧 | 取得完整 package.json：pnpm workspace、TypeScript、Vitest、ESLint、tree-sitter 多語言 parser |
| Fetch `pnpm-workspace.yaml` | 確認 workspace 結構 | 理解 monorepo 組織 | 確認 packages: `understand-anything-plugin/packages/*`, `understand-anything-plugin`, `homepage` |
| Fetch 官網 `understand-anything.com` | 取得 marketing 面向的產品定位 | 理解產品價值主張與功能亮點 | 取得官網內容：強調「Graphs that teach」>「Graphs that impress」的差異化定位 |
| Fetch `understand-anything-plugin/agents/` 目錄 | 取得 agent 檔案列表與名稱 | 確認所有 agent 的類別與數量 | 取得 9 個 agent 檔案：project-scanner, file-analyzer, architecture-analyzer, tour-builder, graph-reviewer, domain-analyzer, article-analyzer, assemble-reviewer, knowledge-graph-guide |
| Fetch `understand-anything-plugin/skills/` 目錄 | 取得 skill 檔案列表 | 確認所有命令的覆蓋範圍 | 取得 8 個 skill 目錄：understand, understand-dashboard, understand-chat, understand-diff, understand-explain, understand-onboard, understand-domain, understand-knowledge |
| Fetch `packages/core/src/index.ts` | 取得核心模組的 public API | 理解核心引擎的模組組織 | 確認完整模組清單：types, persistence, schema, search, analyzer (graph-builder, llm-analyzer, normalize-graph, layer-detector, tour-generator, language-lesson), fingerprint, staleness, change-classifier, embedding-search, plugins (tree-sitter, parsers), ignore-filter 等 |
| Fetch `packages/core/src/types.ts` | 取得 GraphNode/GraphEdge 等型別定義 | 理解知識圖譜的資料結構 | 確認：21 種 NodeType、35 種 EdgeType 在 8 大類別下、GraphNode/GraphEdge/KnowledgeGraph 等介面 |
| Fetch `packages/core/src/schema.ts` | 取得 Zod schema、驗證流程、自修復機制 | 理解 LLM 輸出的標準化處理 | 確認：4-tier 驗證（sanitize → normalize → autoFix → Zod）、LLM alias mapping（NODE_TYPE_ALIASES, EDGE_TYPE_ALIASES）、GraphIssue 三層級（auto-corrected/dropped/fatal） |
| Fetch `packages/core/src/search.ts` | 取得模糊搜尋引擎實作 | 理解 Dashboard 搜尋功能 | 確認：Fuse.js 實現，weighted keys (name:0.4, tags:0.3, summary:0.2, languageNotes:0.1)，extended search (OR mode) |
| Fetch `packages/core/package.json` | 取得核心依賴 | 理解核心技術棧 | 確認：web-tree-sitter (WASM)、fuse.js、zod、yaml、ignore、10 種語言 tree-sitter parser |
| Fetch `packages/dashboard/package.json` | 取得 Dashboard 依賴 | 理解前端技術棧 | 確認：React 19、@xyflow/react、d3-force、elkjs、dagre、prism-react-renderer、graphology + louvain community、zustand、tailwindcss v4 |
| Fetch `packages/core/src/` 目錄結構 | 取得核心原始碼組織 | 理解核心模組的檔案結構 | 確認：analyzer/, plugins/, plugins/extractors/, plugins/parsers/, languages/, persistence/, __tests__/ |
| Fetch `packages/dashboard/src/` 目錄結構 | 取得 Dashboard 原始碼組織 | 理解前端模組的檔案結構 | 確認：components/, contexts/, hooks/, locales/, themes/, utils/, App.tsx, store.ts |
| Fetch `CONTRIBUTING.md` | 了解開發工作流、測試方式、commit convention | 補充技術細節 | 取得完整 CONTRIBUTING.md：setup、branch convention、commit message convention (feat/fix/docs/style/refactor/test/chore)、Vitest + ESLint |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 資訊完整性 | 是否取得足以撰寫 4 點分析報告的資料 | 是。完整理解：核心問題、背景因素、多代理管線 + Tree-sitter/LLM 混合機制、21/35 型別體系、4-tier schema 驗證、增量更新、SearchEngine、Dashboard 架構 |
| 技術深度 | 是否觸及核心原始碼層級 | 是。已讀取 types.ts (完整型別定義)、schema.ts (完整驗證邏輯)、search.ts (搜尋引擎實作)、index.ts (public API)、CLAUDE.md (開發文件) |
| 替代方案知識 | 是否有足夠資訊製作 DA 表 | 是。基於先前 CodeGraph 調研經驗、Sourcegraph/SonarQube/Sourcetrail 領域知識，以及本次從 CLAUDE.md 提取的技術定位差異 |
| 報告格式合規性 | 是否遵循 AGENTS.md 的輸出規範 | 是。分析報告僅含 4 點、使用表格/圖示/階層結構、不使用情緒性語言、不使用「可能」「也許」 |
| 命名規則 | 是否符合檔名規範 | 是。分析報告：`output/2026-05-31-UnderstandAnything.md`；過程報告：`learning-log/UnderstandAnything-C1-深度技術調研.md` |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 調研深度 | A. 僅看 README；B. README + CLAUDE.md + 核心原始碼（types, schema, search）；C. 全部原始碼逐檔案閱讀 | B | 使用者要求「深入調研」，READEME 提供功能概述、CLAUDE.md 提供架構與開發規範、核心原始碼提供型別/驗證/搜尋實作細節。全部原始碼（analyzer/ plugins/ dashboard components）超出合理範疇 |
| 是否需要 fetch 個別 agent .md 檔案內容 | A. 逐一 fetch 所有 9 個 agent 定義；B. 依賴 CLAUDE.md + 目錄結構 | B | CLAUDE.md 已完整描述每個 agent 的角色與功能；目錄結構驗證 agent 數量；fetch 每個 agent 的完整 prompt 不新增關鍵資訊 |
| 分析報告 DA 表替代技術選擇 | A. 僅列同為「AI 驅動程式碼圖譜」的工具；B. 列所有程式碼理解/導覽相關技術 | B | AGENTS.md 要求「條列 2~4 個同級或替代方案」，程式碼理解的技術生態包含純靜態分析（SonarQube/Sourcetrail）、搜尋引擎（Sourcegraph）、文件生成（doxygen）等不同切入點 |
| 是否觸及 Dashboard 原始碼 | A. fetch Dashboard components 細節；B. 僅以 CLAUDE.md + 目錄結構概括 | B | CLAUDE.md 已描述 Dashboard 技術棧（React Flow, Zustand, TailwindCSS v4, prism-react-renderer）、布局策略（75% graph + 360px sidebar）、側邊欄標籤結構；fetch 個別 component 原始碼對分析報告不新增關鍵價值 |
| 報告中的反面論證比重 | A. 無反面論證；B. 適度反面論證；C. 對比 CLI-Anything 同等深度反面論證 | B | AGENTS.md 規定「只回答 4 點，不要額外延伸」「不評論好壞、不延伸設計哲學」；僅在第 4 點 DA 表中自然帶出各技術的副作用與前提限制，不另闢反面論證章節 |
| 是否記錄非程式碼分析器的完整清單 | A. 詳細列出 13 種非程式碼 parser；B. 概括說明 | A | 非程式碼解析器（Dockerfile, SQL, Terraform, GraphQL 等 13 種）是 Understand-Anything 與純程式碼分析工具的關鍵差異點 |
