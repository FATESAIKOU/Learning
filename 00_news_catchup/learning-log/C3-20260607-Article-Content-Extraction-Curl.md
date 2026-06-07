# C3-20260607-Article-Content-Extraction-Curl

## 狀況理解

33 個 article 已分類,需要抓取每篇 raw 文字內容供 4 點解析使用。考慮到 cdp 每次 navigate + get_text 約 4-5 秒且內容回傳到 context 佔 token,改用 `curl + python html2text.py` 批次抓取,把 raw 寫入本地檔。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|------------|------------|--------------|------------|
| 寫 `_scripts/html2text.py` 純 stdlib extractor | 提供 URL→Markdown 轉換,排除 nav/aside/header/footer | 32-34 篇成功抓取 | 32 篇成功,2 篇 Reddit 失敗 |
| 寫 `_scripts/fetch_all.sh.py` 批次跑 35 個 URL | 自動化批次抓取 + 寫入對應類別目錄 | ~10-30 秒完成 | 9 秒完成,34/35 成功,1 NYT 403 |
| 對 NYT 20 改用 cdp navigate + 抓 `article, main, [data-testid="article-body"]` | 繞過 curl 403 | 抓 6000 字 | 成功抓到 |
| 對 Reddit 21, 22 確認 cdp 也被擋 (network security 頁) | 驗證 fallback 不可行 | 確認跳過 | 確認,寫入 `_失敗.md` |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|------------|------------------|----------|
| 抓取成功率 | `wc -c` 每個 raw .md | 32 篇 > 1KB,2 篇 Reddit 0 KB (只有 "Blocked" 訊息) |
| 抓取耗時 | shell 時間測量 | 9 秒完成 32 篇 (curl 模式) |
| 內容品質 | 抽樣檢視 02_Spring_AI.md 開頭 100 字 | 完整、無 nav 雜訊、有正確標題 |
| 失敗清單完整性 | 對照 articles.csv 35 行 vs 抓取結果 32 行 | 3 篇失敗:NYT 20 (cdp 補成功) + Reddit 21, 22 (跳過) |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|--------------|--------------|----------|----------|
| 抓取工具 | A) cdp navigate + get_text (慢、佔 context)<br>B) webfetch (token 爆炸)<br>C) curl + 自寫 html2text (0 token) | C | 32 篇 × cdp 5 秒 = 160 秒且 context 吃緊;curl 9 秒完成 32 篇 |
| html2text 套件 | A) `html2text` pip<br>B) `lynx` / `w3m`<br>C) 自寫 stdlib | C | 環境無 A,無 B;stdlib 的 `html.parser` + `re` 可達 80% 效果 |
| Raw 內容寫入位置 | A) 各類別目錄根 (例 `AI技術/02_xxx_raw.md`)<br>B) `_raw/` 子目錄 | A | 後續要依類別目錄處理,扁平化省事 |
| Reddit 失敗處理 | A) 嘗試各種 UA 與 old.reddit<br>B) 跳過 | B | 試了 old.reddit、.json、.rss 都被封,內容為個人 post,跳過 |
| 抽取 main/article 容器 | A) 嚴格 `<article>`<br>B) 加 fallback `<main>`,`<div class="body">`,最大 div | B | 2 個靜態 HTML 站 (lucumr/sethmlarson) 沒 `<article>`,fallback 抓到;3 站 (DoD, 計画) raw 偏長因 fallback 抓整個 body,後續 4 點解析仍可用 |

## 後續影響

- 步驟 6 (清理) 會刪除所有 raw .md
- 步驟 4 對失敗清單的 cdp 補充是必要 fallback,但**不建議**作為常規抓取手段
- html2text 對 JS-rendered 頁 (Reddit 21/22) 完全無解,需 cdp 真實瀏覽才能處理,但本次跳過
