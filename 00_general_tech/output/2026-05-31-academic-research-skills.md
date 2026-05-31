# academic-research-skills (ARS) 技術分析

## 1. 這個技術解決什麼問題？

學術研究者在從研究構思到論文發表的全流程中，需獨立處理文獻檢索與驗證、引用格式校對、論文結構編排、同儕審查回應、資料完整性檢查等多項繁重工作，這些工作在傳統流程中依賴研究者手動完成，耗時且容易因疏忽而產生以下具體問題：

- **文獻引用錯誤**：Zhao et al. (2026) 對 2.5M 篇論文中的 111M 條引用進行審計，保守估計 2025 年就有 146,932 條幻覺引用（hallucinated citations）
- **AI 生成內容的完整性風險**：Lu et al. (2026, Nature) 列舉了 7 種 AI 在研究流程中的失敗模式：實作 bug 通過自審、幻覺引用、幻覺實驗結果、捷徑依賴、bug 被重構為新見解、方法論捏造、早期階段 frame-lock
- **審查意見回應追蹤困難**：修訂過程中需逐點對應審查意見，人工比對容易遺漏或回應不完整

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

| 因素 | 說明 |
|---|---|
| LLM 自身限制 | 模型存在 frame-lock（在同一認知框架內循環）、sycophancy（使用者反駁即過快讓步）、意圖誤判（無法區分探索型 vs 目標導向型對話） |
| AI 生成與驗證共享認知框架 | 生成論文的 AI 與驗證引用的 AI 處於同一認知框架，導致 31% 引用錯誤率未被自行發現（v2.7 stress test） |
| 缺乏引用來源可追溯性 | 在 v3.7.3 之前，引用不帶來源錨點，無法事後審計引用是否真正支持文章主張 |

### 通用技術背景

| 因素 | 說明 |
|---|---|
| 學術寫作流程分散 | 文獻搜尋（Google Scholar / PubMed）、寫作（LaTeX / Word）、引用管理（Zotero / EndNote）、審查回應各自獨立，缺乏整合式 pipeline |
| 引用格式多樣 | APA、MLA、Chicago、IEEE、Vancouver 各有不同規則，手動轉換易出錯 |
| AI 輔助工具的透明性不足 | 多數 AI 寫作工具不提供決策追溯、不標記 AI 參與程度、不產出可審計的過程記錄 |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 架構：四技能 × 十階段 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  academic-pipeline (v3.9.4.2)                    │
│                      編排器 (5 agents)                            │
├─────────────────────────────────────────────────────────────────┤
│  Stage 1          Stage 2         Stage 3         Stage 5        │
│  RESEARCH ──────► WRITE ────────► REVIEW ───────► FINALIZE       │
│  deep-research    academic-paper  academic-paper  academic-paper  │
│  (13 agents)      (12 agents)     -reviewer       (format-convert)│
│                                    (7 agents)                     │
│       │               │               │                │          │
│       ▼               ▼               ▼                ▼          │
│  [2.5 INTEGRITY]  [4→5 CLAIM     [3→4 Coaching]   [6. PROCESS    │
│   7-mode check      AUDIT]         Socratic max     SUMMARY]      │
│   max 3 retries     opt-in         8 rounds         協作品質評估    │
│                                                       │          │
│  Stage 4/4'                                          │          │
│  REVISE/RE-REVISE ───► [4.5 FINAL INTEGRITY]        │          │
│  academic-paper         zero-tolerance               │          │
│                         cannot skip                  │          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 核心機制

#### 引用完整性（L3 Claim-Faithfulness）

```
v3.7.3 (Locator)                     v3.8 (Audit)
─────────────────                    ─────────────
每條引用寫入時攜帶三層錨點：         ARS_CLAIM_AUDIT=1 啟用後：
                                     對每條引用取出原文段落
<!--anchor:quote:"原文段落"-->       LLM-as-judge 判斷是否支持主張
<!--anchor:page:42-->                5 種 HIGH-WARN 類別：
<!--ref:smith2023-->                  - claim-not-supported
                                     - negative-constraint-violation
                                     - fabricated-reference
                                     - anchorless
                                     - constraint-violation-uncited

v3.9.0 (Cross-Index Triangulation)
───────────────────────────────────
S2 + OpenAlex + Crossref 三方交叉驗證
k=0 → CONTAMINATED-COVERAGE-NOISE
k=1 → 沿用 v3.7.3 CONTAMINATED-UNMATCHED
k=2 → PARTIAL-UNMATCH
k=3 → CONTAMINATED-TRIANGULATION-UNMATCHED
```

#### 7-Mode AI 失敗模式檢查（Stage 2.5 / 4.5）

```
M1: 實作 bug 通過 AI 自審
M2: 幻覺引用
M3: 幻覺實驗結果
M4: 捷徑依賴
M5: 實作 bug 被重構為新見解
M6: 方法論捏造
M7: 早期階段 frame-lock

Stage 2.5: 抽樣 30% claims (min 10), FAIL → 重試 max 3 次
Stage 4.5: 100% claims, zero-tolerance, 不可跳過
```

#### Devil's Advocate 讓步閾值協定

