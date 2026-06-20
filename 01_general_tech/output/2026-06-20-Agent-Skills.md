# Agent Skills 技術分析報告

> 調研對象：`addyosmani/agent-skills`（GitHub, MIT, 63.5k stars, 預設分支 main, 最後更新 2026-06-20）
> 定位：Production-grade engineering skills for AI coding agents — 一組「封裝成 workflow 的工程最佳實踐」，供 AI coding agent 載入並遵循。

---

## 1. 這個技術解決什麼問題？

解決 **AI coding agent 預設走捷徑、跳過資深工程師才會做的工程紀律** 的問題。具體被解決的子問題：

- **Agent 跳過 spec 直接寫 code** → 產出與真實需求脫鉤的程式碼
- **Agent 不寫測試 / 事後補測** → 行為無法驗證、回歸無人看管
- **Agent 過度工程化（over-engineering）** → 引入抽象層、相依套件、clever 解法，超出實際需求
- **Agent 順從使用者（sycophancy）** → 對明顯有問題的方案說「Of course!」直接實作
- **Agent 無驗證就宣稱完成** → 「Seems right」取代實際跑測試 / 看建置輸出
- **Agent 跨工具行為不一致** → 同一份工程知識在 Claude Code / Cursor / Gemini CLI / Antigravity 各自重寫、各自漂移

**模糊點註記**：「skill」一詞在此 repo 並非執行時期可呼叫的函式，而是**一段結構化 Markdown workflow**，靠 agent 讀取後自我約束；它不解決「agent 能力不足」的問題，而是解決「agent 有能力但不走對流程」的問題。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到

| 背景因素 | 說明 |
|----------|------|
| **AI coding agent 預設走最短路徑** | README「Why Agent Skills?」段：agent 預設會跳過 spec、測試、security review 與其他讓軟體可靠的實踐 |
| **資深工程師的判斷是隱性知識** | 什麼時候寫 spec、測什麼、怎麼 review、什麼時候 ship — 這些判斷散落在資深工程師腦中，缺乏可被 agent 遵循的編碼形式 |
| **不同工具的 instruction 系統破碎** | Claude Code 有 `.claude/commands/`、Cursor 有 `.cursor/rules/`、Gemini CLI 有 `GEMINI.md`、Antigravity 有 `commands/` + `plugin.json` — 同一份工程實踐需要重寫多次 |
| **Prompt 本身是 reference doc 而非 workflow** | 一般 prompt 告訴 agent「要記得寫測試」，但不規定步驟、checkpoint、exit criteria，agent 讀完仍會跳過 |

### 通用技術背景（自行補充）

| 背景因素 | 說明 |
|----------|------|
| **LLM 的 token 預算限制** | 一次性塞入所有工程實踐會吃光 context window，需要 progressive disclosure（按需載入子文件） |
| **LLM 的 rationalization 傾向** | 模型會自我合理化跳過步驟（「這太簡單了不需要 spec」），需要顯式的 anti-rationalization 表把藉口與反駁並列 |
| **Google 工程文化的可移植性** | Hyrum's Law、Beyonce Rule、test pyramid、change sizing、Chesterton's Fence、trunk-based、Shift Left — 這些來自 Google 內部工程實踐，已被《Software Engineering at Google》形式化，可直接移植進 skill |
| **Slash command 作為 workflow 入口** | Claude Code / Gemini CLI / Antigravity 都支援 slash command，使得「7 個命令對應 7 個生命週期階段」成為跨工具通用入口 |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體結構

```
agent-skills/
├── skills/                 # 24 個 skill（23 lifecycle + 1 meta）
│   └── <skill-name>/SKILL.md   # 每個 skill 一個資料夾 + 一個 SKILL.md
├── agents/                # 4 個專家 persona（code-reviewer, test-engineer, security-auditor, web-performance-auditor）
├── references/            # 5 份補充 checklist（testing / security / performance / accessibility / observability）
├── hooks/                 # session lifecycle hooks
├── .claude/commands/      # 7 個 slash command（Claude Code 專用）
├── .gemini/commands/      # 7 個 slash command（Gemini CLI 專用）
├── commands/              # 8 個 slash command（Antigravity 專用）
├── plugin.json            # Antigravity plugin manifest
└── docs/                  # 各工具 setup guide
```

### 3.2 生命週期對應：7 個命令 × 6 個階段

```
  DEFINE          PLAN           BUILD          VERIFY         REVIEW          SHIP
 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
 │ /spec│ ───▶ │/plan │ ───▶ │/build│ ───▶ │/test │ ───▶ │/review│ ───▶ │/ship │
 └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘
                                  │
                                  └─ /code-simplify（review 階段簡化分支）
```

