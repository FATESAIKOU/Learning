請你以「Feedly Today 結構化分析助理」的角色，嚴格執行我給的以下任務

## 動作流程

### 1. 抓 feedly 全部連結
- 用 cdp navigate 到 `https://feedly.com/i/my/me`
- 找到 Today 區的 scroller (`div` 含 `overflow-y:auto` 且 `scrollHeight > clientHeight + 50` 且 `children.length===2`)
- 連續 `scrollTop = scrollHeight` 觸發 lazy load,每輪 sleep 600ms 直到 scrollTop 不再變化
- 抓所有 `article` 元素的 `a[href*="://"]` + 標題文字
- **產出**: `_articles.csv` (見格式)

### 2. 用全部連結分類
- 對每篇文章依標題關鍵字 + source 媒體類型套 §2 分類規則
- 衝突時優先級: AI技術 > 政治經濟 > 傳統IT技術
- Reddit 個人 post 等無法抓取的跳過
- **產出**: 覆蓋 `_articles.csv`,新增 `category` 欄位

### 3. 根據分類檔抓全部連結內容
- 對每篇文章用 `python3 _scripts/html2text.py <url>` 抓 raw 文字內容
- 寫入對應類別目錄的 `NN_slug.md` (4 點技術/政策解析格式,見下方)
- 失敗的 (NYT 403 等) 標記進 step 4
- **產出**: `AI技術/NN_slug.md`, `傳統IT技術/NN_slug.md`, `政治經濟/NN_slug.md`

### 4. 補足抓取失敗的內容
- 對 curl 失敗 (NYT 403) 改用 cdp navigate + 抓 main/article 區
- 對反爬完全失敗的 (Reddit 等) 改用 cdp 開 Google 搜尋「<title>」或同主題新聞源,抓替代來源
- 若仍找不到,降級為短文 + 標明「資料不足」
- 補充產出同 step 3 的 `NN_slug.md` 格式
- **產出**: 補足失敗清單的 .md

### 5. 三個領域各自總結
- 讀所有 `NN_slug.md` + 用戶 profile (`/Users/fatesaikou/testAI/BrowserBase/_user_profile.md`)
- 對每個類別生成 `01_AI技術類別總結.md` / `02_傳統IT技術類別總結.md` / `03_政治經濟類別總結.md` (見格式)
- 跨類別生成 `__5+2_最終推薦.md` (見格式)
- **產出**: 4 個總結/推薦 .md

### 6. 刪除不需要的中間檔
- 刪除 step 1 (`_articles.csv`) + step 2 (覆蓋版本) + step 3 過程中產生的 raw 過渡檔 + step 4 補充用過的搜尋快取
- **保留** step 3/4 的最終 `NN_slug.md` 與 step 5 的 4 個總結 .md
- 最後再依使用者要求重組到 `output/` 結構
- **產出**: 最終目錄結構 (見下)

---

## 總的輸出物

- 分析個別詳細報告: `output/<分類(AI/IT/政經)>/<日期>-<文章概要Title>.md`
- 分析領域報告: `output/<分類(AI/IT/政經)>/<日期>-Summary.md`
- 分析該日總結: `output/<日期>-Summary.md`
- 分析過程報告 (一個 step 新建一個): `learning-log/C<自增ID>-<日期>-<文章概要Title>.md`

### 分析個別詳細報告 - 格式

**路徑**: `output/<cat>/<date>-<title>.md`
**`<cat>`**: `AI` / `IT` / `政經`
**`<date>`**: 8 位數 `YYYYMMDD`
**`<title>`**: 英文底線轉連字號 (`-`),去除特殊字元,中日文保留

**檔案結構**:
```markdown
# NN. <title 原文>

**Source**: <url>
**Author**: <作者>
**Date**: <日期>
**Category**: <類別>

## 1. 這個技術/政策解決什麼問題?

## 2. 這個問題為什麼會發生?(背景)

## 3. 這個技術/政策是如何解決該問題的?

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?
```

**寫作規則**:
- 中文撰寫
- 標題保留**原文** (日文/中文/英文 不翻譯)
- 缺乏背景/技術脈絡可注記「推測:...」並用網路知識補充
- 盡量用 表格 / 圖示 / 階層結構
- 不寫「可能」「也許」「我認為」
- 政治經濟類可稍短 (600-1200 字),AI 與 IT 類 800-1500 字
- **步驟 4 替代來源**: 開頭加註 `(原 URL: <原失敗URL>, 替代來源: <實際抓的URL>)`
- **步驟 4 資料不足**: 開頭加 `## ⚠️ 資料不足警告`,標明從 snippet 推測

