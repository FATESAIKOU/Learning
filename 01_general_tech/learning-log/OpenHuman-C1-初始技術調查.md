# OpenHuman-C1-初始技術調查

## 狀況理解
使用者要求調查 OpenHuman（https://github.com/tinyhumansai/openhuman）這個技術。此技術為一個開源 AI agent harness，宣稱提供「個人 AI 超級智能」，核心特色包含 Memory Tree、118+ 第三方整合、Auto-fetch、TokenJuice 壓縮、模型路由等。需要按照 AGENT.md 規範產出分析報告與過程報告。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 GitHub repo README | 取得專案基本定位、功能列表、安裝方式、競品比較 | 理解 OpenHuman 的核心價值主張與使用者面向 | 取得完整 README，含功能說明、安裝方式、vs 競品對照表、技術堆疊概覽 |
| 讀取 package.json | 了解前端技術堆疊、建構工具、依賴 | 確認使用框架與開發工具鏈 | pnpm + Tauri v2 + React + TypeScript，前端為 app/ 目錄下的 monorepo |
| 讀取 Cargo.toml | 了解 Rust core 的依賴、架構模組、功能開關 | 確認 Rust 端的功能邊界與技術選型 | 大量依賴暴露核心設計意圖：rusqlite (SQLite)、axum (HTTP server)、whisper-rs (STT)、tokio-tungstenite (WebSocket)、tokenjuice 整合、matrix-sdk、whatsapp-rust 等 |
| 讀取 GitBook 文檔首頁 | 了解官方文檔結構與核心概念介紹 | 取得完整功能說明架構 | 取得 overview，確認 Memory Tree、TokenJuice、Auto-fetch、Model Routing 為核心子系統 |
| 讀取 Memory Tree 文檔 | 了解核心記憶管線的設計細節 | 取得 pipeline 架構、三種樹結構、Leaf lifecycle、Job queue、Worker pool 設計 | 取得完整 pipeline 說明，含狀態機、佇列類型、排程器、工作池設計 |
| 讀取 TokenJuice 文檔 | 了解 token 壓縮機制 | 取得三層 rule overlay 架構、壓縮 pipeline 位置 | 取得完整說明，含 Builtin/User/Project 三層規則合併、工具輸出壓縮流程圖 |
| 讀取 Auto-fetch 文檔 | 了解自動資料同步機制 | 取得排程週期、state 管理、per-provider 配置 | 取得 20 分鐘 tick 設計、sync_state 結構、budget 上限、錯誤處理 |
| 讀取 Obsidian Wiki 文檔 | 了解 Markdown vault 設計與與 Obsidian 整合 | 取得 vault 目錄結構、與 Memory Tree 的關係 | 取得 vault 路徑結構、Obsidian 整合方式、手動編輯再攝取機制 |
| 讀取 Model Routing 文檔 | 了解模型路由機制 | 取得 hint 表、解析邏輯、配置階層 | 取得 Rust resolve 程式碼片段、5 種 hint、per-agent model pin |
| 讀取 Architecture 文檔 | 了解系統整體架構 | 取得 Tauri + Rust core + React 三層架構圖、資料流 | 取得 ASCII 架構圖、10 步驟資料流、隱私邊界 |
| 讀取 Native Tools 文檔 | 了解內建工具集 | 確認 agent 的工具能力範圍 | 取得 10 個工具家族列表（Web Search、Scraper、Coder、Browser、Cron、Voice、Memory、Integrations、Agent Coordination、System） |
| 讀取 Privacy & Security 文檔 | 了解隱私與安全設計 | 確認本地/雲端資料邊界、加密方案 | 取得明確的本地/後端邊界表、OS keyring 方案、TLS 傳輸、workspace scoping |
| 閱讀 agentmemory repo README | 取得替代方案細節用於 DA 表 | 了解 agentmemory 的核心設計、基準測試、整合方式 | 取得完整 README，含 R@5 95.2%、跨 agent MCP 整合、iii-engine 後端 |
| 閱讀 tokenjuice (vincentkoc) repo README | 了解 TokenJuice 的原始獨立專案 | 確認 OpenHuman 中 TokenJuice 的來源與設計哲學 | 取得 CLI 工具設計、多 host 整合、rule-driven 壓縮引擎 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 技術核心機制 | 檢查 Memory Tree pipeline、TokenJuice、Auto-fetch、Model Routing 的文檔完整性 | 四項核心機制均有獨立文檔頁面，包含架構圖、程式碼片段、配置方式 |
| 技術棧一致性 | 比較 README、Cargo.toml、package.json 中的技術宣告 | 一致：Rust + Tauri v2 + React + SQLite + pnpm |
| 替代方案資訊 | 從 README 比較表獲取 Claude Cowork、OpenClaw、Hermes 資訊，從 agentmemory repo 獲取詳細設計 | 資訊充足以構建 DA 表 |
| 文檔結構 | 檢查 GitBook 文檔的連結完整性 | 部分連結路徑與實際不符（如 `features/memory-tree` vs `features/obsidian-wiki/memory-tree.md`），但 404 頁面提供了正確路徑建議 |
| 授權與開源狀態 | 檢查 LICENSE 檔案與 README 宣告 | GPL-3.0，GitHub 公開 repo，29.6k stars，early beta 狀態 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 分析報告中核心技術的選取範圍 | 1. 僅寫 Memory Tree；2. 寫 Memory Tree + TokenJuice；3. 寫 OpenHuman 整體作為一個技術 | 3. 寫 OpenHuman 整體 | OpenHuman 的核心價值在於將多項機制疊加（Memory Tree + Auto-fetch + TokenJuice + Model Routing + OAuth Integrations），單看任一個子系統無法解釋它解決的問題全貌 |
| DA 表中競爭對手的選取 | 各種 AI agent/coding agent/memory layer 專案 | agentmemory、Mem0、Letta/MemGPT、Claude Cowork、OpenClaw、Hermes | 選取 README 已提及的競品（Claude Cowork、OpenClaw、Hermes），加上記憶領域的關鍵方案（agentmemory、Mem0、Letta），覆蓋「agent harness」與「記憶層」兩個維度 |
| 是否深入探索 Rust 原始碼 | 1. 深入 src/ 目錄結構；2. 維持文檔層級分析 | 2. 維持文檔層級分析 | Cargo.toml 的依賴列表與文檔已提供充分資訊回答 AGENT.md 指定的四個問題；原始碼層級分析在此階段非必要 |
| DA 表中 agentmemory 的定位 | 1. 作為競爭對手；2. 作為 OpenHuman 的互補後端 | 1. 作為競爭對手（但在報告中提及可作為 OpenHuman 後端） | agentmemory 本身是獨立的記憶產品，支援多 agent；但 OpenHuman 也可選擇使用 agentmemory 作為其 Memory 後端 |
