# Open Design 技術分析報告

## 1. 這個技術解決什麼問題？

**讓使用者以任意已安裝的 coding agent（Claude Code、Codex、Cursor 等），透過檔案化的 skills 與 design systems，從自然語言描述直接產出可編輯、可預覽、可匯出的設計產出物（prototype、deck、template、image、video），且完整掌控資料與流程的自主權。**

具體子問題：

- 現有 AI 輔助設計工具（Claude Design）為閉源、付費、雲端限定、鎖定單一供應商
- 傳統設計工具（Figma）為 GUI 操作，不適合 coding agent 驅動
- 使用者已有的 coding agent 無法直接被整合進結構化的設計工作流（skill 選擇 → design system 注入 → sandbox 預覽 → 匯出）
- 品牌設計系統無法以檔案化、可版本控制的形式被 agent 消費

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的

| 背景因素 | 說明 |
|----------|------|
| Anthropic 於 2026 年 4 月發布 **Claude Design** | 首次展示 LLM 可透過 agent loop（brief → direction → artifact → critique → deliver）直接產出設計 artifact；但該產品為閉源、付費、僅限 claude.ai、僅 Anthropic 模型 |
| **Open CoDesign** 是最接近的開源替代，但有架構限制 | Electron-based、使用自有的 `pi-ai` agent loop（無法複用既有 coding agent）、skill 格式為編譯進 app 的 TypeScript module（無法複用社群 SKILL.md）、無 design system 抽象層 |
| 社群已產出大量可複用的設計資產 | `awesome-claude-design`（68+ DESIGN.md 品牌系統）、`guizang-ppt-skill`（magazine-style deck skill）、`awesome-design-skills`（57+ 設計 skills），但缺少統一平台將這些組合起來 |
| Coding agent 生態已成熟 | Claude Code、Codex、Cursor Agent、Gemini CLI 等 17+ CLI 已在開發者機器上，它們能讀寫檔案、執行工具、理解 SKILL.md，但被設計產出場景忽略 |

### 通用技術背景（自行補充）

| 背景因素 | 說明 |
|----------|------|
| **MCP (Model Context Protocol)** 成為跨 agent 的標準介面 | Anthropic 推出的 MCP 協議讓任何 agent 可以透過 stdio JSON-RPC 與外部工具互動，Open Design 利用 MCP server 讓外部 agent 直接查詢 design files |
| **SSE (Server-Sent Events)** 為 streaming 場景的標準解法 | 瀏覽器端可透過 EventSource 或 fetch + ReadableStream 接收 daemon 轉發的 agent 輸出事件，無需 WebSocket |
| **Next.js 16 App Router** 提供 hybrid rendering | SSR for landing page + serverless API routes + static export，讓同一 bundle 可部署 local dev server、Vercel、或 Electron 內 |
| **better-sqlite3** 作為本地嵌入式資料庫 | 比 SQLite CLI 更快，適合 Electron/Node 桌面應用場景；但 Open Design 在 artifact 層堅持使用 plain files + JSONL，SQLite 僅用於 UI state（projects/conversations/messages） |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體架構

```
┌──────────────────────────────────────────────────────────┐
│                      Open Design                          │
├──────────────────────────────────────────────────────────┤
│  apps/web/       Next.js 16 App Router + React 18         │
│                  chat pane · artifact tree · sandbox iframe│
│                  comment mode · slider controls · export   │
├──────────────────────────────────────────────────────────┤
│  apps/daemon/    Node 24 + Express + SSE + better-sqlite3 │
│                  agent detection · skill registry          │
│                  artifact store · design-system resolver   │
│                  MCP server · od CLI                       │
├──────────────────────────────────────────────────────────┤
│  apps/desktop/   Electron shell (macOS + Windows)          │
│                  wraps daemon + web via sidecar IPC        │
├──────────────────────────────────────────────────────────┤
│  skills/         155+ SKILL.md bundles                    │
│  design-systems/ 150+ DESIGN.md brand contracts           │
│  craft/          universal brand-agnostic rules            │
│  design-templates/ decks · prototypes · image/video/audio  │
└──────────────────────────────────────────────────────────┘
```

### 3.2 部署拓樸（三種）

