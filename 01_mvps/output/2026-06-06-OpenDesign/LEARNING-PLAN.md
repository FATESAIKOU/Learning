# OpenDesign 學習計畫

**日期**: 2026-06-06
**目標**: 跑通完整 OpenDesign 工作流（安裝 → 偵測 agent → 選 skill/design system → prompt → sandbox preview → vibe design 迭代 → 匯出），建立心智模型
**Agent**: opencode (v1.16.2, deepseek-v4-pro via Ollama Cloud)
**環境**: M4 Mac Pro, Node v24.15.0

---

## 技術分析

### 1. 這個技術解決什麼問題？

讓使用者以任意已安裝的 coding agent（Claude Code、Codex、OpenCode、Cursor 等），透過檔案化的 skills 與 design systems，從自然語言描述直接產出可編輯、可預覽、可匯出的設計產出物（prototype、deck、template、image、video），且完整掌控資料與流程的自主權。

具體子問題：

| 問題 | 說明 |
|------|------|
| Claude Design 閉源 | Anthropic 2026/4 發布的 Claude Design 為閉源、付費、僅限 claude.ai、僅 Anthropic 模型 |
| Figma 非 agent-native | GUI 操作，不適合 coding agent 驅動的工作流 |
| 無統一 skill/design-system 平台 | 社群已有大量 SKILL.md 和 DESIGN.md，但缺少平台將二者組合，並餵給任意 agent |
| Coding agent 生態被設計場景忽略 | Claude Code、Codex、Cursor 等 21+ CLI 已在使用者機器上，但被設計工作流忽略 |

### 2. 這個問題為什麼會發生？（背景）

**明確提到的背景：**

| 背景因素 | 說明 |
|----------|------|
| Anthropic 發布 Claude Design (2026/4) | 首次展示 LLM 可走 agent loop（brief → direction → artifact → critique → deliver）直接產出設計 artifact |
| Open CoDesign 的架構限制 | Electron-based、自有 agent loop（無法複用既有 coding agent）、skill 格式為 TS module（無法複用社群 SKILL.md） |
| 社群資產已豐富但分散 | `awesome-claude-design`（68+ DESIGN.md）、`guizang-ppt-skill`、`awesome-design-skills`（57+ skills） |
| Coding agent 生態成熟 | Claude Code、Codex、Cursor Agent、Gemini CLI、OpenCode 等 21+ CLI 可讀寫檔案、執行工具、理解 SKILL.md |

**通用技術背景：**

| 背景因素 | 說明 |
|----------|------|
| MCP (Model Context Protocol) | 跨 agent 的標準 stdio JSON-RPC 介面；Open Design 利用 MCP 讓外部 agent 查詢 design files |
| SSE (Server-Sent Events) | 瀏覽器端接收 daemon 轉發的 agent streaming output |
| Next.js 16 App Router | Hybrid rendering (SSR + serverless API + static export) |
| better-sqlite3 | 嵌入式資料庫，用於 UI state；artifact 層使用 plain files + JSONL |

### 3. 這個技術是如何解決該問題的？

**核心機制：三層 Prompt Composition + Agent Adapter + 檔案化 Skills/Design Systems**

```
BASE_SYSTEM_PROMPT   (output contract: wrap in <artifact>, no code fences)
   + active DESIGN.md    (9-section brand contract)
   + active SKILL.md     (workflow and output rules)
```

**執行流程：**
```
browser (web UI) → daemon (localhost:7456)
  → spawn opencode CLI (prompt + skill + DESIGN.md via stdin)
  → stdout (agent events) → SSE stream → artifact parser → sandbox iframe preview
```

**四種 Mode：**

| Mode | Skill type | 產出 |
|------|-----------|------|
| Prototype | prototype-skill | 單頁 HTML prototype |
| Deck | deck-skill | 多頁簡報（HTML + PPTX export） |
| Template | template-skill | 已填充內容的模板 |
| Design System | design-system-skill | DESIGN.md + sample preview |

**Agent Adapter 機制：** 不實作自有 agent loop。每個 adapter 實作 `AgentAdapter` 介面（detect / capabilities / run / cancel），包裝使用者的 CLI。

---

## AI 加速 Prompt

可直接貼給 AI 的 prompt，用於快速生成基礎專案：

