# EverOS-C1-深度技術調研

## 狀況理解

使用者要求對 https://github.com/EverMind-AI/EverOS 進行深入技術調研。
EverOS 是一個為 self-evolving AI agents 提供長期記憶的開源專案（Apache 2.0），6.3k stars，666 commits。
核心組件為 EverCore（記憶作業系統）、HyperMem（超圖記憶架構）、EverMemBench & EvoAgentBench（評測框架）。

使用者要求遵循 AGENTS.md 規範：產出分析報告（output/）與分析過程報告（learning-log/），4 點制格式，使用中文、表格、圖示、階層結構。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取本地 AGENTS.md | 理解任務規範與輸出格式 | 明確輸出物要求（分析報告 4 點、DA 表、learning-log） | 確認格式要求，包括檔名規則與內容格式 |
| 讀取本地目錄結構 | 了解已有分析成果 | 得知先前已分析過 OpenHuman、CodeGraph、CloakBrowser | 目錄有 01_general_tech（技術調研）與 01_nanobot_dockerize |
| 讀取 EverOS README（GitHub webfetch） | 取得專案整體描述 | 理解專案架構、使用方式、benchmark 成績 | 完整 README，包含 quick start、architecture、benchmarks 表格、API 範例 |
| 讀取 EverOS AGENTS.md（GitHub webfetch） | 理解 EverOS 專案本身的開發規範 | 得知專案地圖、開發指令、關鍵 entry points | 6 層架構入口、開發指令（docker/uv/make/pyright）、prompt 路徑 |
| 讀取 EverCore ARCHITECTURE.md | 理解核心記憶系統的架構設計 | 取得 6 層架構細節、記憶建構/檢索流程、技術堆疊 | 完整架構文件：Agentic/Memory/Retrieval/Business/Infra/Core 六層 |
| 讀取 EverCore src/ 目錄結構 | 認識實際程式碼組織方式 | 確認各層實作路徑與關鍵檔案 | 確認 agentic_layer、memory_layer、infra_layer 等實際目錄對應 |
| 讀取 HyperMem README | 理解超圖記憶架構的設計與實作 | 取得三層 hypergraph 結構、coarse-to-fine 檢索、LoCoMo 92.73% 成績 | 完整 paper 方法說明、benchmark 對比表（vs 15 個 baselines）、實驗 pipeline 6 stages |
| 讀取 EverMemBench README | 理解記憶品質評測框架 | 取得 multi-party group chat evaluation 設計、5 memory systems + LLM 評測流程 | 完整 CLI 使用說明、Add→Search→Answer→Evaluate pipeline、5 systems 適配器 |
| 讀取 EverMemOS paper（2601.02163）abstract | 從學術源頭理解設計理念 | 取得 engram-inspired lifecycle 三階段、LoCoMo 93.05% 成績 | 確認三階段：Episodic Trace Formation → Semantic Consolidation → Reconstructive Recollection |
| 讀取 HyperMem paper（2604.08256）abstract | 理解超圖方法的理論背景 | ACL 2026 論文，確認 hypergraph 結構定義與核心貢獻 | 確認 hyperedge 加權傳播、coarse-to-fine retrieval 策略 |
| 讀取 EverMemBench paper（2602.01313）abstract | 理解評測設計的學術動機 | 2400 QA pairs、3 dimensions、multi-party 場景 | 確認 fine-grained recall、memory awareness、user profile understanding 三維評測 |
| 讀取 docs.evermind.ai 首頁 | 理解官方文檔入口與雲端服務 | 得知 EverOS Cloud（託管服務）vs Open Source（自託管）vs API Reference | 確認三路線並存，雲端可快速部署 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 專案整體理解 | 閱讀 README + AGENTS.md + docs 首頁 | 確認：EverOS = use-cases + methods + benchmarks 三部件；核心為 EverCore |
| 核心架構理解 | 閱讀 ARCHITECTURE.md + src/ 目錄 | 確認：6 層架構（Agentic→Memory→Retrieval→Business→Infra→Core），記憶生命週期 = Formation→Consolidation→Recollection |
| 替代方案 / 競爭分析 | 閱讀 README benchmarks 表 + HyperMem 對比表 + paper abstracts | 確認：主要對比有 Traditional RAG、Zep、Mem0、GraphRAG、HyperGraphRAG、Memobase、MemOS 等 |
| 技術堆疊理解 | 閱讀 ARCHITECTURE.md tech stack | 確認：FastAPI + MongoDB + Elasticsearch + Milvus + Redis + Docker |
| 評測框架理解 | 閱讀 EverMemBench + EvoAgentBench README | 確認：5 memory systems + LLM baseline 可比較；2400 QA pairs 三維度 |
| 替代記憶方案分析 | 各方案 GitHub/paper abstract | 整理出 Traditional RAG、Zep、Mem0、HyperMem 的 DA 表 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 調研深度 | A) 僅閱讀 README B) README + 子模組 docs C) README + docs + papers + 源碼目錄 | C | AGENTS.md 要求「若文章本身資訊不足，請盡量從網路搜尋補上」。EverOS 的完整理解需跨越 README→ARCHITECTURE→Papers→Source layout |
| DA 表替代方案選擇 | 多種記憶系統（~15 個 baselines） | 選取 Traditional RAG、Zep、Mem0、HyperMem | 選擇覆蓋不同記憶結構化程度（flat→graph→hypergraph→lifecycle）的代表方案，避免重複 |
| 報告重點 | A) 強調 EverCore 實作細節 B) 強調學術論文設計理念 C) 兼顧兩者 + 與替代方案對比 | C | 使用者要求「深入調研」，需要同時覆蓋技術架構、學術動機與競爭格局 |
| 是否需要 clone repo 閱讀源碼 | A) 僅從 web 閱讀 B) clone 後閱讀關鍵檔案 | A | web fetch 已能覆蓋 README、AGENTS.md、ARCHITECTURE.md、src/ 目錄結構與關鍵子模組 README，源碼層級細節非本次分析重點 |
