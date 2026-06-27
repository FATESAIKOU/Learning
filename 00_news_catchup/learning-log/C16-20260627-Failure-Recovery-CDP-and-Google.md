# C16-20260627-Failure-Recovery-CDP-and-Google

## 狀況理解
Step 4 需補救 6 篇 curl 失敗的文章：OpenAI GPT-5.6（JS 渲染 dots）、2 篇 NYT（paywall 預覽）、fastcompany（403）、2 篇 Medium（member-only snippet）。依 AGENTS.md：NYT/fastcompany 用 CDP navigate + 抓 main/article 區；OpenAI 反爬用 CDP 開 Google 搜尋替代來源；Medium 降級為短文 + 資料不足警告。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|------------|-----------|-------------|-----------|
| CDP navigate OpenAI 頁面 + 多 selector 嘗試 | 繞過 JS 反爬 | 取得文章內容 | 失敗，頁面內容為 dots（反爬機制） |
| CDP Google 搜尋 "GPT-5.6 Sol OpenAI preview" | 找替代來源 | 找到可讀的替代文章 | 成功，找到 help.openai.com 的完整文檔 |
| CDP navigate help.openai.com | 抓取替代來源內容 | 取得完整 GPT-5.6 資訊 | 成功，7339 chars 完整內容 |
| CDP navigate NYT Mythos 文章 | 繞過 paywall | 取得文章內容 | 成功，3118 chars（含部分廣告截斷） |
| CDP navigate NYT SCOTUS 文章 | 繞過 paywall | 取得文章內容 | 成功，2695 chars |
| CDP navigate fastcompany 文章 | 繞過 403 | 取得文章內容 | 成功，2558 chars |
| CDP navigate Medium 文章 ×2 | 取得完整內容 | 取得全文 | 部分成功，member-only 僅有 snippet（1396/1451 chars） |
| 委派 subagent 生成 6 篇 4 點分析 | 補足分析 | 6 篇分析 .md | 成功，替代來源加註、資料不足加警告 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 補救文章數 | find 20260627-*.md 總數 | 32 篇全部分析完成 |
| 替代來源標記 | grep "替代來源" | OpenAI GPT-5.6 正確標記 |
| 資料不足警告 | grep "資料不足警告" | Medium 2 篇正確標記 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| OpenAI 反爬處理 | 1. 放棄 2. Google 搜尋替代來源 3. 用其他 CDP 技巧 | Google 搜尋替代來源 | AGENTS.md 規定反爬失敗改用 Google 搜尋同主題新聞源 |
| Medium member-only 處理 | 1. 跳過 2. 降級為短文+警告 | 降級為短文+警告 | AGENTS.md 規定仍找不到降級為短文+標明資料不足 |
| NYT paywall 處理 | 1. curl 2. CDP navigate | CDP navigate | AGENTS.md 規定 NYT 403 改用 cdp navigate + 抓 main/article 區 |
