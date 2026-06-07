# DeepSeek-Reasonix 技術分析報告

> 日期：2026-05-31
> 版本：v2
> 專案網址：https://github.com/esengine/deepseek-reasonix
> 專案資訊時點：2026-05-31（v0.53.2 / Stars 14.7k / Forks 857 / npm weekly downloads 24,147）

---

## 1. 這個技術解決什麼問題？

**通用 AI coding agent 在長會話（long-running session）中的 token 費用過高，使得持續背景運行經濟上不可行。**

具體數字（引用作者公開的真實用戶案例，2026-05-01 單日數據）：

| 指標 | 數值 |
|------|------|
| 單日輸入 token 總量 | 435M |
| Cache hit | 435,033,856 tokens（99.82%） |
| Cache miss | 767,616 tokens（0.18%） |
| 實際花費（v4-flash） | ~$1.38（註：npm README 寫 ~$12，benchmark README 明細計算為 ~$1.38，後者為更精確數字） |
| 若無 cache 的花費 | ~$61.06 |
| 節省比例 | ~97.7% |

核心主張：DeepSeek API 的磁碟快取（disk cache）本身就存在，但一般 agent 框架在長會話中會因重排歷史、重新序列化工具規格、在 prefix 中插入動態內容等行為，導致 cache hit rate 低於 20%。Reasonix 解決的是「如何讓 agent loop 的 byte layout 維持穩定以最大化命中 DeepSeek 的 prefix cache」這個問題。

---

## 2. 這個問題為什麼會發生？（背景）

### Q1 補充：為何 opencode / Claude Code / Cursor 等不針對 DeepSeek 做 cache-first 設計？

**三大 API 供應商的 cache 機制有本質差異，決定了 agent 框架是否需要「架構級 cache-first 設計」：**

| 面向 | DeepSeek | Anthropic | OpenAI |
|------|----------|-----------|--------|
| cache 儲存層級 | **磁碟（disk cache）**，由 API 自動啟用 | GPU 記憶體內，需額外請求標記 `cache_control` | GPU 記憶體內（預設）/ 擴展 GPU-local storage（24h），自動啟用不需程式碼變更 |
| cache 生命週期 | **數小時到數天**（無活動後自動清除） | **5 分鐘**（可支付 2x 價格延長至 1 小時） | 5-10 分鐘（in-memory）/ 最長 24 小時（extended） |
| cache hit 條件 | 後續請求 byte-for-byte **完整匹配**已持久化的 cache prefix unit | 前綴 byte-for-byte **完整匹配**，但可指定 cache breakpoint 位置 | 基於前 256 token 的 hash 路由 + **完整前綴匹配**（1024 token 以上） |
| cache write 成本 | **無額外寫入費用**，僅 hit/miss 計價差異（hit ~10% of miss） | **1.25x 基礎輸入價格**（5 min）/ **2x**（1h） | **無額外費用**（cache write 不收費） |
| cache hit 價格倍率 | hit 價格 ≈ miss 的 **10%** | hit 價格 ≈ base input 的 **10%** | hit 價格 ≈ base input 的 **50-90%**（原文宣稱 cost 降低高達 90%） |
| 設計含義 | **cache 持久化時間長** → agent 框架有動機在架構層維持 byte stability，因為 cache 能跨越多小時不失效 | **cache 僅存活 5 分鐘** → agent 框架即使維持 byte stability，超過 5 分鐘無請求後 cache 也會失效。框架設計收益遞減，不值得犧牲架構彈性去換 cache hit | **自動啟用+短生命週期** → agent 框架不需要特別設計；cache hit 的收益受生命週期限制，架構層面的 cache-first 設計回報不夠高 |

