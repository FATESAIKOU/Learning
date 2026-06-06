# taste-skill 技術分析報告

## 1. 這個技術解決什麼問題？

**AI coding agent（Codex / Cursor / Claude Code 等）輸出前端程式碼時，系統性產出「AI 味」的 UI——centered hero + 紫色/藍色 AI glow 漸層、Inter 預設字型、三欄等寬 feature card、玻璃擬物濫用、em-dash 氾濫、區段編號 eyebrow（`00 / INDEX`）等可辨識的模板化風格**，導致不同專案輸出的前端長得幾乎一樣，缺乏品牌辨識度與設計品質。

taste-skill 提供一套**可移植的 Agent Skill 指令集**（SKILL.md），安裝後 AI agent 在生成任何前端程式碼前會先讀取這些規則，從設計語言推斷、字型選用、色彩校正、版面配置、動畫紀律到最終 pre-flight 檢查，**系統性覆寫 LLM 的統計預設值偏差**。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的（來自 research/laziness 目錄）

| 背景因素 | 說明 |
|----------|------|
| **RLHF 與運算經濟學** | Reinforcement Learning from Human Feedback 使 LLM 偏向「簡短、安全、完成快」的輸出模式，間接導致 UI 選用最常見的統計模式 |
| **訓練資料偏差** | 訓練語料中「generic 前端程式碼」佔比遠高於「高品質品牌前端」，LLM 學到的是頻率分布而非品質分布 |
| **認知捷徑** | LLM 面對複雜的前端任務時，傾向回退到最節省 tokens 的模板化輸出 |

### 通用技術背景（自行補充）

| 背景因素 | 說明 |
|----------|------|
| **前端框架預設值效應** | Tailwind 的 `slate-900`、`bg-white`、Inter 字型、`shadow-md` 等都內建了特定審美預設，agent 不解釋就直用 |
| **Agent Skill 生態剛起步** | `vercel-labs/agent-skills` 的 `npx skills add` 機制（2025 年推出）提供了標準化的 portable instruction 分發方式，taste-skill 正是此生態中目前 34.3k stars 的最大專案 |
| **LLM 缺乏設計歧視能力** | 語言模型本質上沒有「品味」或「審美」概念——它只做序列預測。需透過明確的逆向指令（anti-pattern 禁令）補償 |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體架構

