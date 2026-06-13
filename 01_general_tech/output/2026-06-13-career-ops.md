# Career-Ops 技術分析報告

## 1. 這個技術解決什麼問題？

**被解決的具體問題：** 求職者在面對數百個職缺時，需要逐一閱讀 JD、手動比對自身履歷、為每個職缺客製化履歷與求職信、填寫重複的表單、追蹤申請進度——這些重複性勞動佔據大量時間，且缺乏系統化的篩選與決策輔助機制。

Career-Ops 將上述流程自動化為一條 AI 驅動的管線（pipeline）：從職缺發現、多維度評分、ATS 優化 PDF 生成、表單填寫輔助、到申請追蹤，全部整合在一個以 AI coding CLI 為執行引擎的本地系統中。

**模糊之處：** 文章未明確說明「評分系統的權重如何校準」——10 個子維度的權重分配僅在作者個人網站（santifer.io）的 case study 中揭露，開源版本已簡化為 6 個區塊（A-F），但權重細節未在 repo 文件中完整公開。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

| 因素 | 說明 |
|------|------|
| 重複性勞動 | 每份職缺需閱讀 800 字 JD、比對技能、改寫履歷、填 15 欄表單，每天處理 10 份即為全職工作量 |
| 通用履歷無效 | 靜態 PDF 無法針對不同職缺凸顯相關的 proof points |
| 缺乏追蹤系統 | 無系統化管理導致重複投遞或遺漏跟進 |
| 零回饋循環 | 投遞後無法得知是履歷問題、匹配問題還是時機問題 |
| 全球市場規模 | AI 領域跨國求職，本地人脈推薦無法覆蓋 6 個國家的公司 |
| 企業端已使用 AI 篩選 | 公司用 AI 過濾候選人，求職者卻缺乏對等的 AI 工具來反向篩選公司 |

### 通用技術背景（補充）

- **ATS（Applicant Tracking System）** 普及：Greenhouse、Lever、Ashby、Workday 等 ATS 平台已成為企業招募的標準基礎設施，求職者的履歷需通過 ATS 的關鍵字解析才能進入 recruiter 視野
- **AI coding CLI 興起**：Claude Code、OpenCode、Gemini CLI、Codex、Qwen 等工具在 2025-2026 年快速成熟，使「以自然語言驅動複雜多步驟工作流」成為可能
- **SPA 職缺頁面**：現代職缺頁面多為 SPA（Single Page Application），傳統 curl/靜態爬蟲無法提取內容，需要瀏覽器自動化（Playwright）

---

## 3. 這個技術是如何解決該問題的？

### 核心機制總覽

```
使用者輸入（URL 或 JD 文字）
        │
        ▼
┌─────────────────────────────────┐
│  AI coding CLI（執行引擎）        │
│  Claude Code / OpenCode /        │
│  Gemini CLI / Codex / Qwen       │
│  讀取 AGENTS.md + modes/*.md     │
└────────────┬────────────────────┘
             │
    ┌────────┼────────┬──────────┐
    ▼        ▼        ▼          ▼
┌───────┐ ┌──────┐ ┌──────┐ ┌──────┐
│modes/ │ │*.mjs │ │batch/│ │dashboard/
│18 個  │ │工具  │ │批次  │ │Go TUI
│技能檔 │ │腳本  │ │編排  │ │儀表板
└───────┘ └──────┘ └──────┘ └──────┘
```

**核心設計決策：** Career-Ops 不是獨立應用，而是一組 markdown 技能檔案 + Node.js 腳本 + Go TUI + Shell 編排器，由使用者選擇的 AI coding CLI 作為執行引擎。「商業邏輯」存在於 markdown 檔案中，由 LLM 在執行時讀取並遵循。

### 3.1 Auto-Pipeline 流程（URL → 評估 → PDF → Tracker）

```
Step 0:    提取 JD（Playwright > WebFetch > WebSearch）
Step 0.5:  活性閘（確認職缺仍有效，404/過期/空殼 → 中止）
Step 1:    A-G 評估（讀取 cv.md + _profile.md + article-digest.md）
Step 2:    儲存報告（reports/{###}-{company-slug}-{date}.md）
Step 3:    生成 PDF（HTML 模板 + 關鍵字注入 + Playwright 渲染）
Step 4:    草擬申請答案（僅 score ≥ 4.5）
Step 5:    更新追蹤器（TSV → merge-tracker.mjs → applications.md）
```

### 3.2 6-Block 評估系統（A-F + G）

| 區塊 | 內容 | 評分 |
|------|------|------|
| **A) Role Summary** | Archetype、Domain、Function、Seniority、Remote、Team size、TL;DR | 定性 |
| **B) Match with CV** | JD 每項要求 ↔ cv.md 確切行號，含 gaps 與緩解策略 | **1-5** |
| **C) Level and Strategy** | 級別檢測、honest positioning、downlevel 應對 | 定性 |
| **D) Comp and Demand** | WebSearch 薪資（Glassdoor/Levels.fyi/Blind）、需求趨勢 | **1-5** |
| **E) Customization Plan** | CV + LinkedIn top 5 修改建議 | 定性 |
| **F) Interview Plan** | 6-10 STAR+R 故事、case study、red-flag Q&A | 定性 |
| **G) Legitimacy** | 職缺真實性（不影響總分） | High Confidence / Proceed with Caution / Suspicious |

**Global Score** = Match + North Star alignment + Comp + Cultural signals + Red flags 的加權平均。

**Score 解讀：** 4.5+ → 強烈建議立即申請；4.0-4.4 → 值得申請；3.5-3.9 → 僅有特定理由時申請；<3.5 → 建議不申請。

