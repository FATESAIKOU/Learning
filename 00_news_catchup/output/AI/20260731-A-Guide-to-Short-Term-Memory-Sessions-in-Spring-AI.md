# 2. A Guide to Short-Term Memory Sessions in Spring AI

**Source**: https://feeds.feedblitz.com/~/964742381/0/baeldung
**Author**: Baeldung
**Date**: 2026-07-31
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

解決「LLM 對話記憶在長對話中溢出 context window」的問題。LLM 本身是 stateless 的,每次請求獨立,要讓模型「記得」先前對話,必須把歷史訊息重新放入 prompt。但隨對話增長,naively 重播全部訊息會超過模型的 context window,導致:

| 問題 | 後果 |
|------|------|
| Context window 溢出 | 請求失敗或被截斷,模型遺失早期脈絡 |
| 舊訊息逐筆刪除 | 工具呼叫(tool call)與其結果被拆散,產生「dangling tool call」—模型看到呼叫卻找不到回傳值 |
| 成本隨對話線性增長 | 每次請求都重送全部歷史,token 費用攀升 |

Spring AI Session(短期記憶 Session 層)以 **event-sourced + turn-aware compaction** 解決上述三項,目標是取代舊有的 `ChatMemory` API。

## 2. 這個問題為什麼會發生?(背景)

### LLM 的 stateless 本質

LLM 推理是無狀態的:模型不保存任何對話歷史,「記憶」完全靠應用層把歷史訊息重新塞進 prompt。這是架構選擇(可擴展性、可重現性),但也把記憶管理的複雜度推給應用開發者。

### 舊 ChatMemory 的缺陷

Spring AI 早期以 `ChatMemory` 提供記憶,常見實作 `MessageWindowChatMemory` 採用**逐筆訊息**的滑動視窗:當訊息數超過上限(如 20 則),就刪除最舊的單一訊息。問題在於:

- 一個「turn」(一輪對話)包含:使用者訊息 + 助理回覆 + 工具呼叫 + 工具回傳結果
- 逐筆刪除會把同一輪的工具呼叫與結果拆開:模型看到「我呼叫了 getWeather()」卻找不到回傳的 JSON,行為出錯
- 對話越長,這類斷裂越多,品質下降

### 多代理與分支的需求

現代 AI 應用常有多個協同 agent,各自需要獨立的歷史隔離;某些場景需要分支(branch)探索不同對話路徑。舊的扁平訊息列表無法表達這類結構。

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 核心資料模型:Event Sourcing

```
Session (ID + userId)
  └─ SessionEvent (immutable, timestamped, unique ID, optional branch)
       └─ wraps Message (User / Assistant / ToolCall / ToolResult)
  └─ 分群為 Turn(一則 user msg + 其後所有 assistant 回覆/工具呼叫/結果,直到下一則 user msg)
```

- **Turn 是不可分割的原子單元**:壓縮永遠沿 turn 邊界進行,絕不拆散同一輪
- **事件不可變 + 帶時間戳**:支援分支標籤(branch label),讓多 agent 共用同一 Session 但隔離歷史

### 3.2 壓縮機制:Trigger + Strategy 分離

| 面向 | 角色 | 選項 |
|------|------|------|
| **Trigger(何時壓縮)** | 決定啟動時機 | `TurnCountTrigger`(N 輪後)、`TokenCountTrigger`(token 估計達上限)、`CompositeCompactionTrigger`(組合條件) |
| **Strategy(如何壓縮)** | 決定壓縮方式 | 見下表 |

四種壓縮策略(全部遵守 turn 邊界):

| Strategy | 需要LLM | 適用場景 | 行為 |
|----------|--------|---------|------|
| `SlidingWindowCompactionStrategy` | 否 | 成本敏感、只需近期脈絡 | 保留最近 N 個事件,丟棄舊事件 |
| `TurnWindowCompactionStrategy` | 否 | 保留最近 N 個完整 turn | 依 turn 為單位滑動 |
| `TokenCountCompactionStrategy` | 否 | 硬性 context window 限制 | 依 token 數壓縮 |
| `RecursiveSummarizationCompactionStrategy` | 是 | 長對話且需回溯舊脈絡 | 模型為被丟棄的 turn 撰寫摘要,以合成事件取代 |

