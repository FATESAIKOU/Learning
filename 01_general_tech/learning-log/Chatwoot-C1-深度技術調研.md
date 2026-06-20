# Chatwoot-C1-深度技術調研

## 狀況理解
使用者要求調研 https://github.com/chatwoot/chatwoot，並已確認採用 `01_general_tech` 工作流程（4 點分析報告格式）。使用者僅提供 GitHub URL，未指定調研重點，故需自行從 README、官方文件、Captain 文件收斂出 Chatwoot 的核心問題、背景、解法與替代方案。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| Read AGENTS.md × 3 + 資料夾結構 | 確認三個工作流程規範與適用場景 | 判斷用哪個流程輸出 | 使用者選 01_general_tech |
| webfetch GitHub repo 頁面 | 取得 README、stars、語言比例、版本、資料夾結構 | 取得基本事實 | 取得完整 README、32.8k stars、Ruby46.9%/Vue27.4%、v4.15.1 |
| webfetch Captain docs 站台 | 取得 Captain AI Agent 完整機制（Assistant/Copilot/Documents/FAQs/Memories/Custom Tools/BYOK/Credits） | 補足 AI 部分細節 | 取得 10 篇 Captain 文章摘要 |
| webfetch chatwoot.com/docs 與 raw README | 補架構與部署資訊 | 確認部署選項與文件結構 | docs 頁面回 404，改用 help-center 入口確認文件分布 |
| 依 4 點格式撰寫分析報告 | 產出 output/20260620-Chatwoot.md | 符合 AGENTS.md 規範 | 完成 4 點 + 附錄決策表 |
| 撰寫本過程報告 | 產出 learning-log/Chatwoot-C1-*.md | 留下調研軌跡 | 本檔 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 分析報告存在 | glob `01_general_tech/output/*Chatwoot*.md` | 已產出 `20260620-Chatwoot.md` |
| 4 點齊全 | 讀報告確認 §1-§4 皆存在 | 4 點 + DA 表 + 附錄決策表 |
| 過程報告編號 | 確認 learning-log 無 Chatwoot 前作 | C1 為首份 |
| 事實可查 | stars/version/語言比例/BYOK/Firecrawl/Custom Tools 皆對應官方文件 | 與 README + Captain docs 一致 |
| 中文撰寫 | 通篇繁體中文（程式碼與欄位名保留英文） | 符合 AGENTS.md 規則 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|------------|-----------|---------|---------|
| 工作流程 | 00_news_catchup / 01_general_tech / 02_mvps | 01_general_tech | 單一專案調研最匹配 4 點格式；使用者亦選此項 |
| 調研深度 | 僅 README / README+Captain docs / 再加原始碼目錄 | README + Captain docs | README 已含架構全貌，Captain docs 補 AI 細節，原始碼層級對 4 點報告非必要 |
| 替代方案選擇 | 只列商業對手 / 商業+開源 / 商業+開源+純LLM派 | 商業(Zendesk/Intercom)+開源(Papercups/Rocket.Chat)+整合派+LLM派 | 涵蓋「同級/替代/不同思考方式」三層，符合 AGENTS.md「2-4 個同級或替代方案」 |
| DA 表欄位 | 預設 5 欄 / 加授權與LLM欄 | 預設 5 欄 | Chatwoot 調研未涉及前次 LeanCTX/HyperFrames 的授權與 LLM 特殊欄位需求 |
| 附錄決策表 | 加 / 不加 | 加 | Chatwoot 技術選型明確（Rails/Vue/ActionCable/BYOK），有助心智模型 |