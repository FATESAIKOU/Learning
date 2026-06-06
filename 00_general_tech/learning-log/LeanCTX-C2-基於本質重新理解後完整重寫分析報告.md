# LeanCTX-C2-基於本質重新理解後完整重寫分析報告

## 狀況理解
使用者在 C1 調研後經由對話逐步理解 LeanCTX 的本質不止壓縮，而是包含 session 生命週期管理與適時記憶召回。同時確認記憶精煉/召回不涉及 LLM API 呼叫（使用本機 ONNX embedding）。使用者要求基於完整理解重寫分析報告，格式維持四項但內容須反映三個本質（壓縮、記憶持久化、適時召回），且不包含對話脈絡參考。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 重讀 LEAN-CTX.md（agent 指令文檔） | 確認 session 恢復機制在實際使用中的行為 | 理解 auto-restore、knowledge wakeup、ctx_overview 的觸發時機 | 確認 session 恢復是自動注入 active session block，含持久化檔案引用 [F1]..[Fn] |
| 重讀 03-memory-and-knowledge.md | 取得記憶層完整 API 與實作細節 | 取得 CCP session、knowledge store、gotcha tracker 的完整命令 | 取得兩層記憶架構（Session / Knowledge）、consolidate 規則式去重、semantic/hybrid/exact 三種召回模式 |
| 重讀 05-advanced.md（proxy/serve 段） | 確認 HTTP serve 模式是否存在 | 為後續 GAS 場景做技術可行性評估 | 確認 lean-ctx serve 提供 HTTP MCP + /v1/tools/call 端點，team serve 內建 Bearer auth |
| 重讀 ARCHITECTURE.md 的 memory/graph 模組清單 | 確認 embedding engine 的實作方式 | 驗證記憶召回是否呼叫外部 LLM API | 確認 dense_backend.rs 使用 ONNX all-MiniLM-L6-v2，無 LLM API 依賴；consolidation_engine.rs 為規則式合併 |
| 重讀 leanctx.com/compare/ | 再次確認競爭者功能矩陣 | 更新 DA 表確保對比準確 | 取得 RTK/Context+/MemGPT 的 feature 矩陣，確認 MemGPT 記憶操作可能觸發 LLM 推論 |
| 重寫 output/2026-06-06-LeanCTX.md | 產出涵蓋三個本質的完整報告 | 報告反映 compression + memory + routing + governance 四維度的正確定義 | 已完成重寫，含 CCP 恢復區塊範例、knowledge API 範例、hybrid search 機制說明 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 三大本質覆蓋 | 檢查報告是否涵蓋壓縮、記憶持久化（CCP + Knowledge）、適時召回（recall/search hybrid） | 3.1~3.4 全部覆蓋，含具體 CLI/MCP 命令範例 |
| 記憶操作獨立性 | 檢查是否明確標註記憶操作不呼叫 LLM API | 3.2 層二明確寫入「所有記憶操作不呼叫外部 LLM API」、ONNX rten runtime 說明 |
| 替代方案對比準確性 | DA 表五維度對比圖是否合理 | 覆蓋矩陣（壓縮/記憶持久化/適時召回/程式碼理解/治理）五軸均正確 |
| 無對話脈絡 | 檢查報告全文是否包含對話參考詞（如「新事實」「經過」） | 全文無此類詞彙 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 報告結構 | A. 維持 3 節（壓縮/路由/記憶）；B. 擴為 4 節（壓縮/記憶/路由/治理） | B. 擴為 4 節 | 記憶層需要獨立為完整章節，與 VISION.md 的四維度框架對齊；治理層補足預算/SLO/Proof 等控制面 |
| 記憶層說明深度 | A. 僅列 API 名稱；B. 含 CLI/MCP 呼叫範例與儲存檔案路徑 | B. 含範例與路徑 | AGENTS.md 要求「善用程式碼或虛擬碼做舉例」，直接給出命令與 JSON 恢復區塊能強化心智模型 |
| LLM 獨立性標註 | A. 僅在記憶層一處標註；B. 記憶層 + DA 表對比 MemGPT 時都標註 | B. 雙處標註 | 記憶操作不呼叫 LLM 是與 MemGPT 的核心差異點，需在對比表中明確 |
