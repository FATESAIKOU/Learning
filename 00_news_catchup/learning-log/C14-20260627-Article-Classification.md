# C14-20260627-Article-Classification

## 狀況理解
Step 2 需要對 _articles.csv 中的 33 篇文章依標題關鍵字 + source 媒體類型進行分類。分類規則：AI技術（含 AI/LLM/Agent 等關鍵字且非政治媒體）、傳統IT技術（含程式語言/框架/開發工具）、政治經濟（其他）。衝突時 AI技術 > 政治經濟 > 傳統IT技術。政治經濟媒體（NYT, Fortune, NBC, Bloomberg 等）即使標題含 AI 也歸政治經濟。Reddit 跳過。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|------------|-----------|-------------|-----------|
| 第一版分類（簡單 substring 匹配） | 快速分類 | 正確分類 | 失敗：`available` 中的 "ai" 被誤匹配為 AI 關鍵字 |
| 第二版分類（regex word boundary `\b`） | 修正英文單詞邊界 | 正確匹配英文關鍵字 | 部分修正，但 CJK 字元旁 `\b` 失效 |
| 第三版分類（自訂 `(?<![a-zA-Z0-9])word(?![a-zA-Z0-9])` 邊界） | 同時處理英文和 CJK 邊界 | 正確匹配 | 成功 |
| 加入日本商業媒體到政治經濟清單 | 正確分類日本媒體文章 | biz-journal, markezine, advertimes, digiday 歸政治經濟 | 成功 |
| 加入 semafor.com 到政治經濟清單 | 新聞媒體應歸政治經濟 | semafor 文章歸政治經濟 | 成功 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 分類數量 | AI技術:5, 傳統IT技術:7, 政治經濟:20, SKIP:1 | 總計 33 篇（含 1 篇跳過） |
| Spring Boot 3.5.16 | 不應匹配 AI（available 含 "ai"） | 正確歸類為 傳統IT技術 |
| aibo 文章 | 不應匹配 AI（aibo 含 "ai"） | 正確歸類為 政治經濟 |
| NYT/NBC/Fortune Anthropic 文章 | 政治媒體即使含 AI 也歸政治經濟 | 正確歸類為 政治經濟 |
| Reddit 文章 | 應跳過 | 正確標記為 SKIP |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 日本媒體分類 | 1. 全部歸政治經濟 2. 依內容判斷 | 全部歸政治經濟 | AGENTS.md 規則：source 為政治/經濟媒體歸政治經濟。markezine/advertimes/digiday 為商業/廣告媒體 |
| semafor.com 分類 | 1. 依標題（含 Anthropic/Mythos AI）歸 AI技術 2. 歸政治經濟 | 歸政治經濟 | semafor 是新聞媒體，類似 NYT/Fortune，即使標題含 AI 也歸政治經濟 |
| メルカリ×ChatGPT 文章 | 1. 歸 AI技術（含 ChatGPT） 2. 歸政治經濟（biz-journal 是商業媒體） | 歸政治經濟 | source 為 biz-journal.jp（商業媒體），依規則歸政治經濟 |