**結論**：DeepSeek 是唯一 cache 生命週期以「小時/天」計的供應商（磁碟快取），這是 Reasonix 做 cache-first loop 的前提條件。Anthropic 的 5 分鐘 TTL 和 OpenAI 的自動 cache 都受 GPU 記憶體限制，無法長期維持，因此 Claude Code、Cursor、Aider 等框架不值得在架構層級為 cache 做深度設計。opencode 不針對 DeepSeek 做 cache-first 設計，因為 opencode 預設後端為 Claude/GPT，其 cache 生命週期短，cache-first 設計的 ROI 不足以支撐框架層級的重構。

### 文章中明確提到：

| 面向 | 內容 |
|------|------|
| DeepSeek API 的 cache 機制 | 所有用戶預設啟用磁碟快取。cache hit 的條件是後續請求的前綴位元組（prefix bytes）必須與已持久化的 cache prefix unit「完全吻合」（byte-for-byte exact match） |
| cache 持久化的時機 | (1) 每個請求結束時在使用者輸入結尾與模型輸出結尾各自持久化一個 cache prefix unit；(2) 當系統偵測到多個請求的共用前綴時，主動持久化該共用前綴；(3) 固定 token 間隔切分 cache prefix unit |
| 一般 agent 框架的行為 | 每回合重排序歷史訊息、重新序列化 tool specs、插入時間戳或其他動態內容——任何 byte drift 都會破壞 prefix 連續性，導致 cache miss |
| DeepSeek 官方 web chat 的 cache hit | 60-80%，但僅限單一對話內；換新會話會因為 system prompt 不同而降到 0% |
| 其他 SDK/Chat UI（Cherry Studio, Open WebUI, Cline, Continue 等）的 cache hit | 30-60%，因為歷史訊息會重排序或 inline tool result 會偏移後續 bytes |

### 通用技術背景（文章中未寫）：

| 面向 | 內容 |
|------|------|
| KV cache（LLM 內部快取） | Transformer 架構在自迴歸生成時，每個新 token 的 attention 計算需參考所有歷史 token 的 Key/Value 向量。若前綴不變，這些 K/V 可復用，避免重算，因此可大幅節省 GPU 計算 → 降低 API 計價 |
| Sliding Window Attention | DeepSeek V3/V4 採用滑動窗口注意力，影響了 cache prefix unit 的儲存與匹配方式（每個 unit 為獨立完整單元） |
| Agent loop 的本質 | 多回合對話中，system prompt + tool definitions + 歷史對話構成了每次 API 請求的輸入。若 agent 框架設計時未考量 byte-level prefix stability，cache hit 將僅靠運氣（incidental hit） |

---

## 3. 這個技術是如何解決該問題的？

### 核心架構：Cache-First Loop（Pillar 1）

將 LLM 的上下文分割為三個區域，各自遵守不同的不變量：

```
┌─────────────────────────────────────────┐
│ IMMUTABLE PREFIX                        │ ← 會話期間固定
│   system prompt + tool_specs + few_shots │   每一回合都完全相同，cache hit candidate
├─────────────────────────────────────────┤
│ APPEND-ONLY LOG                         │ ← 單調增長
│   [assistant₁][tool_call₁][tool_result₁]│   僅追加，不修改不重排
│   [assistant₂][tool_call₂]...           │   保留先前回合的 prefix
├─────────────────────────────────────────┤
│ VOLATILE SCRATCH                        │ ← 每回合重置
│   R1 思考過程, 暫態計畫狀態              │   從不發送到 API（或放在 prefix 外）
└─────────────────────────────────────────┘
```

**四個機制實現 cache stability：**

1. **`ImmutablePrefix`**（`src/memory.ts`）— system prompt 與 tool specs 在 session 啟動時凍結。每次請求發送相同 byte sequence。

2. **`AppendOnlyLog`** — 對話歷史僅追加寫入，不允許原地編輯或重排序。確保先前回合的 byte 序列在後續請求中保持不變。

3. **`VolatileScratch`** — 模型思考鏈（chain-of-thought）與每回合的暫存計畫狀態存在於 cached prefix 之外，不會污染下一回合的 cache hit。

