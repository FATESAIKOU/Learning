# Zed-C1-深度技術調研

## 狀況理解
使用者要求對 https://zed.dev/ 進行深度技術調研，依照 AGENTS.md 規則產出分析報告（output/）與分析過程報告（learning-log/）。Zed 在此目錄中尚未有任何分析產出物，因此本次為首次調研（C1）。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md 與目錄結構 | 理解產出格式規則，確認 Zed 是否已有分析報告 | 掌握 AGENTS.md 規範，確認無重複產出 | 已理解 4 點分析格式 + 過程報告格式；Zed 無既有報告 |
| 從 zed.dev 首頁獲取資訊 | 取得 Zed 的產品定位、核心功能、技術特色 | 了解 Zed 的主要賣點與關鍵能力 | 獲取：GPU 加速、Rust 原生、AI Agent、即時協作、Edit Prediction、ACP 協定等 |
| 從 zed.dev/docs 獲取文件結構 | 取得完整的文件大綱以理解功能覆蓋範圍 | 掌握 Zed 的功能體系（AI、程式碼編輯、協作、語言支援、遠端開發等） | 獲取完整的左側導航目錄結構，確認 Zed 功能涵蓋面 |
| 從 GitHub repo (zed-industries/zed) 獲取資訊 | 取得開源狀況、技術棧、社群規模、授權資訊 | 確認技術實現語言、授權、社群活躍度 | 84.2k stars、38,097 commits、97.8% Rust、GPL-3.0 + Apache-2.0 |
| 從 zed.dev/blog/we-have-to-start-over 獲取架構設計背景 | 理解為什麼 Zed 選擇從底層重建，而非基於現有框架 | 掌握 Atom→Zed 的技術轉折點與 Rust/GPU 的選擇理由 | 獲取：Electron 效能天花板、JavaScript 限制、Rust 多執行緒優勢、GPUI 自研過程 |
| 從 zed.dev/blog/zed-decoded-rope-sumtree 獲取資料結構詳情 | 理解 SumTree/Rope 的核心實作與效能特性 | 掌握 O(log N) 多維度索引、Arc 快照、cursur 機制的細節 | 獲取：TextSummary 結構、cursor 沿維度搜尋、20+ 處 SumTree 使用 |
| 從 zed.dev/ai 獲取 AI 功能詳情 | 了解 Agentic Editing、ACP、MCP、Edit Prediction 的細節 | 掌握 AI 功能的技術架構與運作方式 | 獲取：Agent Panel 工作流、Parallel Agents、ACP 開放協定、Zeta2 模型特性 |
| 從 zed.dev/blog/zed-1-0 獲取 1.0 里程碑資訊 | 了解 Zed 目前的成熟度、發佈狀態與未來方向 | 掌握 Zed 的版本現狀與路線圖 | 獲取：2026/4/29 發佈 v1.0、DeltaDB 開發中、Zed for Business 推出 |
| 從 zed.dev/edit-prediction 獲取 Zeta2 詳情 | 了解編輯預測模型的技術細節 | 掌握 Zeta2 的訓練資料、評估方式、與 LSP 的整合方式 | 獲取：diff-aware metrics、從真實編輯中訓練、支援多 provider |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 所有資訊來源均已取得 | 對照 AGENTS.md 的要求，檢查是否涵蓋：問題描述、背景、核心機制、替代方案 | 已涵蓋：zed.dev 官網、docs、GitHub repo、部落格技術文章 (3 篇深度文章)、AI 產品頁面、Edit Prediction 頁面 |
| DA 表替代技術覆蓋 | 條列至少 4 個同級/替代方案 | 已列出 VS Code、Cursor、IntelliJ IDEA、Neovim 共 4 個替代方案，含 DA 表 |
| 輸出目錄存在 | 檢查 output/ 與 learning-log/ 目錄 | 目錄已存在，檔案已寫入 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| DA 表替代方案選擇 | 1) VS Code, 2) Cursor, 3) IntelliJ IDEA, 4) Neovim, 5) Sublime Text, 6) Helix, 7) Fleet | VS Code、Cursor、IntelliJ IDEA、Neovim | 這四個方案在同級編輯器市場中佔據不同定位（Electron 生態、AI 原生 fork、JVM 原生、終端機原生），能最完整涵蓋不同的技術切入點 |
| 技術深度文章選擇 | zed.dev 部落格有多篇 Zed Decoded 系列文章 | We Have to Start Over + Rope & SumTree + Zed is 1.0 | 這三篇涵蓋了 Zed 最核心的技術決策：為什麼重寫、核心資料結構如何設計、目前成熟度 |
| AI 功能頁面 vs 文件頁面 | 1) zed.dev/ai 產品頁, 2) zed.dev/docs/ai/overview | 選擇 zed.dev/ai 產品頁 + Edit Prediction 頁面 | 產品頁面提供更高層次的架構概述與使用者面向的描述，適合分析報告的定位 |