前三者「直接丟棄」舊事件,快速免費;第四者付出一次額外模型呼叫,換取舊脈絡的濃縮保留。

### 3.3 整合至 ChatClient:SessionMemoryAdvisor

`SessionMemoryAdvisor` 是標準 Spring AI Advisor,掛入 `ChatClient` 管線後:

1. **呼叫前**:從 Session 載入歷史事件,重播為訊息
2. **呼叫後**:將新一輪 exchange(使用者輸入 + 助理回覆)附加至 Session
3. **自動壓縮**:Session 增長超過 Trigger 時自動壓縮

```java
SessionMemoryAdvisor.builder(sessionService)
    .defaultUserId("alice")
    .compactionTrigger(new TurnCountTrigger(20))
    .compactionStrategy(SlidingWindowCompactionStrategy.builder().maxEvents(10).build())
    .build();
```

### 3.4 持久化與生產部署

| 面向 | 選項 |
|------|------|
| 儲存 | `InMemorySessionRepository`(開發)、`spring-ai-starter-session-jdbc`(PostgreSQL/MySQL/MariaDB/H2) |
| 模型 | Provider-agnostic(OpenAI / Anthropic / 本地模型) |
| TTL | `CreateSessionRequest` 可設存活時間,過期 Session 自動清理 |
| 查詢 | `findById()`、`findByUserId()`、`getEvents()`(底層事件流)、`getMessages()`(扁平訊息) |

### 3.5 遷移路徑

舊 `MessageWindowChatMemory(20)` ≡ 新 `TurnCountTrigger(20)` + `SlidingWindowCompactionStrategy`。API 目前在 `spring-ai-community` 孵育,定位為未來取代 `ChatMemory` 的預設實作。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 定位 | 與 Spring AI Session 差異 |
|------|------|--------------------------|
| **LangChain ConversationBufferMemory / SummaryMemory** | Python 生態記憶抽象 | 概念相近,但無 turn-aware 邊界保護,工具呼叫易斷裂 |
| **LangGraph checkpointer** | 狀態機式記憶持久化 | 適合複雜 agent 圖,但語意較重 |
| **Mem0 / Zep** | 外部記憶服務(向量+摘要) | 跨對話長期記憶,需額外服務依賴 |
| **自建 DB + 手動重播** | 完全自控 | 彈性最高,但需自行處理壓縮/邊界/分支 |
| **MCP(Memory 參考實作)** | 用戶學習中,提供記憶協定 | MCP 偏向「模型如何存取外部記憶來源」,Session 偏向「應用如何管理對話歷史」 |

### 思考方式:Event Sourcing + 不可變事件

本方案的深層設計借鑑 **Event Sourcing**:不儲存「目前狀態」,而儲存「事件流」,狀態由重播事件衍生。這帶來三項優勢:可重建任意時點、可分支、可稽核。對於需要合規與審計的企業 AI 應用(如客服、法務),事件流比扁平訊息列表更值得採用。

### 對用戶情境的對照

用戶正在學習 Spring+AI,本篇是 Spring AI 記憶層的**下一代官方方向**。建議優先用 `SessionMemoryAdvisor` 而非舊 `ChatMemory`,因為:
1. turn-aware 壓縮避免工具呼叫斷裂—在 agent 場景(用戶探索 Cursor+Claude)尤其關鍵
2. JDBC 持久化契合用戶 Rails + RDBMS 的熟悉環境
3. 分支標籤為未來多 agent 協同預留擴充空間

未來轉管理職後,理解「記憶壓縮策略的取捨(成本 vs. 回溯能力)」也是評估團隊 AI 功能架構的判準之一。