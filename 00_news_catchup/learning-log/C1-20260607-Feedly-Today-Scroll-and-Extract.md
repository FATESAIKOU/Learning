# C1-20260607-Feedly-Today-Scroll-and-Extract

## 狀況理解

使用者指示執行 Feedly Today 區報吿,起始動作為開啟 CDP 瀏覽器並導航到 `https://feedly.com/i/my/me`,接著需要把 Today 區所有文章抽出成連結一覽表。Feedly 預設介面是 SPA + infinite scroll,不能簡單的 `navigate` 後讀 DOM,必須先觸發滾動以 lazy-load 所有文章。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|------------|------------|--------------|------------|
| `bash start_browser.sh` 啟動 Chrome + CDP server | 準備瀏覽器自動化環境 | Chrome 跑在 CDP 9222,Cookies/登入狀態保留 | 成功,CDP endpoint 200 |
| `cdp_navigate` 到 `https://feedly.com/i/my/me` | 進入 Feedly Today 區 | 頁面標題「受信トレイ」,看到文章列表 | 成功,標題正確 |
| `cdp_screenshot` 全頁 + 視覺驗證 UI | 確認 Today/Me/Explore tabs 與「1–50 / 19,751 行」分頁指示器存在 | 看到分頁 UI 結構 | 成功,看到「<」「>」按鈕 |
| `cdp_evaluate` 找 scroller (`div.overflowY:auto`, `scrollHeight > clientHeight + 50`, `children===2`) | 找到內部 scroller | 該 div 為文章列表容器 | 找到 `div.Tm.aeJ` |
| `cdp_evaluate` 跑 20 輪 `scrollTop = scrollHeight` 迴圈,每輪 sleep 600ms | 觸發 lazy load 把全部文章載入 DOM | scrollTop 停止變化表示到底 | 20 輪後 `scrollTop=5857, scrollHeight=6719`,到底 |
| `cdp_evaluate` 抓所有 `article` 元素的 `a[href*="://"]` + 標題 | 產出 article metadata | 35 個 article | 抓到 35 個 (與 Feedly 預期一致) |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|------------|------------------|----------|
| 連結數量 | `find tr` 或 `document.querySelectorAll('article')` 計數 | 35 個 article 元素 (符合 Feedly 預期) |
| 連結內容完整性 | 過濾 `feedly.com` 後剩餘非內部連結 | 34 個 (1 個 feedblitz redirect) |
| 標題抓取 | 每個 article 內 `h*` 標題文字 | 全部抓到,中文/英文/日文混合 |
| 是否需要重抓 | 對照 `1–50` 預期 vs 抓到數量 | 一致,無需重跑 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|--------------|--------------|----------|----------|
| 分頁擷取方式 | A) 點「>」按鈕逐頁 navigate<br>B) 連續 `scrollTop = scrollHeight` 一次到底<br>C) `cdp_key('g')` + `cdp_key('o')` 鍵盤序列 | B | A 點按鈕需先抓到精確座標(我點錯過),B 在一次 evaluate 內完成,失敗風險最低;Gmail hash `#inbox/p2` 證明可直連跳頁但 SPA 對 hash 跳 page 反應不一 |
| 文章 metadata 抓取時機 | A) 滾動結束後一次抓<br>B) 邊滾邊抓 | A | Feedly 用 React 渲染,DOM 結構穩定;一次抓取所有 35 筆效率最高,避免 race condition |
| 連結過濾規則 | A) 排除所有 `feedly.com`<br>B) 只排除內部路徑 (`/i/`、`/u/`) | A | 抓到的連結都不含內部路徑前綴,A 更簡潔 |
| scroller 識別 | A) `document.scrollingElement`<br>B) 找特定 selector<br>C) 找所有 overflow-y:auto 的 div 中最長的 | C | document 是整頁(無 overflow),Gmail 與 Feedly 都用內部 div,C 通用 |