```
Topology A — 全本地（預設）
  browser → Next.js dev server (localhost:3000)
             → daemon (localhost:7456)
               → spawn: claude / codex / cursor / …

Topology B — Web on Vercel + daemon on user machine
  browser → od.yourdomain.com (Vercel)
             → tunnel (cloudflared)
               → daemon on laptop
                 → spawn agent CLI

Topology C — Vercel + direct API (no daemon)
  browser → Vercel serverless → Anthropic Messages API (BYOK)
  ※ 無本地 agent，功能降級
```

### 3.3 核心機制：Prompt Composition（三層堆疊）

對於每一次生成，daemon 構建三層 system prompt：

```
BASE_SYSTEM_PROMPT   (output contract: wrap in <artifact>, no code fences)
   + active DESIGN.md    (9-section brand contract)
   + active SKILL.md     (workflow and output rules)
```

```
DESIGN.md 格式（9-section, per awesome-claude-design）:

# <Brand Name>
## Visual Theme & Atmosphere
## Color Palette & Roles
## Typography Rules
## Component Stylings
## Layout Principles
## Depth & Elevation
## Do's and Don'ts
## Responsive Behavior
## Agent Prompt Guide
```

### 3.4 Agent Adapter 機制（核心差異化設計）

OD 不實作自己的 agent loop。每個 adapter 實作相同介面：

```typescript
interface AgentAdapter {
  readonly id: string;        // "claude-code" | "codex" | …
  detect(): Promise<AgentDetection | null>;
  capabilities(): AgentCapabilities;
  run(params: AgentRunParams): AsyncIterable<AgentEvent>;
  cancel(runId: string): Promise<void>;
  resume?(runId: string, message: string): AsyncIterable<AgentEvent>;
}
```

支援的 agent（v0.9.0）：

| Adapter | CLI cmd | Skill loading | Surgical edit | Streaming |
|---------|---------|---------------|---------------|-----------|
| claude-code | `claude` | native (symlink) | ✅ | stream-json |
| codex | `codex` | prompt injection | 〜 (regenerate) | line-based |
| cursor-agent | `cursor-agent` | .cursorrules | ✅ | JSON lines |
| gemini-cli | `gemini` | prompt injection | ❌ (regenerate) | stream-json |
| copilot | `copilot` | prompt injection | ✅ (edit tool) | JSONL |
| opencode | `opencode` | 〜 | ✅ | stdio |
| devin | `devin acp` | native + prompt inject | ✅ | ACP JSON-RPC |
| hermes | `hermes` | prompt injection | ✅ | ACP JSON-RPC |
| pi | `pi --mode rpc` | prompt injection | ✅ | pi-rpc JSON-RPC |
| kimi | `kimi` | prompt injection | ✅ | ACP JSON-RPC |
| qwen | `qwen` | prompt injection | ✅ | stream-json |
| deepseek | `deepseek exec --auto` | prompt injection | ✅ | plain text |
| …and more | | | | |

### 3.5 Skill 系統

Skills 是 Claude Code 的 `SKILL.md` 格式 + OD extensions (optional `od:` YAML block)：

```
<skill-root>/
├── SKILL.md           # manifest + workflow (YAML frontmatter + Markdown body)
├── assets/            # templates, images, boilerplate
└── references/        # knowledge files for planning
```

```yaml
# SKILL.md frontmatter 範例
---
name: saas-landing
description: "Single-page SaaS landing page."
triggers: ["saas landing", "marketing page"]
od:
  mode: prototype
  preview:
    type: html
    entry: index.html
  design_system:
    requires: true
    sections: [color, typography, layout]
  inputs:
    - name: product_name
      type: string
      required: true
  parameters:
    - name: accent_hue
      type: hue
      default: 18
      range: [0, 360]
---
```

Skill 發現與優先級：

| Location | Priority | Purpose |
|----------|----------|---------|
| `./.claude/skills/` | 1 (highest) | project-private |
| `./skills/` | 2 | project-committed |
| `~/.claude/skills/` | 3 | user-global |

### 3.6 四種 Mode（對應四種 skill type）

