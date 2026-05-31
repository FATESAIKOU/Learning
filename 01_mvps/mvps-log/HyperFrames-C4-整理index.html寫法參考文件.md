# HyperFrames-C4-整理index.html寫法參考文件

## 狀況理解

使用者要求：
- 從官方文件或網路搜尋中，整合一份 HyperFrames 的 `index.html` 寫法說明
- 目標讀者是 **AI agent**（給 LLM 閱讀的參考文件）
- 存放於 `2026-05-31-HyperFrames/` 目錄下

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 擷取 `https://hyperframes.heygen.com/concepts/compositions` | 取得 composition 核心概念文檔 | 取得 root element、clip types、nested comp、variables 規則 | 取得完整 composition 結構定義 |
| 擷取 `https://hyperframes.heygen.com/concepts/data-attributes` | 取得所有 data-* 屬性定義 | 取得 timing、media、composition 三類屬性表格 | 取得完整屬性表 + relative timing 語法 |
| 擷取 `https://hyperframes.heygen.com/reference/html-schema` | 取得 HTML schema 完整規範 | 取得 clip types 區分、框架自動管理的行為、output checklist | 取得 video/img/audio/comp 四類 clip 的完整寫法 |
| 擷取 `https://hyperframes.heygen.com/guides/gsap-animation` | 取得 GSAP 動畫規則 | 取得 paused timeline、timeline duration、what NOT to do | 取得四個支援方法、position parameter 用法、composition duration 等於 tl.duration() |
| 擷取 `https://hyperframes.heygen.com/guides/common-mistakes` | 取得常見錯誤案例 | 取得 animating video dims、media playback conflict、missing class="clip" 等坑 | 取得 8 個具體錯誤與修復方式 |
| 整合產出 `index.html-guide.md` | 產出 AI agent 可讀的 index.html 寫法參考 | 含 minimal example、強制規則、完整 data-* 表、clip types、GSAP 規則、常見錯誤、驗證 checklist | 7 個段落，結構化 Markdown，寫入成功 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 目錄結構 | `ls 01_mvps/output/2026-05-31-HyperFrames/` | 4 個檔案：index.html, index.html-guide.md, LEARNING-PLAN.md, README.md |
| guide 內容完整性 | 對照官方 docs 六大面向 | ✅ minimal example、data-* 表、clip types、GSAP rules、common mistakes、validation checklist |
| 範例程式碼 | 每個規則都附 code block | ✅ JavaScript/HTML/CSS 範例，含正確/錯誤對比 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 文件語言 | ① 繁體中文 ② 英文 | ② 英文 | 目標讀者是 AI agent（LLM），英文訓練資料佔比遠高於繁體中文，agent 讀英文規範更精確 |
| 結構粒度 | ① 僅最小範例 + 規則 ② 完整 data-* 表 + clip types + GSAP + 常見錯誤 + checklist | ② 完整涵蓋 | 使用者要求「給 AI 讀的寫法說明」，AI agent 需要完整 schema 參考才能正確產出 composition，僅給最小範例不足以防止 agent 犯錯 |
| 常見錯誤章節 | ① 不包含（因為有 lint） ② 包含 | ② 包含 | lint 只能抓結構性問題，許多錯誤（timeline duration 太短、CSS transform 衝突、video 屬性動畫）是 runtime 問題，agent 需要提前知道 |
| 驗證 checklist | ① 不包含 ② 包含 | ② 包含 | 給 agent 一個產出後自我驗證的清單，降低出錯率 |