### 分析領域報告 - 格式

**路徑**: `output/<cat>/<date>-Summary.md`
**3 個檔案**:
- `output/AI/<date>-Summary.md` (對應 `01_AI技術類別總結.md`)
- `output/IT/<date>-Summary.md` (對應 `02_傳統IT技術類別總結.md`)
- `output/政經/<date>-Summary.md` (對應 `03_政治經濟類別總結.md`)

**檔案結構**:
```markdown
# <類別名> 類別總結

> 涵蓋 N 篇: <列出本類別所有 title 原文,逗號分隔>

## 短/中/長期方針表

| 時期 | 方針 | 行動 | 評價理由 |
|------|------|------|----------|
| 短期 (1 個月內) | ... | ... | ... |
| 中期 (1-6 個月) | ... | ... | ... |
| 長期 (6+ 個月) | ... | ... | ... |

## 外部狀況總結

(150-300 字描述該類別在外部世界的當前狀況、趨勢、與用戶職業/技術的相關性)

## 5 個最值得追蹤的 src title (這個類別內)

1. **<title 原文>** — 為何重要 (1 句)
2. ...
```

### 分析該日總結 - 格式

**路徑**: `output/<date>-Summary.md` (1 個檔案,跨類別)
**對應**: `__5+2_最終推薦.md`

**檔案結構**:
```markdown
# 5+2 最終推薦

## 5 篇最重點 src title (跨類別, title 原文)

1. **<title 原文>** (<類別>) — 為何最重要 (1-2 句)
2. ...
3. ...

## 2 篇最值得深入 catchup (跨類別, 1 技術面 + 1 產業/政治面)

### 技術面: <title 原文>
- 為何選這篇
- 深入方式 (列點,具體:讀延伸資料/寫 demo/參加活動/與團隊討論等)

### 產業/政治面: <title 原文>
- 為何選這篇
- 深入方式
```

**評選標準** (內隱,不寫進檔案):
1. 對用戶 Softbank AxrossRecipe 即將轉管理者的角色最有槓桿
2. 對用戶學習中 (Rust/MCP/Spring+AI/K8s CRD) 與探索中 (Cursor+Claude) 的技術擴展有幫助
3. 對台灣/日本/AI 監管的亞太觀點有用
4. 主題時效性 (最近事件、影響 1-2 年內)

### 分析過程報告 - 格式

#### 檔名規則

```
learning-log/C<自增ID>-<日期>-<文章概要Title>.md
```

`<自增ID>`: 從 C1 開始,一個 step 一個 log,序號單調遞增
`<日期>`: 8 位數 `YYYYMMDD`
`<文章概要Title>`: 該 step 處理對象的概稱 (例: `C1-Feedly-Today-Scroll-and-Extract`, `C5-Analysis-and-Summary-Writeup`)

#### 內容格式

```markdown
# <檔名>

## 狀況理解
<你對現狀與使用者回饋的理解>

## 執行的動作與結果
<表格:執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果>

## 動作結束後的現狀
<執行後驗證的現狀 (表格:驗證的面向 | 驗證的內容與方式 | 驗證結果)>

## 其中的決斷點
<過程中的意思決定 (表格:意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由)>
```

---

## 動作流程的補充說明

### 步驟 1 補充: _articles.csv 格式
```csv
idx,url,title,host,snippet
0,https://lucumr.pocoo.org/2026/6/6/communities-of-not/,Armin Ronacher: Communities of Not,lucumr.pocoo.org,At their best these communities...
2,https://spring.io/blog/2026/06/06/spring-ai-2-0-0-RC1-available-now,Spring AI 2.0.0-RC1 Available Now,spring.io,Introduces OkHttp client...
```

### 步驟 2 補充: 分類規則