### 3.3 Batch Processing 架構

```
Conductor（headed browser）或 Standalone script（batch-runner.sh）
  │
  ├─ Job 1: Chrome 讀取 JD → headless worker (claude -p / opencode run)
  │    └─► report .md + PDF + tracker TSV + stdout JSON
  ├─ Job 2: 同上（平行）
  └─ End: merge-tracker.mjs → applications.md
```

**關鍵特性：**
- 每個 worker 是獨立 headless 程序，200K token context
- `batch-state.tsv` 追蹤進度（pending/processing/completed/failed/skipped/rate_limited/paused_rate_limit）
- Lock file（`batch-runner.pid`）防雙重執行
- State lock（`mkdir` atomic）防並行寫入競爭
- `--parallel N` 支援多 worker 並行

### 3.4 ATS PDF 生成

**16-step pipeline：**
1. 從 JD 提取 15-20 關鍵字
2. 檢測 JD 語言 → CV 語言
3. 檢測公司地點 → 紙張格式（US/CA → letter，其他 → A4）
4. 檢測 archetype → 調整 framing
5. 改寫 Professional Summary（注入關鍵字 + exit narrative bridge）
6. 選取 top 3-4 最相關專案
7. 依 JD 相關性重排 experience bullets
8. 建立 competency grid（6-8 關鍵字短語）
9. 自然注入關鍵字（只改寫詞彙，不虛構技能）
10. 從 `templates/cv-template.html` 生成 HTML
11. `node generate-pdf.mjs` → Playwright 渲染 PDF

**設計：** Space Grotesk（標題）+ DM Sans（內文）、單欄 ATS-safe 佈局、cyan-purple 漸層標題線、0.6in 邊距。

### 3.5 Human-in-the-Loop 設計

- 系統**永不自動提交申請**
- Score < 4.0 時強烈建議不申請
- 求職信生成需通過 4 個互動提示並經使用者批准後才生成 PDF
- Apply mode 有 preflight gate：驗證職缺仍有效、公司/角色與報告匹配
- 所有 AI 生成內容標記為「草稿」，需使用者審查

### 3.6 Pipeline 完整性檢查

| 機制 | 工具 |
|------|------|
| 去重 | `dedup-tracker.mjs`（company+role 匹配） |
| 合併 | `merge-tracker.mjs`（TSV → applications.md） |
| 狀態正規化 | `normalize-statuses.mjs` |
| 健康檢查 | `verify-pipeline.mjs` |
| 活性檢查 | `check-liveness.mjs` / `liveness-core.mjs` |
| 設定檢查 | `doctor.mjs`（驗證 cv.md、profile.yml、portals.yml 存在） |

### 3.7 Data Contract 分層

- **User Layer**（永不自動更新）：`cv.md`、`config/profile.yml`、`modes/_profile.md`、`portals.yml`、`data/*`、`reports/*`、`output/*`
- **System Layer**（可安全自動更新）：`modes/_shared.md`、`modes/oferta.md`、所有 `*.mjs`、`dashboard/*`、`templates/*`、`batch/*`

### 3.8 AI CLI 整合方式

| CLI | 設定檔 | 指令定義位置 | Headless 指令 |
|-----|--------|-------------|--------------|
| **Claude Code** | `CLAUDE.md`（`@AGENTS.md` wrapper） | `.claude/commands/` | `claude -p "prompt"` |
| **OpenCode** | `OPENCODE.md`（`@AGENTS.md` wrapper） | `.opencode/commands/` | `opencode run "prompt"` |
| **Gemini CLI** | `GEMINI.md`（`@./AGENTS.md` wrapper） | `.gemini/commands/*.toml` | `gemini -p "prompt"` |
| **Codex** | `.agents/` 目錄 | — | `codex exec "prompt"` |
| **Qwen** | `.qwen/` 目錄 | — | `qwen -p "prompt"` |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|---------|-------------|---------------|----------------|
| **Simplify.jobs** | Chrome 擴充自動填充求職表單 | 需安裝 Chrome 擴充；僅支援部分 ATS 平台 | 僅覆蓋單一環節（表單填充），無評估/追蹤/PDF 生成功能 | 減少重複填表時間 |
| **Teal HQ** | 雲端求職追蹤平台 + AI 履歷分析 | 需帳號與網路連線；資料存於雲端 | SaaS 訂閱費用；資料所有權在平台方；AI 為關鍵字層級分析非語意評估 | 集中管理求職進度，基礎履歷優化建議 |
| **Jobscan** | ATS 關鍵字比對工具 | 需手動貼上 JD 與履歷文字 | 僅關鍵字匹配層級，無流程自動化；月費訂閱制 | 提升履歷的 ATS 通過率 |
| **Huntr** | 視覺化 Kanban 求職追蹤 | 需帳號；瀏覽器擴充或 Web app | SaaS 模式；AI 功能為輔助性質非核心決策引擎 | 求職狀態視覺化管理 |

### 各方案切入點差異

| 方案 | 核心切入點 |
|------|-----------|
| **Career-Ops** | 以 **AI agent 多維度決策輔助**為核心，全流程自動化（發現→評估→生成→追蹤），本地執行、markdown 技能定義 |
| **Simplify.jobs** | 僅解決「填寫表單」的單一環節 |
| **Teal HQ** | 雲端平台的「集中管理」思維，AI 為輔助 |
| **Jobscan** | 僅解決「ATS 關鍵字匹配」的單一環節 |
| **Huntr** | 視覺化追蹤的工具思維，非決策輔助系統 |
