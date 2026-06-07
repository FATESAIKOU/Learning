# Understand-Anything 分析報告

> 分析日期：2026-05-31
> 專案倉庫：https://github.com/Lum1104/Understand-Anything (Lum1104, 46.1k stars, MIT)
> 官網：https://understand-anything.com

---

## 1. 這個技術解決什麼問題？

**開發者加入陌生的大型程式碼庫時，無法快速掌握整體架構、模組依賴關係與業務邏輯。**

Understand-Anything 透過多代理（multi-agent）管線 + Tree-sitter/LM 混合分析，將任意程式碼庫轉換為互動式知識圖譜（knowledge graph），並提供可視化 Dashboard 供探索、搜尋與提問。

### 被解決的具體問題：

| 問題面向 | 具體描述 |
|---------|---------|
| **程式碼規模巨大，線性閱讀不可能** | 200,000 行程式碼，無法逐行閱讀理解 |
| **靜態分析看不到意圖** | import/export 依賴圖只看結構，不理解「這個檔案在做什麼」 |
| **文件過時或不存在** | 專案文件常缺失或不更新，無法反映實際程式碼狀態 |
| **新人 onboarding 成本高** | 新團隊成員需要數週才能理解系統架構 |
| **變更影響範圍不明** | 修改一段程式碼時，無法快速判斷影響哪些模組 |
| **業務邏輯與程式碼脫節** | 程式碼反映實作，但業務流程（auth flow、payment pipeline）隱含在程式碼中，難以提取 |

### 問題描述的明確程度

專案 README 對問題的描述具體：以「200,000 行程式碼，從哪裡開始」作為具體場景。目標使用者為「剛加入新團隊的開發者」。問題邊界清晰：聚焦於程式碼庫理解，不涉及 runtime 監控、效能分析或其他 DevOps 面向。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景因素

| 因素 | 說明 |
|------|------|
| **程式碼規模膨脹** | 現代軟體專案動輒數十萬行，單一人員無法記憶全域架構 |
| **傳統程式碼導覽工具的侷限** | grep、IDE jump-to-definition 提供線性/點對點導覽，無法展示全域結構 |
| **文件維護與程式碼脫鉤** | 手寫文件容易過時，與實際程式碼不一致 |

### 通用技術背景（補充）

| 背景因素 | 說明 |
|---------|------|
| **GitHub Copilot / Claude Code 生態成熟** | AI coding assistant 成為主流開發工具，為「plugin」形式交付程式碼分析提供整合基礎 |
| **Tree-sitter 的成熟** | Incremental parsing library 為跨語言結構化分析提供高效基礎設施 |
| **LLM 語義理解能力提升** | LLM 能從程式碼中提取摘要、標籤、架構層次等語義資訊，這是純靜態分析做不到的 |
| **知識圖譜在程式碼領域的應用歷史** | Sourcetrail、Sourcegraph 等先行者驗證了「可視化程式碼關係圖」的需求存在 |
| **AI coding assistant plugin 生態** | Claude Code Plugins、Codex Skills、Copilot Extensions 等機制普及，使第三方分析工具能以 plugin 形式整合入開發工作流 |
| **Monorepo 與微服務架構的普及** | 分散的程式碼組織方式增加跨模組理解難度 |

### 需求驗證

專案 GitHub 指標（46.1k stars, 3.7k forks, 547 commits, 59 open issues, 69 open PRs, v2.7.3）表明需求真實存在且被社群驗證。

---

## 3. 這個技術是如何解決該問題的？

### 核心機制總覽

```
使用者命令
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  多代理管線 (Multi-Agent Pipeline)                            │
│                                                             │
│  ┌──────────────────┐                                       │
│  │ project-scanner  │  掃描專案結構                           │
│  │                  │  發現檔案、語言、框架                     │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ file-analyzer    │  解析每檔案                             │
│  │  (平行執行,       │  提取函數、類別、import/export           │
│  │   5 concurrent)   │  生成節點(node) 與邊(edge)              │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ architecture-    │  識別架構層次                           │
│  │ analyzer         │  API/Service/Data/UI/Utility           │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ tour-builder     │  生成引導式學習導覽                       │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ graph-reviewer   │  驗證圖譜完整性與參考完整性               │
│  └──────────────────┘                                       │
│                                                             │
│  可選代理：                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ domain-analyzer  │  │ article-analyzer │                 │
│  │ (提取業務領域)    │  │ (分析 wiki)      │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  知識圖譜 JSON (.understand-anything/knowledge-graph.json)
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  互動式 Dashboard                                            │
│  - React + ReactFlow (force-directed / hierarchical layout)  │
│  - 依架構層次顏色編碼                                         │
│  - 模糊/語義搜尋                                             │
│  - 節點點擊 → 摘要、關係、引導導覽                              │
│  - 業務領域視圖切換                                           │
│  - 原始碼檢視器 (prism-react-renderer)                       │
└─────────────────────────────────────────────────────────────┘
```

