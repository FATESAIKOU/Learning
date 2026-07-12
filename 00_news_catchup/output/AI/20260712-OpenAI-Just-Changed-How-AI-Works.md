# 01. OpenAI Just Changed How AI Works — And Most People Haven't Noticed Yet

**Source**: https://medium.com/@nk271452/openai-just-changed-how-ai-works-and-most-people-havent-noticed-yet-1165ea8c5daa
**Author**: Grow up
**Date**: 2026-07-09
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

GPT-5.6 解決的是 **AI 模型選擇的結構性問題**：過去 OpenAI 一次只發布一個模型（GPT-4 → GPT-4o → GPT-5），使用者沒有真正的選擇權，只能使用最新版處理所有任務。這導致兩個痛點：

| 痛點 | 說明 |
|------|------|
| 成本剛性 | 簡單任務和複雜任務使用同一模型，浪費 token 成本 |
| 能力錯配 | 需要深度推理時模型不夠強，簡單任務時又過度消耗資源 |

GPT-5.6 以 **三層能力分級（Sol / Terra / Luna）** 讓使用者依任務複雜度選擇對應模型，同時推出 **ChatGPT Work** 將 ChatGPT 從對話工具轉型為工作執行環境。

## 2. 這個問題為什麼會發生?(背景)

AI 模型發展到 2026 年中，已出現明顯的 **能力-成本不對稱**：

- **模型能力分化**：前沿模型（如 Sol）在複雜推理、程式碼生成上遠超中階模型，但成本高出 3-5 倍
- **使用場景多元化**：同一使用者一天內可能從「寫一封 email」（簡單）切換到「分析 500 頁技術文件並產出架構圖」（複雜）
- **競爭壓力**：Anthropic 的 Claude Fable 5 / Mythos 5 在 SWE-Bench 等程式碼基準上領先，OpenAI 需要差異化定位
- **商業模式轉型**：從「賣 API token」轉向「賣工作成果」，ChatGPT Work 是這個轉向的載體

GPT-5.6 的定價結構反映了這個背景：

| 模型 | 輸入 (每 1M token) | 輸出 (每 1M token) | 定位 |
|------|---------------------|---------------------|------|
| Sol | $5 | $30 | 旗艦，複雜工作 |
| Terra | $2.50 | $15 | 日常平衡型 |
| Luna | $1 | $6 | 輕量快速 |

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 三層能力分級架構

```
Sol (旗艦)
├── 複雜程式碼、研究、資安、科學、設計
├── Ultra 模式：4 個 agent 並行工作流
└── 付費方案 (Plus/Pro/Business/Enterprise)

Terra (平衡)
├── 日常寫作、研究、內容創作
├── 效能 = GPT-5.5，成本減半
└── 免費方案 (Free/Go) 也可用

Luna (輕量)
├── 小規模快速任務
├── 最低延遲、最低成本
└── 付費方案可選
```

### 3.2 Ultra 模式：多 Agent 協調

Ultra 設定是 GPT-5.6 的核心創新。對高難度任務，Sol 可同時啟動 4 個 agent 實例並行處理不同工作流，最後合併結果。這不是簡單的 ensemble voting，而是 **協調式多 agent 工作流**，以更高 token 消耗換取更強輸出品質。

### 3.3 ChatGPT Work：從對話到工作執行

ChatGPT Work 將模型定位從「問答工具」轉為「工作發生地」：
- 讀取文件與連接的工作應用中的素材
- 轉換為可分享的產出（簡報、文件、試算表、介面原型、前端 prototype）
- 更強的版面判斷力與參考文件遵循度

### 3.4 程式碼基準表現

| 基準 | GPT-5.6 Sol | Claude Fable 5 | Claude Mythos 5 |
|------|-------------|-----------------|-----------------|
| Artificial Analysis Coding Agent Index | **80.0** | 77.2 | - |
| SWE-Bench Pro | 64.6% | 80.0% | **80.3%** |

Sol 在 Coding Agent Index 上以更少 token、更短時間、更低成本領先，但在 SWE-Bench Pro 上落後 Claude 約 15 個百分點。這顯示 Sol 在 agent 化程式碼任務上強，但在大型程式碼庫的實際修復任務上仍有差距。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

### 4.1 競爭者對照

| 方案 | 策略 | 差異 |
|------|------|------|
| **Anthropic Claude** | 單一模型 + 思考預算控制 (extended thinking) | 不拆分模型，而是在同一模型內調整推理深度 |
| **Google Gemini** | 多尺寸模型 (Ultra/Pro/Flash/Nano) | 類似分級策略，但未整合到工作執行環境 |
| **開源模型 (Llama 4, Mistral)** | 不同參數規模的獨立模型 | 無統一品牌下的分級，使用者需自行選擇部署 |
| **OpenAI GPT-5.6** | 三層命名分級 + 工作執行平台 | 首次將模型分級與產品平台深度整合 |

### 4.2 對用戶的意義

對在 Softbank AxrossRecipe 使用 Ruby on Rails + React + GCP 的技術管理者而言：

- **Terra 已足夠日常開發**：Terra 效能等同 GPT-5.5，成本減半，適合 code review、文件生成、日常問答
- **Sol 用於關鍵決策**：架構設計、複雜 bug 排查、跨系統整合方案時啟用 Sol + Ultra 模式
- **ChatGPT Work 方向值得追蹤**：如果 ChatGPT Work 能整合 Jira/Notion/GitHub，將直接影響開發團隊的工作流程設計
- **SWE-Bench 差距提醒**：在實際大型程式碼庫修改上 Claude 仍領先，不應完全依賴單一模型

### 4.3 結構性趨勢

GPT-5.6 的發布標誌著 AI 模型市場從「軍備競賽」進入「產品化分層」階段。模型不再只是比參數量和 benchmark 分數，而是比 **任務匹配度、成本效率、工作流整合度**。這對即將轉管理職的技術人員意味著：選用 AI 工具的策略思維比追最新模型更重要。

---

*字數: ~1,200*