| 命令 | 啟動的 skill | 核心原則 |
|------|-------------|---------|
| `/spec` | interview-me, idea-refine, spec-driven-development | Spec before code |
| `/plan` | planning-and-task-breakdown | Small, atomic tasks |
| `/build` | incremental-implementation (+ frontend / api / context / source / doubt / TDD) | One slice at a time |
| `/test` | test-driven-development (+ browser-testing-with-devtools) | Tests are proof |
| `/review` | code-review-and-quality (+ code-simplification, security, performance) | Improve code health |
| `/code-simplify` | code-simplification | Clarity over cleverness |
| `/ship` | shipping-and-launch (+ git-workflow, ci-cd, deprecation, docs, observability) | Faster is safer |

`/build auto` 變體：批准計畫一次後自動執行所有 task，但每個 task 仍 test-driven + 個別 commit，失敗或風險步驟暫停。

### 3.3 Skill 的解剖（anatomy）

每個 `SKILL.md` 都遵循同一結構：

```
┌─────────────────────────────────────────────────┐
│  SKILL.md                                       │
│  ┌─ Frontmatter ─────────────────────────────┐  │
│  │ name: lowercase-hyphen-name              │  │
│  │ description: Guides agents through [task]│  │
│  │              Use when…                   │  │
│  └───────────────────────────────────────────┘  │
│  Overview         → 這個 skill 做什麼           │
│  When to Use      → 觸發條件                    │
│  Process          → 逐步 workflow               │
│  Rationalizations → 藉口 + 反駁表              │
│  Red Flags        → 出問題的徵兆               │
│  Verification     → 證據要求（非協商）          │
└─────────────────────────────────────────────────┘
```

**四個關鍵設計選擇**：

| 設計選擇 | 做法 | 解決的問題 |
|---------|------|-----------|
| **Process, not prose** | skill 是 agent 要 follow 的 workflow（有步驟、checkpoint、exit criteria），不是讀完就忘的參考文件 | 防止 agent 讀完但不行動 |
| **Anti-rationalization** | 每個 skill 內建「常見藉口 ↔ 反駁」表 | 直接預防模型自我合理化跳步 |
| **Verification is non-negotiable** | 每個 skill 結尾有 evidence requirements（測試通過 / 建置輸出 / runtime data） | 「Seems right」永不成立 |
| **Progressive disclosure** | `SKILL.md` 是入口；references 只在需要時載入 | 控制 token 用量，不全塞進 context |

### 3.4 範例：spec-driven-development 的 Gated Workflow

```markdown
SPECIFY ──→ PLAN ──→ TASKS ──→ IMPLEMENT
   │          │        │          │
   ▼          ▼        ▼          ▼
 Human      Human    Human      Human
 reviews    reviews  reviews    reviews
```

每階段都需人類 review 才進下一階段。Phase 1 Specify 強制先列 ASSUMPTIONS：

```
ASSUMPTIONS I'M MAKING:
1. This is a web application (not native mobile)
2. Authentication uses session-based cookies (not JWT)
...
→ Correct me now or I'll proceed with these.
```

並用三層 boundaries 系統（Always / Ask first / Never）明確劃分 agent 的行為邊界。

### 3.5 Meta-skill：using-agent-skills

入口 skill，定義「task 進來 → 對應到哪個 skill」的決策樹，以及 6 條跨 skill 通用的核心行為：

1. **Surface Assumptions** — 實作前顯式列出假設
2. **Manage Confusion Actively** — 遇到不一致 STOP、命名、提問、等回應
3. **Push Back When Warranted** — 對壞方案直說並量化副作用
4. **Enforce Simplicity** — 主動抵抗過度複雜
5. **Maintain Scope Discipline** — 只動被要求的範圍
6. **Verify, Don't Assume** — 沒驗證不算完成

### 3.6 跨工具載入機制

| 工具 | 載入方式 |
|------|---------|
| Claude Code | `/plugin marketplace add addyosmani/agent-skills` + `/plugin install` |
| Cursor | 複製 `SKILL.md` 到 `.cursor/rules/` |
| Antigravity CLI | `agy plugin install https://github.com/addyosmani/agent-skills.git` |
| Gemini CLI | `gemini skills install https://github.com/addyosmani/agent-skills.git --path skills` |
| Windsurf | 加到 Windsurf rules 設定 |
| OpenCode | 透過 AGENTS.md 與 `skill` tool |
| GitHub Copilot | `agents/` 當 persona，skill 內容放 `.github/copilot-instructions.md` |
| Kiro IDE/CLI | 放 `.kiro/skills/`（Project 或 Global level） |
| Codex / 其他 | 純 Markdown，任何吃 system prompt 的 agent 都能用 |

