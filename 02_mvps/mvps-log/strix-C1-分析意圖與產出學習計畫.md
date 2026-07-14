# strix-C1-分析意圖與產出學習計畫

## 狀況理解

- 使用者想學習 AI 滲透測試工具 **Strix**（github.com/usestrix/strix），並實際用它對目標網站 **axross-recipe.com** 進行滲透測試。
- 使用者具備以下 AI 資源：
  - **Ollama Cloud**：Ollama 官方提供的雲端 LLM API（不需自建）
  - **Claude Pro**：可透過 Anthropic API 使用的 Claude 服務
- 使用者最終目標：產出一份滲透報告 + 理解 Strix 這類 AI 滲透工具的**用法與能力邊界**。
- 目標網站 axross-recipe.com 是 SoftBank 旗下的工程師食譜分享平台，包含：用戶註冊/登入、Markdown 編輯器、食譜發布/檢索、評論功能、付費方案（法人プラン）等功能。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 讀取 `02_mvps/` 目錄結構 | 理解專案根目錄現狀 | 確認 output/ 與 mvps-log/ 存在 | 兩目錄均存在且為空 |
| 讀取 `AGENTS.md` | 理解 Agent 行為規範與三步驟流程 | 確認格式要求、語言限制、產出物規範 | 完整讀取 83 行，確認所有規則 |
| 搜尋 Strix GitHub README | 取得 Strix 核心架構、功能、安裝方式 | 理解工具能做什麼、怎麼用 | 取得完整資訊：CLI 工具、Docker 沙箱、LiteLLM 支援、多 Agent、3 種掃描模式 |
| 搜尋 axross-recipe.com 首頁 | 了解目標網站的功能與結構 | 確認是否有註冊/登入、API、表單等攻擊面 | 確認包含：用戶註冊/登入、Markdown 編輯、食譜發布、搜尋、評論、付費方案 |
| 搜尋 Strix LLM Providers 文件 | 確認如何用 Anthropic API 與 Ollama 配置 | 取得正確的 `STRIX_LLM` 格式 | `anthropic/claude-sonnet-4-6` 格式可用；Ollama 需設 `LLM_API_BASE` |
| 搜尋 Strix Local Models 文件 | 確認 Ollama Cloud 可行性 | 判斷 Ollama Cloud 是否適合 Strix agentic 任務 | 文件指出本地模型（含 Ollama）在 agentic 任務上能力不足，推薦雲端高階模型 |
| 搜尋 Strix CLI Reference | 取得完整 CLI 參數 | 確認 headless 模式、scan mode、budget 控制 | 確認 `-n` 非互動模式、`--scan-mode` 三種深度、`--max-budget-usd` |
| 搜尋 Strix Scan Modes | 確認三種模式的差異與適用場景 | 正確選擇 quick/standard/deep | quick=分鐘級、standard=30-60分、deep=1-4小時（預設） |
| 建立目錄 `output/2026-07-14-strix/` | 準備學習計畫與後續產出物存放位置 | 目錄建立成功 | 成功 |
| 撰寫 `LEARNING-PLAN.md` | 產出包含技術分析、AI Prompt、Checklist 的完整計畫 | 依照 AGENTS.md 格式要求完成 | 成功寫入，含 9 步驟的 Checklist |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 目錄結構 | `ls output/2026-07-14-strix/` | `LEARNING-PLAN.md` 存在 |
| 技術分析完整性 | 包含「解決什麼問題」「為什麼發生」「如何解決」三點 | 已填寫完畢 |
| AI Prompt 可用性 | Prompt 可直接貼給其他 AI 使用 | 包含安裝、配置、分析報告的完整情境 |
| Checklist 覆蓋範圍 | 從環境建置到最終報告的完整流程 | 9 步驟涵蓋 Phase 1-4 |
| 產出物驗證標準 | 每一步皆有明確驗證方式 | 已定義執行指令或產出檔案 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 主要 LLM Provider | ① Ollama Cloud ② Anthropic Claude API | 選擇 ② Anthropic Claude API 為主、Ollama Cloud 為備用 | Strix 官方文件明確指出本地/小型模型在 agentic 任務（工具使用、多步規劃、自我修正）上能力不足；Claude Sonnet 4.6 是官方推薦的三大模型之一 |
| 掃描深度策略 | ① 只跑 Quick ② Quick + Deep 兩次掃描對比 | 選擇 ② Quick + Deep 兩次 | Quick 可快速驗證工具是否正常運作（5分鐘），Deep 才是真正產出有價值報告的模式；兩次結果對比有助於理解「掃描深度」的實際差異 |
| 是否對目標網站進行手動 Recon | ① 直接掃描 ② 先手動收集資訊再掃描 | 選擇 ② 先手動 Recon | 了解目標網站的技術棧與攻擊面有助於對比 AI 的自動化偵查結果，評估 Strix 的偵查能力 |
| 掃描報告格式 | ① 僅記錄原始輸出 ② 結構化報告（含 Executive Summary、CVSS、修復建議） | 選擇 ② 結構化報告 | 使用者目標之一是「理解功能邊界」，結構化報告便於事後對比 Strix 的輸出品質 vs 專業人工報告 |
| 能力邊界分析獨立成檔 | ① 合併在滲透報告中 ② 獨立成 `capability-boundary.md` | 選擇 ② 獨立成檔 | 使用者明確表示最終目標之一為「理解 Strix 的能力邊界」，獨立文件便於聚焦分析 |
