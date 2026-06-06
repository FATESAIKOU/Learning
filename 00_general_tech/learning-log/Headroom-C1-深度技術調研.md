# Headroom-C1-深度技術調研

## 狀況理解
使用者要求深入調研 GitHub repo `chopratejas/headroom`，這是一個 AI agent 的 context compression layer，主打 60-95% token 節省、本地運行、可逆壓縮。需要按照 AGENTS.md 規範輸出分析報告和過程報告。repo 目前 14.8k stars、941 forks、v0.23.0（2026-06-04），以 Python 77% + Rust 18.2% 構成。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md 與工作目錄結構 | 理解輸出規範與既有檔案結構 | 確認規則與輸出目錄狀態 | 規則已理解，output/ 有 12 篇歷史報告，learning-log/ 有 23 篇歷史記錄 |
| Fetch GitHub repo 頁面 | 獲取 README 與 repo 結構 | 取得技術全貌（功能、架構、benchmark、比較） | 成功取得完整 README（含架構圖、benchmark 表、agent 兼容矩陣、比較表） |
| Fetch 官方文件：Architecture | 深入了解 pipeline 與核心組件 | 理解 CacheAligner / ContentRouter / CCR / SmartCrusher 機制 | 成功取得架構文檔（三階段 pipeline、各 stage 詳細說明、CCR 機制、TOIN） |
| Fetch 官方文件：CCR | 了解可逆壓縮的設計 | 理解 Compress-Cache-Retrieve 四個階段 | 成功取得 CCR 文檔（壓縮儲存、工具注入、回應攔截、前後文追蹤、BM25 搜索） |
| Fetch 官方文件：How Compression Works | 了解各內容類型的壓縮策略 | 取得各類型 detection signal / compressor / savings 對照 | 成功取得（7 種內容類型對照表、結構保留策略、實際壓縮率、batch compression） |
| Fetch 官方文件：Benchmarks | 了解壓縮效能與準確度數據 | 驗證「不損害準確度」的宣稱 | 成功取得（compression latency、accuracy benchmark、production telemetry 50K+ sessions） |
| Fetch RTK repo | 了解同級替代方案 RTK | 比較 scope、deploy mode、是否 local、是否 reversible | 成功取得 RTK README（59.3k stars，CLI proxy，僅覆蓋 shell command output，不可逆） |
| Fetch lean-ctx repo | 了解同級替代方案 lean-ctx | 比較 scope 與切入點差異 | 成功取得 lean-ctx README（2.5k stars，Context OS，68 MCP tools，覆蓋更廣含 code graph + memory） |
| Fetch 官方文件：Limitations | 了解限制與安全閘 | 確認何時幫助/不幫助、code compression 安全保護 | 成功取得（幫助 vs 不幫助場景表、安全閘機制、Adaptive K 保留策略、TOIN 冷啟動說明） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| repo 基本資訊完整性 | 檢查是否取得 README、架構、CCR、壓縮、benchmark、限制文檔 | 6 份文檔全部取得，資訊充足 |
| 替代方案資訊完整性 | 檢查是否取得 RTK、lean-ctx、Compresr、OpenAI Compaction 資訊 | 從 Headroom README 的比較表 + RTK/lean-ctx README 取得足夠資訊 |
| 輸出目錄狀態 | 檢查 output/ 和 learning-log/ 目錄存在且可寫入 | 兩個目錄存在，已寫入分析報告 |
| 分析報告格式完整性 | 檢查是否涵蓋規定的 4 點 + DA 表 | 4 點全部涵蓋，DA 表含 5 個技術 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 資料取得渠道 | 1) 僅 GitHub README 2) README + 官方文檔 3) README + 文檔 + 外部搜尋 | 選項 2：README + 官方文檔 | README 已含足夠結構化資訊，官方文檔可補充架構/CCR/benchmark/limitations 細節；外部搜尋的替代方案資訊在 README 比較表中已有提及 |
| 替代方案研究深度 | 1) 僅引用 Headroom README 比較表 2) 額外 fetch RTK + lean-ctx README | 選項 2：額外 fetch | 比較表中的 Compresr/Token Co. 為 hosted 服務且資訊較少，但 RTK (59.3k stars) 和 lean-ctx 是主要競品，值得深入了解其技術差異 |
| DA 表技術選取 | 1) 3 個 2) 4 個 3) 5 個 | 選項 3：5 個 | 規格要求 2-4 個，5 個為：RTK (CLI)、lean-ctx (Context OS)、OpenAI Compaction (provider-native)、Compresr/Token Co. (hosted API)、LLMLingua (LM-based)；涵蓋 CLI/proxy/provider/hosted/ML 五種不同切入點，資訊價值更高 |
| 文件語言 | 1) 英文 2) 中文 | 選項 2：中文 | AGENTS.md 明確要求使用中文 |
