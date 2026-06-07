# LeanCTX-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `yvgude/lean-ctx` 進行深度技術調研。該專案標榜為 "Context OS for AI development"，宣稱透過單一 Rust 二進位提供壓縮、記憶、路由、驗證四維度的 context 管理能力，支援 30+ AI coding 工具。需產出符合 `01_general_tech/AGENTS.md` 規範的分析報告（4 點格式）與過程記錄。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| fetch GitHub repo README (yvgude/lean-ctx) | 取得專案核心介紹、功能清單、安裝方式、使用場景 | 掌握專案全貌與核心價值主張 | 成功取得完整的 README.md，含 11 段旅程說明、benchmark 數據、30+ 支援工具清單 |
| fetch ARCHITECTURE.md | 取得完整架構設計文檔 | 理解內部模組設計、資料流、處理管線 | 取得 1190 行詳細架構文檔，含 3 張流程圖、完整模組清單 |
| fetch VISION.md | 理解長期路線圖與設計哲學 | 理解四個維度的願景、現狀與未來方向 | 取得四維度詳細說明（壓縮/路由/記憶/驗證），各維度已實現功能與未實現方向 |
| fetch LEAN-CTX.md | 取得給 AI agent 的指令文檔 | 理解實際使用時 agent 如何呼叫工具 | 取得工具映射表（MUST USE vs NEVER USE）、10 種讀取模式指南 |
| fetch docs/reference/README.md | 取得完整參考文件索引 | 了解所有文檔組織結構 | 取得 14 段旅程的完整清單與附錄索引 |
| fetch leanctx.com/compare/ | 取得與競爭產品對比 | 補充 DA 表的替代技術資訊 | 取得與 RTK、Context+、MemGPT/Letta 的功能矩陣對比 |
| fetch appendix-mcp-tools.md | 取得全套 68 個 MCP 工具清單 | 了解工具完整覆蓋範圍 | 取得 7 大類 68 工具的分類與參數一覽 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 報告完整性 | 檢查 4 點格式是否全部涵蓋（問題/背景/解法/替代方案 DA 表） | 4 點全覆蓋，DA 表包含 4 個替代技術 |
| 資料來源覆蓋 | 確認至少讀取 repo README + 架構 + 競爭對比 | 讀取 7 份來源文檔，資訊充足 |
| 輸出物存在 | 確認 `output/2026-06-06-LeanCTX.md` 已寫入 | 已寫入 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 替代技術範圍 | A. 僅列 RTK/Context+；B. 加入 MemGPT/Letta；C. 加入更多自訂規則方案 | B. 列 RTK、Context+、MemGPT/Letta、手動 Rules | 官網 compare 頁面明確列出此三者為主要對比對象，外加手動規則做為零工具 baseline |
| 架構細節深度 | A. 詳列所有模組；B. 僅摘要核心模組 | B. 僅摘要核心模組（壓縮/路由/記憶/驗證） | 報告格式要求精簡，且 VISION.md 的四維度框架已足夠結構化說明 |
| 是否需要 CDP | A. 使用 CDP 繞過反爬；B. 全部使用 web fetch | B. 全部使用 web fetch | GitHub 與 leanctx.com 無反爬阻擋，web fetch 即可完整取得 |
