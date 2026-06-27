# OpenMontage-C1-深度技術調研

## 狀況理解

使用者要求：
1. 先 catchup 目前資料夾（特別是 AGENTS.md）
2. 深入調研 `https://github.com/calesthio/OpenMontage`

目前資料夾結構：
- `01_general_tech/AGENTS.md`：定義「技術解析助理」角色與輸出格式（分析報告 4 點 + DA 表 + 學習過程報告），格式嚴格受限
- `01_general_tech/output/`：已有 30+ 份歷史分析報告
- `01_general_tech/learning-log/`：已有 40+ 份學習過程報告

OpenMontage 是 calesthio 開發的開源 agentic 影片製作系統，24k stars，AGPL-3.0 授權。核心訴求是「agent-first architecture」——AI coding assistant 本身就是 orchestrator，讀 YAML pipeline manifest + Markdown skill 驅動整個影片製作流程，Python 僅提供工具與持久化。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `01_general_tech/AGENTS.md` | 理解輸出格式規則與角色定義 | 確認 4 點分析 + DA 表 + 學習過程報告格式 | 已理解：分析報告含 4 段落（問題/背景/解法/替代方案）+ DA 表 5 欄 + learning-log 4 段格式 |
| 讀取 `00_news_catchup/AGENTS.md` 與 `02_mvps/AGENTS.md` | 確認這是三個獨立工作流，OpenMontage 屬於 `01_general_tech` | 避免誤用其他工作流格式 | 確認 OpenMontage 單一專案調研對應 `01_general_tech`，非新聞批次也非 MVP 實作 |
| 讀取 `learning-log/OpenDesign-C1-深度技術調研.md` 與 `output/2026-06-06-OpenDesign.md` | 參考歷史報告的風格、深度、架構 | 以 OpenDesign 報告為基準（同為 GitHub 專案調研） | 已參考：OpenDesign 報告含架構圖、程式碼範例、表格密度、DA 表 4 方案；本次報告對齊此標準 |
| 擷取 GitHub repo 首頁 README | 取得整體介紹、功能列表、pipeline 列表、provider 矩陣 | 理解 OpenMontage 是什麼、做什麼、與競品差異 | 已取得完整 README：12 pipelines、52+ tools、500+ skills、zero-key 免費路徑、3 條免費製作路徑、provider 矩陣、平台支援 |
| 擷取 `AGENT_GUIDE.md` | 了解 agent 合約、Rule Zero（所有製作必走 pipeline）、決策溝通合約、runtime 鎖定規則 | 取得 agent 行為規範與治理規則 | 已取得完整 agent guide：onboarding、reference video 流程、Rule Zero、preflight、provider menu 呈現規則、composition runtime HARD RULE、motion-required 規則、selector pattern、stage agent、reviewer protocol、checkpoint protocol、3-layer 知識架構、what not to do |
| 擷取 `docs/ARCHITECTURE.md` | 理解系統拓樸、repo layout、BaseTool 契約、registry、selector、checkpoint、budget、3-layer 知識、config、測試架構 | 取得完整技術架構參考 | 已取得完整架構文件：agent-first 原則、repo layout、BaseTool 契約欄位表、ToolRegistry 方法、selector 7 維評分、11 個 canonical artifact、budget 生命週期、3-layer 知識架構、config.yaml、env var 表、media profiles、composition runtime 三引擎、測試架構、6 個關鍵設計決策 |
| 擷取 `config.yaml` | 取得實際 runtime 配置 | 驗證文件描述與實際 config 一致 | 已取得：llm provider 預設 anthropic、budget mode 預設 warn/總額 $10/單次審批 $0.50、checkpoint policy guided、output 預設 1080p 30fps CRF 23 |
| 擷取 `pipeline_defs/animated-explainer.yaml` | 取得具體 pipeline manifest 範例 | 理解 YAML manifest 實際結構與 stage 定義 | 已取得完整 manifest：reference_input 支援、orchestration budget $2/20min、compatible_playbooks、research/proposal/script 各 stage 的 skill/produces/tools_available/review_focus/success_criteria/human_approval_default |
| 擷取 `tools/base_tool.py` | 取得 BaseTool 實際契約程式碼 | 驗證架構文件描述的 BaseTool 欄位與實作一致 | 已取得：ToolTier/ToolStability/ToolStatus/ToolRuntime enum、ResourceProfile/RetryPolicy/ToolResult dataclass、BaseTool ABC、_load_dotenv 機制 |
| 列出 `pipeline_defs/` 目錄 | 確認 12 個 pipeline 檔案存在 | 驗證 README 宣稱的 pipeline 數量 | 確認 13 個 yaml（含 framework-smoke 測試用），對應 README 的 12 pipelines + 1 測試 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 報告格式合規性 | 對照 AGENTS.md 的 4 點格式 + DA 表欄位要求 | 分析報告含 4 段落（問題/背景/解法/替代方案），DA 表含 5 個替代方案含 5 欄（技術名/技術解法/技術使用前提/技術使用副作用/技術使用預期效果） |
| 技術深度 | 確認核心機制（agent-first 架構、3-layer 知識、pipeline manifest、BaseTool 契約、selector 7 維評分、3 runtime、品質閘、預算治理、checkpoint）均有涵蓋 | 涵蓋整體架構圖、3-layer 知識表、pipeline manifest YAML 範例、BaseTool Python 契約、selector 評分維度、3 runtime 對比表、4 個品質閘、CostTracker 生命週期、checkpoint JSON 結構、免費路徑表 |
| 資訊覆蓋面 | 確認擷取了 README + AGENT_GUIDE + ARCHITECTURE + config.yaml + animated-explainer.yaml + base_tool.py + pipeline_defs 目錄列表 | 共擷取 7 份來源文件 + 1 個目錄列表，覆蓋產品定義、agent 合約、系統架構、runtime 配置、具體 pipeline 範例、工具契約實作、pipeline 清單驗證 |
| DA 表完整性 | 確認有 5 個替代方案（Remotion 單獨 / CapCut+Premiere / MoviePy+FFmpeg / Runway+Pika+Kling） | 已列出 5 個方案含完整 5 欄，涵蓋程式化渲染器、GUI 編輯器、低階組裝、單一供應商雲端產品四種切割角度 |
| 與歷史報告風格一致性 | 對照 `output/2026-06-06-OpenDesign.md` 的詳細度與架構風格 | 架構圖、程式碼範例、表格密度、附錄結構與 OpenDesign 報告一致 |
| 文件版本漂移查覺 | 比對 README（52 tools / 500+ skills）、ARCHITECTURE（57+ tools）、AGENT_GUIDE 的數字差異 | 已在報告 §1 指出 tool/skill 數量在不同文件不一致（48/52/57+、400+/500+），標明為文件版本漂移非核心機制模糊 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 報告結構聚焦點 | ① 聚焦「產品」（12 pipeline 功能列表） ② 聚焦「架構」（agent-first / 3-layer / BaseTool / selector） ③ 兩者平衡 | ③ 兩者平衡但偏架構 | OpenMontage 的核心創新在架構層（agent-as-orchestrator + pipeline-as-YAML + skill-as-Markdown + 品質閘合約），產品功能是架構的結果；但完全略過 pipeline 列表會讓讀者不知能做什麼，故保留 pipeline 表與免費路徑表 |
| 替代方案選取 | ① Runway/Pika/Kling 單一供應商 ② 加上 Remotion 單獨使用 ③ 再加 CapCut/Premiere ④ 再加 MoviePy/FFmpeg 腳本 | 5 個方案全選 | AGENTS.md 要求 2-4 個但 OpenMontage 的替代方案光譜需 5 個才能涵蓋：程式化渲染器（Remotion 單獨）、GUI 編輯器（CapCut/Premiere）、低階組裝（MoviePy/FFmpeg）、單一供應商雲端（Runway/Pika/Kling）；多列一個有助理解 OpenMontage 的「pipeline + 品質閘 + 多供應商降級」獨特性 |
| DA 表欄位設計 | ① 沿用歷史 5 欄 ② 加入授權/LLM 依賴欄 | ① 沿用 5 欄 | OpenMontage 與替代方案的授權差異（AGPL vs 商業 vs 開源）已寫進「技術使用副作用」欄；LLM 依賴差異（agent-first vs GUI vs 腳本）已寫進「技術使用前提」欄，無需另列 |
| 免費路徑是否獨立章節 | ① 整合進 §3 解法 ② 獨立子章節 | ② 獨立子章節 §3.11 | 零 API key 即可產出影片是 OpenMontage 的關鍵差異化（多數 AI 影片工具需付費），值得獨立呈現三條免費路徑 |
| 品質閘細節深度 | ① 僅列表 ② 詳列每閘檢查項 | ② 詳列 | 品質閘是 OpenMontage 與所有競品的關鍵差異（強制 post-render self-review、slideshow risk scoring），需足夠細節才能理解為何這是「production-grade」而非玩具 |
| pipeline manifest YAML 範例是否納入 | ① 僅描述結構 ② 完整 YAML 範例 | ② 完整 YAML 範例 | pipeline manifest 是 OpenMontage 的核心抽象，讀者需看到實際 YAML 結構（stages/skill/produces/review_focus/success_criteria/human_approval_default）才能理解「agent 讀 YAML 驅動流程」如何運作 |