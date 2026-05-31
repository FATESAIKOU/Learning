# C7-CloakBrowser-深度技術調研.md

## 狀況理解
- 使用者要求對 GitHub 上的 CloakHQ/CloakBrowser 專案進行深度技術調研
- 需依照 AGENTS.md 規範產出兩份文件：分析報告（output/）與分析過程報告（learning-log/）
- 這是該目錄的首次 CloakBrowser 調研，output 目錄中原有 CodeGraph 與 OpenHuman 兩份歷史報告
- learning-log 目錄中原有 C1–C6 共六份過程報告，本次為 C7

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md | 理解任務規範與輸出格式要求 | 取得報告格式模板與撰寫規則 | 取得 4 點分析格式、DA 表欄位定義、過程報告模板 |
| 讀取目錄結構 | 確認既有報告與自增 ID 狀態 | 決定新報告檔名與 ID | output/ 有 2 份歷史報告；learning-log 有 C1–C6；本次為 C7 |
| WebFetch GitHub README | 取得 CloakBrowser 專案核心資訊 | 理解技術定位、功能列表、測試結果、API、安裝方式 | 取得完整 README（含 58 patches 說明、30+ 檢測結果表、API 文檔、comparison 表） |
| WebFetch CHANGELOG.md | 取得版本演進歷程與 patch 細節 | 確認各版本新增的 patch 類型與數量變化 | 取得從 v0.1.0 (16 patches) 到 v0.3.31 (58 patches) 的完整變更記錄 |
| WebFetch BINARY-LICENSE.md | 了解授權模式（wrapper MIT vs 二進位專有） | 補充分析報告中技術使用前提的資訊 | 取得：wrapper MIT、二進位禁止再散布/逆向、OEM/SaaS 需另授權 |
| WebFetch pyproject.toml | 取得依賴關係與技術棧資訊 | 確認環境需求、依賴版本 | Python ≥3.9，依賴 playwright≥1.40 + httpx≥0.24；可選 geoip/patchright/serve |
| WebFetch Wikipedia: Browser fingerprinting | 補充通用技術背景（EFF 研究、Canvas entropy、歷史） | 提供分析報告第 2 點的通用背景補充 | 取得：83.6% 指紋唯一、Canvas 5.7 bits entropy、2014 年 AddThis 使用 canvas fingerprinting |
| WebFetch npm: playwright-stealth | 確認現有替代方案狀態 | 作為 DA 表對比素材 | 確認為佔位套件（placeholder），尚未可用 |
| WebFetch PyPI: camoufox | 取得 Camoufox 技術特徵 | 作為 DA 表對比素材 | 取得：Firefox 基底、BrowserForge 指紋生成、geoip 支援 |
| WebFetch GitHub: undetected-chromedriver | 取得 undetected-chromedriver 技術特徵 | 作為 DA 表對比素材 | 取得：Selenium 基底、修補 chromedriver 二進位、JS injection |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 分析報告格式完整性 | 檢查 output/2026-05-31-CloakBrowser.md 是否符合 AGENTS.md 第 4 點格式（問題→背景→解法→替代方案+DA表） | 符合：包含 4 大點、DA 表含 5 欄位、4 個替代方案、切入點差異說明 |
| 分析報告內容準確性 | 比對 README 中的技術規格與報告中的描述 | 一致：58 patches、30+ 檢測、reCAPTCHA 0.9、Chromium 146、平台支援表 |
| 過程報告格式完整性 | 檢查是否包含狀況理解/執行動作/現狀/決斷點四個段落 | 符合 |
| 自增 ID 不重複 | 確認 C7 未被使用 | learning-log/ 中無 C7 檔案，ID 唯一 |
| 目錄結構 | 確認 output/ 與 learning-log/ 目錄存在 | 兩目錄皆存在，無需建立 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| DA 表替代方案選擇 | (a) 僅列 README Comparison 表中的方案；(b) 加入 Camoufox；(c) 加入 puppeteer-extra stealth plugin | 選擇 (b) + (c)，共 4 個方案 | Camoufox 與 CloakBrowser 同為原始碼層級修補但基底不同（Firefox vs Chromium），為重要對比維度；puppeteer-extra 是最淺層的 JS injection 方案，可展示修補層級光譜 |
| playwright-stealth 是否納入 DA 表 | (a) 納入；(b) 排除 | 排除 | npm 確認為 placeholder 套件，不可用 |
| 分析報告中是否需要圖示 | (a) 使用 ASCII art 圖示；(b) 僅純文字 | 使用 ASCII art 圖示 | AGENTS.md 要求「全體說明最好配合使用圖示作說明」 |
| 通用技術背景資料來源 | (a) 僅使用 CloakBrowser README；(b) 補充 Wikipedia browser fingerprinting；(c) 補充學術論文 | 選擇 (b) | Wikipedia 提供公認的 EFF 研究數據（83.6% 唯一、Canvas 5.7 bits），具權威性且時間成本合理 |
