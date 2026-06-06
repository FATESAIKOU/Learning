# OpenDesign-C1-分析意圖與產出學習計畫

## 狀況理解

使用者已完成 OpenDesign 技術的「基礎認知 catchup」（見 `00_general_tech/output/2026-06-06-OpenDesign.md`），現在要在 `01_mvps/` 目錄下進行實作學習。目標：

1. 跑通完整 OpenDesign 流程，建立使用時的心智模型
2. 了解 video design 的能力邊界，以及未來公司內導入 Figma 設計流時 OpenDesign 的建構方式
3. 最終在 web chat 上做 vibe design，內部用 opencode（已配置 deepseek-v4-pro via Ollama Cloud）

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md | 確認任務規範與互動格式 | 理解三階段流程與輸出物規範 | 已讀取，格式明確 |
| 讀取既有 OpenDesign 技術報告 | 確認既有的背景知識 | 避免重複產出相同的技術分析 | 報告完整，涵蓋架構、adapter、skill system、安裝指引 |
| 檢查 opencode 版本 | 確認 agent 可用性 | v1.16.2 | 已確認可用 |
| 檢查 Node.js 版本 | 確認 daemon 環境 | v24.15.0 | 已確認符合要求（~24） |
| 檢查 pnpm / npx / od | 確認建置工具與 CLI 狀態 | 應有 pnpm~10.33, od 未安裝 | pnpm 未安裝（asdf 無對應版本）；od 未安裝（/usr/bin/od 是 macOS octal dump） |
| 讀取 GitHub README | 取得最新版本資訊 | v0.10.0 最新狀態 | 21+ agent、150+ design systems、261 plugins、支援 opencode |
| 讀取 QUICKSTART.md | 取得最準確的安裝與啟動指引 | 四種安裝方式、環境需求 | pnpm 10.33.x + corepack、Desktop App / Docker / source 三種方式 |
| 建立 output 目錄 | 準備產出目錄 | `output/2026-06-06-OpenDesign/` | 已建立 |
| 產出 LEARNING-PLAN.md | 步驟二的必要產出 | 含技術分析、AI Prompt、Todo Checklist | 已寫入，60 分鐘 4 個 Phase 共 10 步驟 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 目錄結構 | output 目錄存在且含 LEARNING-PLAN.md | 通過 |
| 環境就緒度 | opencode 可用、Node ~24 | 通過 |
| 環境缺項 | pnpm 未安裝、od 未安裝 | 待處理（即 Phase A） |
| 學習計畫完整性 | 4 Phase × 10 steps，含驗證標準 | 通過 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 安裝方式 | A: Desktop App（推薦）、B: CLI 一鍵安裝、C: 從原始碼執行 | Desktop App (A) | 使用者目標是建立心智模型，不是改原始碼；Desktop App 零設定，含 web UI + daemon + 內建 skills/design-systems |
| 是否需要先安裝 pnpm | A: 安裝 pnpm、B: 跳過 | 安裝 pnpm（A1） | 雖然 Desktop App 不需要 pnpm，但 (a) 學習路徑上備用 (b) 公司導入場景可能需要從 source 客製 |
| agent 選擇 | opencode（已配置）、其他 CLI | opencode | 使用者明確指定用 opencode + deepseek-v4-pro，且 opencode v1.16.2 已可用 |
| skill 選擇 | web-prototype、saas-landing、dashboard 等 | web-prototype（預設） | 快速驗證流程的最短路徑，也是 OD 預設的 prototype mode skill |
