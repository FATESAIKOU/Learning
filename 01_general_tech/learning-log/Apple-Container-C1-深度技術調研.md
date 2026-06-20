# Apple-Container-C1-深度技術調研

## 狀況理解

使用者要求調研 Apple 官方開源專案 `apple/container`（https://github.com/apple/container）。

任務定位：屬於 `01_general_tech` 技術解析流程，非 MVP 實作。需依 AGENTS.md 規範產出兩個檔案：
- 分析報告 `output/2026-06-20-Apple-Container.md`（4 點格式 + DA 表）
- 本過程報告 `learning-log/Apple-Container-C1-深度技術調研.md`

現狀掌握：
- 此 repo 為 2026-06-09 剛發布 1.0.0 的專案，38.9k stars，屬高度關注的新專案。
- 使用者僅給 GitHub URL，未指定想深入的方向，故採「全面性技術解析」範圍，涵蓋架構、機制、同類比較。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 閱讀 `01_general_tech/AGENTS.md` 與資料夾結構 | 確認任務流程與輸出格式 | 鎖定 4 點分析格式與 log 格式 | 確認為 general_tech 流程，需 DA 表 |
| webfetch `apple/container` README | 取得專案定位、需求、安裝流程 | 理解專案目標與使用門檻 | 取得：Swift 撰寫、Apple Silicon 限定、macOS 26、OCI 相容、依賴 Containerization package |
| webfetch `docs/technical-overview.md` | 取得底層架構與機制細節 | 釐清 per-container VM 模型與 XPC 組成 | 取得：每 container 一個輕量 VM、XPC helpers 結構、macOS 26 依賴原因、macOS 15 限制 |
| webfetch `apple/containerization` README | 取得底層 runtime 細節 | 釐清 vminitd、kernel、Rosetta 2 機制 | 取得：vminitd init 系統、vsock gRPC、優化 kernel、sub-second boot、Rosetta 2 for linux/amd64 |
| 收斂同類方案（Docker Desktop / Colima / OrbStack / Lima）背景知識 | 完成第 4 點 DA 表 | 提供替代方案切入點差異 | 完成 DA 表，區分共享 VM vs per-container VM 兩派 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 資訊來源覆蓋度 | README + technical-overview + containerization README 三份一手資料交叉比對 | 覆蓋定位、架構、底層、限制四面向 |
| 格式合規性 | 對照 AGENTS.md 4 點格式與 log 格式 | 全部欄位齊備，DA 表欄位齊全 |
| 背景脈絡補足 | macOS 不原生支援 Linux container 的歷史因素、共享 VM 模型的權衡 | 已在報告第 2 點與第 4 點切入點差異說明 |
| 替代方案客觀性 | DA 表涵蓋 4 個同級方案，含副作用與前提 | 無情緒性語言，僅描述機制 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 任務歸屬模組 | (a) 01_general_tech 技術解析 (b) 02_mvps 實作教練 | (a) | 使用者原文為「調研」，未要求實作專案，符合 general_tech 定義 |
| 調研深度範圍 | (a) 僅 README 表層 (b) 含 technical-overview + containerization 底層 (c) 含原始碼層級 | (b) | AGENTS.md 要求補足背景與技術脈絡；(c) 對「調研」過度，留待後續 C2 若有需要再深入 |
| 替代方案選取 | Docker Desktop / Colima / OrbStack / Lima / Podman / Finch | 選前四項 | 此四項為 macOS 上 Linux container 主流方案，與 Apple Container 同質性最高；Podman/Finch 與 Lima/Colima 機制重疊，避免 DA 表冗餘 |
| macOS 26 依賴的處理 | (a) 視為單純版本要求 (b) 視為架構關鍵前提並說明原因 | (b) | technical-overview 明確指出 macOS 26 強化了 Virtualization.framework 與 vmnet，是 per-container VM 模型可行的技術前提，需在報告中點出 |