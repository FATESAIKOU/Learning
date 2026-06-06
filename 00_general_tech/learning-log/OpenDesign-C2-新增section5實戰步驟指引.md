# OpenDesign-C2-新增section5實戰步驟指引

## 狀況理解

使用者在前兩輪對話中，先做了 Open Design 的深度技術調研，接著詢問了兩個實戰問題：
1. 沒有 Figma 訂閱能否用 Open Design 做 vibe design（答：可以，OD 本身就是 Figma alternative）
2. 能否接上 opencode 內部的 Ollama 訂閱（答：可以，兩種路徑皆可行）

最後要求：「學習紀錄多加第五大項，給出我用 opencode + opendesign 的一步一步步驟指示」

需要在已輸出的 `output/2026-06-06-OpenDesign.md` 分析報告中，新增 Section 5 的實戰步驟指引。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取現有分析報告 | 確認目前報告結構與內容邊界 | 確認 Section 1-4 已完成，需新增 Section 5 | 報告現有 262 行、4 個章節，DA 表完整 |
| 撰寫 Section 5 內容 | 提供 OpenCode + Open Design 的逐步操作指引 | 覆蓋 Phase 0（前置確認）到 Phase 6（進階用法）加常見問題與最小流程總結 | 已完成七個小節：架構總覽圖、Phase 0-6、常見問題、最小可行流程 |
| 編輯分析報告檔案 | 將 Section 5 追加到檔案末端 | 不影響既有 Section 1-4 內容 | 透過 edit tool 在 DA 表切割點差異表格後插入完整 Section 5 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 報告完整性 | 確認 output/2026-06-06-OpenDesign.md 包含 5 個章節 | Section 1-5 全部存在，結構無斷裂 |
| Section 5 覆蓋範圍 | 確認涵蓋前置確認、安裝、設定、skill/DS 選擇、生成預覽、迭代 loop、進階用法、FAQ、最短路徑 | 全部涵蓋 |
| 操作步驟可執行性 | 確認每個步驟有具體命令或 UI 操作說明 | 所有命令皆可複製貼上執行（opencode --version、curl install、od daemon 等） |
| 與既有內容一致性 | 確認 Section 5 的架構描述與 Section 3 的技術細節一致 | 架構總覽圖與 Section 3.1/3.2/3.8 一致；adapter 機制與 Section 3.4 一致 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| Section 5 的組織方式 | ① 線性步驟 1→2→3 ② Phase-based (Phase 0-6) ③ 按功能模組分類 | ② Phase-based | Phase-based 能清楚區分「前置準備」「安裝」「設定」「使用」「進階」，適合不同起點的使用者跳讀 |
| 是否包含 MCP server 進階用法 | ① 排除（聚焦基本流程） ② 包含 | ② 包含 | 使用者情境是 opencode 重度用戶，MCP mode 讓 opencode 內部直接呼叫 OD 是顯著價值點 |
| 是否包含手寫 DESIGN.md 範例 | ① 僅提及 ② 給完整 heredoc 範例 | ② 給完整 heredoc | 使用者明確表示想做 vibe design（自行調整風格），手寫 DESIGN.md 是核心能力 |
| 常見問題收錄範圍 | ① 僅 opencode 相關 ② opencode + OD 通用 | ② 兩者兼收 | 初次使用者常遇到 opencode 偵測、model 輸出格式、Ollama 連通性三類問題 |
