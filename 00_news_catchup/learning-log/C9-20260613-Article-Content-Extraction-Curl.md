# C9-20260613-Article-Content-Extraction-Curl

## 狀況理解
Step 2 產出 33 篇待抓取文章（排除 2 篇 SKIP）。需用 `html2text.py` 對每篇 URL 抓取 raw 文字內容。`html2text.py` 不存在，需先建立。預期 NYT、FastCompany 等付費牆媒體會失敗，需在 Step 4 處理。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 建立 `_scripts/html2text.py`（純 stdlib） | 提供 URL→text 的提取工具 | 找 `<article>`/`<main>` 容器，排除 script/style/nav/header/footer | 成功建立，fallback 機制（最大 div 文本塊）有效 |
| 建立 `_scripts/batch_fetch.py` 批次執行 | 對 33 篇文章平行抓取 | 每篇回傳 title + text + error status | 33 篇全數執行，31 篇成功，2 篇失敗 |
| 測試 html2text.py 在 Spring AI、TWIR、NYT 的行為 | 驗證提取品質 | Spring AI/TWIR 完整提取，NYT 僅 preview | Spring AI 10000 chars, TWIR 10000 chars, NYT 2405 chars (preview) |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 成功率 | 33 篇中成功數 | 31 篇成功（含 NYT preview），2 篇 FastCompany 403 |
| 內容品質 | 抽查 text length 與內容相關性 | 技術文章（Spring AI, scikit-learn, TWIR）品質佳；feedblitz 只有 19 chars（link aggregator）；digiday.jp 只有 94 chars（JS 渲染頁面） |
| 失敗清單 | 記錄需 Step 4 處理的文章 | FastCompany 403 × 2, feedblitz 短內容, digiday.jp 短內容 × 2, NYT paywall × 2, Medium 短內容 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| html2text 實作方式 | (A) 使用 trafilatura/goose3 等外部庫 (B) 純 stdlib 自建 | 選擇 (B) | AGENT.md 明確要求純 stdlib；自建 parser 可控性更高 |
| 短內容處理 | (A) 立即標記失敗 (B) 保留內容等 Step 4 CDP 補足 | 選擇 (B) | 短內容仍有 snippet 資訊可用；CDP 可解決 JS 渲染問題 |
| 批次執行方式 | (A) 平行 async (B) 循序執行 | 選擇 (B) | 避免對目標伺服器造成壓力；html2text.py 是 subprocess 呼叫，平行化複雜度不划算 |
