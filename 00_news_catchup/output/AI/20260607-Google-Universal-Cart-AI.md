# 28. Google 検索やYouTubeから直接買える新機能 AIが自動でセール品探す (原文)

**Source**: https://digiday.jp/platforms/googles-latest-commerce-moves-deepen-the-battle-over-agentic-shopping/
**Author**: Kimeko McCoy(Digiday US),翻譯:英じゅんこ,編輯:京岡栄作
**Date**: 2026/06/05
**Category**: AI技術

## 1. 這個技術解決什麼問題?

本文報導 **Google「Universal Cart(通用購物車)」** 與其底層 **Universal Commerce Protocol(UCP)** 的策略佈局,解決的問題是:**在「代理型購物(agentic shopping)」時代,平台如何掌握消費者從「發現 → 比較 → 決策 → 結帳」的全鏈路**。

被解決的子問題:
1. **購物行為碎片化** — 消費者在 Search / YouTube / Gemini / Gmail 看到商品,跨平台加入購物車體驗差
2. **價格 / 促銷資訊分散** — 使用者需手動搜尋折扣
3. **Amazon / Meta / TikTok Shop 已搶佔 agentic commerce** — Google 必須快速建立自有標準與生態

## 2. 這個問題為什麼會發生?(背景)

| 因素 | 說明 |
|---|---|
| **平台圍牆花園(Walled Garden)趨勢** | Amazon 從商品 → 搜尋 → 廣告 → Prime Video → Alexa,建構自有閉環 |
| **TikTok Shop 爆發** | 2024-2025 銷售額達 49 億美元,證明「內容場 + 交易場」可融合 |
| **LLM 進入購物決策** | ChatGPT 推出「Instant Checkout」(雖已下線)、Amazon Rufus 整合購物,證明「AI 助手 + 結帳」可行 |
| **代理型 AI 從工具 → 代理** | 消費者授權 AI 代理跨網站代為購物,平台需提供 API / protocol 給 AI |
| **Google 既是入口又是廣告主** | 若放任 Amazon / Meta 掌握 agentic commerce,Google 廣告營收將被切斷 |

> 通用背景:**「AI 代理代替使用者購物」是 2025-2026 平台競爭的決勝點**,所有大廠都在搶這個賽道。

## 3. 這個技術是如何解決該問題的?

### 3.1 Universal Cart 的核心機制

```text
┌──────────────────────────────────────────────────┐
│            Google 通用購物車 (Universal Cart)      │
├──────────────────────────────────────────────────┤
│                                                  │
│  入口(多通路加入)                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐   │
│  │ Search   │ YouTube  │ Gemini   │ Gmail    │   │
│  └─────┬────┴─────┬────┴─────┬────┴────┬─────┘   │
│        ↓          ↓          ↓         ↓          │
│        └──────────┴─────┬────┴─────────┘          │
│                         ↓                         │
│              ┌──────────────────┐                 │
│              │ Universal Cart   │                 │
│              │ (Gemini 驅動)     │                 │
│              │   • 自動找促銷    │                 │
│              │   • 套用會員價    │                 │
│              │   • BNPL 整合     │                 │
│              └────────┬─────────┘                 │
│                       ↓                           │
│                  Google Pay                       │
└──────────────────────────────────────────────────┘
```

### 3.2 Universal Commerce Protocol (UCP) — 底層協議

- 2026/01 公開
- Google 生態系內執行 agentic shopping 的**基礎設施層**
- 讓 Search、YouTube Ads、Gemini 之間能無縫交換商品 / 購物車狀態
- 目前持續強化功能(BNPL、會員價自動套用都是後續加入)

### 3.3 業界定位(Google 自述)

> Google VP Ashish Gupta:
> 「Google は小売事業者でもマーケットプレイスでもない。この立場はエージェント時代においても変わらない」
> (Google 既非零售商也不是 marketplace,這個立場在 agent 時代也不變。)

Google 的策略定位:**Matchmaker(媒合者)** — 串接消費者與品牌,而非自營商品。

