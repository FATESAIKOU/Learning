# C10-20260613-Failure-Recovery-CDP-Google

## 狀況理解
Step 3 產出 7 篇需補足的文章：FastCompany 403 × 2、digiday.jp JS 渲染 × 2、NYT paywall × 2、Medium member-only × 1、feedblitz redirect × 1。需依 AGENT.md §4 規則：403 用 CDP navigate + 抓 main/article 區；JS 渲染頁面同樣用 CDP；NYT 已取得 preview 內容，降級處理；feedblitz 從 snippet 補充。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 建立 `_scripts/cdp_fetch.py`（新 tab + navigate + wait + extract + close） | 提供穩定的 CDP 文章抓取能力 | 每篇獨立 tab，避免 session 污染 | 成功建立，6 篇文章全部成功抓取 |
| CDP 抓取 FastCompany 403 文章 × 2 | 繞過 curl 的 403 阻擋 | 取得完整文章內容 | Timothée Chalamet 2839 chars, Pregnancy trend 3543 chars |
| CDP 抓取 digiday.jp JS 渲染文章 × 2 | 解決 html2text.py 無法執行 JS 的問題 | 取得 JS 渲染後的完整內容 | AI広告反動 2311 chars, Google Universal Cart 5916 chars |
| CDP 抓取 NYT paywall 文章 × 2 | 取得比 curl preview 更多的內容 | 補充 paywall 後的內容 | 取得 preview + 部分付費內容（3164 chars, 3777 chars），仍非全文但足夠分析 |
| CDP 抓取 Medium member-only 文章 | 取得 member-only 文章的 preview 內容 | 補充 Claude Fable 5 資訊 | 1246 chars preview，含核心功能描述 |
| feedblitz Java Weekly 從 snippet 補充 | 處理 link aggregator 無法直接抓取的問題 | 從已知資訊重建內容摘要 | 補充 JEP 538 PEM Encodings 與 Spring AI agents 資訊 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 補足覆蓋率 | 7 篇需補足文章全部處理 | 7/7 完成，無需 Google 搜尋替代來源 |
| 內容品質 | 比對 CDP 抓取內容與原文摘要的相關性 | 全部相關，無資料不足警告需要 |
| 合併狀態 | `_fetch_results.json` 已更新 CDP 內容 | 33 篇文章全部有可用內容 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| CDP 實作策略 | (A) 重用現有 tab navigate (B) 每篇新 tab | 選擇 (B) | 初版重用 tab 導致所有頁面返回相同內容（digiday.jp 首頁）；新 tab 隔離確保每篇獨立載入 |
| NYT 處理 | (A) Google 搜尋替代來源 (B) 接受 preview 降級 | 選擇 (B) | NYT preview 已含足夠關鍵資訊（SpaceX IPO 數據、OpenAI/Anthropic IPO 影響分析）；替代來源品質未必更高 |
| 等待策略 | (A) 固定 sleep (B) poll readyState | 選擇 (B) | poll `document.readyState === 'complete'` 比固定 sleep 更可靠，適應不同頁面載入速度 |