```
┌──────────────────────────────────────────────────────────────────┐
│                      taste-skill 體系                              │
├──────────────────────┬───────────────────────────────────────────┤
│  程式碼生成技能        │  圖片生成技能（無程式碼輸出）                  │
├──────────────────────┼───────────────────────────────────────────┤
│  taste-skill (v2)    │  imagegen-frontend-web                    │
│  taste-skill-v1      │  imagegen-frontend-mobile                 │
│  gpt-tasteskill      │  brandkit                                 │
│  image-to-code-skill │                                           │
│  redesign-skill      │                                           │
│  soft-skill          │                                           │
│  minimalist-skill    │                                           │
│  brutalist-skill     │                                           │
│  output-skill        │                                           │
│  stitch-skill        │                                           │
├──────────────────────┴───────────────────────────────────────────┤
│  安裝: npx skills add https://github.com/Leonxlnx/taste-skill     │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 核心機制：三轉盤（Three Dials）+ 硬規則 + Pre-Flight 檢查

taste-skill v2（目前預設版本）的核心運作模式：

#### Step 0: Brief Inference（理解任務）
Agent 在產生任何程式碼之前，先從使用者提示中推斷：頁面類型（landing / portfolio / redesign）、氛圍詞（"minimalist", "Awwwards", "Apple-y"）、目標受眾、品牌資產、參考連結、隱性約束。輸出一行 **Design Read**。

```
"Reading this as: B2B SaaS landing for technical buyers, with a Linear-style
minimalist language, leaning toward Tailwind utilities + Geist + restrained motion."
```

#### Step 1: Dial 設定
根據 Design Read 設定三個 1-10 的轉盤值，後續所有版面/動畫/密度決策都由這三個值驅動：

| 轉盤 | 範圍 | 說明 |
|------|------|------|
| `DESIGN_VARIANCE` | 1（完美對稱）~ 10（藝術混亂） | 驅動版面是否 centered、對稱、非對稱 |
| `MOTION_INTENSITY` | 1（靜態）~ 10（電影級物理） | 驅動動畫深度：hover → scroll-triggered → 磁力物理 |
| `VISUAL_DENSITY` | 1（藝廊級空白）~ 10（駕駛艙級密集） | 驅動單位視口的資訊量 |

預設 baseline = `8 / 6 / 4`，根據設計語言自動推斷覆寫：

```
"minimalist / clean / editorial"     →  5-6 / 3-4 / 2-3
"premium consumer / Apple-y"         →  7-8 / 5-7 / 3-4
"playful / Awwwards / experimental"  →  9-10 / 8-10 / 3-4
"public-sector / accessibility"      →  3-4 / 2-3 / 4-5
```

#### Step 2: 設計系統地圖
若 Design Read 對應到一個官方設計系統（Material、Fluent、Carbon、Polaris、GOV.UK、USWDS），則**使用官方 npm package**。若對應的是一個美學方向（glassmorphism、bento、brutalism、editorial），則用 web 標準實作並誠實標註。

#### Step 3: 硬規則層（反制 LLM 統計偏差）

taste-skill v2 包含大量不可協商的「硬規則」，覆蓋 9 個面向：

| 面向 | 關鍵禁令 |
|------|---------|
| **字型** | Inter 非預設；Serif 極度不鼓勵為預設（Fraunces / Instrument_Serif 被點名禁用）；`leading-none` 義大利體 descender 需 `leading-[1.1]` + `pb-1` |
| **色彩** | 「AI Purple/Blue glow」禁止預設；暖 beige+brass+espresso 被禁止作為 premium-consumer 預設色板；一個 accent 貫穿整頁；純黑 `#000000` 禁止 |
| **版面** | `DESIGN_VARIANCE > 4` 時 centered hero 禁止；hero 標題 ≤ 2 行、subtext ≤ 20 字；hero top padding ≤ `pt-24`；每 3 個 section 最多 1 個 eyebrow；split-header 模式禁止為預設；section-layout-repetition 禁止（8 section 需 ≥ 4 種 layout family） |
| **卡片與容器** | 3 欄等寬 card 禁止；bento grid 必須 N item = N cell（不允許空格）；card 僅在 elevation 溝通 hierarchy 時使用 |
| **按鈕與互動** | 按鈕文字必須與背景有 WCAG AA 對比；CTA 文字不可換行；同一 intent 的 CTA 全頁只用一個 label；必須實作 loading/empty/error 三態 |
| **動畫** | `window.addEventListener('scroll')` 禁止（需用 `useScroll` / `ScrollTrigger` / `IntersectionObserver`）；`requestAnimationFrame` + React state 禁止；marquee 每頁最多 1 個；`MOTION_INTENSITY > 3` 時必須 honor `prefers-reduced-motion` |
| **圖片** | Div-based fake screenshot 禁止；純文字 hero 禁止；hand-rolled SVG icon 不鼓勵（用 Phosphor/HugeIcons/Radix/Tabler）；logo wall 必須用 Simple Icons 真實 SVG |
| **內容** | em-dash（`—`）完全禁止；section 編號 eyebrow（`00 / INDEX`）禁止；version label 在 hero 禁止；fake precise number（`4.1×`, `48k`）若非真實資料則禁止；AI 文案 cliché（"Elevate", "Seamless", "Next-Gen"）禁止 |
| **主題** | 整頁 theme lock：不允許 mid-page light/dark flip；雙模式必須從頭設計 |

#### Step 4: 動畫骨架（Canonical Skeletons）

v2 提供可直接複製貼上的程式碼骨架：

- **§5.A GSAP Sticky-Stack**：card 堆疊滾動，使用 `start: "top top"`、`pin: true`、`scrub: true`
- **§5.B GSAP Horizontal-Pan**：水平滾動綁定垂直 scroll，使用 `start: "top top"`、`end: "+="+distance`、`scrub: 1`
- **§5.C Scroll-Reveal Stagger**：輕量 Motion `whileInView` 替代方案

#### Step 5: Pre-Flight Checklist

輸出程式碼前強制檢查清單（共 20+ 項），所有項目必須誠實通過才能 ship。若失敗則退回修正。

### 3.3 多技能分工

每個 `skills/` 下的子目錄是一個獨立 Skill，透過 `--skill` flag 選擇安裝：