### Tree-sitter + LLM 混合分析

```
靜態分析 (Tree-sitter, 確定性)：
  - 解析原始碼為 CST (Concrete Syntax Tree)
  - 提取 import/export、函數/類別定義、呼叫點、繼承關係
  - importMap：掃描階段預解析，傳遞給 file-analyzer，避免重複推導
  - 指紋(fingerprint)變更檢測：支援增量更新，僅重新分析已變更的檔案

語義分析 (LLM, 非確定性)：
  - 讀取 Tree-sitter 解析結果 + 原始碼全文
  - 生成：plain-English summary、tags、架構層次、業務域映射
```

### 知識圖譜資料結構

```typescript
// 21 種節點類型（5 code + 8 non-code + 3 domain + 5 knowledge）
type NodeType =
  | "file" | "function" | "class" | "module" | "concept"       // code
  | "config" | "document" | "service" | "table" | "endpoint"    // non-code
  | "pipeline" | "schema" | "resource"                          // non-code
  | "domain" | "flow" | "step"                                  // domain
  | "article" | "entity" | "topic" | "claim" | "source";       // knowledge

// 35 種邊類型（8 大類別）
type EdgeType =
  // Structural: imports, exports, contains, inherits, implements
  // Behavioral: calls, subscribes, publishes, middleware
  // Data flow: reads_from, writes_to, transforms, validates
  // Dependencies: depends_on, tested_by, configures
  // Semantic: related, similar_to
  // Infrastructure: deploys, serves, provisions, triggers
  // Schema/Data: migrates, documents, routes, defines_schema
  // Domain: contains_flow, flow_step, cross_domain
  // Knowledge: cites, contradicts, builds_on, exemplifies, categorized_under, authored_by
```

### Schema 驗證與自修復

```
輸入 JSON
    │
    ▼
sanitizeGraph()     ← null → undefined、lowercase enum-like
    │
    ▼
normalizeGraph()    ← LLM 別名映射（func→function, extends→inherits...）
    │
    ▼
autoFixGraph()      ← 缺失欄位自動填充預設值、型別強制轉換
    │
    ▼
Zod schema validation ← 逐節點/邊驗證、斷裂引用移除
    │
    ▼
輸出：validated KnowledgeGraph + issues[]
```

### 命令體系

```
/understand              主要分析管線（支援 incremental、--auto-update、--language）
/understand-dashboard     啟動互動式 Dashboard
/understand-chat          針對程式碼庫提問
/understand-diff          分析當前變更的影響範圍
/understand-explain       深度解釋特定檔案或函數
/understand-onboard       生成新團隊成員的 onboarding 指南
/understand-domain        提取業務領域知識
/understand-knowledge     分析 Karpathy-pattern LLM wiki
```

### 跨平台支援

13+ AI coding 平台支援，包含 Claude Code (native plugin)、Codex、OpenCode、Cursor、Copilot、Gemini CLI、Vibe CLI、Trae 等。跨平台安裝透過統一的 `install.sh` 腳本 + 平台 symlink。

### 增量更新機制

```
1. 指紋(fingerprint)計算：content hash + function 簽名 + import 集合
2. 變更檢測：比較新舊指紋
3. change-classifier：分類變更層級（minor/major/structural）
4. 僅重新分析已變更檔案
5. mergeGraphUpdate：合併新舊圖譜
6. /understand --auto-update：post-commit hook 自動觸發增量更新
```

### 本地化支援

```
--language zh         中文（簡體）
--language zh-TW      中文（繁體）
--language ja         日文
--language ko         韓文
--language ru         俄文
（預設：en）
```

影響範圍：節點摘要、Dashboard UI 標籤、引導導覽說明。

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 決策分析表 (DA Table)

