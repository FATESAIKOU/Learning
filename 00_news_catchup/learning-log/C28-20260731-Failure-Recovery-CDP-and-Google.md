# C28-20260731-Failure-Recovery-CDP-and-Google

## 狀況理解
Step 4 需補救 4 篇 curl 失敗的文章：codezine ×2（IBM 量子、Google Docs Gemini，安全檢查頁面）、markezine ×2（TikTok 廣告、AEO，CAPTCHA）。依 AGENTS.md：CDP navigate + 抓 main/article 區；反爬完全失敗改用 Google 搜尋替代來源；仍找不到降級為短文+資料不足警告。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|------------|-----------|-------------|-----------|
| CDP navigate codezine IBM 量子 | 繞過安全檢查 | 取得文章內容 | 失敗，頁面為安全檢查頁 |
| CDP Google 搜尋 IBM HRL 買収 | 找替代來源 | 找到可讀的替代文章 | 成功，找到 note.com（部分付費）和 investing.com |
| CDP navigate note.com | 抓取替代來源 | 取得 IBM HRL 買収資訊 | 部分成功，取得開頭部分（付費截斷） |
| CDP navigate codezine Google Docs | 繞過安全檢查 | 取得文章內容 | 失敗 |
| CDP Google 搜尋 Google Docs Gemini | 找替代來源 | 找到 rakumo.com 的 Google Workspace 7月アップデート | 成功，取得完整 Gemini in Docs/Sheets/Slides 資訊 |
| CDP navigate markezine ×2 | 繞過 CAPTCHA | 取得文章內容 | 失敗，CAPTCHA 阻擋 |
| CDP Google 搜尋 TikTok 広告 / AEO | 找替代來源 | 找到替代文章 | 替代來源不夠精確，降級為資料不足 |
| 委派 subagent 生成 4 篇分析 | 補足分析 | 4 篇分析 .md | 成功，替代來源加註、資料不足加警告 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 補救文章數 | find 20260731-*.md 總數 | 32 篇全部分析完成 |
| 替代來源標記 | grep "替代來源" | IBM 量子、Google Docs Gemini 正確標記 |
| 資料不足警告 | grep "資料不足警告" | markezine 2 篇正確標記 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| codezine 安全檢查處理 | 1. 放棄 2. Google 搜尋替代來源 | Google 搜尋替代來源 | AGENTS.md 規定反爬失敗改用 Google 搜尋 |
| markezine CAPTCHA 處理 | 1. 手動解 CAPTCHA 2. Google 搜尋 3. 降級為資料不足 | 降級為資料不足 | 替代來源不夠精確，AGENTS.md 規定降級為短文+警告 |