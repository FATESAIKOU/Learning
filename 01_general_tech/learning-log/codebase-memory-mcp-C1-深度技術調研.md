# codebase-memory-mcp-C1-深度技術調研

## 狀況理解
- 使用者要求調研 GitHub 專案 `DeusData/codebase-memory-mcp`，並依 AGENTS.md 規範產出分析報告與學習日誌。
- 此專案為 MCP（Model Context Protocol）code intelligence server，以 Pure C + tree-sitter 建構持久化知識圖譜，主打毫秒級索引、單一靜態二進位、零依賴。
- 已存在先前的 `CodeGraph` 系列報告（2026-05-30），但那是針對不同 repo 的調研；本次 `codebase-memory-mcp` 為獨立技術，自增 ID 從 C1 重新起算。
- 需補的背景脈絡：MCP 協議定位、tree-sitter 與 LSP 的差異、LLM coding agent 的 token 成本問題、同類替代方案（Sourcegraph / graphify / Aider repo-map / Sourcegraph Cody 等）。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| webfetch GitHub repo 主頁 | 取得 README、功能清單、效能基準、架構 | 掌握技術全貌與官方論述 | 取得完整 README（含 14 MCP tools、Hybrid LSP、158 語言、效能表、arXiv 連結） |
| webfetch arXiv:2603.27277 摘要頁 | 取得第三方學術評估數據 | 取得 benchmark 數據與方法學 | 取得 abstract：31 個 repo 評測、83% answer quality vs 92%、10× fewer tokens、2.1× fewer tool calls；19/31 graph-native 查詢追平或超越 |
| bash 檢視 output/ 與 learning-log/ 目錄 | 確認既有報告、避免命名衝突、決定自增 ID 起點 | 確認技術名與 ID 編號 | 確認無同名 `codebase-memory-mcp` 檔案，從 C1 起算 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 資訊完整性 | 4 點分析報告所需資料是否齊備（問題/背景/機制/替代方案） | 齊備：README 提供機制與背景，arXiv 提供量化評估，替代方案可由通用技術背景推導 |
| 報告命名合規 | 日期 2026-06-27、技術名 `codebase-memory-mcp`、位於 `output/` | 合規 |
| 日誌命名合規 | `codebase-memory-mcp-C1-深度技術調研.md`、位於 `learning-log/` | 合規 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 技術名命名 | (a) `codebase-memory-mcp` (b) `Codebase-Memory` (c) 沿用舊 `CodeGraph` | (a) `codebase-memory-mcp` | 與 repo 實際名稱一致，避免與既有 `CodeGraph` 系列混淆 |
| 是否合併舊 CodeGraph 報告 | (a) 合併追加 QA (b) 視為獨立新技術 | (b) 獨立新技術 | repo 不同、技術細節差異大（Pure C、Hybrid LSP、158 語言 vs 舊報告內容），獨立調研可保持脈絡清晰 |
| 替代方案選取 | tree-sitter 原生 / Sourcegraph / graphify / Aider repo-map / LSP-only / GitHub Copilot workspace | 選 tree-sitter 原生、Sourcegraph (Cody)、Aider repo-map、graphify 四項 | 涵蓋「同為靜態 AST」「同為 code graph+web UI」「同為 token 壓縮 map」「同為知識圖譜產物」四個切入點，形成對照 |