4. **Auto-compact** — 當上下文接近上限時，較舊的回合被折疊成摘要訊息。摘要請求被設計為復用主 agent 已快取的 system/tool/history prefix，盡量維持 cache coherence。

### 輔助機制：

| 機制 | 作用 |
|------|------|
| 平行工具派發（Parallel Tool Dispatch） | 標記 `parallelSafe` 的工具（唯讀操作如 read_file、web_search 等）以 `Promise.allSettled` 並行執行，結果仍按宣告順序寫入歷史以維持 byte stability |
| 逐回合 cache hit 監控 | 在 TUI 頂部狀態欄顯示 `prompt_cache_hit_tokens / (hit + miss)` 比例 |
| Auto-compact 閾值控制 | 40% 上下文比例觸發 preemptive shrink，80% 觸發緊急閾值 |

### 實現細節：

- **語言**：TypeScript 5.6+，ESM，Node ≥22
- **CLI 框架**：Commander.js + Ink 5（React 18 TUI）
- **授權**：MIT
- **發佈**：npm 套件 `reasonix`，`npx reasonix code` 可一鍵執行

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 比較對象

| # | 技術名 | 概述 |
|---|--------|------|
| A | **Reasonix** | DeepSeek 原生的終端 AI coding agent，以 cache-first loop 為架構核心，目標是極低成本長會話 |
| B | **Claude Code** | Anthropic 的終端 AI coding agent，Claude 模型專用。封閉原始碼，收費較高 |
| C | **Cursor** | IDE 整合型的 AI coding 工具（基於 VS Code），支援 OpenAI/Anthropic 模型，訂閱制收費 |
| D | **Aider** | 開源（Apache 2）的終端 AI coding agent，支援任意 LLM backend（透過 OpenRouter 等），不綁定單一模型 |

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|--------------|----------------|------------------|
| **Reasonix** | 架構層級將上下文分割為 ImmutablePrefix / AppendOnlyLog / VolatileScratch，確保每回合請求的 byte prefix 與 DeepSeek 磁碟快取機制精確對齊 | 必須使用 DeepSeek API（v4-flash / v4-pro）；需要付費 API key；Node ≥22 | 鎖定單一後端供應商，無法切換模型到非 DeepSeek 服務；不支援離線/本機模型；目前無公開發布的 task success benchmark 數據（僅有 cache hit 率數據） | cache hit 率 99%+；單日成本從 ~$61 降至 ~$1.38（v4-flash）；token 成本約為同級競品的 1/10 |
| **Claude Code** | Anthropic 自家 agent 框架，使用 Claude 模型。提示快取（prompt caching）需手動標記 cache breakpoints，cache 生命週期 5 分鐘（可付費延長至 1 小時） | 必須使用 Anthropic API（Claude 模型）；需付費 API key | Prompt cache 生存時間僅 5 分鐘（vs DeepSeek 數小時到數天）；cache write 需額外付費（1.25x base）；封閉原始碼，無法自訂 loop 行為 | cache hit 率取決於使用模式與手動標記品質；整體成本較高（Claude 單價遠高於 DeepSeek）；推理品質在難題上較優（作者也承認 Claude Opus 在 hardest-leaderboard 上仍贏） |
| **Cursor** | IDE 整合，透過 IDE 提供檔案感知與程式碼補全。使用 OpenAI/Anthropic 後端，cache 機制由各後端各自提供，不要求使用者理解或控制 | 需要安裝 Cursor IDE（非終端）；需要訂閱或自帶 API key | 非終端原生（必須在 IDE 內使用）；無法用於 CI/CD pipeline；無跨模型統一 cache 策略；不支援純終端 headless 模式 | 適合 IDE 重度使用者；cache hit 率不透明（由後端決定）；無 long-session 成本優化設計 |
| **Aider** | 通用 LLM agent 框架，支援任意模型。架構上未對特定後端的 cache 機制做深度最佳化，cache hit 屬於「偶發性」命中 | 可使用任意 LLM（OpenAI、Anthropic、DeepSeek、Ollama 等）；開源 Apache 2 | cache hit 率低且不可預測（取決於後端與 prompt 結構的偶然對齊）；token 成本較高；無 auto-compaction 等成本控制機制 | 支援最多後端；可用於離線/本機模型；成本可低至零（若使用本機 Ollama）；cache 效益因後端而異 |

