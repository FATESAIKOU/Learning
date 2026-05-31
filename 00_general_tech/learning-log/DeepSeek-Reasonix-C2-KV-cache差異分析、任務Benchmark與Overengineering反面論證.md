# DeepSeek-Reasonix-C2-KV-cache差異分析、任務Benchmark與Overengineering反面論證.md

## 狀況理解

使用者對 C1 的輸出提出三點不滿意：

1. **Q1（核心疑點）**：KV cache 是 LLM 通用議題，為何只有 DeepSeek 需要一個專屬的 cache-first SDK？opencode / Claude Code 等為何不對應產生類似架構？

2. **Q2（盲區）**：Reasonix 的成本優勢有 data，但**任務完成品質**上的 benchmark 是什麼？跟 Claude/Aider 比誰的 coding 能力更強？

3. **Q3（嚴格要求）**：Reasonix 在其想解決的問題上是否存在 **overengineering**？需逐事項列表 + 判定理由，且所有判定必須進行**完全的反面論證**（先蒐集反對證據，再收斂出結論並明確適用範圍）。

使用者特別強調「本次學習檔案內的判定結果都要進行完全的反面論證 搜集大量反面資料 最後總結出真正的結論與適用範圍」，這要求本紀錄中的每個判定都需有 A/B 兩面證據矩陣。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 Anthropic 官方 prompt caching 文件 | 了解 Anthropic 端的 cache 機制（生命週期、成本、啟用條件） | 取得與 DeepSeek disk cache 的可比較參數 | 取得關鍵差異：Anthropic cache TTL 預設 5 分鐘（可付費延長至 1h），cache write 需額外 1.25x cost，需手動標記 cache breakpoints |
| 讀取 OpenAI 官方 prompt caching 文件 | 了解 OpenAI 端的 cache 機制 | 取得與 DeepSeek 和 Anthropic 的三方對比 | 取得關鍵差異：OpenAI cache 自動啟用（≥1024 tokens），無額外費用，基於前 256 token hash 路由，但 TTL 也僅 5-10 分鐘（extended 24h 僅限新模型） |
| 對照 DeepSeek KV cache 文件（C1 已取得） | 建立三方 cache 機制差異矩陣 | 歸納出為何 DeepSeek 是唯一適合 cache-first 架構的後端 | 完成三方對比表：DeepSeek = 磁碟快取 + 數小時 TTL + 無 write cost → agent 框架做 cache-first 設計的 ROI 成立；Anthropic/OpenAI = GPU 記憶體 + 5-10min TTL + 可能有 write cost → ROI 不成立 |
| 讀取 Reasonix benchmarks/README.md | 了解 τ-bench-lite harness 的設計範圍與實際產出 | 取得 task success 相關的 benchmark 數據 | 發現：harness 存在且設計合理（8 tasks、DB predicate、非 LLM judge），但**無公開發布的 task success rate 數字**。僅測量 cache hit rate / cost gap，不測任務完成品質 |
| GitHub search "benchmark task success" in reasonix repo | 搜尋是否有任何公開的 task quality 討論或數據 | 確認是否遺漏任何 benchmark 結果 | 僅找到 1 個結果：#1467「RFC: Core Capability Evaluation Suite」於 2026-05-22 提出——證明社群也意識到目前缺乏能力回歸測試 |
| 讀取 Reasonix bug issues（label:bug, 11 open results） | 蒐集 overengineering 的反面證據（維護負擔、品質問題） | 確認功能廣度是否造成了實際的穩定性問題 | 取得 11 個 open bug：TUI 渲染（#2362, #2379）、桌面端按鈕無回應（#2364）、界面卡頓（#2369）、429 API 錯誤（#2387）、沙箱環境干擾 CLI（#2371）等 |
| 讀取 Reasonix 作者開的 open issues（esengine 本人，10+ results） | 了解核心團隊當前的工程優先級與未完成基礎設施 | 判斷 feature 擴張是否超過核心工程能力 | 取得：LSP-backed symbol nav（#457）、TUI 資訊架構重構（#368）、auto-checkpoint（#407）、feishu/wechat bridge（#410）、discord bridge（#1202）等——大量 RFC/tracking issue 處於 open 狀態，說明核心基礎設施尚未穩定 |
| 讀取 npm package 頁面 | 確認目前版本、下載量、依賴數 | 了解專案當前的社群規模與複雜度 | npm v0.53.2、weekly downloads 24,147、33 dependencies、152 versions |
| 對照 opencode 的設計理念（從現有 AGENTS.md 推測） | 理解 opencode 為何不做 cache-first 設計 | 補足 Q1 的實例對比 | opencode 預設後端為 Claude/GPT，其 cache TTL 短，cache-first 架構的 ROI 不足以支撐框架層級重構 |
| 建立 overengineering 4 面向 × 2 立場（A=是 vs B=否）的證據矩陣 | 對每個面向進行完整的反面論證 | 每個判定都先有 A/B 兩方證據再收斂 | 完成：面向 1（三分區）→ 否、面向 2（repair pipeline）→ 部分是、面向 3（cost control）→ 否（邊界）、面向 4（功能廣度）→ 是 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| Q1 三方 cache 差異的正確性 | 對照三份官方文件（DeepSeek KV cache、Anthropic prompt caching、OpenAI prompt caching） | 三方差異已完整量化：DeepSeek 磁碟快取+數小時 TTL 是 cache-first 設計的唯一前提條件，Anthropic/OpenAI 的短 TTL 使 cache-first 設計的 ROI 不成立。opencode 等工具不需做 cache-first 設計的理由成立 |
| Q2 benchmark 缺失的確認 | 閱讀 benchmarks/README.md + GitHub search「benchmark task success」+ #1467 RFC 討論 | 確認：Reasonix 沒有公開發布的 task success rate benchmark。Harness 存在但僅測量 cache hit/cost，不測任務完成品質。社群 #1467 也認為需要補充能力測試 |
| Q3 overengineering 判定的證據來源可追溯性 | 檢查每個判定引用的證據 | 面向 1：benchmark README + DeepSeek API 文件；面向 2：ARCHITECTURE.md repair pipeline 描述 + bug issues；面向 3：ARCHITECTURE.md 設計演進記錄；面向 4：345 open issues + 11 bugs + 作者開的 RFC/tracking issues |
| 報告更新完整性 | 檢查 v2 報告是否包含 Q1-Q3 的所有新內容 | 第 2 節新增三方 cache 差異對比 + Q1 分析；第 4 節 DA 表更新 cache 相關描述 + 新增 Q2 benchmark 分析段落；新增第 5 節 Overengineering 分析（4 面向 × 2 立場 + 總結判定表 + 適用範圍） |
| 學習紀錄格式符合 AGENTS.md 要求 | 對照已有範例（CodeGraph-C6, EverOS-C4） | 4 區塊（狀況理解/動作與結果/現狀/決斷點）完整，表格格式對齊 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| Q1 回答的證據層級 | (A) 只引用 Reasonix 自己的說法 (B) 三方官方文件交叉對比 | (B) 三方文件交叉對比 | Reasonix 自己的說法「DeepSeek is the only backend where cache-first makes sense」需要外部驗證。對比 Anthropic TTL 5min / OpenAI auto-cache / DeepSeek disk cache + hours TTL 的差異，可客觀證明此主張 |
| Overengineering 分析的面數 | (A) 整體二元判定 (B) 拆解為 4-5 個獨立面向各自判定 | (B) 拆解為 4 個面向 | 遵循 EverOS-C4 的先例（5 技術各自分析 overengineering）。Reasonix 的複雜度不適合單一結論——核心架構和功能廣度的 overengineering 程度不同。拆解後結論更精確 |
| 反面論證的格式 | (A) 文字段落 (B) 立場 A vs B 表格 | (B) 立場 A vs B 表格 | 遵循 CodeGraph-C6 的先例。表格格式使反方/正方證據對比可視化，避免論述偏袒。每個面向的判定基於 A/B 證據矩陣收斂 |
| Overengineering 總結是否給出場景收斂 | (A) 只判定不給場景 (B) 給出「適合/不適合」的場景對照 | (B) 給出場景對照 | 使用者要求「總結出真正的結論與適用範圍」。僅說「是/否 overengineering」不足，需要具體指出何種場景下 Reasonix 是合適選擇、何種場景下不是 |
| Tool-call repair 的 partial overengineering 判定 | (A) 全部四 pass 都判定為不必要 (B) 區分 flatten+scavenge（過度）vs storm+truncation（合理） | (B) 區分判定 | ARCHITECTURE.md 對四 pass 的說明各有不同技術理由。flatten 處理 >10 param schema（極低頻場景）、scavenge 修補模型缺陷（應該由 API 端解決），兩者與 storm/truncation（通用 guard）有本質差異，不適合一刀切 |
| 功能廣度 overengineering 的判定依據 | (A) 主觀評價多 vs 少 (B) 以 open issues 數量、prerelease 狀態、核心團隊規模為客觀證據 | (B) 客觀證據 | 345 open issues + 桌面端 prerelease（未簽章）+ 僅 9 核心貢獻者 + 多個 RFC/tracking issue 未完成，是功能廣度超過維護能力的客觀信號，不依賴主觀感受 |
