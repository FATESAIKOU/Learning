# HyperFrames 技術分析報告

## 1. 這個技術解決什麼問題？

將 **HTML + CSS + seekable animation runtime** 定義的畫面，直接轉換為 **逐幀確定性（deterministic）的 MP4 影片**。核心場景是：

- **AI coding agent 可以透過寫 HTML 來生成影片**（而非需要 GUI 操作或專有 API）
- **人類可透過視覺編輯器直接編輯同一份 HTML DOM**（所見即所得，不需 build step）
- **同樣的輸入保證產生完全相同的影片輸出**（逐幀獨立 capture, 沒有 wall-clock 依賴），適合 CI/CD 自動化

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的

| 背景因素 | 說明 |
|----------|------|
| Remotion 證明 headless Chrome 可做可靠影片渲染，但其 React 模型有兩個侷限 | ① Agent 寫 React 比寫 HTML 更容易出錯（LLM 訓練資料中 HTML 比例遠高於 React）② 第三方動畫庫（GSAP, Anime.js）有自己的時鐘（`performance.now()`），在 React per-frame render 中會以 wall-clock 速度跑完動畫，而非逐幀精確定位 |
| 傳統影片工具（Premiere, After Effects）不是 agent-friendly | API 複雜、需要 GUI 操作、無確定性輸出保證 |
| 程式化影片生成需求增長 — 特別是在 HeyGen 自身生產管線中 | 需要批次生成、CI 回歸測試、自動化內容產線 |

### 通用技術背景（自行補充）

| 背景因素 | 說明 |
|----------|------|
| Headless Chrome 提供 `HeadlessExperimental.beginFrame` API | 允許外部程式精確控制瀏覽器 compositor 的每一幀，而非依賴 wall-clock 截屏。這是逐幀確定性 capture 的基礎設施 |
| FFmpeg 的 `image2pipe` 輸入 | 可透過 pipe 接收逐幀 RGBA buffer 並編碼為影片，不需要先寫入磁碟。Remotion 也採用此模式 |
| Chromium 的 deterministic paint | 在 `chrome-headless-shell` + `--disable-gpu` + 相同字型集合下，同樣的 DOM/CSS 在不同機器上產生 pixel-identical 輸出（僅限 Linux `BeginFrame` 模式） |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體架構

```
┌─────────────────────────────────────────────────────────┐
│                    HyperFrames Stack                      │
├───────────────┬──────────────────────────────────────────┤
│  packages/    │  說明                                     │
├───────────────┼──────────────────────────────────────────┤
│  cli          │  命令列工具：init, preview, lint, render   │
│  core         │  型別、HTML parser/generator、linter、     │
│               │  runtime、Frame Adapter 介面              │
│  engine       │  低層 capture 引擎：headless Chrome +      │
│               │  BeginFrame API 逐幀截取                  │
│  producer     │  完整渲染管線：capture + FFmpeg 編碼 +     │
│               │  音訊混音                                  │
│  studio       │  瀏覽器內的視覺編輯器 UI                   │
│  player       │  <hyperframes-player> Web Component       │
│  shader-transitions │  WebGL shader 轉場效果              │
│  aws-lambda   │  AWS Lambda 分散式渲染                    │
└───────────────┴──────────────────────────────────────────┘
```

### 3.2 核心機制：Composition = HTML + data-* 時間線 + Frame Adapter

一個 composition（影片專案）就是一個 HTML 檔案，透過 `data-*` 屬性定義時間線：

```html
<!-- 根元素：定義 composition ID、解析度、開始時間 -->
<div id="root" data-composition-id="root"
     data-start="0" data-width="1920" data-height="1080">

  <!-- 影片片段：track 0, 從第 0 秒開始播放 5 秒 -->
  <video class="clip" data-start="0" data-duration="5"
         data-track-index="0" src="intro.mp4" muted playsinline></video>

  <!-- 文字標題：track 1, 從第 1 秒開始顯示 4 秒 -->
  <h1 id="title" class="clip" data-start="1" data-duration="4"
      data-track-index="1">Launch day</h1>

  <!-- 背景音樂：track 2, data-volume 控制音量 -->
  <audio data-start="0" data-duration="5" data-track-index="2"
         data-volume="0.5" src="music.wav"></audio>

  <!-- GSAP 動畫：timeline 必須 paused + 註冊到 window.__timelines -->
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
    window.__timelines = window.__timelines || {};
    window.__timelines["root"] = tl;
  </script>
</div>
```

### 3.3 關鍵規則

| 規則 | 說明 |
|------|------|
| **class="clip"** | 所有有時間線的元素必須加上此 class |
| **data-***  屬性 | `data-composition-id`, `data-start`, `data-duration`, `data-track-index`, `data-width`, `data-height` |
| **GSAP timeline: paused + 註冊** | `gsap.timeline({ paused: true })` 且註冊到 `window.__timelines[compositionId]` |
| **Script 不可控制 media playback** | framework 自動從 data-* 屬性管理 clip 的顯示/隱藏/播放，script 只負責動畫效果 |

### 3.4 Frame Adapter Pattern（動畫 runtime 統一介面）

所有動畫 runtime 透過同一個介面與渲染引擎對接：

```typescript
type FrameAdapter = {
  id: string;
  init?: (ctx: FrameAdapterContext) => Promise<void> | void;
  getDurationFrames: () => number;    // 回傳總幀數
  seekFrame: (frame: number) => Promise<void> | void;  // 跳到指定幀
  destroy?: () => Promise<void> | void;
};
```