| 技術名 | 團隊導入成本 | 團隊導入前提 | 團隊導入效果 | overengineering 臨界線 |
|--------|-------------|-------------|-------------|----------------------|
| **Understand-Anything** | **低**。1 條命令安裝；首次分析使用 LLM token（平台內建，無額外 API 費用）；維護：重新執行 `/understand` | 團隊使用 Claude Code / Codex / Cursor 等 AI coding assistant；專案本地可訪問 | 新成員快速獲得全域架構圖；團隊共用一份 JSON 圖譜；增量更新降低重複分析成本 | 團隊少於 3 人、專案少於 50 檔案、或團隊不使用 AI coding assistant：IDE 內建 jump-to-definition 已足夠 |
| **Sourcegraph** | **中-高**。自建需部署伺服器（Docker/K8s）、配置 LSIF/SCIP indexer、持續維護；cloud 版按人頭計費 | 團隊規模 > 20 人；多倉庫/跨語言程式碼庫；有 DevOps 人力維護伺服器 | 跨倉庫搜尋與精確導覽；批次變更（campaigns）；code intelligence（hover/definition/references） | 團隊少於 10 人、或僅有單一倉庫、或團隊已有 IDE 內建 code navigation：部署 Sourcegraph 成本超過效益 |
| **SonarQube** | **中**。需部署 SonarQube 伺服器（Docker）；為各語言配置 scanner；設定 quality gate rule | 團隊需有 code quality 治理需求；CI/CD 已上線；有工程師持續處理掃描結果 | 程式碼品質/安全問題自動檢測；技術債量化追蹤；CI 品質閘門 | 團隊未建立 code review 文化、或無專人處理掃描結果、或專案處於早期快速迭代階段：大量 false positive 消耗工程師時間 |
| **Sourcetrail** (已停止維護) | **低**（安裝客戶端）。但無維護更新，新語言/新版語言不支援 | 僅 C/C++/Java/Python 專案；不需語義理解（純靜態依賴圖已足夠） | 離線互動式依賴圖；符號級 cross-reference | 已停止維護（2021）：對新語言或語言新版本不支援是硬性限制，任何新專案都不適合導入 |
| **doxygen + graphviz** | **低**。安裝 CLI 工具即可；但需工程師手寫結構化註解 | 原始碼需有 Doxygen/Javadoc 格式註解；團隊有 API 文件生成需求 | 自動化 API 文件網站生成；靜態呼叫圖/繼承圖 | 團隊的程式碼沒有結構化註解習慣：需要從零建立註解文化，人力成本超過文件生成效益 |
| **人工手寫架構文件** | **中**。資深工程師時間成本；需持續維護保持與程式碼一致 | 有資深工程師對全域架構已有完整了解；團隊有文件維護流程 | 精確可控的架構文件；可嵌入設計決策說明；不受工具限制 | 團隊流動性高、文件維護人手不足、或專案變動頻繁：文件快速過時，維護成本超過閱讀效益 |

### overengineering 判定矩陣

```
                         團隊 ≤ 3 人         團隊 4-15 人           團隊 15+ 人 / 多倉庫
                         ──────────         ────────────          ──────────────────────
Understand-Anything      過度（IDE         適度導入                適度導入
                         導覽已夠）         （onboarding 加速）      （圖譜共用有價值）

Sourcegraph               過度              過度                    適度導入
                         （無跨倉需求）     （維護成本 > 效益）      （跨倉搜尋剛需）

SonarQube                 過度              適度導入                適度導入
                         （無人力處理       （若團隊有 code         （CI 品質閘門剛需）
                         掃描結果）          review 文化）

doxygen                   看註解文化         看註解文化              看註解文化
                         （無結構化註解     （無結構化註解           （無結構化註解
                         則過度）           則過度）                 則過度）

人工手寫文件               適度              過度                    過度
                         （團隊小、         （變動快、              （規模大、
                         溝通成本低）       維護成本 > 效益）        維護不可能）
```

### 各方案從團隊視角的切入點差異

```
問題：開發團隊如何降低新成員 / 既有成員的程式碼庫理解成本？

Understand-Anything ────► 自動化生成式（Agent 代勞分析）
                           導入成本：極低（一條命令）
                           適用：日常使用 AI coding assistant 的團隊
                           不適用：團隊無 AI coding 習慣、專案過小

Sourcegraph ──────────────► 搜尋基礎設施（部署搜尋引擎）
                           導入成本：中高（需 DevOps 人力）
                           適用：多倉庫、跨團隊、大量程式碼搜尋場景
                           不適用：小團隊、單一倉庫

SonarQube ────────────────► 品質治理基礎設施（部署掃描引擎）
                           導入成本：中（需 CI 整合 + 規則調校）
                           適用：已有 code review 流程、重視程式碼品質的團隊
                           不適用：快速原型階段、無專人處理掃描結果

doxygen ──────────────────► 註解驅動（工程師手寫結構化註解）
                           導入成本：低（工具安裝）+ 中（人力寫註解）
                           適用：API 文件為交付物的團隊
                           不適用：無結構化註解文化的團隊

人工手寫文件 ─────────────► 全人力（資深工程師撰寫）
                           導入成本：高（資深人力時間）
                           適用：小型穩定團隊、架構變動少
                           不適用：團隊流動性高、專案快速演進
```
