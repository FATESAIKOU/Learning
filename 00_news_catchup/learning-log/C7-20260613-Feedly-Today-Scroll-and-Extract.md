# C7-20260613-Feedly-Today-Scroll-and-Extract

## 狀況理解
使用者要求執行 Feedly Today 的完整 catchup 流程。Step 1 的目標是從 `https://feedly.com/i/my/me` 的 Today 區抓取所有文章連結與標題。CDP browser 已在 localhost:9222 運行，Feedly 頁面已開啟。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 建立 `_scripts/cdp_helper.py` 直接透過 WebSocket 操作 CDP | 繞過 MCP 工具限制，直接使用 Chrome DevTools Protocol | 可 navigate、scroll、eval JS、extract articles | 初版因 flatten mode 的 event interleaving 導致 KeyError，修正後成功 |
| 找到 Today 區的 scroller div (`overflow-y:auto`, `scrollHeight > clientHeight + 50`) | 定位需要 lazy-load 滾動的容器 | 精準滾動目標區域 | 找到 scrollHeight=2101, clientHeight=600 的 div |
| 連續 `scrollTop = scrollHeight` 15 輪，每輪 sleep 600ms | 觸發 Feedly 的 lazy load 機制載入全部文章 | scrollHeight 不再變化時停止 | 4 輪後 scrollHeight 穩定在 6785，共載入 35 篇文章 |
| `querySelectorAll('article')` + 提取 `a[href*="://"]` 與標題文字 | 結構化提取所有文章資料 | idx, url, title, host, snippet | 成功提取 35 篇，含完整 metadata |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 文章數量 | 比對 Feedly UI 顯示的文章數與提取數 | 35 篇，涵蓋 AI/IT/政經/車輛/運動等多領域 |
| 資料完整性 | 檢查每篇文章是否有 url, title, host, snippet | 全部 35 篇欄位完整 |
| 產出檔案 | `_articles.csv` 存在且格式正確 | 符合 AGENT.md 指定的 CSV 格式 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| CDP 操作方式 | (A) 使用 MCP server 的 cdp_* 工具 (B) 直接 WebSocket + CDP protocol | 選擇 (B) | MCP 工具未在 opencode.json 中配置；`websockets` library 可用，直接控制更靈活 |
| 滾動策略 | (A) 滾動整個 window (B) 找到 scroller div 精準滾動 | 先 (B) 後 fallback (A) | AGENT.md 指定找 `overflow-y:auto` 的 div；找到後精準滾動效率更高 |
| 提取粒度 | (A) 只取 url+title (B) 加 snippet 輔助後續分類 | 選擇 (B) | snippet 對 Step 2 的分類判斷有輔助價值 |
