# 3. Previewing GPT-5.6 Sol: a next-generation model

(原 URL: https://openai.com/index/previewing-gpt-5-6-sol, 替代來源: https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna)

**Source**: https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna
**Author**: OpenAI
**Date**: 2026-06
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

GPT-5.6 Sol 家族解決的是 **AI 模型在專業領域的深度推理能力不足與推理成本過高** 的雙重問題。

| 問題面向 | 具體痛點 |
|----------|----------|
| 軟體工程 | 現有模型在大型程式碼庫重構、跨檔案依賴追蹤、複雜 debug 上仍頻繁出錯 |
| 電腦使用 (Computer Use) | Agent 操作 GUI 時對多步驟任務的規劃與錯誤恢復能力不足 |
| 專業知識工作 | 法律、醫療、金融等領域需要極低幻覺率的深度推理 |
| 科學研究 | 跨學科文獻綜合、實驗設計、數據分析需要長鏈推理 |
| 網路安全 | 漏洞分析、攻擊鏈重建需要系統性思維 |
| 推理成本 | 高能力模型 (如 GPT-5.x) 的 API 價格阻礙大規模部署 |

GPT-5.6 Sol 定位為旗艦推理模型，Terra 和 Luna 則以不同價位覆蓋不同成本敏感度的場景。

## 2. 這個問題為什麼會發生?(背景)

**推理能力的 scaling law 與成本呈非線性關係。**

自 GPT-4 以來，模型能力的提升主要來自三個方向：
1. **更大規模的預訓練** — 但資料牆 (data wall) 已接近瓶頸
2. **RLHF/DPO 等對齊技術** — 改善安全性但未顯著提升推理深度
3. **推理時計算擴展 (test-time compute scaling)** — 讓模型在回答前進行更多內部推理步驟，是目前最有效的方向

但 test-time compute scaling 的代價是：每次推理消耗的 token 數大幅增加，直接推高 API 成本。GPT-5.6 家族透過分級定價 (Sol $5/$30, Terra $2.50/$15, Luna $1/$6 per 1M tokens) 讓不同場景選擇合適的性價比。

**與美國政府協調的階段性釋出策略** 反映了 AI 安全治理的新現實：最先進模型需經過政府安全審查後才能對外開放。目前僅限 trusted partners 預覽。

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 三層模型分級

```
GPT-5.6 家族
├── Sol    ($5/$30)  ← 旗艦，最強推理能力
├── Terra  ($2.50/$15) ← 中階，平衡能力與成本
└── Luna   ($1/$6)   ← 輕量，高性價比
```

### 3.2 Explicit Cache Breakpoints 機制

這是 GPT-5.6 的關鍵基礎設施創新：

| 機制 | 說明 | 成本影響 |
|------|------|----------|
| Cache breakpoints | 開發者可在 prompt 中標記 cache 邊界點 | 精細控制哪些部分被快取 |
| 30-min minimum cache life | 快取至少保留 30 分鐘 | 短時間內重複呼叫大幅降低成本 |
| Cache writes | 1.25x uncached input rate | 寫入快取的成本略高於未快取輸入 |
| Cache reads | 90% discount | 命中快取時輸入成本降至原價 10% |

這對以下場景有直接價值：
- Agent 循環中重複使用相同的 system prompt 和工具定義
- RAG 應用中固定的 context window 前綴
- 多輪對話中不變的歷史訊息

### 3.3 階段性釋出策略

```
Trusted Partners (當前)
  → 安全評估與紅隊測試
    → 政府協調審查
      → 分階段對外開放
```

此策略平衡了前沿能力釋出與國家安全考量，也為企業用戶提供了提前評估的窗口。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 代表 | 與 GPT-5.6 的差異 |
|------|------|------------------|
| Anthropic Claude Opus 5 | Anthropic | 同樣定位旗艦推理，但採用 Constitutional AI 路線，Mythos 5 因國安審查被限制釋出 |
| Google Gemini 3 Pro | Google | 依託 TPU 基礎設施，在長上下文 (2M+) 有優勢，但推理深度評測落後 |
| 開源模型 (Llama 4, DeepSeek-R2) | Meta / DeepSeek | 成本接近零但推理能力與旗艦閉源模型仍有差距 |
| 混合推理架構 (Router + 多模型) | OpenRouter / 自建 | 將簡單查詢路由到便宜模型，複雜查詢路由到強模型，但增加系統複雜度 |
| 本地部署 + 量化 | llama.cpp / vLLM | 適合隱私敏感場景，但無法達到旗艦模型的推理深度 |

**對用戶的啟示**：GPT-5.6 的 cache breakpoints 機制對 Spring AI + MCP 的 Agent 場景有直接價值 — Agent 循環中 system prompt 和 tool definitions 可被 cache，大幅降低重複推理成本。Luna 的 $1/$6 定價使 AI 驅動開發 (Cursor+Claude 探索中) 的後端成本進入可大規模部署的區間。
