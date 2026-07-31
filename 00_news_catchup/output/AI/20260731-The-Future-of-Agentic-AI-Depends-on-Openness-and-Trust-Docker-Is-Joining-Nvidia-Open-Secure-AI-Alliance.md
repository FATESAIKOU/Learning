# 3. The Future of Agentic AI Depends on Openness and Trust. That's Why Docker Is Joining Nvidia's Open Secure AI Alliance.

**Source**: https://www.docker.com/blog/docker-joins-nvidia-open-secure-ai-alliance/
**Author**: Tushar Jain
**Date**: 2026-07-30
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

解決「Agentic AI 缺乏信任基礎,企業不敢將 agent 放到業務核心」的問題。具體而言:

| 痛點 | 說明 |
|------|------|
| 智力過剩、信任不足 | 業界已確認 AI agent 能改造軟體開發,但不敢把 agent 放到業務中樞 |
| 廠商綁定風險 | 選模型即選架構,換模型要重寫應用、重思治理 |
| 治理真空 | 單一公司無法獨力建立安全/治理/信任框架 |

Docker 加入由 NVIDIA 主導的 **Open Secure AI Alliance**,目標是建立開放、跨廠商的信任基礎:讓 agent 的執行環境(runtime)、身分(identity)、治理(governance)、安全(security)形成可互通的開放標準。

## 2. 這個問題為什麼會發生?(背景)

### Agentic AI 的成熟拐點

過去數月,業界對話焦點已從「AI agent 能不能改造軟體開發」轉向「我們能否信任這些系統、能否安全置於業務核心」。這代表 agent 的能力問題已大致解決,信任問題成為下一階段的瓶頸。

### 信任的來源分裂

作者提出關鍵論點:**智力來自模型,信任來自圍繞模型的 runtime、身分、治理與安全**。這兩者分屬不同層次:

- 模型層:OpenAI、Anthropic、開源權重模型—提供「能力」
- 環境層:容器、沙箱、身分驗證、稽核日誌、權限邊界—提供「可信賴性」

當產業只聚焦模型能力時,環境層的治理碎片化,企業無從評估 agent 行為的可預測性。

### 開放權重模型的策略地位

幾乎所有 Docker 接觸的客戶都已把開放權重(open-weight)模型納入核心策略。客戶需求是:能在開源與前沿模型間**無縫路由**,依任務選模型,而不必每次重寫應用或犧牲治理/安全。

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 開放聯盟模式

| 面向 | 做法 |
|------|------|
| 組織 | Docker 加入 NVIDIA 主導的 Open Secure AI Alliance |
| 目標 | 建構 agent 執行環境所需的安全、治理、信任框架 |
| 原則 | 開放生態、共享責任—單一公司無法獨力建立信任 |
| 延伸 | 信任必須從模型層延伸到 agent 執行環境 |

### 3.2 Docker 的容器傳統與 agent 時代對應

Docker 以容器生態贏得 2000 萬開發者信任,其核心信念是「開發者在有選擇自由時表現最好」。此信念直接對應 agent 時代:

- **容器時代**:讓應用跨環境可攜 → **agent 時代**:讓 agent 在受控環境中執行
- **開放權重 + 前沿模型路由**:客戶選對模型做對的事,不必重寫架構、不必犧牲治理

### 3.3 信任的技術內涵(推測:從 Docker 近期系列文章推導)

結合 Docker 同期發布的相關文章,可推測 Open Secure AI Alliance 的信任框架涵蓋:

| 層面 | 推測對應技術 |
|------|-------------|
| Runtime 隔離 | Docker Sandboxes—隔離 agent,防止祕密外洩(對應「Coding Agent Horror Stories」篇) |
| 治理 | Guardrails 而非猜測—企業安全領袖共識,治理不能拖慢開發者 |
| 身分/權限 | Agent 的身分邊界、可執行動作白名單 |
| 開放互通 | 開放權重與前沿模型間的路由標準 |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 定位 | 與本聯盟差異 |
|------|------|-------------|
| **MCP(Model Context Protocol)** | 用戶學習中,Anthropic 主導的模型上下文協定 | MCP 解決「模型如何連接外部工具/資料」,聯盟解決「agent 在何種可信環境執行」—互補而非競爭 |
| **OpenAI Confident AI / AI Safety 研究軌道** | 前沿實驗室自建安全框架 | 廠商內部,非開放跨廠 |
| **OWASP AI Security / NIST AI RMF** | 標準組織的 AI 風險框架 | 偏政策/合規,缺乏 runtime 實作 |
| **K8s + NetworkPolicy + OPA** | 雲原生隔離與策略 | 已成熟,但未針對 agent 行為模式特化 |
| **WASM sandbox / Firecracker microVM** | 輕量執行隔離 | 技術可被聯盟採納為 runtime 基礎 |

### 思考方式:智力 vs. 信任的分層治理

本篇核心思想值得內化為架構判準:**評估 AI 系統時,把「能力」與「可信賴性」分開評估**。一個能力強但無信任框架的 agent,在企業落地時的風險遠高於能力中等但治理完備者。

### 對用戶情境的對照

- **GCP/GKE 環境**:用戶團隊在 GKE 上運行,容器隔離與 NetworkPolicy 是現成的 agent runtime 基礎,可直接對應聯盟訴求
- **即將轉管理者**:評估團隊導入 agent 時,應要求「agent 能做什麼/不能做什麼」的白名單與稽核日誌—這正是信任框架的實務落地
- **Cursor+Claude 探索**:開發端 agent 也需信任邊界(祕密隔離、程式碼外洩防護),Docker Sandbox 思路可借鏡
- **亞太觀點**:NVIDIA 主導的開放聯盟、日本企業(如 avatarin)採用 OpenAI,顯示亞太在 agent 治理上跟隨開放標準而非自建封閉體系