| Mode | Skill type | 產出 | 耗時 |
|------|-----------|------|------|
| **Prototype** | `prototype-skill` | 單頁 HTML/JSX prototype | 60-120s |
| **Deck** | `deck-skill` | 多頁簡報（HTML + PPTX export） | 90-180s |
| **Template** | `template-skill` | 已填充內容的模板 | 20-40s |
| **Design System** | `design-system-skill` | `DESIGN.md` + sample preview | 60-180s |

### 3.7 Artifact Store（純檔案架構）

```
./.od/
├── app.sqlite              # UI state: projects/conversations/messages/tabs
├── artifacts/
│   └── 2026-04-24T10-03-12-landing/
│       ├── artifact.json   # metadata (skill, mode, prompt, parent)
│       ├── index.html      # primary output
│       └── assets/         # generated images, fonts
├── history.jsonl           # append-only action log
└── projects/<id>/          # per-project working dir + agent cwd
```

### 3.8 MCP Server（跨 agent 互通）

```
od mcp install <agent>    # 一鍵安裝到 Claude Code / Codex / Cursor / …
```

MCP server 暴露以下能力給外部 agent：

```
od search-files "primary button"   # 跨 projects 搜尋
od get-file design-systems/linear-app/DESIGN.md
od get-artifact <slug>             # 最新 rendered artifact
od plugin run web-prototype --brief "..."
od skill list --scenario marketing
```

### 3.9 典型工作流

```
1. PM submits brief
   ↓
2. Designer (or agent) locks direction
   ├─ pick from 5 curated directions, OR
   └─ drop screenshot/URL → agent extracts DESIGN.md
   ↓
3. Agent emits <artifact> → streams into sandboxed iframe
   ↓
4. Hand off to engineering (real HTML/CSS) OR export PPTX/PDF/MP4
   ↓
5. OD accumulates defaults (screenshots, fonts, palettes, confirmed artifacts)
```

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **Open Design** | Agent adapter shell：不自有 agent loop，而是將使用者已安裝的 coding agent CLI 包裝為統一介面；檔案化 skills (SKILL.md) + design systems (DESIGN.md) + MCP server 實現跨 agent 互通 | Node 24、pnpm 10.33、已安裝至少一個支援的 coding agent CLI 或使用 BYOK API fallback；macOS/Windows/Linux 桌面或 Docker | 需同時運行 daemon process（~150MB RAM）；純 API 模式（無本地 agent）功能受限（無 filesystem artifacts、無 PPTX export）；不同 agent 能力不一（skill loading、surgical edit 等皆需 adapter 處理） | 以任意 agent 從自然語言產出 prototype/deck/template/design system；輸出為真實 HTML/CSS/PDF/PPTX/MP4 檔案；品牌一致性由 DESIGN.md 確保 |
| **Claude Design** (Anthropic) | Anthropic 自有的 agent loop，透過 claude.ai 提供設計 artifact 產出 | 需 Claude Pro/Max/Team 訂閱；僅 Anthropic 模型；僅 claude.ai 介面 | 閉源無法自訂；產出存於 Anthropic 雲端；無法換 agent 或 model provider；無法自訂 skill/design system 格式 | 從 brief 產出高品質 design artifact；AI 輔助的設計迭代流程 |
| **Figma** | GUI-based 向量設計工具，透過 plugin 擴展；有 Figma AI 輔助功能 | 需 Figma 訂閱（Pro/Org）；需人類操作 GUI | 非 agent-native（需 GUI）；產出為 Figma 格式非真實 code；無法被 coding agent 直接讀寫 | 專業級 UI/UX 設計；協作編輯；豐富 plugin 生態 |
| **Lovable / v0 / Bolt** | 雲端 AI 設計工具，從 prompt 產出 web app/site，內建 agent loop | 各平台自有訂閱；雲端限定；不可自訂 agent | 閉源、產出存於平台雲端；僅限內建模型；不可自訂技能或設計系統 | 快速產生 web app prototype；適合非技術人員 |

### 切割點差異

