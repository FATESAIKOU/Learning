# Maigret-C1-深度技術調研.md

## 狀況理解

使用者要求調研 GitHub 專案 `soxoj/maigret`，並依 AGENTS.md 規範輸出「分析報告」與「分析過程報告」兩份 markdown。

現狀：
- 工作目錄已存在 output/ 與 learning-log/，但無任何 Maigret 相關檔案
- 使用者未提出質問型問題，故不觸發 §5 User Q&A
- 需補足的背景：Maigret 與同類工具（Sherlock、WhatsMyName、Maltego、SpiderFoot）的差異定位、底層抽取引擎 socid_extractor 的角色、反封鎖機制細節

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| Read AGENTS.md | 確認輸出格式與規則 | 取得報告格式與命名規則 | 取得 4 點分析 + QA 章節 + learning-log 格式 |
| webfetch GitHub maigret README | 取得專案主功能、安裝、使用 | 取得 §1~§3 主素材 | 取得完整 README 內容（含 features、AI、CF bypass、Tor/I2P） |
| webfetch readthedocs features 頁 | 取得功能細節 | 補足 README 未深入的機制 | 取得 recursive、self-check、activation、CF webgate 細節 |
| webfetch readthedocs quick-start | 確認基本使用 | 驗證最小可行指令 | 取得指令範例 |
| webfetch socid_extractor repo | 釐清 L2 抽取引擎角色 | 解釋 Maigret 如何從「探測」升級為「dossier」 | 取得 130+ 站、欄位 ontology、stable ID 用途 |
| webfetch sherlock repo | 同類對比基準 | 構建 §4 DA 表 | 取得 Sherlock 400+ 站、無抽取、無遞迴的定位 |
| bash ls output/learning-log | 確認既有檔案 | 避免覆蓋、確認 ID 自增起點 | 確認無 Maigret 既有檔，本輪為 C1 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 分析報告存在性 | ls output/2026-06-27-Maigret.md | 已建立 |
| 報告章節合規 | 比對 AGENTS.md §1~§4 + §5 + 附錄 | §1~§4 齊全；§5 標註「無提問」；附錄列來源 |
| learning-log 存在性 | ls learning-log/Maigret-C1-*.md | 已建立 |
| 檔名規則合規 | 比對 `<技術名>-C<自增ID>-<做的事情總結>.md` | `Maigret-C1-深度技術調研.md` 符合 |
| 中文輸出 | 通篇中文 | 合規 |
| 不使用比喻/情緒語言 | 掃描禁用詞 | 合規（圖示使用 ASCII 階層結構而非比喻） |
| DA 表欄位齊全 | 技術名/解法/前提/副作用/預期效果 | 4 欄齊全，列 4 個同類技術 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 技術名命名 | (a) Maigret (b) soxoj-maigret (c) maigret-osint | Maigret | README 主標即為 `Maigret`，且與既有 log 命名風格（JDK25、HyperFrames）一致 |
| 同類對比對象選取 | Sherlock / WhatsMyName / Maltego / SpiderFoot / Social Links API / UserSearch | 選前四者 | Social Links API 與 UserSearch 為商業 SaaS，非同級開源框架；DA 表要求「同級或替代方案」 |
| §3 敘述深度 | (a) 僅列功能 (b) 拆三層偵測 + 反封鎖 + AI | 選 (b) | AGENTS.md 要求「描述核心機制」並「善用程式碼/虛擬碼」，三層架構最能呈現 Maigret 區別於 Sherlock 的本質 |
| 是否使用 CDP | README web fetch 是否遭遇阻擋 | 否，全程 webfetch | GitHub 與 readthedocs 均順利取得，依規則不啟用 CDP |
| §5 QA 章節處理 | (a) 省略 (b) 保留空章節標註無提問 | 選 (b) | AGENTS.md 規定「無提問則無此節」，但仍保留章節骨架供後續遞增接續，避免下次追加時需重新建立章節標題 |