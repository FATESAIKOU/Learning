# C22-20260712-Failure-Recovery-CDP-and-Google

## 狀況理解
Step 3 中 NYT 文章 (idx 19, 23) 因 paywall 截斷內容。需依 AGENTS.md §4 用 CDP navigate 嘗試抓取，失敗則用 Google 搜尋替代來源。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| cdp_navigate 到 NYT opinion (idx 19) | 嘗試繞過 paywall 抓全文 | 取得完整文章內容 | 仍被 paywall 截斷，僅取得約 30% 預覽內容 |
| cdp_navigate 到 NYT Apple-OpenAI (idx 23) | 嘗試繞過 paywall 抓全文 | 取得完整文章內容 | 仍被 paywall 截斷，僅取得約 40% 預覽內容 |
| Google 搜尋 "Apple sues OpenAI stealing company secrets 2026" | 找替代來源 | 找到非 paywall 的完整報導 | 找到 The Guardian, BBC, Reuters, CNBC 等多家替代來源 |
| curl The Guardian 替代文章 | 抓取完整替代內容 | 取得 Apple-OpenAI 訴訟完整報導 | 成功抓取 The Guardian 全文，寫入 raw_23_alt.txt |
| Google 搜尋 "World cutting ties with America Trump NATO Europe de-risking 2026" | 找 NYT opinion 替代來源 | 找到同主題分析 | 找到 POLITICO, Project Syndicate, NPR 等相關文章，但無直接替代 |
| curl NPR NATO summit 文章 | 補充背景資訊 | 提供 NATO 峰會背景 | 成功抓取 NPR 文章，作為 NYT opinion 的背景補充 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| idx 23 (Apple-OpenAI) 替代來源 | The Guardian 全文 | 成功，subagent 使用 Guardian 為主要來源 |
| idx 19 (NYT opinion) 處理 | 標記 ⚠️ 資料不足 + NPR 背景補充 | 降級處理，subagent 基於 snippet 推測分析 |
| 替代來源標記 | 分析 .md 開頭加註原 URL 和替代來源 | 已正確標記 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| NYT opinion 替代來源選擇 | (1) POLITICO (2) Project Syndicate (3) NPR (4) 降級為資料不足 | 選 (4) + (3) 背景補充 | POLITICO/Project Syndicate 均 404，NPR 主題不同（NATO 峰會報導 vs 全球去美國化分析），無法直接替代 |
| Apple-OpenAI 替代來源選擇 | (1) The Guardian (2) BBC (3) Reuters (4) CNBC | 選 (1) | The Guardian 內容最完整，包含訴訟細節、時間線、雙方回應 |