支援的 runtime：GSAP（主）、Anime.js、CSS keyframes、Lottie/dotLottie、Three.js/WebGL、WAAPI。

### 3.5 渲染管線（deterministic rendering）

```
1. 載入 HTML 到 headless Chrome
2. 注入 HyperFrames runtime（管理 clip mount/unmount + seek）
3. 對每一幀 f ∈ [0, totalFrames]：
   ├─ t = f / fps
   ├─ renderSeek(t) → pause 所有 timeline → seek 到精確時間 → 更新 media element
   ├─ HeadlessExperimental.beginFrame → 擷取 compositor pixel buffer
   └─ pipe pixel buffer → FFmpeg image2pipe 編碼
4. 音訊混音（從 media element 的 audio track 合併）
5. 輸出 MP4/MOV/WebM
```

**兩種 capture mode：**

| Mode | 條件 | 特性 |
|------|------|------|
| **BeginFrame** | Linux + `chrome-headless-shell` | 精確逐幀控制，pixel-identical 跨機器 |
| **Screenshot** | macOS/Windows，或 composition 包含 iframe/rAF loop | 自動 fallback，注入 virtual-time shim |

### 3.6 Agent Integration 設計

| 設計點 | 做法 |
|--------|------|
| **Skills 系統** | `npx skills add heygen-com/hyperframes` 安裝 agent 技能，教導 agent 撰寫正確的 composition |
| **CLI: non-interactive by default** | 所有命令 flag-driven，輸出 plain text，適合 agent 呼叫 |
| **確定性輸出** | 同一 HTML → 同一影片，適合 CI 回歸測試 |
| **無 build step** | `index.html` 可直接在瀏覽器預覽，不需要 bundler |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 | 授權模式 | 是否需要外接 LLM |
|--------|----------|-------------|---------------|-----------------|---------|----------------|
| **HyperFrames** | HTML + CSS + data-\* 屬性定義 composition，透過 headless Chrome BeginFrame API 逐幀 capture 後以 FFmpeg 編碼為 MP4/MOV/WebM | Node.js 22+、FFmpeg（本機需安裝）、可選 Docker；CLI 安裝即可用（`npx hyperframes`），不需註冊/登入/API Key | Render 每 worker 消耗約 256MB RAM；Docker 模式啟動較慢；非 BeginFrame 模式（macOS/Windows）輸出不保證跨機器 pixel-identical | 確定性逐幀輸出，同一 HTML → 同一影片；可從 CLI 或 agent 驅動；支援透明背景、HDR | **Apache 2.0（開源免費，任意規模商用）** | 否（本身是渲染引擎，不依賴 LLM。LLM 是可選的「內容輸入來源」，使用者可手寫 HTML 完全不碰 LLM） |
| **Remotion** | React 組件作為 composition，透過 `useCurrentFrame()` hook 在每幀重新 render 組件樹 | 團隊需熟悉 React/TypeScript；使用 bundler（webpack） | 第三方動畫庫（GSAP、Anime.js）的內部時鐘在渲染時以 wall-clock 速度運行，導致動畫時序錯亂；任意 HTML/CSS 需先轉換為 JSX | 確定性影片輸出；React 生態複用（型別安全、元件複用）；成熟的 Remotion Lambda 分散式渲染 | **商業授權（Source-available，超過小團隊 threshold 需付費，有 per-render fee）** | 否（本身不依賴 LLM） |
| **Motion Canvas** | TypeScript + HTML Canvas imperative API，使用 generator function 定義時間線動畫 | 僅適合 2D Canvas 動畫（數學動畫、圖表動畫）；不自帶影片編碼 | 不支援任意 HTML/CSS；不支援影片/音訊素材直接放在時間線上；無 GUI 編輯器 | 適合數學/程式教育影片；generator-based 時間線直覺易讀；可嵌入網頁做互動展示 | **MIT（免費）** | 否（本身不依賴 LLM） |
| **Manim** | Python-based，使用 scene object 定義動畫，主要用於數學視覺化 | 僅適合數學/科學動畫場景；Python 生態；無瀏覽器渲染 | 不支援 HTML/CSS；不自帶影片編碼（需手動 pipe 到 FFmpeg）；對非數學場景缺乏支援 | 高品質數學動畫輸出（3Blue1Brown 風格）；社群提供的數學物件豐富 | **MIT（免費）** | 否（本身不依賴 LLM） |
| **After Effects / Premiere** | GUI-based 時間線編輯器，非程式化方案 | 需要人類操作 GUI；無法程式化批次生成 | 無法被 agent 操控（無 headless API）；輸出非確定性；需授權費用 | 專業級影片製作結果；豐富的 plugin 生態；業界標準 | **商業訂閱制（付費）** | 否（部分新版功能可能內建 AI 輔助，與外部 LLM 無關） |

### 切入點差異

| 技術 | 切入角度 |
|------|---------|
| HyperFrames | **Agent-first** + HTML-native：讓 LLM 用最熟悉的 HTML 產生影片，人類也可編輯同一份 HTML |
| Remotion | **React developer-first**：讓熟悉 React 的前端工程師用元件化思維寫影片 |
| Motion Canvas | **Educator-first**：讓數學/程式教育者用 generator 語法定義逐步動畫 |
| Manim | **Math visualization-first**：讓數學家/科學家用 Python 做精確數學動畫 |
| After Effects | **Designer-first**：讓專業設計師用 GUI 做最高品質影片 |
