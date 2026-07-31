# 4. React forms done right

**Source**: https://reactdigest.net/newsletters/2330-react-forms-done-right
**Author**: Vu Nguyen (主題) / React Digest #567
**Date**: 2026-07-26
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

本篇為 React Digest 週報，集結 5 篇文章，主題圍繞「React 表單與狀態管理的正確心智模型」。各自解決：

| 文章 | 解決的問題 |
|------|-----------|
| **React forms done right**（Vu Nguyen） | 表單被誤以為只是 UI，實為驗證+非同步+無障礙+伺服器往返交疊的狀態問題；缺統一原型 |
| **Props, composers, and providers**（Maxime Grébauval） | props 鑽過深、單元件負擔過重、每變體新增一 prop 的失控 |
| **The absolute state of management**（Alex Russell） | Redux/Apollo 被誤稱「state management」，實為薄資料快取；即時協作場景崩潰 |
| **Invoker popover commands**（Sergio Xalambrí） | 用 React state 管理選單開關導致樣板碼過多 |
| **React2Shell（CVSS 10.0）**（Durgesh Pawar） | RSC Flight protocol 反序列化 sink 可被遠端程式碼執行 |

對使用者（Rails + React 全端、即將轉管理者）最相關：表單原型選型、元件組合決策、RSC 資安。

## 2. 這個問題為什麼會發生?(背景)

1. **React 19 server actions 使「server-first 表單」復興**，但生態仍停留在 client-side library 預設（react-hook-form、Formik、TanStack Form）
2. **元件組合缺乏漸進決策框架**：開發者要嘛 under-engineer（純 props 鑽孔）要嘛 over-engineer（一開始就 compound component），缺「痛點驅動升階」的判準
3. **「state management」詞彙被行銷綁架**：Redux/Apollo 實為資料快取而非真正的狀態管理，導致開發者在即時協作場景誤用，直到碰壁才尋找 CRDT
4. **Popover API / Invoker Commands 等瀏覽器原生 API 成熟**，但 React 生態仍慣性依賴狀態驅動
5. **RSC Flight protocol 為效能而生，但引入序列化 sink**：開發者對此攻擊面認知不足，CVSS 10.0 漏洞「React2Shell」浮現

推測背景：React Digest 編輯刻意把「正確心智模型」（前 3 篇）與「原生 API 回歸」「資安」編排在一起，反映 2026 年 React 社群的「去狀態化、回歸平台、正視 RSC 風險」基調。

## 3. 這個技術/政策是如何解決該問題的?

### 表單三原型（Vu Nguyen）
```
需求強度
├── 輕量 → React 19 server action form（原生，無 library）
├── 多步 wizard → TanStack Form（型別+驗證+非同步整合）
└── 高效能可編輯表格 → 客製化虛擬化 + 細粒度狀態
```
核心：依需求強度選型，避免一律套重型 library。

### 組合模式漸進升階（Maxime）
| 階段 | 觸發痛點 | 手法 |
|------|---------|------|
| 1 | 起步 | 純 props |
| 2 | shape 變多 | compound component |
| 3 | 同 UI 需多來源資料 | Composer + Provider |
| 4 | 狀態跨邊界 | 共享契約後的 state lift |
「每升一階付出間接成本，只在真痛點出現時才升」——可量化的決策框架。

### 真正的 state management（Alex Russell）
- Redux/Apollo 是「無查詢、無持久化、無衝突解決的薄快取」
- 即時協作正解為 **CRDT + sync engine**（如 Yjs、Automerge、Liveblocks）
- 開發者常在「加即時協作」那一刻才發現既有方案不夠

### Invoker Popover Commands（Sergio）
- 用瀏覽器 Popover API + `command` 屬性，免去 React state 開關
- TS 支援、基本樣式齊備；適合簡單選單，複雜情境才上 library

### React2Shell 防禦（Durgesh）
- Flight protocol 反序列化 sink 可被攻擊者利用導致 RCE
- 防禦排序：嚴格 schema 驗證 → CSRF hardening → 輸出 sanitize

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 領域 | 替代方案 | 與本文作法對比 |
|------|---------|--------------|
| 表單 | react-hook-form、Formik、Conform、Zod-first | TanStack Form 型別與非同步整合更現代；React 19 server action 適合無複雜客戶端驗證場景 |
| 組合模式 | Headless UI、Radix、shadcn/ui | 本文給「升階判準」，這些 library 給「成品元件」——需先有判準再選 library |
| 即時協作 | Yjs、Automerge、Liveblocks、Replicache | CRDT 系為 Alex Russell 指定的正解 |
| 選單 | Radix Popover、Headless UI Menu | 原生 Popover API + Invoker 在簡單場景更輕 |
| RSC 資安 | tRPC（型別安全 RPC）、自接 JSON-RPC + Zod | Flight protocol 為 RSC 專屬，需獨立防禦 |

**思考方式啟發**：
- **痛點驅動升階**（Maxime 模式）對使用者即將任管理者的最大價值：提供「何時引入抽象」的量化判準，避免團隊過早抽象或永遠不抽象。可直接套用於 K8s CRD、MCP server、Spring AI adapter 等學習線的決策
- **「詞彙被行銷綁架」的警覺**（Alex Russell 點出 Redux/Apollo 命名問題）——審技術選型時，先釐清工具真實能力而非名稱
- **「回歸平台」趨勢**：Popover API、CSS :has()、Container Queries 等，2026 年瀏覽器原生能力逐步取代 React utility——使用者 React 工作中可主動評估「這功能能否不裝 library」

**行動建議**：
1. 在 AxrossRecipe 既有 React 表單中，挑一個簡單場景改寫為 React 19 server action form，對比 react-hook-form 寫法
2. 將 Maxime 的「升階判準表」整理為團隊 code review checklist，作為管理者上任後的具體工具
3. 追蹤 React2Shell 後續修補進度，若團隊使用 RSC 需排入安全升級時程
4. CRDT 方面以 Yjs + 一個共筆 demo 起步，理解 sync engine 與 Redux 快取的根本差異