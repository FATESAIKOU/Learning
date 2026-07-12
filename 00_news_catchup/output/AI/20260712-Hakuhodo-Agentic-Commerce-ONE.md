# 03. 博報堂、エージェンティックコマース領域の統合ソリューションを始動

**Source**: https://markezine.jp/news/detail/77149
**Author**: MarkeZine編集部
**Date**: 2026-07-10
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

博報堂推出的「Agentic Commerce ONE」解決的是 **企業在 AI Agent 主導的商務時代的準備不足問題**。

Agentic Commerce（エージェンティックコマース）指 AI agent 代替消費者執行從「資訊搜尋 → 商品比較 → 購買決策 → 支付完成」的完整購物流程。對企業而言，這意味著：

| 傳統商務 | Agentic Commerce |
|---------|-----------------|
| 消費者自己搜尋、比較、下單 | AI agent 代理執行全流程 |
| 品牌對「人」溝通 | 品牌對「AI agent」溝通 |
| 行銷漏斗針對人類決策路徑 | 需針對 agent 的 API/資料結構優化 |
| UX 設計針對人類感官 | 需設計 machine-readable 的產品資訊 |

企業面臨的核心問題：**當消費者的購物決策被 AI agent 代理時，品牌如何確保自己被選中？**

## 2. 這個問題為什麼會發生?(背景)

### 2.1 日本市場的 Agentic Commerce 趨勢

博報堂買物研究所的調查顯示：
- **4 人に 1 人**（25%）已在使用生成 AI 輔助購物
- **6 割**（60%）的消費者表示願意將最終購買判斷委託給 AI

這不是遙遠的未來趨勢，而是正在發生的消費行為轉變。

### 2.2 技術成熟度曲線

```
2023-2024: ChatGPT 普及 → 消費者習慣用 AI 詢問產品建議
    ↓
2025: AI agent 框架成熟 (OpenAI Agents SDK, LangGraph, CrewAI)
    ↓
2026: Agentic Commerce 從概念進入實作階段
    ├── AI 可串接電商 API 查詢價格/庫存
    ├── AI 可比較跨平台商品規格
    └── AI 可執行支付（需消費者最終授權）
```

### 2.3 企業的準備鴻溝

GiftX 調查指出：**AI 利用の約 7 割は「チャット止まり」、AI エージェント化に到達は約 1 割**。多數企業的 AI 應用仍停留在「用 ChatGPT 寫文案」的層次，尚未準備好讓自己的產品/服務被 AI agent 發現、評估、選擇。

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 Agentic Commerce ONE 架構

博報堂將集團內商務領域的專業人才與知識整合為一站式解決方案：

```
Agentic Commerce ONE
│
├── 戦略策定 (Strategy)
│   ├── 品牌在 agentic commerce 時代的定位
│   ├── 目標 agent 平台選擇 (ChatGPT, Claude, Gemini...)
│   └── 競爭分析
│
├── 実装 (Implementation)
│   ├── 產品資料結構化 (structured data for AI agents)
│   ├── API 整合 (讓 agent 可查詢庫存/價格/規格)
│   ├── AI Optimization (AIO) — 針對 AI agent 的搜尋優化
│   └── データ基盤構築
│
└── 運用 (Operations)
    ├── 監控 agent 管道的流量與轉換
    ├── 持續優化產品資訊
    └── ガバナンス (治理) — 確保品牌一致性
```

### 3.2 第一彈：Agentic Commerce 診斷

首個落地服務是 **「エージェンティックコマース診断」**，從兩個維度評估企業準備度：

| 評估維度 | 具體項目 |
|---------|---------|
| **ビジネス視点** (商業視角) | 品牌戰略、治理機制、運營體制 |
| **テクノロジー視点** (技術視角) | 資料基礎架構、AI 整合度、AIO (AI Optimization) |

診斷後輸出 **優先行動清單**，讓企業知道從何處開始準備。

### 3.3 博報堂的獨特優勢

博報堂作為日本最大廣告代理集團之一，擁有：
- **生活者データ**：長期積累的消費者行為資料，可訓練 agent 理解日本消費者偏好
- **ブランド戦略知見**：數十年品牌建立經驗，可轉化為 agent 時代的品牌溝通策略
- **集團內跨領域人才**：媒體、數據、創意、技術人才可在 Agentic Commerce ONE 框架下協作

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

### 4.1 全球 Agentic Commerce 生態對照

| 方案/趨勢 | 提供者 | 焦點 | 與博報堂方案的差異 |
|-----------|--------|------|-------------------|
| **GEO (Generative Engine Optimization)** | 各 SEO 工具商 | 針對 AI 搜尋引擎的內容優化 | 偏技術面，缺乏品牌戰略層 |
| **OpenAI ChatGPT Plugins / Actions** | OpenAI | 讓服務接入 ChatGPT | 平台特定，非跨 agent 策略 |
| **Google AI Overviews 對應** | Google | 針對 Google 搜尋的 AI 摘要優化 | 僅限 Google 生態 |
| **Amazon Rufus** | Amazon | Amazon 內部的 AI 購物助手 | 平台封閉，品牌無法控制 |
| **Agentic Commerce ONE** | 博報堂 | 跨平台 agentic commerce 戰略到執行 | 日本市場特化 + 品牌戰略 + 技術實作整合 |

### 4.2 AI Optimization (AIO) vs SEO 的範式轉移

| | SEO (傳統) | AIO (Agentic Commerce) |
|---|---|---|
| 目標對象 | 搜尋引擎爬蟲 | AI agent 的推理引擎 |
| 優化標的 | 關鍵字密度、反向連結、meta tags | 結構化資料、API 可及性、產品屬性完整性 |
| 成功指標 | 搜尋排名、點擊率 | Agent 選擇率、agent 媒介轉換率 |
| 內容形式 | HTML 網頁 | JSON-LD, Schema.org, API response |

### 4.3 對用戶的意義

對在 Softbank AxrossRecipe 的技術管理者而言：

1. **Agentic Commerce 是 AI agent 趨勢的商業化落地**：與用戶正在學習的 MCP、Spring AI 直接相關——這些技術正是 agent 與外部服務互動的基礎設施
2. **AIO 是新興專業領域**：類似 2010 年代的 SEO 爆發，AIO 將成為未來 2-3 年的高需求技能
3. **Softbank 集團的潛在應用**：Softbank 旗下有 PayPay（支付）、Yahoo! Japan（電商/搜尋），agentic commerce 對這些業務有直接影響
4. **管理職視角**：理解 agentic commerce 的商業邏輯比理解技術細節更重要——這是與事業部門溝通的橋樑

### 4.4 趨勢判斷

博報堂此舉代表日本廣告/行銷產業正式承認：**未來的消費者不是「人」，而是「人的 AI agent」**。品牌溝通需要從「打動人心」擴展到「讓 AI agent 能正確理解並推薦」。這不是取代傳統行銷，而是新增一個技術密集型溝通管道。

---

*字數: ~1,100*