```
You are an OpenDesign skill author. Create a SKILL.md for a "web-prototype" mode skill.

Requirements:
- mode: prototype
- preview: type html, entry index.html
- design_system: requires true, sections [color, typography, layout]
- inputs: product_name (string, required), description (string, optional)
- The body of SKILL.md should guide the agent to produce a single-page HTML prototype with hero, features, pricing, and CTA sections
- Use Tailwind CSS v4 CDN for styling
- Output must be wrapped in <artifact> tags with no markdown code fences

Output format: a complete SKILL.md file with YAML frontmatter.
```

---

## Todo Checklist（60 分鐘學習路徑）

### Phase A: 環境建置

- [x] **A1. 安裝 pnpm（透過 asdf）**
  - 目的：後續若需從原始碼安裝或建置 OpenDesign 時必備
  - 驗證：`pnpm --version` 回傳版本號（目標 ~10.33.x）
  - 實際結果：pnpm 11.5.2（走 Desktop App 不需 source build，版本不影響）
  - 預估時間：5 分鐘

- [ ] **A2. 下載並安裝 OpenDesign Desktop App**
  - 目的：取得 web UI（chat + sandbox preview）+ daemon + 內建 skills/design-systems
  - 驗證：啟動 app 後瀏覽器打開 `http://localhost:7456`，看到 Home 畫面
  - 預估時間：5 分鐘

- [ ] **A3. 驗證 opencode agent 被 OpenDesign 偵測**
  - 目的：確認 daemon PATH 掃描成功找到 opencode，agent 下拉選單顯示 opencode（已打勾）
  - 驗證：UI 左上方 agent 選單為 opencode；若未偵測到則進 Settings → Rescan
  - 預估時間：5 分鐘

### Phase B: 首次 Prototype 產生

- [ ] **B1. 選 skill + design system + 輸入 prompt**
  - 目的：使用預設 `web-prototype` + `Neutral Modern`，輸入一個簡單的 landing page prompt
  - 驗證：按下 Send 後，左側 chat 顯示 agent streaming 輸出；右側 sandbox iframe 出現 prototype
  - Prompt 範例：「幫我做一個 AI 筆記工具的 landing page，簡約風格，含 hero、features、pricing、CTA」
  - 預估時間：10 分鐘

- [ ] **B2. 觀察 artifact 產出結構**
  - 目的：理解 daemon 如何從 opencode 的 stdout 解析 `<artifact>` 標籤並渲染到 iframe
  - 驗證：點擊底部 artifact 檔案樹，確認有 `index.html` 及可能的 `assets/` 目錄
  - 預估時間：5 分鐘

### Phase C: Vibe Design 迭代

- [ ] **C1. 執行至少 3 輪 vibe design 迭代**
  - 目的：體驗「看效果 → 打字 → 改 → 再看」的核心 loop
  - 驗證：每次迭代後 sandbox iframe 自動刷新，頁面確實依指令變更
  - 範例指令：「把 CTA 按鈕改成橘色」「hero 加上漸層背景」「縮小 pricing card 間距」
  - 預估時間：10 分鐘

- [ ] **C2. 切換不同 design system 觀察差異**
  - 目的：理解 DESIGN.md 如何影響產出風格
  - 驗證：選 `Linear` 或 `Stripe` design system，以相同或類似 prompt 重新產生，對比視覺差異
  - 預估時間：5 分鐘

### Phase D: 了解輸出與邊界

- [ ] **D1. 匯出 HTML 檔案**
  - 目的：理解產出物為真實 HTML/CSS（非 Figma 格式），可直接交付工程
  - 驗證：下載 HTML 後以瀏覽器直接打開，樣式/互動正常
  - 預估時間：3 分鐘

- [ ] **D2. 嘗試不同 skill mode（如有時間）**
  - 目的：擴展心智模型，了解 prototype / deck 等 mode 的能力邊界
  - 驗證：選 `simple-deck` skill，輸入簡報 prompt，觀察多頁簡報預覽
  - 預估時間：7 分鐘

- [ ] **D3. 總結能力邊界與導入設想**
  - 目的：根據實際操作經驗，整理 OpenDesign 的能力邊界與公司內導入 Figma 設計流的建構方式
  - 驗證：產出一份簡短筆記，記錄 (a) 能做到的事 (b) 做不到的事 (c) 與 Figma 的互補關係
  - 預估時間：5 分鐘

---

**總預估時間：60 分鐘**