### 3.4 競爭格局

| 平台 | 核心產品 | 特性 |
|---|---|---|
| **Google** | Universal Cart + UCP + Gemini | 跨 Search / YouTube / Gemini 統一購物車 |
| **Amazon** | Alexa+ + Alexa for Shopping | 整合 AI 助理,Rufus 已淘汰 |
| **OpenAI** | (已下線) Instant Checkout | Web 全域結帳實驗 |
| **Meta** | AI 購物研究工具(2026/3 測試) | 對抗 Gemini / ChatGPT |
| **TikTok Shop** | 內容場 + 交易場 | 美國年銷售 49 億美元 |

### 3.5 兩種代理分類(業界分析師觀點)

```text
水平型代理(Horizontal Agent)        垂直型代理(Vertical Agent)
─────────────────────────            ──────────────────────────
Google / OpenAI / Anthropic          Amazon / Walmart
跨領域通用 AI 助手                   特定購物場域深度整合
靠 matchmaker 收費 / 廣告             自營商品 + 自有物流
```

### 3.6 消費者信任危機(普及關鍵障礙)

| 調查來源 | 數據 |
|---|---|
| Quad + Harris Poll:「不喜歡 AI 存取我的購買紀錄」 | **54%** 美國消費者 |
| 「對 AI 處理個資方式感到不安」 | **73%** 美國消費者 |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 技術 / 框架 | 技術解法 | 使用前提 | 副作用 | 預期效果 |
|---|---|---|---|---|
| **Amazon Alexa+ / Rufus 整合** | 在 Alexa 內建 LLM 助理,直接從語音購物 | 已是 Amazon 生態用戶 | vendor lock-in,Amazon 自有品牌偏見 | 對 Amazon Prime 會員流暢 |
| **ChatGPT Instant Checkout(已下線)** | OpenAI 在 ChatGPT 內完成 Web 全域結帳 | (此方案已下線) | 失敗原因:小品牌轉換率低 | 教訓:agentic commerce 需要更深的商家整合 |
| **Shopify Shop App + AI** | 商家自建 AI 購物助理,Shopify 提供後台 | 中小商家 / DTC 品牌 | 需商家自行經營流量 | 對品牌方有最高掌控度 |
| **MCP(Model Context Protocol)商業版** | AI 代理透過統一 protocol 呼叫商家 API(購物、付款、物流) | 商家已實作 MCP server | 標準仍在早期 | 跨平台 agent 通用的長遠解 |

> **切入點差異**:
> - **Google Universal Cart** 採「**水平媒合 + 多通路入口**」:利用既有 Search / YouTube 流量優勢
> - **Amazon Alexa+** 採「**垂直整合 + 語音入口**」:自有商品 / 倉儲 / 會員體系
> - **OpenAI Instant Checkout** 採「**Web 全域代理**」:試圖中立,但因缺乏商家深度整合而失敗
> - **Shopify AI** 採「**商家賦能**」:把 agentic commerce 能力下放給中小品牌
> - **MCP 商業版** 採「**開放協議**」:長期最中立,但需生態系成熟

---

**對用戶的意義**:
- **RoR / React / GCP 開發者**:若公司經營電商後台,可關注 **UCP / MCP** 規範 — 未來若要讓自家商店被 ChatGPT、Gemini、Alexa+ 的 agent 抓取,需支援這些 protocol
- **即將轉管理者**:此領域「信任」(73% 消費者對 AI 處理個資感到不安)遠比「技術」更關鍵;**隱私設計(zero-party data、最小權限、明確 opt-in)** 才是 2026 勝出要素
- **AI 投資判斷**:文章顯示 agentic commerce 還在「燒錢搶市佔」階段,OpenAI Instant Checkout 失敗可作為「不是所有大廠做對的事都能成功」的警示
- **GCP 背景**:Vertex AI + Agent Builder 已有類似概念(Agent Garden / Agent Engine),Google 內部技術與 Universal Cart 的 Gemini 串接值得追蹤
