# Tolaria-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `refactoringhq/tolaria` 進行深度技術調研，已持有 README，需補充：
- docs/ARCHITECTURE.md、docs/ABSTRACTIONS.md、docs/GETTING-STARTED.md
- src/ 與 src-tauri/ 目錄結構
- mcp-server/ 目錄
- demo-vault-v2/ 目錄
- 網路上的技術分析與評論
- 核心問題、技術架構、關鍵設計決策
- 與 Obsidian / Notion / Logseq / Foam / Dendron 的對比

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 從 GitHub raw 取得 README.md | 確認已持有的 README 內容與最新版本一致 | 取得完整 README 作為分析基礎 | 成功取得，15.9k stars, 3,078 commits, 1,266 releases |
| 從 GitHub raw 取得 docs/ARCHITECTURE.md | 了解系統設計、技術棧、資料流 | 取得完整架構文檔 | 成功取得，包含 Tauri+React+TypeScript 架構、三層資料表示、不變量規則 |
| 從 GitHub raw 取得 docs/ABSTRACTIONS.md | 了解核心抽象與模型 | 取得 VaultEntry、SidebarSelection、Type 系統等核心型別定義 | 成功取得，包含完整資料模型、frontmatter 格式、Type document 機制 |
| 從 GitHub raw 取得 docs/GETTING-STARTED.md | 了解程式碼導航方式 | 取得程式碼庫導航指引 | 成功取得，包含目錄結構說明、開發環境設定 |
| 取得 src/ 目錄內容 | 了解前端架構 | 取得 React/TypeScript 前端模組清單 | 成功取得，包含 App.tsx、約 90 個 custom hooks、BlockNote/CodeMirror 雙編輯器 |
| 取得 src-tauri/ 目錄內容 | 了解 Rust 後端架構 | 取得 Rust 模組清單 | 成功取得，包含 vault/、frontmatter/、git/、search.rs、ai_agents.rs、mcp.rs |
| 取得 mcp-server/ 目錄內容 | 了解 MCP server 實作 | 取得 MCP tools 清單與傳輸層設計 | 成功取得，15 個 tools、stdio+WebSocket 雙傳輸層、自動註冊目標 |
| 取得 demo-vault-v2/ 目錄內容 | 了解示範 vault 結構 | 取得示範筆記與 type 定義 | 成功取得，包含多種 type 的示範筆記與 AGENTS.md |
| 搜尋網路評論與技術分析 | 補充社群觀點 | 取得外部評價 | 成功取得，Tolaria 定位為「AI agent 的結構化資料源」，與 Obsidian/Notion 的核心差異在於 MCP server + git 原生整合 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 架構完整性 | 對比 README 架構描述與實際目錄結構 | 一致：Tauri (Rust) + React (TypeScript) + MCP Server (Node.js) |
| Files-first 原則 | 閱讀 ARCHITECTURE.md 三層資料表示與不變量 | 確認：Disk-first writes、Optimistic UI with rollback、Cache is disposable、Filesystem wins |
| Types as lenses | 閱讀 ABSTRACTIONS.md Type 系統 | 確認：Type 由 frontmatter `type:` 決定，非資料夾位置；無必要欄位、無驗證；Type document 定義顯示屬性 |
| AI agent 整合 | 閱讀 ai_agents.rs 與 AGENTS.md 機制 | 確認：支援 6 種 CLI agent（Claude/Codex/OpenCode/Pi/Gemini/Kiro），Safe/Power User 雙模式，結構化 context snapshot |
| MCP server | 閱讀 mcp-server/ 目錄 | 確認：15 個 tools（讀取/寫入/UI 控制），stdio+WebSocket 雙傳輸層，自動註冊到 5 個目標設定檔 |
| Git 整合 | 閱讀 git/ 模組 | 確認：shell out 到系統 git CLI、AutoGit 閒置 checkpoint、Pulse View、conflict resolution |
| 競品對比 | 基於對 Obsidian/Notion/Logseq/Foam/Dendron 的已知資訊 | Tolaria 的核心差異化在於 MCP server + git 原生整合 + 多 CLI AI agent 支援 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 分析報告深度 | (A) 僅基於 README 撰寫 / (B) 深入原始碼與架構文檔 | (B) 深入原始碼與架構文檔 | AGENTS.md 要求「若文章本身資訊不足，請盡量從網路搜尋補上」，Tolaria 有完整的 docs/ 目錄可供深入分析 |
| 競品對比範圍 | (A) 僅 Obsidian / (B) Obsidian + Notion + Logseq + Foam/Dendron | (B) 完整 5 方案對比 | 需覆蓋不同 PKM 典範（本地檔案、雲端資料庫、outliner、VS Code 插件）以呈現 Tolaria 的差異化 |
| DA 表欄位 | (A) 簡化 4 欄 / (B) 完整 5 欄（技術名、技術解法、技術使用前提、技術使用副作用、技術使用預期效果） | (B) 完整 5 欄 | 遵循 AGENTS.md 規定的 DA 表格式 |