| 技術 | 切割角度 |
|------|---------|
| Open Design | **Integration shell** — 不自有 agent/model/skills，將三者組合成設計工作流；檔案即介面 |
| Claude Design | **Proprietary product** — Anthropic 自有的完整 stack，從模型到 UI 到 skill 全封閉 |
| Figma | **GUI canvas** — 以像素為單位的手動設計工具，AI 為輔助而非主驅動 |
| Lovable / v0 | **Cloud generator** — 雲端一站式的 prompt-to-app，封閉生態且無 design system 抽象 |

---

## 5. OpenCode + Open Design 實戰步驟指引

### 架構總覽

```
┌──────────────┐     spawn      ┌──────────────┐    internal routing    ┌──────────────┐
│  Open Design  │ ────────────→ │   opencode    │ ────────────────────→ │  Ollama Cloud │
│   (daemon)    │               │   (CLI)       │                       │  (or local)   │
│               │ ←──────────── │               │ ←──────────────────── │               │
│  localhost:   │  SSE stream   │  on your PATH │    model response     │  your sub     │
│  7456         │               │               │                       │               │
└──────────────┘               └──────────────┘                       └──────────────┘
```

關鍵：Open Design 只負責把 prompt + skill + DESIGN.md 餵給 opencode，**不碰 API key、不碰 model routing**。你的 opencode 內部的 Ollama 訂閱完全維持原樣。

---

### Phase 0 — 前置確認

```bash
# 檢查 opencode 是否已安裝且可正常執行
opencode --version

# 確認 opencode 能正常調用 Ollama（用一句 smoke test）
echo 'say hello' | opencode

# 檢查 Node 版本（需 ~24）
node --version
```

| 檢查項 | 命令 | 預期結果 |
|--------|------|---------|
| opencode 存在 | `which opencode` | 回傳絕對路徑，如 `/usr/local/bin/opencode` |
| opencode 可執行 | `opencode --version` | 回傳版本號 |
| Ollama 連通 | `echo 'reply in 1 word: ok' \| opencode` | 回傳 `ok` |
| Node 版本 | `node --version` | 需 `v24.x.x` |

---

### Phase 1 — 安裝 Open Design

```bash
# 方案 A: 桌面版（推薦，零設定）
# 直接從 https://github.com/nexu-io/open-design/releases 下載 macOS/Windows 版
# 安裝後啟動即可，app 會自動偵測你 PATH 上的 opencode

# 方案 B: CLI 一鍵安裝（如果你偏好 terminal）
curl -fsSL https://open-design.ai/install.sh | sh -s opencode

# 方案 C: 從原始碼執行（如果你想看/改原始碼）
git clone https://github.com/nexu-io/open-design.git
cd open-design
corepack enable && pnpm install
pnpm tools-dev run web
```

---

### Phase 2 — 啟動與首次設定

```bash
# 如果走方案 B (CLI 安裝)，直接啟動 daemon
od daemon
# 打開瀏覽器 http://localhost:7456

# 如果走方案 C (原始碼)，啟動 dev loop
pnpm tools-dev run web
# 自動啟動 daemon + web UI，打開 terminal 印出的 URL
```

初次啟動後：

```
1. Open Design 自動掃描 PATH，偵測到 opencode
2. UI 左上方 agent 下拉選單會顯示 opencode（已打勾）
3. 如果沒偵測到 → Settings → Execution mode → 按「Rescan」
4. 確認 agent 選為 opencode
```

---

### Phase 3 — 選 Skill + Design System + 打 Prompt

UI 頂部有三個選擇器：

```
┌───────────────────────────────────────────────────────────┐
│  Agent: [opencode ▼]    Skill: [web-prototype ▼]          │
│  Design System: [Neutral Modern ▼]                        │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 幫我做一個募資簡報用的 landing page，主打 AI 筆記工具 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                 [Send →] │
└───────────────────────────────────────────────────────────┘
```

| 選擇器 | 作用 | 範例值 |
|--------|------|--------|
| **Agent** | 選 opencode（你 PATH 上的 CLI） | opencode |
| **Skill** | 選產出類型，決定 agent 的行為流程 | `web-prototype`、`saas-landing`、`dashboard` |
| **Design System** | 選品牌風格，自動注入 palette/typography/layout | `Neutral Modern`、`Linear`、`Stripe` |

---

### Phase 4 — 產生與預覽

