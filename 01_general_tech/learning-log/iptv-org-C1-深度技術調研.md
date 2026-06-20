# iptv-org-C1-深度技術調研

## 狀況理解

- 使用者要求調研 `https://github.com/iptv-org/iptv`。
- 本任務套用 `01_general_tech/AGENTS.md` 的「技術解析助理」角色與輸出格式（分析報告 4 點 + DA 表 + 分析過程報告）。
- 使用者未指定學習目標或實作意圖，故定位為「純技術理解型調研」：回答這個專案做什麼、為何存在、如何運作、有哪些同類方案。
- 既有資料夾無 iptv-org 相關檔案，故為首次調研，分析報告為新建、過程報告自增 ID 從 C1 起。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 閱讀 `01_general_tech/AGENTS.md` 與 `02_mvps/AGENTS.md` | 確認輸出格式與角色規則 | 選對正確 workflow | 兩份 AGENTS.md 皆讀完，判定本任務走 general_tech 路線 |
| `webfetch` GitHub repo 主頁 | 取得 repo 全貌（stars、結構、README） | 掌握專案定位 | 取得 126k stars、TypeScript 55.3%、目錄結構、README 內容 |
| `webfetch` iptv-org.github.io | 確認對外入口 | 驗證消費端 URL 樣態 | 載入為動態搜尋頁，無靜態內容，改以 raw m3u 驗證 |
| `webfetch` raw `PLAYLISTS.md` | 取得完整分類/語言/國家清單 | 取量化數據 | 取得各分類頻道數（News 967、Sports 412…）與各語言頻道數 |
| `webfetch` raw `CONTRIBUTING.md` | 取得貢獻規則、Stream Description Scheme、scripts、workflows | 還原運作機制 | 完整取得 m3u 格式定義、scripts 列表、workflows 說明 |
| `webfetch` raw `package.json` | 取得實際指令與依賴 | 驗證腳本真實存在 | 取得 14 個 npm script、關鍵依賴（tsx、hls-parser、iptv-playlist-parser、@iptv-org/sdk、m3u-linter） |
| `webfetch` GitHub API `streams/` 目錄 | 確認內部清單檔案命名規則 | 驗證「按國家分檔」設計 | 確認 `ad.m3u / ae.m3u / af.m3u …` 命名，部分含 `_pluto` / `_samsung` 後綴（次來源） |
| `webfetch` raw `streams/tw.m3u` | 取得台灣實例 | 確認 `#EXTINF` 實際長相 | 取得 50+ 條含 `tvg-id` / 畫質 / `[Geo-blocked]` / `[Not 24/7]` 的條目，驗證格式 |
| `webfetch` GitHub API `scripts/commands/playlist/` | 確認腳本檔與 README 對應 | 驗證 package.json 指令對應真實檔案 | 確認 edit/export/format/generate/test/update/validate.ts 皆存在 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 專案定位 | README + 法律聲明 | 確認為「公開可播放 IPTV 連結聚合器」，不儲存影音 |
| 運作機制 | CONTRIBUTING + package.json + workflows | 確認每日 CI 全自動：api:load → update → lint → validate → generate → export → readme，部署 GitHub Pages |
| 資料模型 | CONTRIBUTING 的 Stream Description Scheme + tw.m3u 實例 | 確認 `#EXTINF:-1 tvg-id="...",TITLE (QUALITY) [LABEL]` + URL + 可選 `#EXTVLCOPT` |
| 量化規模 | PLAYLISTS.md + streams 目錄 | 確認 240+ 國家檔、8,000+ 頻道、25+ 語言、30+ 分類 |
| 同類方案 | 依技術背景推導 Jellyfin/tvheadend/epg/私有 m3u/Xtream Codes | 產出 DA 表 5 列 |
| 輸出符合 AGENTS.md | 比對 4 點格式、表格、圖示、條列、全中文、無「可能/也許」 | 分析報告符合規範 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 套用哪份 AGENTS.md | (A) 01_general_tech 技術解析助理<br>(B) 02_mvps 實作教練 | A | 使用者要求「調研」一個 GitHub 專案，非要求一小時內產出專案，屬分析型任務 |
| 是否需要 CDP 繞驗證 | (A) 用 CDP 抓 GitHub 動態頁<br>(B) 用 raw.githubusercontent 與 GitHub API | B | raw 文字檔與 GitHub API 皆無反爬，CDP 非必要；AGENTS.md 規定「優先走一般 web fetch」 |
| 是否實際 clone repo 跑 npm | (A) clone 並執行 `npm run playlist:test`<br>(B) 僅以網路資料推導機制 | B | 使用者只要「調研」，未要求驗證執行；先交付分析報告，實作留待後續 MVPs 流程 |
| streams 檔為何有 `_pluto` / `_samsung` 後綴 | (A) 視為不同國家<br>(B) 視為同一國的次來源 | B | 檔名前綴仍是國家 iso（如 `br_pluto.m3u`、`au_samsung.m3u`），對應 aggregator 來源分檔管理，最終被 generate 腳本合併進 `countries/xx.m3u` |
| Xtream Codes 是否列為「同類方案」 | (A) 列入並標註法律風險<br>(B) 不列入 | A | 它是 IPTV 領域事實上的主流聚合模式，讀者需理解 iptv-org 為何明文排除，否則 DA 表不完整 |