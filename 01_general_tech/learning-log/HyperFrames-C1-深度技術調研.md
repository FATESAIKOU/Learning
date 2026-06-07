# HyperFrames-C1-深度技術調研

## 狀況理解

使用者要求：
1. 先 catchup 目前資料夾（特別是 AGENTS.md）
2. 深入調研 `https://github.com/heygen-com/hyperframes`

目前資料夾結構：
- `01_general_tech/AGENTS.md`：定義「技術解析助理」角色與輸出格式（分析報告 + 學習過程報告）
- `01_general_tech/output/`：已有 6 份歷史分析報告（CodeGraph, OpenHuman, CLI-Anything, CloakBrowser, EverOS, LingBot-Map）
- `01_general_tech/learning-log/`：已有 14 份學習過程報告
- `01_nanobot_dockerize/`：獨立資料夾，非本次目標

HyperFrames 是由 HeyGen 開源（Apache 2.0）的影片渲染框架，22.6k stars，核心訴求是「Write HTML, Render video, Built for agents」。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取根目錄與 `01_general_tech/AGENTS.md` | 理解專案結構與任務規則 | 確認 AGENTS.md 中的輸出格式與限制 | 已理解：需產出分析報告 + 學習過程報告，格式嚴格受限 |
| 擷取 GitHub repo 首頁 README | 取得專案的整體介紹與架構說明 | 理解 HyperFrames 是什麼、做什麼、怎麼用 | 已取得完整 README，含架構圖、使用方式、package 列表 |
| 擷取 AGENTS.md（repo 中的） | 理解 repo 的開發慣例與結構 | 取得 monorepo 結構、build/test/lint 命令、關鍵慣例 | 已取得：bun 作為 package manager, oxlint/oxfmt, composition 驗證規則 |
| 擷取 DESIGN.md | 理解品牌設計系統 | 取得色彩/字型/元件 pattern | 已取得完整設計系統定義 |
| 擷取 Quickstart 文件 | 理解快速入門流程 | 取得 init/preview/render 步驟與 HTML 範例 | 已取得：兩種上手方式（agent / 手動），最小 composition 範例 |
| 擷取 Compositions 概念文件 | 理解核心 composition 資料模型 | 取得 clip types, data-* 屬性, nested composition, variables | 已取得完整技術細節 |
| 擷取 @hyperframes/core API 文件 | 理解核心套件的型別與 API | 取得 parseHtml, lint, compiler, runtime, frame adapter | 已取得完整 API 文件 |
| 擷取 Rendering 指南 | 理解渲染管線、品質參數、GPU/Docker 模式 | 取得 local/docker 兩種模式、quality presets、workers 機制 | 已取得完整渲染參數說明 |
| 擷取 Frame Adapters 概念 | 理解動畫 runtime 整合機制 | 取得 adapter 介面定義、seek contract、支援的 runtime 列表 | 已取得 adapter v0 spec |
| 擷取 HyperFrames vs Remotion 對比 | 理解與最直接競品的差異 | 取得 agent 寫 HTML vs React 的實證差異、GSAP 時鐘問題 | 已取得詳細對比，含圖示說明 |
| 擷取 @hyperframes/engine API 文件 | 理解底層 capture 引擎機制 | 取得 BeginFrame API、seek contract、HDR APIs | 已取得完整引擎 API |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 報告格式合規性 | 對照 AGENTS.md 的四點格式要求 | 分析報告包含 4 個必要段落（問題、背景、解法、替代方案），格式符合 |
| DA 表完整性 | 確認有 2~4 個替代方案 | 提供 4 個替代方案：Remotion, Motion Canvas, Manim, After Effects |
| 技術深度 | 確認核心機制、架構圖、程式碼範例均有涵蓋 | 包含 composition 結構、rendering pipeline、frame adapter pattern |
| 資訊來源可靠性 | 資訊來自 GitHub repo 官方文件與 docs 站 | 所有資訊來自 heygen-com/hyperframes repo 與 hyperframes.heygen.com |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 報告深度範圍 | ① 僅 README 層級概述 ② 深入到每個 package 的 API ③ 涵蓋核心概念 + 架構 + 對比 | ③ 涵蓋核心概念 + 架構 + 對比 | 使用者要求「深入調研」，需要覆蓋 composition 模型、渲染機制、adapter pattern、與競品對比 |
| 替代方案選取 | ① 僅選 Remotion ② 選 4 個不同切入角度 | ② 選 4 個 | AGENTS.md 要求 2~4 個，4 個能更完整展現技術光譜（React / Canvas / Python / GUI） |
| 是否 clone repo | ① 直接 clone 到本地分析原始碼 ② 僅透過 web fetch 取得文件 | ② 僅透過 web fetch | 文件本身資訊量充足（README + docs + AGENTS.md + DESIGN.md + package docs），無需原始碼層級分析 |
| HDR/transparent 等進階功能是否納入 | ① 全部納入 ② 僅核心概念 | ② 僅核心概念 | 分析報告的主題是「技術解決什麼問題+怎麼做」，HDR 等屬於使用細節，不影響核心分析 |