### 各技術的切入點差異：

- **Reasonix**：從「如何讓 agent loop 產生的 byte sequence 維持不變以觸發 DeepSeek 的磁碟快取」切入，目標是成本最小化。是唯一以「後端 cache 機制作為架構設計核心約束」的解決方案。成本優化有實證數據。
- **Claude Code**：從「如何提供最高品質的編碼輔助」切入，利用 Anthropic 自家的 prompt caching 但 cache 生命週期極短（5 min），成本控制不是主要設計目標。
- **Cursor**：從「如何在 IDE 內提供無縫 AI 輔助」切入，使用者體驗整合優先，cache 與成本由底層模型決定，使用者不可控。
- **Aider**：從「如何讓使用者自由選擇 LLM backend」切入，靈活性優先，cache 效益取決於使用者選擇的後端，不做架構層級的 cache 保證。

### Q2 補充：Reasonix 在 task success 上的 Benchmark 狀況

Reasonix 的 benchmark 位於 `benchmarks/` 目錄，架構如下：

- **`benchmarks/tau-bench/`**：自訂的 τ-bench-lite harnees（8 個零售場景多輪任務），對比「cache-hostile baseline」vs「CacheFirstLoop + Reasonix」。所有成功謂詞（success predicates）為**確定性 DB 檢查**（非 LLM judge）。
- **`benchmarks/real-world-cache/`**：單一真實用戶的 DeepSeek dashboard 截圖 case study。

**關鍵事實**：

| 指標 | 現狀 |
|------|------|
| 有公開發布的 task success 率對比（Reasonix vs baseline vs Claude）嗎？ | **沒有**。benchmark harness 存在但未公開發布 report.md 或具體 success rate 數字。benchmark README 說明 runner 可輸出 `results-*.json` 和 `report.md`，但 repo 中未包含實際執行結果 |
| harness 設計測量什麼？ | **cache hit rate / cost gap**，而非 task completion 品質。harness 的核心理念是：「baseline 與 Reasonix 共享同一 DeepSeekClient，唯一差異是 prefix stability，任何 cache-hit/cost 差距都可歸因於 Pillar 1」 |
| 有對比 Claude 嗎？ | **沒有真實執行**。benchmark README 明確寫「running Claude for real is out of scope」，僅從 token 計數估算成本 |
| task success 謂詞是什麼？ | 確定性 DB 檢查（如「DB 中的 address 被正確更新」），非 LLM judge。但 8 個 task 數量極少（vs 原版 τ-bench 的 airline + retail 數百任務），不足以建立統計顯著性 |
| 社群對此有聲音嗎？ | 有。issue #1467「[RFC] Core Capability Evaluation Suite」於 2026-05-22 由貢獻者提出，說明社群也意識到需要「local, fast regression testing for contributors & maintainers」——暗示現有 benchmark 不足以做能力回歸測試 |

**結論**：Reasonix 在**成本**上有實證的量化優勢（99.82% cache hit），但在**任務完成品質**上缺乏公開的對比 benchmark。作者自身在 Non-goals 中承認「Claude Opus still wins some benchmarks；DeepSeek is competitive on coding」。cache-first 設計僅保證「便宜」，不保證「更好」。

### 選擇指引（依使用場景）：

