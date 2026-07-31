# 06. オラクル Fusion Applications でAIエージェント型アプリを開発可能に

**Source**: https://it.impress.co.jp/articles/-/29639
**Author**: 日川佳三(IT Leaders編集部)
**Date**: 2026-07-31
**Category**: 政治經濟

## 1. 這個技術/政策解決什麼問題?

Oracle 於 2026/7/14 宣布在「Oracle Fusion Applications」(涵蓋 ERP/HCM/SCM/CX 四領域的雲端基幹業務應用套裝)中新增兩項 AI Agent 開發手段,解決企業導入 Agentic AI 的三個核心障礙:

| 障礙 | 解決方式 |
|------|----------|
| **獨立 AI 工具缺乏企業治理** | 在 Fusion Applications 內原生執行,繼承既有安全、治理、審批、稽核軌跡 |
| **No-code 與 Pro-code 之間斷層** | 同時提供「Agentic Applications Builder」(自然語言)與「AI Studio Skill」(連接 Claude Code 等外部 IDE) |
| **獨立 AI 應用需另設 Runtime** | 開發的應用直接操作 Fusion 的 business objects、workflow,無需額外 runtime |

核心價值主張:讓企業在不破壞既有治理架構的前提下,將「自律執行業務的 AI 應用」納入生產環境。

## 2. 這個問題為什麼會發生?(背景)

- **AI Agent 市場成熟但企業部署滯後**:多數企業 AI 仍停留在「對話助手」階段,Agentic AI(自律執行多步驟業務)進入生產困難,主因是治理、安全、與既有系統整合問題。
- **獨立 AI 工具的 Shadow AI 風險**:各部門自行導入 ChatGPT、獨立 Agent 平台,造成資料外洩、無審批軌跡、與基幹系統資料不一致。
- **Oracle Fusion 既有安裝基盤**:Fusion Applications 已是涵蓋財務、人事、供應鏈、客戶服務的完整基幹系統,Oracle 選擇在既有平台上疊加 AI Agent 能力,而非另建獨立產品。
- **AI Agent Studio 已運行中**:Oracle 先前已內嵌「Oracle AI Agent Studio for Fusion Applications」平台,多個 Agent 已在運行,本次是擴展開發手段而非從零開始。
- **競爭壓力**:微軟 Copilot、Salesforce Agentforce、SAP Joule 都在搶企業 Agent 平台市場,Oracle 需以「與基幹系統原生整合」差異化。

## 3. 這個技術/政策是如何解決該問題的?

| 功能 | 機制 |
|------|------|
| **Agentic Applications Builder** | 自然語言開發,生成多 Agent + 畫面 + workflow 的完整應用 |
| **AI Studio Skill** | 連接 Claude Code 等外部 IDE、版本管理、AI 編程工具,供開發者用 Pro-code 方式 |
| **原生執行** | 應用在 Fusion 內 native 運行,直接操作 business objects,不需外部 runtime |
| **治理繼承** | 安全、governance、審批流程、稽核軌跡自動繼承自 Fusion 既有框架 |
| **追加費用なし** | 對 Fusion 客戶與合作夥伴免費提供,降低採用門檻 |

預期應用場景(Oracle 設想):

```
Fusion Agentic Applications
  ├─ 財務決算迅速化(自動關帳流程)
  ├─ 債權回収改善(自動跟催、分級處理)
  └─ 供應鏈執行合理化(自動補貨、異常處理)
```

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 框架 | 機制 | 對比 |
|------|------|------|
| **Salesforce Agentforce** | 在 CRM 平台上建構 Agent,類似原生整合策略 | 競爭對手;覆蓋範圍限 CRM/服務 |
| **Microsoft Copilot Studio + Dynamics 365** | 與微軟生態深度整合 | 跨 ERP/CRM 但治理依賴 M365 Entra |
| **SAP Joule** | SAP S/4HANA 的 AI 副駕駛 | 與 Oracle 直接競爭,各佔 ERP 市場份額 |
| **獨立 Agent 平台(LangChain/LangGraph)** | 框架靈活,可跨後端 | 需企業自行建構治理,本事件示範風險高 |
| **Spring+AI(用戶學習中)** | 在 Spring 生態內整合 AI,程式碼可控 | 適合自建應用,需自建治理層 |
| **MCP(用戶學習中)** | 標準化 AI 與工具/資料來源介接 | 跨平台協議,可作為 Agent 與既有系統橋接 |

**對用戶的啟示**:

1. **企業 Agentic AI 的關鍵瓶頸是治理整合,不是模型能力**——AxrossRecipe(Ruby on Rails + React + GCP)若要導入 Agent,應優先思考如何與既有 Rails 應用的權限、審計、資料模型整合,而非單純選擇 Agent 框架。
2. **No-code + Pro-code 雙軌是設計模式**——Oracle 同時提供自然語言與 Claude Code 連接,反映企業內非技術與技術成員需並存協作。未來管理者可思考:AI 工具的選擇應兼顧兩種使用者的工作流。
3. **「追加費用なし」策略**——將 AI 能力內嵌於既有授權,降低採用阻力,是企業軟體市場的關鍵競爭手段。AxrossRecipe 內部孵化時,若採用既有雲服務(GCP)的 AI 能力而非另購,可降低成本與治理複雜度。
4. **Oracle 的「原生整合 vs. 獨立 AI 工具」對照**——與前一篇 Anthropic 隔離失靈事件對讀,更凸顯「在受治理環境內運行 AI」的重要性。獨立 Agent 平台的靈活性伴隨治理盲區。