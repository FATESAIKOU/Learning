# C8-20260613-Article-Classification

## 狀況理解
Step 1 產出 35 篇文章的 `_articles.csv`。需依 AGENT.md §2 分類規則將每篇歸入 AI技術 / 傳統IT技術 / 政治經濟 / SKIP，衝突時優先級 AI技術 > 政治經濟 > 傳統IT技術，且 source 為政治經濟媒體（NYT, Fortune, Bloomberg 等）即使標題含 AI 也歸政治經濟。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 逐篇檢查 title 關鍵字 + host 媒體類型 | 依分類規則矩陣進行歸類 | 每篇有明確 category | 35 篇全部分類完成 |
| 對衝突案例套用優先級規則 | 處理跨類別關鍵字文章 | 正確優先級排序 | digiday.jp 的 AI 廣告文章（title 含 AI 但 source 非政治經濟媒體）歸 AI技術；NYT 的 SpaceX/AI 文章歸政治經濟 |
| 標記 Reddit 個人 post 為 SKIP | 排除無法抓取內容的文章 | 減少 Step 3/4 的失敗處理 | 2 篇 Reddit 標記 SKIP（motion capture, continual learning） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 分類覆蓋率 | 35 篇中 SKIP 以外全部分類 | AI技術 7 篇, 傳統IT技術 7 篇, 政治經濟 19 篇, SKIP 2 篇 |
| 分類正確性 | 抽查邊界案例（NYT AI 文章、digiday.jp AI 文章） | NYT 正確歸政治經濟；digiday.jp 正確歸 AI技術（非政治經濟媒體） |
| CSV 更新 | `_articles.csv` 新增 category 欄位 | 格式正確，覆蓋原檔 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| digiday.jp 分類 | (A) AI技術 (B) 政治經濟 | 選擇 (A) | digiday.jp 是行銷媒體非政治經濟媒體（非 NYT/Fortune/Bloomberg 等級），title 含 AI 關鍵字，依規則歸 AI技術 |
| 政治經濟類文章數量 | (A) 全部 19 篇都做 Step 3 (B) 預先篩選高相關 | 先全做 Step 3，Step 5 再篩選 | Step 2 只負責分類不負責篩選；篩選邏輯留給 Step 5 依用戶 profile 判斷 |