```bash
# 安裝全部
npx skills add https://github.com/Leonxlnx/taste-skill

# 安裝單一技能
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

| 技能 (install name) | 用途 |
|---------------------|------|
| `design-taste-frontend` (v2) | 預設通用 anti-slop 前端 |
| `design-taste-frontend-v1` | v1 原始版本，相容性鎖定 |
| `gpt-taste` | GPT/Codex 強化版：更高 layout variance、更強 GSAP、Python RNG 模擬打破重複性 |
| `image-to-code` | Image-first pipeline：先生成設計圖 → 深度分析 → 再寫程式碼 |
| `redesign-existing-projects` | 現有專案審計 + 升級，不改寫架構 |
| `high-end-visual-design` (soft-skill) | 高冷/奢華/Apple 風，double-bezel nested 架構 |
| `minimalist-ui` | Notion/Linear 風，暖色 monochrome + 扁平 |
| `industrial-brutalist-ui` | 瑞士印刷 + CRT terminal，極簡工業風 |
| `full-output-enforcement` (output-skill) | 強制完整輸出，禁止 placeholder comment |
| `stitch-design-taste` | Google Stitch 相容的 `DESIGN.md` 生成 |

### 3.4 圖片生成技能（非程式碼）

這組技能產出的是**設計參考圖**而非程式碼，通常與 ChatGPT Images / Codex image mode 搭配使用：

| 技能 | 產出 |
|------|------|
| `imagegen-frontend-web` | 網站 section comps，**一 section 一張圖**，16:9 水平 |
| `imagegen-frontend-mobile` | 行動版畫面、mockup 組 |
| `brandkit` | Logo 系統、色板、字型、identity board（3×3 grid） |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|----------------|
| **taste-skill** | 可移植 SKILL.md 指令集，agent 載入後在生成程式碼前套用三轉盤 + 硬規則 + pre-flight 檢查，系統性覆寫 LLM 設計預設值 | 支援 `npx skills add` 的 agent 環境（Codex, Cursor, Claude Code 等）；或直接複製 SKILL.md 內容貼入對話 | 規則密集時可能與 agent 本身的 system prompt 衝突；v2 仍在 experimental 階段，規則持續迭代；部分技能需 GSAP/Motion 等外部依賴 | Agent 產出的前端脫離「AI 模板感」；品牌辨識度提升；layout/motion/color 有系統性設計而非隨機 |
| **手寫 per-prompt anti-slop 指令** | 使用者在每次 prompt 中手動加入「不要用 Inter」「禁止 3 欄等寬 card」「不要 centered hero」等指令 | 使用者需具備前端設計知識才能列舉 anti-pattern；每次 prompt 需重複撰寫 | 覆蓋不完整（使用者未必知道所有 AI tell）；每次手寫耗費 tokens 且可能遺漏；無跨專案一致性 | 對單一生成有效；適合輕量需求 |
| **DESIGN.md / 設計系統文件法** | 撰寫一份結構化設計文件（色板 hex、字型 stack、元件規格、anti-pattern 列表），作為 agent 的 system prompt 或 context 檔案上傳 | 使用者需有能力撰寫完整設計系統規格；適合已有明確設計語言的團隊 | 需手動維護；與 `npx skills add` 生態無整合；無法像 taste-skill 一樣從 brief 自動推斷 dial 值 | 提供精確的設計約束；適合團隊已有品牌規範的場景 |
| **vercel-labs/agent-skills 生態中的其他設計 skills** | 同樣使用 `npx skills add` 機制安裝，但專注其他面向（如 Tailwind 專用規則、元件庫偏好、無障礙規範等） | 需該 skill 存在於 registry 中；生態仍在早期 | 單一 skill 通常只覆蓋特定領域；無法提供 taste-skill 的跨面向整合（layout + color + type + motion + content 聯動） | 針對特定需求的精準改進 |

### 切入點差異

| 技術 | 切入角度 |
|------|---------|
| **taste-skill** | **Agent-behavior-first**：不是提供元件庫或視覺模板，而是改寫 agent 的決策邏輯本身（從 brief 推斷 → dial 設定 → 硬規則過濾 → pre-flight 驗證） |
| **手寫 anti-slop 指令** | **Prompt-level**：在對話層面追加限制，但無系統性跨規則聯動 |
| **DESIGN.md 法** | **Constraint-file**：用靜態文件定義「應該長怎樣」，而非「如何做出判斷」 |
| **其他 agent skills** | **Domain-specific**：各自解決特定面向（字型、無障礙、Tailwind），不提供 taste-skill 的端到端設計判斷鏈 |