| 場景 | 推薦 |
|------|------|
| 長時程背景運行的 terminal agent，成本敏感 | Reasonix |
| 極難推理任務（如數學證明、演算法設計），預算充裕 | Claude Code |
| IDE 內開發，需要與編輯器深度整合 | Cursor |
| 離線環境或已部署本機模型，預算零 | Aider + Ollama |
| 需要彈性切換多種 LLM backend | Aider |

---

## 5. Overengineering 分析

### 問題定義

Reasonix 的 cache-first loop 設計涉及四個核心機制（ImmutablePrefix、AppendOnlyLog、VolatileScratch、Auto-compact），加上輔助機制（Parallel Dispatch、Tool-call Repair 四 pass、Cost Control 四 tier）。需判定這些設計在「解決長會話 token 成本過高」這個問題上，是否存在 overengineering。

### 反面論證：立場 A（是 overengineering） vs 立場 B（不是 overengineering）

#### 面向 1：ImmutablePrefix + AppendOnlyLog + VolatileScratch 三分區

| | 立場 A：是 overengineering | 立場 B：不是 overengineering |
|---|---|---|
| 主張 | 三分區是對一個簡單原則的過度抽象化。核心訴求僅是「不要重寫歷史訊息」——任何有設計紀律的 agent 框架都應該能做到 append-only log，不需要為此發明三分區術語和專用實作 | DeepSeek 的 cache 要求 byte-for-byte 完全吻合。一般框架的「append-only」只保證訊息順序不亂，但不保證 tool spec 序列化順序不變、不保證 thinking content 不混入 prefix、不保證 compact 後的 summary byte 與原來 prefix 的連續性。三分區是在 byte-level invariant 上的精確工程，不是抽象過度 |
| 證據 | Claude Code 和 Cursor 從未宣稱需要三分區設計，但仍能運作（成本較高但功能正常）。opencode 的設計中也沒有類似的三分區記憶體模型 | Reasonix 的真實用戶數據證明 99.82% cache hit 需要四個機制同時作用（benchmark README 明確指出：「DeepSeek gave us cacheable bytes. The four mechanisms above are how we keep the bytes cacheable」）。分開任一個機制都會導致 hit rate 顯著下降 |
| **判定** | **不是 overengineering** | 三分區是 DeepSeek byte-exact cache match 的必要條件，非過度設計。證據強度：高（benchmark 數據 + DeepSeek API 文件 + 實作明確） |

#### 面向 2：Tool-Call Repair 四 pass（flatten / scavenge / truncation / storm）

| | 立場 A：是 overengineering | 立場 B：不是 overengineering |
|---|---|---|
| 主張 | 這些是 DeepSeek 模型自身的缺陷（tool-call JSON 不完整、重複呼叫、參數遺漏），應該是模型提供者修復的問題，不該由 client-side 框架承擔修復責任。四 pass pipeline 增加了複雜度卻只服務一個有缺陷的模型 | 所有 LLM 都有 tool-call 格式錯誤的問題，不是 DeepSeek 特有。Anthropic 的 prompt caching 文件也提到 tool_choice 變更會 invalidate 整個 cache，說明所有後端都有類似限制。client-side repair 是務實手段——等待模型修復是策略風險，本地修復是工程確定性 |
| 證據 | OpenAI 的 prompt caching 文件未提及需 client-side repair；Anthropic 的 cache diagnostics（beta）提供了「比較連續請求並報告前綴分歧點」的工具，證明這類問題應由 API 層解決 | Reasonix 的 issue tracker 中有多個 bug 與 tool-call repair 相關（如 desktop 端按鈕無回應 #2364、提示顯示不全 #2362），說明 repair pipeline 本身引入了新的維護負擔。但 ARCHITECTURE.md 中明確列出的四種 failure mode（thinking 內的 tool-call、>10 param 丟失、storm、truncation）在 DeepSeek 平台上都有實證 |
| **判定** | **部分是 overengineering** | **flatten**（>10 param auto nest/unnest）是架構級解法，不應由 agent 框架解決——應由模型提供更好的結構化輸出支援。**scavenge**（regex scan thinking 取回遺漏的 tool call）是彌補模型缺陷的權宜之計，若 DeepSeek 日後修復則此 pass 成為 dead code。**storm** 和 **truncation** 是合理的 guard，所有 agent 框架都需要。**過度部分：flatten + scavenge 的複雜度與其問題規模不成比例（>10 param schema 的場景比例極低）** |