```
rebuttal score 1-5 評分 →
  score ≤ 3: 堅守立場，重述原始攻擊
  score ≥ 4: 允許讓步（需 rebuttal 直接以證據回應核心攻擊）
  禁止連續讓步
  讓步率追蹤
  每個 checkpoint 後觸發 frame-lock 檢測
```

#### Socratic Mentor 意圖偵測層

```
對話開始 + 每 3 回合分類使用者意圖：
  exploratory（探索型）:
    - 禁用自動收斂
    - 最大回數提升至 60
    - 禁止 "Want me to summarize?" 提示
  goal-oriented（目標導向型）:
    - 標準收斂行為

對話健康指標（每 5 回合靜默自評）：
  - persistent agreement（持續同意）
  - conflict avoidance（衝突迴避）
  - premature convergence（過早收斂）
```

#### Material Passport 文獻語料庫流程

```
┌──────────────────────┐
│  User Corpus          │
│  Zotero / Obsidian    │────► Adapter ────► passport.yaml
│  / folder of PDFs     │     (out-of-band)   + rejection_log.yaml
└──────────────────────┘
                                              │
                     ┌────────────────────────┘
                     ▼
              Phase 1 Consumer Agents:
              bibliography_agent + literature_strategist_agent
              │
              ├─ Step 0: minimal shape check
              ├─ Step 1: pre-screen corpus against RQ
              ├─ Step 2: search-fills-gap (4-case dispatch)
              ├─ Step 3: merge → final_included
              └─ Step 4: emit Search Strategy + PRE-SCREENED block

              4 Iron Rules:
              1. Same criteria (corpus entries = DB results)
              2. No silent skip (any skipped entry logged with reason)
              3. No corpus mutation (read only)
              4. Graceful fallback on parse failure
```

#### Sprint Contract（審稿盲審協定）

```
Phase 1 (paper-blind):  每個 reviewer 提交評分計畫
                        ↓ <phase1_output> data delimiter
Phase 2 (paper-visible): 基於已提交的計畫進行審查
                        ↓
editorial_synthesizer:  三步機械化協議
  1. 建立評分矩陣
  2. 以 panel-relative quantifier 評估
  3. 依嚴重性排序解決優先級衝突

forbidden-ops list: 禁止事後修改評分標準
```

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 4.1 替代方案 DA 表

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|---|---|---|---|---|
| **PaperOrchestra** (Song et al., 2026, Google) | 多 agent LLM 協作論文生成，Semantic Scholar API 驗證，VLM 圖表驗證 | 需 Google 生態系、需 Semantic Scholar API 存取 | 閉源，不可自行部署；僅覆蓋生成與初步驗證，不包含完整 peer review 模擬 | 自動化論文初稿生成，引用正確率提升 |
| **The AI Scientist** (Lu et al., 2026, Nature) | 全自主 AI 研究系統，從 idea generation 到 paper writing 到 peer review 全自動化 | 需大量算力、需 ICLR 等 venue 的 workshop 投稿管道 | 實作 bug、幻覺結果、捷徑依賴、methodology fabrication 等 7 種失敗模式；ICLR 2025 workshop 得分 6.33/10 | 可在無人類介入下完成完整研究循環並投稿 |
| **Claude-Code-Skills-for-Academics** (aspi6246) | Claude Code skills 集合，專注於 read-only constraint、anti-pattern codification、認知框架方法（教「如何思考」而非「操作步驟」） | 需 Claude Code、需手動安裝 skills | 功能範圍較小，不包含多階段 pipeline 編排、不包含 cross-index 引用驗證 | 輕量級學術寫作輔助，強調認知框架訓練 |
| **Experiment Agent** (Imbad0202) | 與 ARS 互補：在 ARS Stage 1 (RESEARCH) 與 Stage 2 (WRITE) 之間填補實驗執行缺口；支援 Python/R 實驗、人類研究 IRB 倫理清單、11 型統計謬誤檢測 | 需與 ARS 搭配使用（可獨立使用），需 Claude Code | 不包含文獻搜尋、寫作、審查功能；僅處理實驗階段 | 實驗可重現性驗證、統計謬誤自動檢測 |
| **Zotero + Overleaf + 手動流程** | 文獻管理 + LaTeX 協作編輯 + 人工 peer review 回應 | 無特殊前提 | 引用驗證全人工、無完整性檢查、無 AI 失敗模式防護、審查回應追蹤需手動管理 | 傳統學術寫作流程，正確性依賴研究者自身嚴謹度 |

### 4.2 各方案切入點差異

```
解決問題的切入點不同：

  PaperOrchestra ──→ 自動化生成 + 基本驗證（強調「產出」）
  The AI Scientist ──→ 全自主研究循環（強調「自動化」）
  aspi6246 方案 ────→ 認知框架訓練（強調「思考方式」）
  Experiment Agent ──→ 實驗執行驗證（強調「實驗環節」）
  ARS ──────────────→ 全流程 human-in-the-loop 輔助（強調「人機協作 + 完整性防護」）

  ARS 的差異化：在每個階段強制人類 checkpoint，
  且引入了其他方案沒有的：
  - 7-mode AI 失敗模式系統性檢查
  - L3 claim-faithfulness 引用審計
  - Cross-index 三方引用交叉驗證
  - Sprint Contract 盲審協定
  - Devil's Advocate 讓步閾值防 sycophancy
```