```
按下 Send 後的流程：

1. daemon 將 BASE_SYSTEM_PROMPT + DESIGN.md + SKILL.md 組成 system prompt
2. daemon spawn opencode CLI，透過 stdin 送入 prompt
3. opencode 走內部 Ollama 訂閱執行 model inference
4. opencode 的 stdout (agent events) 被 daemon 轉換為 SSE stream
5. 瀏覽器即時顯示：
   ├─ 左側：chat log + tool call 進度
   ├─ 右側：sandboxed iframe 預覽（agent 寫出 index.html 後自動載入）
   └─ 底部：artifact 檔案樹（index.html、assets/）
```

**預覽功能**：
- 即時 hot-reload：agent 每寫一次檔案，右側 iframe 自動刷新
- 多幀切換：desktop / tablet / phone 寬度預覽
- 匯出：HTML / PDF / ZIP

---

### Phase 5 — 迭代修改（Vibe Design Loop）

核心 loop：「看效果 → 打字描述要改什麼 → agent 修改 → 再看效果」

```
┌──────────────────┐
│  看 sandbox 預覽  │ ← 起點
└────────┬─────────┘
         │ 覺得 CTA 太下面、hero 太空、顏色不對…
         ▼
┌──────────────────┐
│  打字描述要改什麼  │  「把 CTA 移到 hero 下方」「hero 加半透明動畫」
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  opencode 收到    │  同一 session，daemon 重新 spawn opencode
│  修改指令＋既有檔  │  附帶已產生的 artifact 檔案內容
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  iframe 自動刷新  │  回到起點
└──────────────────┘
```

---

### Phase 6 — 進階用法

#### 6.1 用你自己的 Design System

```bash
# 從 URL 提取 brand
# 在 OD UI 的 Design System mode 中：
#   "analyze https://airbnb.com" → agent 自動產生 DESIGN.md

# 或手寫 DESIGN.md，放到專案目錄
cat > ./DESIGN.md << 'EOF'
# My Brand

## Visual Theme & Atmosphere
Warm, editorial, terracotta accent

## Color Palette & Roles
- Primary: #E07A5F
- Background: #F4F1DE
- Text: #3D405B

## Typography Rules
- Headings: Georgia, serif
- Body: Inter, system-ui
EOF
```

#### 6.2 從 opencode 內部呼叫 OD（MCP mode）

```bash
# 一鍵安裝 MCP server 到 opencode
od mcp install opencode

# 之後在 opencode 內部直接呼叫：
#   "use open-design to generate a landing page with the Linear design system"
#   "od search-files pricing card"
#   "od get-artifact my-landing"
```

#### 6.3 直接從 Terminal 用 od CLI

```bash
# 不開 GUI，直接從 CLI 產生（適合 script / automation）
od plugin run web-prototype --brief "SaaS landing page for AI note app"
od skill list
od project list
```

---

### 常見問題

| 問題 | 解法 |
|------|------|
| opencode 沒被偵測到 | `which opencode` 確認在 PATH 上 → OD Settings → 按 Rescan；macOS 若從非 login shell 啟動 OD，PATH 可能不完整 |
| 產生卡住/無回應 | 先確認 `echo 'reply ok' \| opencode` 可正常執行；檢查 Ollama 訂閱是否有效 |
| artifact 沒出現在 iframe | model 輸出沒包在 `<artifact>` 標籤內 → 檢查 daemon log，或換一個更嚴格的 skill |
| 想換 model | opencode 的 model 選擇維持在你 opencode 設定內（config file / env var），OD 不介入 |

---

### 最小可行流程總結（5 分鐘上手）

```bash
# 1. 確認環境
opencode --version && node --version

# 2. 安裝 Open Design（CLI 模式）
curl -fsSL https://open-design.ai/install.sh | sh -s opencode

# 3. 啟動並打開瀏覽器
od daemon
# → 瀏覽器開 http://localhost:7456

# 4. UI 中：
#    Agent: opencode（預設自動選）
#    Skill: web-prototype
#    Design System: Neutral Modern
#    Prompt: 「幫我做一個個人 portfolio 頁面，簡約風格」

# 5. 看右側 preview → 打字改 → 再看 → 改到滿意 → 匯出 HTML
```
