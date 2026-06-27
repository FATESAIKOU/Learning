# OpenMontage 技術分析報告

## 1. 這個技術解決什麼問題？

**讓任意已安裝的 AI coding assistant（Claude Code、Cursor、Copilot、Codex、Windsurf）直接作為「影片製作總監」，用自然語言一句話驅動完整影片製作流程——從研究、腳本、資產生成、剪輯到最終渲染——並以純檔案化的 YAML pipeline manifest 與 Markdown skill 指令定義整個工作流，Python 僅負責工具與持久化，不負責編排。**

具體子問題：

- 現有 AI 影片工具多為「單一 prompt → 一支短片」的黑箱產品，缺少結構化、可審查、可恢復的端到端製作流程
- 製作一支影片涉及多個異質能力（研究、影像、語音、音樂、剪輯、字幕、渲染），分散在十幾個供應商，使用者難以自行組合與切換
- 免費/開源路徑與付費雲端 API 路徑長期分裂，缺乏統一的選擇與降級機制
- 影片品質缺乏強制驗證，AI 產出常出現「幻燈片式假影片」「黑幀」「字幕未燒入」等問題，無法在交付前自動攔截

問題描述的模糊之處：README 稱「12 pipelines, 52 tools, 500+ agent skills」，但 README、ARCHITECTURE.md、AGENT_GUIDE.md 對 tool 數量的描述不一致（48/52/57+），skill 數量也浮動（400+/500+）。這是文件版本漂移，非核心機制模糊。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的

| 背景因素 | 說明 |
|----------|------|
| AI coding agent 生態成熟 | Claude Code、Cursor Agent、Copilot、Codex 等 CLI 已能讀寫檔案、執行工具、理解 Markdown 指令，但被侷限在「軟體開發」場景，未延伸到影片製作 |
| 影片製作供應商高度碎片化 | 影片生成（Kling/Runway/Veo/Grok/Higgsfield/MiniMax/HeyGen/本地 WAN/Hunyuan/CogVideo/LTX）、影像生成（FLUX/Imagen/DALL-E/Recraft/Grok/本地）、語音（ElevenLabs/OpenAI/Google/Piper）、音樂（Suno/ElevenLabs）各自為政，無統一介面 |
| 影片生成成本不透明且易失控 | 單支 AI 影片可能花 $0.15 到 $3，但使用者無法在執行前知道會花多少，容易超支 |
| 「免費 AI 影片」普遍是騙局 | 多數工具實際上是「靜態圖片 + Ken Burns 動畫」，偽裝成「影片」，缺少真正的動態影像檢驗 |
| 真實影片剪輯長期需人工 | 紀錄片、訪談、podcast 剪輯需要專業剪輯師，AI 工具無法從 2 小時來源素材切出 12 支短片 |

### 通用技術背景（自行補充）