#### 面向 3：Cost Control 四 tier（flash-first / auto-compaction / /model switch / `<<<NEEDS_PRO>>>`）

| | 立場 A：是 overengineering | 立場 B：不是 overengineering |
|---|---|---|
| 主張 | 四個成本控制機制層層疊加，過度細分。`<<<NEEDS_PRO>>>` 自我升級標記是一種 hack——讓模型自己決定何時需要更強的推理，增加了 prompt token 消耗且不保證準確。flash-first 預設已經處理了大部分場景，`<<<NEEDS_PRO>>>` 是多餘的 | 四個機制的互補性強：(1) flash-first 處理常規任務；(2) auto-compaction 防止長會話 token 膨脹；(3) /model switch 給使用者手動控制；(4) `<<<NEEDS_PRO>>>` 作為最後防線——模型比任何靜態規則更了解自己的推理需求。四個機制共同降低 active user 從 $150-250/month 降到 ~$10-20/month |
| 證據 | `<<<NEEDS_PRO>>>` 的準確性未有公開測試數據。可能出現 false positive（flash 可以解但被升級→浪費成本）或 false negative（該升級但沒標記→任務失敗），兩者都沒有量化。此外此機制在 v0.50.0 前為 `/pro` 單回合武裝模式，0.50.0 後改為自我升級+sticky model，說明設計本身經歷了重大變更——原有設計被證明不合用 | ARCHITECTURE.md 明確記錄了設計演進（`/pro` one-shot 在 0.50.0 被移除），說明設計根據實際使用回饋迭代。`<<<NEEDS_PRO>>>` 的 bare marker 不消耗 token（純粹一行），有 rationale 版本僅多一行，token 成本可忽略 |
| **判定** | **不是 overengineering（但在邊界上）** | 四個 tier 各有用途且互補，沒有冗餘。但 `<<<NEEDS_PRO>>>` 缺乏量化準確度數據，其設計假設（模型知道自己何時需要更強推理）未經獨立驗證。如果未來出現更好的模型 routing 方案（如基於 task type 的靜態路由），此機制可能被簡化 |

#### 面向 4：整體 feature 廣度（MCP / Skills / Memory / Hooks / Permissions / Dashboard / Desktop / QQ Channel / Plan Mode / Checkpoint / Replay / Diff / Semantic Index / Jobs...）

| | 立場 A：是 overengineering | 立場 B：不是 overengineering |
|---|---|---|
| 主張 | Reasonix 宣稱「cache-first loop」是核心，但實際 feature 列表已膨脹到包含 QQ 通道、桌面客戶端、web dashboard、semantic index、jobs、plan mode——這些與 cache-first 無直接關聯。一個以「成本最小化」為核心賣點的專案不應該同時維護 Tauri 桌面端和 QQ bot 整合。這是 scope creep | 這些是終端 coding agent 的基礎功能，不是 overengineering。Claude Code 也有 hooks、MCP、plan mode；Cursor 有更複雜的 IDE 整合。Reasonix 是社群驅動專案，feature 來自社群需求（QQ 通道對中國市場是剛需），不是核心團隊的設計膨脹 |
| 證據 | 目前有 345 open issues（含大量 bug），顯示維護負擔已超過核心團隊能力。桌面端仍是 prerelease（未簽章、Gatekeeper 警告），QQ 通道在 v0.53.2 剛加入（穩定性未知）。11 個 open bug 中有多個是 TUI 渲染和桌面端問題（#2379 文本無法複製、#2364 按鈕無法點擊、#2369 界面卡頓、#2362 提示顯示不全） | 14.7k stars 和 oosmetrics「Agents Top 2 by velocity」「CLI Top 3 by velocity」證明社群需求真實存在。QQ 通道和桌面端是中國使用者社群的實際需求，非核心團隊的自我感覺良好 |
| **判定** | **功能廣度層面是 overengineering，但非架構層面** | Cache-first loop（Pillar 1）本身的設計不是 overengineering。但**圍繞 cache-first loop 的附加功能（desktop、QQ、semantic index、dashboard）在目前的專案成熟度下構成了 scope creep**——這些功能的維護成本分散了對核心 cache-first 機制的工程資源，且部分功能（desktop prerelease）的完成度不足以證明其優先級合理性。Issue #368「TUI information architecture — borrow opencode's zoned layout」也暗示現有 TUI 設計本身還在迭代中，feature 應先收斂而非擴張。 |

