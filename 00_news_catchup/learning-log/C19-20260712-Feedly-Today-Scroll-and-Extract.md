# C19-20260712-Feedly-Today-Scroll-and-Extract

## 狀況理解
Feedly Today 區需透過 lazy-load scroll 載入全部文章。頁面結構為 `#feedlyFrame` 內的 scrollable div，需連續 `scrollTop = scrollHeight` 觸發載入。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| cdp_navigate 到 feedly.com/i/my/me | 進入 Feedly 個人頁面 | 載入 Today 文章列表 | 成功載入，頁面 title 為 "Feedly – Keep up with the topics and trends you care about" |
| JS 搜尋 scrollable div (overflow-y:auto, scrollHeight > clientHeight + 50, children.length===2) | 定位 Today 區的 scroller | 找到目標容器 | 找到 `#feedlyFrame` (scrollHeight=2331, clientHeight=862, children=2) |
| 連續 2 輪 scrollTop = scrollHeight + sleep 600ms | 觸發 lazy load 載入全部文章 | scrollTop 不再變化時停止 | 第 1 輪: 0→1469 (articleCount: 12→34), 第 2 輪: 1469→5605 (articleCount: 34), 第 3 輪: 5605→5605 (scrollHeight 不變, 停止) |
| JS 提取所有 article 的 a[href*="://"] + 標題文字 | 收集文章連結和標題 | 產出 _articles.csv | 成功提取 34 篇文章 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 文章數量 | 最終 articleCount = 34 | 34 篇，符合預期 |
| 資料完整性 | 每篇有 url, title, host, snippet | 全部 34 篇欄位完整 |
| _articles.csv 產出 | 寫入檔案 | 成功寫入 34 行資料 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| scroller 定位方式 | (1) 用 AGENTS.md 指定的條件 (overflow-y:auto + scrollHeight > clientHeight + 50 + children.length===2) (2) 用 class name 硬編碼 | 選 (1) | 遵循 AGENTS.md 規範，避免 class name 變更導致失效 |
| scroll 停止條件 | (1) scrollTop 不再變化 (2) articleCount 不再增加 | 選 (1) | AGENTS.md 指定用 scrollTop 判斷 |
