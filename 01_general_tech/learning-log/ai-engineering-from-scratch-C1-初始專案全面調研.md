# ai-engineering-from-scratch-C1-初始專案全面調研

## 狀況理解
使用者要求針對 GitHub 專案 `rohitg00/ai-engineering-from-scratch` 進行「深入調研」。根據 AGENTS.md 的規範，需以「技術解析助理」角色產出分析報告（`output/`）與分析過程報告（`learning-log/`）。
該專案是一個開源 AI 工程課程，503 堂課、20 階段、~314 小時，以 MIT 授權發布。使用者指定的 URL 為 `https://github.com/rohitg00/ai-engineering-from-scratch`。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取本地 AGENTS.md 與目錄結構 | 理解任務規範與輸出格式 | 確認分析報告與過程報告的格式要求 | 取得 AGENTS.md 完整規範（4點分析格式、DA表要求），確認 output/ 與 learning-log/ 目錄存在 |
| 以 WebFetch 抓取 repo README | 取得專案全貌與核心定位 | 理解課程結構、階段列表、教學方法 | 取得 README 完整內容：20 Phase 列表、Lesson Structure（6 beats: MOTTO→PROBLEM→CONCEPT→BUILD→USE→SHIP）、內建 Agent Skills、503課/20階段/~314小時 |
| 抓取 ROADMAP.md | 取得所有階段與課程的完成狀態、時間估算 | 確認課程範圍與進度 | Phase 0-10 均標記為 ✅ Complete，共 ~314 小時。後續 Phase 11-19 處於不同程度（部分完成/計畫中） |
| 抓取 CHANGELOG.md | 了解專案演進歷史與最新進展 | 掌握版本時間線 | 2026-Q1 完成 Phase 0-3；2026-04 完成 Phase 4；最新加入 scaffold-lesson.sh、PR/Issue 模板等 |
| 抓取 AGENTS.md | 理解 repo 對 contributor/AI agent 的操作規範 | 了解課程品質保證機制 | 取得完整規範：hard rules（單課單 commit、conventional commits、dependency allowlist、lesson contract 含 quiz.json schema、CI gates） |
| 抓取 LESSON_TEMPLATE.md | 理解每堂課的標準模板 | 掌握教學設計框架 | 取得 folder structure、docs/en.md 格式（frontmatter + 6 sections）、quiz.json schema、output file format |
| 抓取 CONTRIBUTING.md | 理解貢獻流程與規範 | 了解開源協作方式 | 取得貢獻方式（add lesson/translation/output/fix）、lesson doc 格式、style guidelines、PR 流程 |
| 瀏覽 phases/ 目錄 | 確認所有 Phase 目錄結構 | 驗證 20 階段是否都存在 | 確認 00 到 19 共 20 個目錄，從 setup-and-tooling 到 capstone-projects |
| 瀏覽 glossary/ | 了解術語表結構 | 確認輔助資源 | 取得 terms.md（60+ 術語，含常見誤解 vs 真實定義）和 myths.md（20 常見迷思） |
| 瀏覽 projects/ | 了解專案目錄 | 確認專案空間是否存在 | 目前僅有 .gitkeep，尚無完整專案內容 |
| 瀏覽 scripts/ | 了解自動化工具腳本 | 確認品質工具鏈 | 取得 8 個腳本：audit_lessons.py、build_catalog.py、check_readme_counts.py、install_skills.py、lesson_run.py、link_check.py、scaffold-lesson.sh、scaffold_workbench.py |
| 瀏覽 outputs/ | 了解輸出物種類與數量 | 確認 Ship It 產出物 | 取得 outputs/ 結構（agents/、mcp-servers/、prompts/、skills/）+ index.json |
| 瀏覽 .claude/skills/ | 了解內建 Agent Skills | 確認教學輔助工具 | `find-your-level`（定位測驗）和 `check-understanding`（階段測驗），各含 SKILL.md |
| 搜尋 Hacker News 討論 | 尋找社群討論與評價 | 取得外部觀點 | 找到相關討論串但內容較少，主要討論 MCP 與 Claude 相關技術 |
| 造訪官方網站 | 了解前端展示層 | 確認使用者體驗 | 取得 aiengineeringfromscratch.com 結構（Contents、Catalog、Roadmap、Glossary）+ 進度追蹤功能 |
| 抓取 SPONSORS.md | 了解贊助模式與社群規模 | 評估專案成熟度 | 取得 tier ladder（$25-$5000/mo）、流量數據（7 天 33K 訪客/30 天 55K 訪客）、贊助規則 |
| 抓取 FORKING.md | 了解 fork 使用場景 | 評估再製性 | 取得 Teams/Schools/Bootcamps/Other Languages 四種 fork 指南 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 課程完整性 | 從 README/ROADMAP 交叉比對 20 Phase 的課程列表 | Phase 0-10 已完成（✅），Phase 11-19 進度不等，部分為計畫中（⬚） |
| 教學方法論 | 從 README + LESSON_TEMPLATE 驗證 | 確認「Build It / Use It / Ship It」三段式教學法 + 6-beat lesson structure |
| 品質保證機制 | 從 AGENTS.md 驗證 CI/CD + audit 規則 | 確認 `audit_lessons.py` blocking gate、dependency allowlist、quiz.json schema、test requirement |
| 社群活躍度 | 從 GitHub 頁面（Stars 28.9K / Forks 4.7K）、SPONSORS.md 流量數據 | 高活躍度開源專案，2026 Q1-2 快速成長 |
| 開源生態相容性 | 從 FORKING.md、AGENTS.md、CONTRIBUTING.md 驗證 | MIT 授權，明確的貢獻指南，支援團隊/學校/Bootcamp fork 使用 |
| 同類競爭分析 | 從網路搜尋比對 fast.ai、d2l.ai、Karpathy、HuggingFace | 確認差異化定位：唯一線性全覆蓋路徑 + Ship It 產出工具閉環 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 分析報告的技術對象定義 | 分析「整個 curriculum 框架」 vs 分析「其中一個特定 Phase 技術」 | 分析整個 curriculum 框架 | 使用者要求「深入調研」repo 整體，且這是第一份報告，需建立全貌理解 |
| DA 表的對比對象選擇 | fast.ai / d2l.ai / Karpathy / HuggingFace / 其他 | fast.ai、d2l.ai、Karpathy series、HuggingFace Course | 這四個是 AI 自學領域最具代表性的開源資源，涵蓋不同教學方法論 |
| 是否使用 CDP 繞過反爬 | Reddit 搜尋結果遇到 CAPTCHA | 跳過 Reddit，不使用 CDP | Reddit 非核心資訊來源；repo 本身文檔已足夠完整；CDP 成本高且規範建議「必要時使用」 |
| 分析報告的深度層次 | 只覆蓋 README 表面的 4 點分析 vs 深入 AGENTS.md/ROADMAP 等內部規範 | 深入所有核心文檔 | AGENTS.md 的規範要求「若文章本身資訊不足請從網路搜尋補上」，repo 內部文檔是主要資訊源 |
| Phase 11-19 未完成的處理 | 忽略未完成部分 vs 標註現狀 | 於報告中標註「進度不等」 | 需要誠實反映目前狀態，避免誤導；但不影響對整體設計的分析 |