### 3.7 設計哲學來源

README 明確指出 skill 內嵌 Google 工程文化，源自《Software Engineering at Google》與 Google engineering practices guide：

| 來源概念 | 對應 skill |
|---------|-----------|
| Hyrum's Law | api-and-interface-design |
| Beyonce Rule + test pyramid | test-driven-development |
| Change sizing + review speed norms | code-review-and-quality |
| Chesterton's Fence | code-simplification |
| Trunk-based development | git-workflow-and-versioning |
| Shift Left + feature flags | ci-cd-and-automation |
| Code-as-liability | deprecation-and-migration |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 | 授權模式 | 是否需要外接 LLM |
|--------|----------|-------------|---------------|-----------------|---------|----------------|
| **Agent Skills (addyosmani)** | 24 個結構化 SKILL.md（含步驟、checkpoint、anti-rationalization 表、verification gate）+ 7 個 slash command + 4 個 persona，透過 frontmatter description 由 agent 自動觸發 | AI coding agent 需支援 slash command 或可讀 instruction 檔（Claude Code / Cursor / Gemini CLI / Antigravity / OpenCode / Copilot / Kiro 擇一） | skill 數量多需學習對應關係（靠 meta-skill 緩解）；每個 skill 強制 verification 會增加單次任務步驟數；對極簡單任務（typo 修正）流程過重 | 跨工具一致的工程紀律；agent 行為可預期、可審計；anti-rationalization 表直接壓制跳步傾向；progressive disclosure 控制 token | **MIT（開源免費）** | 否（skill 本身是靜態 Markdown，agent 讀取後自我約束；是否呼叫 LLM 取決於宿主 agent，與 skill 無關） |
| **Cursor Rules / `.cursor/rules/`** | 專案或全域規則檔，agent 載入後作為持續 context | Cursor IDE；規則需手動維護 | 無生命週期階段對應、無 verification gate、無 anti-rationalization 結構；規則之間無依賴順序；跨工具不可攜 | 簡單專案慣例一致化；上手門檻低；與 Cursor IDE 深度整合 | 視內容授權（Cursor 本身商用，規則檔作者自定） | 否 |
| **Claude Code Subagents / `.claude/agents/`** | 定義具備專屬 system prompt、工具白名單的子 agent，可被主 agent 委派 | Claude Code；需理解 subagent 委派模型 | subagent 間無共享 workflow；各自獨立、易產生幻覺「完成」；coordination 靠主 agent 手動 | 專家角色分工；工具權限隔離；平行處理子任務 | Claude 訂閱（subagent 機制為 Claude Code 內建） | 否（subagent 是 Claude 模型的不同角色，不外接其他 LLM） |
| **Aider `/docs` + convention files** | 約定檔案（CONVENTIONS.md 等）載入作為持續 context，搭配 Aider 的 edit/test/commit 自動化 | Aider CLI；git repo | 無結構化 workflow、無階段劃分；偏向「慣例提示」而非「流程強制」；無 anti-rationalization | 輕量級慣例一致化；與 Aider 的 git 操作深度整合 | Apache 2.0（Aider 本身） | 否 |
| **Meta-prompt / System prompt 工程（手寫）** | 在 system prompt 中手寫工程紀律要求 | 任何 LLM API | 難以維護、難以跨專案複用；無 verification gate；隨 prompt 長度增長效果遞減；無 anti-rationalization 結構 | 完全可控；可針對單一專案客製；無工具相依 | 自製（無授權問題） | 否 |

### 切入點差異

| 技術 | 切入角度 |
|------|---------|
| **Agent Skills** | **Workflow-first + 跨工具**：把工程紀律編碼成有步驟、checkpoint、verification 的可執行 workflow，並透過 slash command 對應生命週期，同時跨 8+ 種 agent 工具通用 |
| **Cursor Rules** | **IDE-native + 慣例提示**：在 Cursor 內以規則檔形式提供持續 context，輕量但無流程強制 |
| **Claude Code Subagents** | **角色分工 + 權限隔離**：以子 agent 切分專家角色與工具白名單，聚焦「誰做」而非「怎麼做」 |
| **Aider convention files** | **Git-native + 慣例**：與 Aider 的 git 操作綁定，輕量提供慣例提示，無結構化流程 |
| **手寫 system prompt** | **完全客製 + 專案綁定**：最自由但最難維護與複用，無 verification 結構 |