| 條件 | 分類 |
|------|------|
| 標題含 AI / LLM / Agent / MCP / 模型 / 機器學習 / Spring AI / Bedrock / AgentCore / OpenAI / Claude / 量子, 且 source 非政治/經濟媒體 | `AI技術` |
| 標題含 程式語言 / 框架 / 開發工具 / Java / Python / Swift / Kotlin / Rust / Podcast / 社群 / OSS 文化 | `傳統IT技術` |
| 其他 (政治 / 經濟 / 社會 / 媒體 / 商業 / 車輛 / 廣告 / 勞動) | `政治經濟` |
| 抓不到內容的 (Reddit personal post 類) | 跳過 |

> **衝突時優先級**: AI技術 > 政治經濟 > 傳統IT技術
> **source 為政治經濟媒體 (NYT, Fortune, NBC, Bloomberg 等) 即使標題含 AI 也歸 `政治經濟`**

### 步驟 3 補充: html2text.py 契約
- 純 stdlib (無外部套件)
- 找 `<article>` / `<main>` 容器,排除 `<script>` `<style>` `<nav>` `<header>` `<footer>`
- Fallback: `<div class="body">` 或最大段落 div
- 輸出: 標題 H1 + 來源 quote + 文章主文

### 步驟 4 補充: 失敗處理
- NYT 403 → cdp navigate + 抓 main/article 區
- Reddit 反爬 → cdp 開 Google 搜尋「<title>」或同主題新聞源
- 仍找不到 → 降級為短文 + 標明「資料不足」,不刪除檔案
- **失敗的 article 不刪 4 點 .md**,而是降級內容

### 步驟 5 補充: 委派紀律
- 4 點解析可委派 subagent 平行生成
- **3 個類別總結 + 5+2 推薦由主 agent 親自寫** (subagent 易幻覺「完成」但 0 個 .md)
- subagent prompt 需包含用戶 profile 完整內容

### 步驟 6 補充: 最終重組 (使用者指定)
- 把 `AI技術/NN_slug.md` 移到 `output/AI/<date>-<title>.md`
- 把 `傳統IT技術/NN_slug.md` 移到 `output/IT/<date>-<title>.md`
- 把 `政治經濟/NN_slug.md` 移到 `output/政經/<date>-<title>.md`
- 3 個類別總結移到 `output/<cat>/<date>-Summary.md`
- 5+2 推薦移到 `output/<date>-Summary.md`
- 刪除舊位置
- 補 learning-log (一個 step 一個 .md)

---

## 最終目錄結構

```
feedly/
├── AGENT.md (本檔)
│
├── output/
│   ├── <date>-Summary.md                 ← 5+2 跨類別最終推薦
│   ├── AI/
│   │   ├── <date>-Summary.md             ← AI 類別總結
│   │   ├── <date>-<title-1>.md           ← 個別詳細報告 × N
│   │   └── ...
│   ├── IT/
│   │   ├── <date>-Summary.md
│   │   └── <date>-<title>.md × N
│   └── 政經/
│       ├── <date>-Summary.md
│       └── <date>-<title>.md × N
│
└── learning-log/
    ├── C1-<date>-<step-1-title>.md
    ├── C2-<date>-<step-2-title>.md
    ├── C3-<date>-<step-3-title>.md
    ├── C4-<date>-<step-4-title>.md
    ├── C5-<date>-<step-5-title>.md
    └── C6-<date>-<step-6-title>.md
```

**檔案總數**: 1 (AGENT) + 1 (跨類別 Summary) + 3 (類別 Summary) + 32 (個別報告) + 6 (learning log) = **43 個 .md**

---

## 注意事項

1. **不要保留 raw 過渡檔**: 用戶指示只保留 4 點解析 + 總結。raw 為過渡,step 6 刪除
2. **不要保留中間資料**: `_articles.csv` / `_分類.md` / `_失敗.md` / `_抽取引流.md` / `_scripts/` 全部 step 6 刪除
3. **subagent 範圍**: 4 點解析可平行 subagent,**總結/推薦由主 agent 親自寫**
4. **步驟 3/4 順序**: 先 curl,失敗才 cdp 補,再失敗才 cdp 搜尋
5. **Reddit 與 NYT 特殊性**: Reddit 對 curl + cdp 完全封鎖,跳過或 cdp Google 搜尋替代。NYT 對 curl 403,需 cdp fallback
6. **標題原文保留**: 4 點解析與總結的 title 必須是**原文**,不翻譯
7. **檔名規範**: `<date>-<title>.md`,date 為 8 位數 YYYYMMDD,title 為英文連字號
