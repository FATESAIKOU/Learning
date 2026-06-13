# Career-Ops-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `santifer/career-ops` 進行全面深度調研，涵蓋 11 個具體面向：完整 README、各 AI agent 整合文件（AGENTS.md/CLAUDE.md/OPENCODE.md/GEMINI.md）、modes/ 目錄（14 個技能模式）、dashboard/（Go TUI）、batch/（批次處理）、templates/、scaffolder/、providers/、config/、網路評價與技術分析、以及結構化總結。使用者已持有截斷的 README，需要補全所有缺失資訊。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 從 raw.githubusercontent.com 抓取完整 README.md | 取得未被截斷的完整 README 內容 | 獲得完整專案說明、功能列表、架構圖、使用方式 | 成功取得 23KB 完整 README，含 11 種語言版本、功能表、quick start、專案結構、tech stack |
| 抓取 AGENTS.md | 理解 canonical agent instructions（所有 CLI 共用） | 獲得完整 agent 行為規範、data contract、onboarding 流程、skill modes 對照表、pipeline integrity 規則 | 成功取得 21KB AGENTS.md，含 6-step onboarding、15 個 skill mode 定義、TSV tracker 格式、canonical states、ethical use 規則 |
| 抓取 CLAUDE.md | 理解 Claude Code 專屬配置 | 獲得 Claude Code wrapper（imports AGENTS.md）+ Claude 專屬指令 | 成功取得 23KB CLAUDE.md，內容與 AGENTS.md 高度重疊，含 Claude Code 專屬 slash commands 對照表 |
| 抓取 OPENCODE.md | 理解 OpenCode 整合方式 | 獲得 OpenCode 配置內容 | 成功取得，內容僅 `@AGENTS.md` 一行引用 + 註解 |
| 抓取 GEMINI.md | 理解 Gemini CLI 整合方式 | 獲得 Gemini CLI 配置內容 | 成功取得，內容僅 `@./AGENTS.md` 一行引用 + 註解 |
| 抓取 modes/ 目錄列表 | 了解所有技能模式檔案 | 獲得 15 個模式檔 + 6 個語言子目錄的完整清單 | 成功取得完整目錄：_shared.md、_profile.template.md、auto-pipeline.md、oferta.md、ofertas.md、pdf.md、cover.md、scan.md、batch.md、apply.md、contacto.md、deep.md、tracker.md、training.md、project.md、pipeline.md、patterns.md、followup.md、interview-prep.md、interview.md、latex.md、update.md + de/fr/ja/ar/tr/pt/ru/ua 語言子目錄 |
| 抓取 modes/_shared.md | 理解系統核心規則與評分邏輯 | 獲得 scoring system、archetype detection、global rules、writing style calibration | 成功取得 12KB，含 6 個 archetype 定義、5 維度評分系統、Posting Legitimacy (Block G) 信號權重表、ATS 相容寫作規則 |
| 抓取 modes/oferta.md | 理解單一職缺評估的完整 A-G 流程 | 獲得 7 個 block 的詳細執行指令 | 成功取得 13KB，含 liveness gate、archetype detection、Block A-G 完整格式、STAR+R 故事框架、report 儲存格式、tracker 記錄規則 |
| 抓取 modes/auto-pipeline.md | 理解 URL → 評估 → PDF → tracker 全自動流程 | 獲得 5-step pipeline 完整指令 | 成功取得 5KB，含 Step 0 JD 提取策略（Playwright > WebFetch > WebSearch）、Step 0.5 liveness gate、Step 1-5 完整流程 |
| 抓取 modes/batch.md | 理解批次處理架構 | 獲得 conductor + worker 架構、兩種模式（--chrome / standalone）、batch-state.tsv 格式 | 成功取得 5KB，含 Mode A (Conductor --chrome) 與 Mode B (Standalone script) 完整流程、錯誤處理表、resumability 設計 |
| 抓取 modes/pdf.md | 理解 ATS PDF 生成完整流程 | 獲得 16-step pipeline、HTML template placeholder 對照表、Canva CV 可選流程 | 成功取得 10KB，含 keyword injection 策略（ethical, truth-based）、ATS 規則、設計規範、cover letter sub-flow |
| 抓取 batch/batch-prompt.md | 理解 headless worker 的 self-contained prompt | 獲得 worker 接收的完整系統提示 | 成功取得 20KB，含所有 placeholder、A-G 評估完整指令、PDF 生成 configurable gate（auto_pdf_score_threshold）、machine summary YAML 格式、TSV tracker 格式 |
| 抓取 batch/batch-runner.sh | 理解批次編排器的實作細節 | 獲得 shell script 完整邏輯 | 成功取得 23KB，含 lock file 防雙重執行、state lock 機制、rate limit 處理（session limit vs transient rate limit）、parallel job control、resumability |
| 抓取 dashboard/main.go | 理解 Go TUI 儀表板架構 | 獲得 Bubble Tea ELM 架構、view state 切換、data pipeline | 成功取得 4.7KB，含 PipelineModel/ViewerModel/ProgressModel 三種 view、report summary lazy loading、inline status update、URL 開啟 |
| 抓取 dashboard/internal 目錄 | 了解儀表板內部套件結構 | 獲得 data/model/theme/ui 四個子套件 | 成功取得目錄結構：data/（解析 applications.md）、model/（資料模型）、theme/（Catppuccin Mocha 主題）、ui/screens/（畫面元件） |
| 抓取 templates/ 目錄 | 了解模板檔案 | 獲得 cv-template.html、cv-template.tex、cover-letter-template.html、portals.example.yml、states.yml | 成功取得完整清單 |
| 抓取 templates/states.yml | 理解 canonical states 定義 | 獲得 8 個正式狀態及其 aliases | 成功取得：Evaluated/Applied/Responded/Interview/Offer/Rejected/Discarded/SKIP，含 dashboard_group 分類 |
| 抓取 config/profile.example.yml | 理解使用者 profile 設定結構 | 獲得完整 YAML 設定範本 | 成功取得 5.6KB，含 candidate/target_roles/narrative/compensation/location/cv/cover_letter/auto_pdf_score_threshold 所有欄位 |
| 抓取 providers/ 目錄 | 了解 ATS API 提供者模組 | 獲得 9 個 provider 模組清單 | 成功取得：_http.mjs、_types.js、ashby.mjs、greenhouse.mjs、lever.mjs、recruitee.mjs、smartrecruiters.mjs、solidjobs.mjs、workable.mjs、workday.mjs、local-parser.mjs |
| 抓取 scaffolder/ 目錄 | 了解 npx 安裝器架構 | 獲得 package.json + bin/cli.mjs | 成功取得：scaffolder 為 npm 套件 `@santifer/career-ops`，提供 `npx @santifer/career-ops init` 一鍵安裝 |
| 抓取 DATA_CONTRACT.md | 理解 user layer vs system layer 分離機制 | 獲得完整檔案分類表 | 成功取得：user layer（永不自動更新）vs system layer（可安全自動更新）的完整清單 |
| 抓取 docs/SETUP.md | 理解安裝流程 | 獲得 quick start 與 manual clone 兩種安裝路徑 | 成功取得：npx 一鍵安裝、手動 git clone、Playwright chromium 安裝、dashboard 建置 |
| 抓取 santifer.io/career-ops-system | 取得作者 case study 深度內容 | 獲得私人 rubric 10 子維度、實際數據（631 evaluations）、lessons learned | 成功取得完整 case study：含 10 個原始子維度權重表、score distribution、before/after 對比、FAQ |
| 抓取 Business Insider 報導 | 取得第三方媒體分析 | 獲得作者背景故事、工具開發動機、社群反應 | 成功取得報導內容：6 週開發、740+ 職缺評估、66 申請、12 面試、1 offer |
| 抓取 modes/scan.md | 理解 portal scanner 完整策略 | 獲得 4-level discovery strategy、title/location filter、dedup 邏輯 | 成功取得 20KB，含 Level 0-3 完整策略、local_parser_ok 規則、careers_url 管理規範、ATS API 解析慣例 |
| 抓取 modes/apply.md | 理解即時申請輔助模式 | 獲得 8-step workflow、preflight gate、form question 分類 | 成功取得 6.4KB，含 Playwright 表單讀取、response generation、"I'm choosing you" tone 框架 |
| 抓取 modes/cover.md | 理解求職信生成器完整流程 | 獲得 10-step 互動流程、4 個必填提示、language rules | 成功取得 13KB，含 slug mode/paste mode、company research baked-in、keyword mirroring、gap detection、PDF 生成 |
| 抓取 modes/interview-prep.md | 理解面試準備模式 | 獲得 audience-segmented 研究策略、per-audience 問題準備 | 成功取得 17KB，含 recruiter-screen/hiring-manager/peer-tech/panel-mixed 四種 audience 的完整準備框架 |
| 抓取 modes/patterns.md | 理解 rejection pattern 分析 | 獲得 analyze-patterns.mjs 輸出格式、recommendation 應用 | 成功取得 5.3KB，含 funnel analysis、archetype performance、score threshold recommendation |
| 抓取 modes/followup.md | 理解跟進節奏追蹤 | 獲得 followup-cadence.mjs 輸出、per-contact-type 郵件框架 | 成功取得 6.3KB，含 urgency dashboard、email/LinkedIn follow-up 範本、cadence rules |
| 抓取 modes/contacto.md | 理解 LinkedIn 外展模式 | 獲得 4 種聯絡人類型的 3-sentence 訊息框架 | 成功取得 2.8KB，含 Recruiter/Hiring Manager/Peer/Interviewer 四種框架 |
| 抓取 modes/deep.md | 理解深度公司研究模式 | 獲得 6-axis structured prompt | 成功取得 1.6KB，含 AI Strategy/Recent moves/Engineering culture/Likely challenges/Competitors/Candidate angle |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|-------------|
| 專案完整性 | 確認所有 11 個調研面向均已覆蓋 | 全部覆蓋：README、4 個 agent 檔案、modes/（15 個模式 + 8 個語言子目錄）、dashboard/（Go TUI + 4 個 internal 套件）、batch/（prompt + runner.sh）、templates/（5 個檔案）、scaffolder/（npm 套件）、providers/（11 個模組）、config/（profile.example.yml）、網路資料（case study + Business Insider） |
| 技術架構理解 | 交叉比對 AGENTS.md、modes/*.md、batch/* 的流程描述 | 架構清晰：AI coding CLI 為執行引擎，modes/*.md 為技能定義，*.mjs 為工具腳本，Go 為 TUI，Shell 為批次編排。Data Contract 明確分離 user layer 與 system layer |
| 14 個技能模式完整性 | 逐一抓取並閱讀所有 mode 檔案 | 實際為 18 個模式檔（含 interview、latex、update）+ 1 個 _shared.md + 1 個 _profile.template.md。核心模式：auto-pipeline、oferta、ofertas、pdf、cover、scan、batch、apply、contacto、deep、tracker、training、project、pipeline、patterns、followup、interview-prep、interview、latex、update |
| 6-block 評估系統 | 閱讀 _shared.md + oferta.md + batch-prompt.md | A) Role Summary、B) Match with CV、C) Level and Strategy、D) Comp and Demand、E) Customization Plan、F) Interview Plan、G) Posting Legitimacy（不影響總分）。原始私人 rubric 有 10 個加權子維度，開源版簡化為 6 個 categorical dimensions |
| AI CLI 整合方式 | 閱讀 AGENTS.md/CLAUDE.md/OPENCODE.md/GEMINI.md | 設計模式：AGENTS.md 為 canonical source of truth，CLAUDE.md/OPENCODE.md/GEMINI.md 均為 `@AGENTS.md` 的 thin wrapper。各 CLI 的 slash commands 定義在 `.claude/commands/`、`.opencode/commands/`、`.gemini/commands/` 中 |
| 人機迴路設計 | 閱讀 AGENTS.md ethical use 章節 + auto-pipeline.md + apply.md | 明確：系統永不自動提交申請；score < 4.0 強烈建議不申請；求職信需 4 個互動提示 + 使用者批准才生成 PDF；apply mode 有 preflight gate 驗證職缺仍有效 |
| Pipeline 完整性機制 | 閱讀 AGENTS.md pipeline integrity 章節 | 7 個機制：dedup-tracker.mjs、merge-tracker.mjs、normalize-statuses.mjs、verify-pipeline.mjs、check-liveness.mjs、update-system.mjs、doctor.mjs。TSV tracker additions 為唯一新增入口，禁止直接編輯 applications.md |
| 與其他求職工具對比 | 搜尋 Simplify.jobs、Teal HQ、Jobscan、Huntr 的公開資訊 | Career-Ops 的核心差異：(1) AI coding CLI 作為執行引擎而非自建後端，(2) markdown 技能檔而非程式碼邏輯，(3) 本地執行資料不外洩，(4) 多維度語意評估而非關鍵字比對 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 調研深度 | (A) 僅閱讀目錄結構與 README；(B) 深入閱讀所有 mode 檔案、腳本、shell script 原始碼 | 選擇 B | 使用者明確要求 "in depth" 且列出 11 個具體面向，需完整理解技術架構與實作細節 |
| 網路資料來源 | (A) 僅依賴 GitHub repo；(B) 額外搜尋作者 case study、媒體報導 | 選擇 B | 使用者要求 "Search the web for any blog posts, reviews, or technical analysis"，且 repo 內文件對評分權重等細節揭露不足 |
| 分析報告結構 | (A) 自由格式；(B) 嚴格遵循 AGENTS.md 規定的 4 點格式 | 選擇 B | AGENTS.md 明確規定分析報告只回答 4 點，不得額外延伸 |
| 語言模式覆蓋 | (A) 僅列舉主要模式；(B) 完整列出所有 18 個模式 + 8 個語言子目錄 | 選擇 B | 使用者要求 "the 14 skill modes and what each does"，需完整覆蓋 |
| DA 表對比對象 | (A) 僅列舉 2 個；(B) 列舉 4 個同級替代方案 | 選擇 B | AGENTS.md 規定條列 2-4 個同級或替代方案 |