### Overengineering 總結判定表

| 面向 | 判定 | 核心理由 | Overengineering 程度 |
|------|------|----------|---------------------|
| 三分區（ImmutablePrefix / AppendOnlyLog / VolatileScratch） | **否** | DeepSeek byte-exact cache match 的必要條件，benchmark 數據支持 | 0/5 |
| Tool-Call Repair 四 pass | **部分是**（flatten + scavenge） | flatten 處理的 >10 param 場景占比極低；scavenge 修補的是 DeepSeek 自身缺陷，應由模型端解決。storm + truncation 為合理 guard | 2/5 |
| Cost Control 四 tier | **否**（邊界上） | 四個 tier 功能互補，但 `<<<NEEDS_PRO>>>` 缺乏量化準確度數據 | 1/5 |
| 整體 feature 廣度（desktop / QQ / dashboard / semantic index...） | **是**（scope creep） | 與 cache-first 核心無直接關聯；維護成本超過當前團隊能力（345 open issues）；桌面端為 prerelease 狀態 | 3/5 |
| **綜合** | **核心架構不是 overengineering；功能廣度是** | Cache-first loop 的設計本質合理且有數據支持。但 0.53.2 版本的 feature surface 已偏離「成本最小化 coding agent」的核心定位，向 full-platform（terminal + desktop + web dashboard + IM channels）方向擴張，在僅 9 個核心貢獻者 + prerelease 桌面端的現狀下，構成了 scope creep | **架構：0/5；功能：3/5** |

### 適用範圍（基於 overengineering 分析的場景收斂）

| 場景 | 是否適合 Reasonix | 理由 |
|------|-------------------|------|
| 長時程 coding agent，每天 >4 小時背景運行，DeepSeek API 可用 | **適合** | core cache-first loop 設計為此場景最佳化，成本優勢顯著 |
| 短任務（<10 輪對話），不關心底層 cache 機制 | **可能不適合** | cache-first 設計的收益在短會話中無法體現，三分區複雜度成為負擔。直接使用 DeepSeek API 或輕量 wrapper 即可 |
| 需要非 DeepSeek 模型（Claude、GPT、本地 Ollama） | **不適合** | cache-first loop 僅在 DeepSeek 磁碟快取機制下有效。使用其他後端時，Reasonix 的成本優勢消失，但需承受單一後端鎖定的代價 |
| 需要 IDE 整合 | **不適合** | Reasonix 明確 non-goal 為 IDE integration，terminal-only |
| 對穩定性要求高於成本 | **可能不適合** | 桌面端 prerelease、345 open issues、TUI 渲染 bug 尚存——如果穩定性優先於成本，Claude Code 或 Cursor 更成熟 |
| 中國開發者，需要 QQ/微信整合 | **適合（但注意成熟度）** | QQ 通道在 v0.53.2 剛加入，功能存在但穩定性待驗證 |