| 背景因素 | 說明 |
|----------|------|
| LLM agent 的「指令驅動編排」模式成型 | 以 Claude Code 為代表，agent 不需要程式碼 orchestrator，讀 YAML manifest + Markdown skill 即可驅動多步驟任務；OpenMontage 將此模式應用到影片製作 |
| Remotion 程式化影片成熟 | Remotion 以 React 元件定義影片場景，可被 agent 程式化生成 `composition.tsx`，而非人工在 GUI 內剪輯 |
| WhisperX 提供字級時間戳 | 影片字幕可從語音自動生成並精確對齊，是 TikTok 風格逐字字幕的技術基礎 |
| CLIP/BLIP-2 視覺語言模型 | 讓「從語意檢索素材」成為可能，OpenMontage 的 documentary-montage pipeline 用 CLIP 對免費素材庫做語意排序 |
| FFmpeg 為後製通用工具 | 字幕燒入、音軌混合、色彩分級、轉碼全可由 FFmpeg 完成，是免費路徑的基石 |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體架構：Agent-First，無 Python Orchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                         OpenMontage                              │
├─────────────────────────────────────────────────────────────────┤
│  User 的 AI coding assistant (Claude Code / Cursor / Codex / …)   │
│  ↑ 這就是 orchestrator，沒有獨立的 Python 編排器                    │
├─────────────────────────────────────────────────────────────────┤
│  pipeline_defs/*.yaml    Pipeline manifest (階段、工具、品質閘)    │
│  skills/pipelines/*/*.md Stage director skill (如何執行每階段)    │
│  skills/meta/*.md        Reviewer / checkpoint / onboarding      │
│  .agents/skills/*        Layer 3: 供應商技術知識 (FFmpeg/GSAP…)   │
├─────────────────────────────────────────────────────────────────┤
│  tools/  (Python BaseTool 子類，~57 個)                          │
│    video/  audio/  graphics/  enhancement/  analysis/            │
│    avatar/  subtitle/  (透過 tool_registry 自動發現)              │
├─────────────────────────────────────────────────────────────────┤
│  remotion-composer/  React/Remotion 渲染引擎                      │
│  HyperFrames         HTML/CSS/GSAP 渲染引擎 (npx hyperframes)     │
│  FFmpeg              影片組裝、字幕燒入、轉碼                      │
├─────────────────────────────────────────────────────────────────┤
│  lib/  config / checkpoint / pipeline_loader / cost_tracker      │
│  schemas/  15 JSON Schema (artifact、checkpoint、pipeline)       │
│  styles/  3 個 playbook (clean-professional / flat-motion / …)   │
└─────────────────────────────────────────────────────────────────┘
```

核心控制流：

```
User: "Make a 60-second explainer about black holes"
    ↓
Agent 讀 pipeline_defs/animated-explainer.yaml  (知道 8 階段流程)
    ↓
Agent 讀 skills/pipelines/explainer/<stage>-director.md  (知道每階段如何執行)
    ↓
Agent 用 tool_registry.discover() 列出可用工具,呈現 capability menu
    ↓
Agent 逐階段執行: research → proposal → script → scene_plan → assets → edit → compose
    每階段: 呼叫 Python tool → 寫 checkpoint (JSON) → 自審 (reviewer skill)
    ↓
Pre-compose 驗證閘 (delivery promise / slideshow risk / renderer governance)
    ↓
Render (Remotion / HyperFrames / FFmpeg, 由 edit_decisions.render_runtime 路由)
    ↓
Post-render 自審 (ffprobe / frame extraction / audio analysis / promise verify)
    ↓
final.mp4  (僅在自審通過時交付)
```

### 3.2 三層知識架構

| Layer | 位置 | 角色 | 範例 |
|-------|------|------|------|
| Layer 1 | `tools/` + `pipeline_defs/` | **存在什麼** — 可執行能力 + 編排定義 | `video_compose.execute()`, `animated-explainer.yaml` |
| Layer 2 | `skills/` | **如何使用** — OpenMontage 慣例、品質標準 | `skills/pipelines/explainer/script-director.md` |
| Layer 3 | `.agents/skills/` | **底層如何運作** — 供應商技術知識 | `.agents/skills/ai-video-gen/SKILL.md` (Kling prompt 結構) |

工具的 `agent_skills` 欄位從 Layer 1 連結到 Layer 3。Agent 呼叫任何生成工具前，必須先讀其 Layer 3 skill，否則視為違反合約。

### 3.3 Pipeline Manifest（YAML 定義生產流程）

```yaml
# pipeline_defs/animated-explainer.yaml 結構
name: animated-explainer
version: "2.0"
category: generated
stability: production
default_checkpoint_policy: guided

reference_input:
  supported: true
  analysis_depth: standard
  analysis_tools: [video_analyzer, transcript_fetcher, scene_detect, frame_sampler]

orchestration:
  mode: executive-producer
  skill: pipelines/explainer/executive-producer
  budget_default_usd: 2.00
  max_revisions_per_stage: 3
  max_wall_time_minutes: 20

compatible_playbooks:
  recommended: [clean-professional, flat-motion-graphics]
  also_works: [minimalist-diagram]
  custom_allowed: true

stages:
  - name: research
    skill: pipelines/explainer/research-director
    produces: [research_brief]
    tools_available: []
    checkpoint_required: false
    human_approval_default: false
    review_focus:
      - Content landscape mapped with at least 3 existing pieces
      - Data points are specific and sourced, not vague
      - At least 3 angles_discovered, each with grounded_in references
    success_criteria:
      - Schema-valid research_brief with at least 3 data_points
      - At least 5 sources cited with URLs

  - name: proposal
    required_artifacts_in: [research_brief]
    produces: [proposal_packet, decision_log]
    checkpoint_required: true
    human_approval_default: true   # 必須人工批准才能進入 asset 階段
    review_focus:
      - Concept options are genuinely different (structure, hook, audience)
      - Cost estimate is itemized and honest
      - Quality/cost tradeoffs clearly presented

  # ... script → scene_plan → assets → edit → compose
```

12 個 pipeline：

| Pipeline | Category | 產出 | Stability |
|----------|----------|------|-----------|
| animated-explainer | generated | 研究型解說影片 | production |
| animation | animation | 動態圖像、kinetic typography | production |
| avatar-spokesperson | talking_head | 虛擬主播 | production |
| character-animation | animation | SVG 角色綁定 + GSAP 時間軸 | beta |
| cinematic | cinematic | 電影預告、情緒剪輯 | production |
| clip-factory | custom | 長片切多支短片 | beta |
| documentary-montage | generated | CLIP 語意檢索免費素材剪輯 | beta |
| hybrid | hybrid | 真實素材 + AI 支援視覺 | production |
| localization-dub | custom | 字幕、配音、翻譯 | beta |
| podcast-repurpose | hybrid | Podcast 精華轉影片 | beta |
| screen-demo | screen_recording | 軟體螢幕錄影 + 解說 | production |
| talking-head | talking_head | 真人演講鏡頭 | beta |

### 3.4 BaseTool 契約（統一工具介面）

所有工具繼承 `BaseTool`，宣告以下欄位並實作 `execute()`：

```python
class BaseTool(ABC):
    name: str
    version: str
    tier: ToolTier            # CORE / VOICE / ENHANCE / GENERATE / SOURCE / ANALYZE / PUBLISH
    capability: str           # tts / image_generation / video_generation / video_post / …
    provider: str             # elevenlabs / openai / ffmpeg / kling / flux / …
    runtime: ToolRuntime      # LOCAL / LOCAL_GPU / API / HYBRID
    stability: ToolStability  # EXPERIMENTAL / BETA / PRODUCTION
    dependencies: list        # cmd:ffmpeg, env:ELEVENLABS_API_KEY, python:torch
    input_schema: dict        # JSON Schema for inputs
    output_schema: dict       # JSON Schema for outputs
    fallback_tools: list[str] # 有序降級鏈
    agent_skills: list[str]   # 指向 Layer 3 skill
    resource_profile: ResourceProfile  # CPU/RAM/VRAM/disk/network
    retry_policy: RetryPolicy

    @abstractmethod
    def execute(self, inputs: dict) -> ToolResult: ...
```

`ToolResult` 攜帶 `success`、`data`、`artifacts`（檔案路徑）、`cost_usd`、`duration_seconds`、`seed`、`model`。

Tool Registry 為 singleton，透過 `pkgutil.walk_packages()` 自動發現所有 `BaseTool` 子類，無需手動註冊。查詢介面：

| 方法 | 用途 |
|------|------|
| `get_by_capability("tts")` | 列出某能力的所有工具 |
| `get_by_provider("elevenlabs")` | 列出某供應商的所有工具 |
| `get_available()` | 只回傳依賴已滿足的工具 |
| `find_fallback("elevenlabs_tts")` | 解析降級鏈 |
| `support_envelope()` | 完整能力報告給 agent 消費 |
| `provider_menu_summary()` | 人類可讀的能力摘要（X of Y configured） |

### 3.5 Selector Pattern（多供應商自動路由）

三個 selector 抽象多供應商能力，**從 registry 動態發現供應商**，新增工具即自動可用：

| Selector | 路由到 | 評分維度 (7 維) |
|----------|--------|------------------|
| `tts_selector` | 所有 `capability="tts"` 工具 | task fit 30% / quality 20% / control 15% / reliability 15% / cost 10% / latency 5% / continuity 5% |
| `image_selector` | 所有 `capability="image_generation"` 工具 | 同上 |
| `video_selector` | 所有 `capability="video_generation"` 工具 | 同上 |

路由優先級：`user preference > availability > discovery order`。Selector 自動轉換不同供應商的 input schema 差異。

### 3.6 三個 Composition Runtime

| Engine | 擅長 | 依賴 |
|--------|------|------|
| **Remotion** | React 元件定義影片：spring 動畫、stat card、chart、TikTok 逐字字幕、TalkingHead avatar、TerminalScene | Node.js + `remotion-composer/` + node_modules |
| **HyperFrames** | HTML/CSS/GSAP：kinetic typography、product promo、launch reel、website-to-video、SVG 角色 rig | Node ≥ 22 + FFmpeg + `npx hyperframes` |
| **FFmpeg** | 純剪接、concat、trim、字幕燒入（無合成需求時的 fallback） | `ffmpeg` binary（永遠可用） |

關鍵治理規則：`render_runtime` **在 proposal 階段鎖定**（`edit_decisions.render_runtime`），整個流程不變。若兩個 runtime 都可用，agent **必須同時呈現兩者**並由使用者選擇——不允許 agent 悄悄選一個「預設」。若鎖定的 runtime 在 compose 時不可用，agent 必須呈現結構化 blocker，不可靜默切換到另一個 runtime。

### 3.7 品質閘（Production Governance）

| 閘口 | 時機 | 檢查項 |
|------|------|--------|
| Pre-compose validation | compose 前 | delivery promise 是否被違反（例：「motion-led」影片卻 80% 靜態圖）、slideshow risk score、renderer family 是否存在 |
| Post-render self-review | render 後 | ffprobe 驗證、4 點 frame extraction 檢黑幀/破 overlay、audio level 分析（靜音/clip）、delivery promise 驗證、字幕存在性 |
| Slideshow risk scoring | compose 前 | 6 維度分析：repetition、decorative visuals、weak motion、shot intent、typography overreliance、unsupported cinematic claims |
| Source media inspection | 使用者自帶素材時 | probe 每個檔案的 resolution/codec/audio channels/duration，不可從檔名幻覺內容 |

### 3.8 預算治理

```python
# CostTracker 生命週期
entry_id = cost_tracker.estimate(tool, operation, estimated_usd)
cost_tracker.reserve(entry_id)           # 鎖定預算
# ... 執行 tool ...
cost_tracker.reconcile(entry_id, actual_usd)  # 記錄實際花費
```

| 模式 | 行為 |
|------|------|
| `observe` | 只追蹤，不強制 |
| `warn` | 超支時 log warning，允許執行（預設） |
| `cap` | 超支時拒絕操作 |

控制項：總預算（預設 $10）、reserve holdback（預設 10%）、單次 action 審批門檻（預設 $0.50）、新付費工具首次使用需確認。

### 3.9 Checkpoint 系統

每階段結束寫 JSON checkpoint 到 `projects/<name>/pipeline/checkpoint_<stage>.json`：

```json
{
  "version": "1.0",
  "project_id": "black-holes-explainer",
  "stage": "script",
  "status": "completed",
  "human_approval_required": false,
  "human_approved": true,
  "artifacts": { "script": { ... } },
  "review": { ... },
  "cost_snapshot": { ... }
}
```

Status：`pending` / `in_progress` / `awaiting_human` / `completed` / `failed`。任何階段失敗可從最後一個 checkpoint 恢復，不重跑已完成階段。

### 3.10 決策審計軌跡

每個重大決策（供應商選擇、style playbook 選擇、音樂曲目、語音選擇、renderer family、任何 fallback 或降級）都記錄到 `decision_log`，含 `alternatives_considered`、`confidence`、`reasoning`。整個流程的決策累積持久化，可回溯為何最終影片長這樣。

### 3.11 免費路徑（零 API key 即可產出影片）

| 能力 | 免費工具 | 說明 |
|------|---------|------|
| 旁白 | Piper TTS | 完全離線的 TTS |
| 開放素材 | Archive.org + NASA + Wikimedia Commons | 免費/開放檔案影像 |
| 額外素材 | Pexels + Unsplash + Pixabay | 免費素材（developer key 免費申請） |
| 合成 (React) | Remotion | spring 動畫、stat card、字幕、TalkingHead |
| 合成 (HTML) | HyperFrames | kinetic typography、promo、launch reel |
| 後製 | FFmpeg | 編碼、字幕燒入、音軌混合、色彩分級 |
| 字幕 | 內建 | 自動生成含字級時間戳 |

三條免費路徑：
- **影像式影片**：Piper 旁白 + AI 影像 + Remotion 動畫
- **本地角色動畫**：SVG rig + pose library + GSAP timeline + HyperFrames render
- **真實影片紀錄片**：documentary-montage pipeline 用 CLIP 從免費素材庫語意檢索真實動態影像剪輯

---

## 4. 是否存在解決類似問題的其他技術 / 橺架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **OpenMontage** | Agent-first 架構：無 Python orchestrator，AI coding agent 讀 YAML pipeline manifest + Markdown stage director skill 驅動 8 階段流程；57+ Python BaseTool 透過 registry 自動發現；3 個 selector 做 7 維度評分路由；3 runtime（Remotion/HyperFrames/FFmpeg）在 proposal 鎖定；強制品質閘（pre-compose + post-render self-review + slideshow risk scoring）+ 預算治理 + checkpoint 恢復 + 決策審計軌跡 | Python 3.10+、FFmpeg、Node.js 18+、一個 AI coding assistant（Claude Code/Cursor/Copilot/Codex/Windsurf）；付費能力需對應 API key，免費路徑零 key 即可 | 需在 IDE 內由 agent 逐步驅動（非一鍵指令）；品質閘增加流程摩擦但保證交付；skill 知識需持續維護避免與供應商 API 漂移；AGPL-3.0 授權限制商業閉源衍生 | 從一句話到完成影片含研究/腳本/資產/剪輯/渲染/字幕/旁白/音樂；可產出真實影片（documentary-montage）非僅靜態圖動畫；每個決策可審計；可從 checkpoint 恢復 |
| **Remotion (單獨使用)** | React 元件定義影片，`composition.tsx` 程式化生成場景，`npx remotion render` 輸出 MP4 | Node.js + React 開發能力；需自行準備所有素材（影像/語音/音樂/字幕） | 無 agent 編排，所有流程需人工或自行寫 script；無供應商選擇/降級機制；無預算治理；無品質閘 | 程式化定義影片，版本控制友善；適合已有素材的開發者自行合成 |
| **CapCut / Adobe Premiere + AI 功能** | GUI 影片編輯器 + 內建 AI 功能（自動字幕、AI 語音、模板） | 需 GUI 操作；需訂閱（Premiere）或免費但有浮水印（CapCut） | 非 agent-native，無法被 coding agent 程式化驅動；產出為專有格式非程式碼；AI 功能封閉不可替換 | 專業級剪輯 + 內建 AI 輔助；適合人類操作 |
| **MoviePy / FFmpeg 腳本** | Python 庫或直接 FFmpeg CLI 程式化組裝影片 | Python 開發能力；需自行整合所有供應商 API；需自行處理字幕/語音/音樂 | 無 pipeline 抽象，需自行設計流程；無品質閘；無預算治理；無 checkpoint 恢復 | 完全程式控制影片組裝；適合簡單 concat/trim/overlay 場景 |
| **Runway / Pika / Kling (單一供應商產品)** | 單一雲端平台從 prompt 生成短片，內建 agent loop | 各平台訂閱；雲端限定；不可換供應商 | 閉源、產出存於平台雲端；僅限內建模型；無 pipeline 抽象；無多供應商降級 | 快速產生單一短片；適合非技術人員；不適合結構化多階段製作 |

### 切割點差異

| 技術 | 切割角度 |
|------|---------|
| OpenMontage | **Agent-orchestrated pipeline system** — 不自有模型/供應商，將 coding agent 變成影片製作總監；pipeline + skill + tool 三層分離；品質閘為強制合約 |
| Remotion (單獨) | **Programmatic renderer** — 只解決「如何用程式碼定義影片」，不解決「如何從想法到成品」的全流程 |
| CapCut / Premiere | **GUI editor + AI assist** — 以人類 GUI 操作為主，AI 為輔助而非主驅動；無法被 agent 程式化 |
| MoviePy / FFmpeg 腳本 | **Low-level assembly** — 只提供剪接原語，流程與品質管控需自行建構 |
| Runway / Pika / Kling | **Single-provider generator** — 雲端一鍵生成，封閉生態，無 pipeline 抽象與多供應商降級 |

---

## 附錄 A：典型工作流（animated-explainer pipeline）

```
1. User: "Make a 60-second explainer about black holes"
   ↓
2. Agent 讀 pipeline_defs/animated-explainer.yaml
   ↓
3. Preflight: registry.discover() → provider_menu_summary()
   呈現能力菜單給使用者:
     Video Generation:  0/13 configured
     Image Generation:  1/7 configured
     Text-to-Speech:    1/3 configured
     Composition:       3/3 configured (FFmpeg, Remotion, HyperFrames)
   ↓
4. Stage: research
   Agent 跑 15-25+ web searches (YouTube/Reddit/news/academic)
   產出 research_brief (JSON, schema-validated)
   ↓
5. Stage: proposal (human_approval_default: true)
   Agent 提出 3-4 個概念方向 + 成本估算 + 工具路徑
   呈現 Remotion vs HyperFrames 兩個 runtime (HARD RULE)
   等待使用者批准
   ↓
6. Stage: script
   Agent 寫含時間戳的腳本,標註增強提示與發音指南
   產出 script (schema-validated)
   ↓
7. Stage: scene_plan
   Agent 定義場景序列 (type/description/timing/asset需求)
   產出 scene_plan
   ↓
8. Stage: assets
   Agent 呼叫 image_selector / video_selector / tts_selector / music_gen
   每次呼叫前讀該工具的 Layer 3 skill (例: ai-video-gen 學 Kling prompt 結構)
   產出 asset_manifest (含 path/source tool/scene association)
   ↓
9. Stage: edit
   Agent 定義剪輯決策 (in/out timings/overlays/subtitle/music)
   鎖定 render_runtime (與 proposal 一致,不可靜默換)
   產出 edit_decisions
   ↓
10. Pre-compose validation gate
    檢查: delivery promise / slideshow risk / renderer family
    失敗則 block,不進入 render
    ↓
11. Stage: compose
    video_compose 讀 edit_decisions.render_runtime 路由到對應引擎
    _render_via_hyperframes / _remotion_render / _render_via_ffmpeg
    產出 render_report + final.mp4
    ↓
12. Post-render self-review
    ffprobe 驗證 / 4 點 frame extraction / audio level 分析
    / delivery promise 驗證 / 字幕存在性
    失敗則不交付
    ↓
13. final.mp4 交付給使用者
```

## 附錄 B：關鍵設計決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| Orchestrator 位置 | 在 LLM agent 內,非 Python | 可除錯（讀 skill 即可）、模型無關（換 agent 不換架構）、決策透明 |
| 智慧存放位置 | Markdown skill,非 Python code | 調整 agent 行為只需編輯文字檔,不需改程式碼 |
| 供應商路由 | Selector pattern + 7 維評分 | 缺 API key 自動降級到下一供應商或本地替代 |
| Runtime 鎖定 | proposal 階段鎖定,全程不變 | 防止 agent 靜默切換改變產出特性（治理違規） |
| 品質驗證 | 強制 post-render self-review | 防止交付黑幀/破 overlay/無字幕/違反 delivery promise 的垃圾 |
| 預算 | estimate→reserve→reconcile 生命週期 | 執行前知道成本,不會意外超支 |
| 恢復 | Checkpoint JSON per stage | 任何階段失敗可從最後 checkpoint 恢復,不重跑 |
| 授權 | AGPL-3.0 | 開源但限制商業閉源衍生 |