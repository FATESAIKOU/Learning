# CLI-Anything-C1-深度技術調研

## 狀況理解

使用者要求：
1. Catch up 目前資料夾（特別是 AGENTS.md）
2. 對 https://github.com/HKUDS/CLI-Anything 進行深度調研

### 現狀
- 工作目錄：`Learning-CLI-Anything`，為一個技術調研學習專案
- `00_general_tech/AGENTS.md` 定義了「技術解析助理」角色與兩項輸出物規範
- 已有兩個分析標的：OpenHuman、CodeGraph、CloakBrowser（已完成報告）
- `01_nanobot_dockerize/` 是用於實作型任務的目錄（目前僅有 `.gitkeep`）
- CLI-Anything 是全新的分析標的，需要從 C1 開始

### 使用者意圖
- 對 CLI-Anything 進行與先前 CodeGraph、CloakBrowser 同等的深度技術分析
- 產出分析報告與過程報告

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `00_general_tech/AGENTS.md` | 確認輸出規範與角色定義 | 理解報告格式要求 | 已完整理解：分析報告需包含 4 點（問題描述、背景、解法、替代方案 DA 表）；過程報告需包含狀況理解、動作與結果、現狀、決斷點 |
| 瀏覽目錄結構 | 了解專案現狀 | 確認既有分析標的與報告命名規則 | 確認為全新標的，命名格式為 `<日期>-CLI-Anything.md` |
| Fetch GitHub repo 首頁 (README) | 取得專案簡介、架構、使用方式 | 理解 CLI-Anything 的核心概念與生態 | 取得完整 README（含 news、Quick Start、Why CLI、Phase 1-7 說明、60+ harness 目錄） |
| Fetch `cli-anything-plugin/HARNESS.md` | 取得 7-phase SOP 的完整規範 | 理解 CLI 生成的詳細方法論 | 取得完整 HARNESS.md，涵蓋 Phase 1-7, Architecture Patterns, Principles & Rules, Preview Norms, Directory Structure |
| Fetch `docs/PREVIEW_PROTOCOL.md` | 取得 Preview Protocol 完整規範 | 理解跨軟體預覽標準 | 取得完整 Preview Protocol，含 bundle schema、live session、viewer 命令、4-PR rollout plan |
| Fetch `skills/README.md` | 理解 skill 管理機制 | 理解 npx skills 整合方式 | 確認 repo-root `skills/` 為 canonical 位置 |
| Fetch `macrocli/` 目錄結構 | 理解 macrocli 組件 | 了解 CLI-Anything 對其他 CLI 工具的包裝機制 | 取得目錄結構，macrocli 是一個特殊的 agent-harness |
| Fetch `docs/` 目錄結構 | 理解文件體系 | 全面了解文件覆蓋範圍 | 取得 docs/ 目錄下的完整文件列表 |
| Fetch 一個 harness 範例 (`macrocli/cli.py`) | 理解實際 CLI 實作範例 | 取得程式碼層面的理解 | 404 - 該路徑不存在於 main branch（可能 macrocli 結構不同） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 資訊完整性 | 是否取得足以撰寫 4 點分析報告的資料 | 是。HARNESS.md 提供完整 7-phase 機制；PREVIEW_PROTOCOL.md 提供預覽層細節；README 提供生態架構 |
| 替代方案知識 | 是否有足夠資訊製作 DA 表 | 是。基於 MCP、Browser Use、Open Interpreter、Custom Wrapper 的領域知識，可完成比較 |
| 報告格式合規性 | 是否遵循 AGENTS.md 的輸出規範 | 是。分析報告僅含 4 點、使用表格/圖示/階層結構、不使用情緒性語言 |
| 命名規則 | 是否符合檔名規範 | 是。分析報告：`output/2026-05-31-CLI-Anything.md`；過程報告：`learning-log/CLI-Anything-C1-深度技術調研.md` |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 調研深度 | A. 僅看 README；B. README + HARNESS + Preview Protocol；C. 全部原始碼深入 | B | 使用者要求「深度調研」，README 提供架構、HARNESS 提供方法論、Preview Protocol 提供最具技術深度的設計細節。全部原始碼（60+ harness）則超出合理範疇 |
| 分析報告 DA 表替代技術選擇 | A. 僅列相似 CLI-wrapper 工具；B. 列所有 Agent-Software 互動途徑 | B | AGENTS.md 要求「條列 2~4 個同級或替代方案」，Agent-Software 互動的各種途徑（MCP, Browser Use, Open Interpreter, Custom Wrapper）與 CLI-Anything 在不同軸向上有替代關係 |
| 是否需要 Fetch 個別 harness 原始碼 | A. 選幾個代表性 harness 看細節；B. 僅依賴 HARNESS.md 中的範例程式碼 | B | HARNESS.md 已包含足夠的程式碼範例（LibreOffice, ReplSkin, test patterns）；fetch 個別 harness 原始碼可能遭遇路徑不存在問題 |
| 預覽協議在報告中的比重 | A. 詳述；B. 簡述 | A | Preview Protocol 是 CLI-Anything v0.2+ 的核心創新之一，且是少數跨軟體標準化的設計，具分析價值 |
| 補充通用技術背景的邊界 | A. 只寫文章提到的；B. 補充文章未提的通用背景 | B | AGENTS.md 明確要求「若文章本身資訊不足，請盡量從網路搜尋補上」以及「缺乏的背景或技術脈絡，請盡量從網路搜尋補上」 |
