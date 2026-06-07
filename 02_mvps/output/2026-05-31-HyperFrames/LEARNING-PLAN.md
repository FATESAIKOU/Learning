# HyperFrames CLI 全流程學習計畫

> 環境：M4 Mac Pro (Apple Silicon) · Node.js v24.15.0 · FFmpeg installed · arm64

---

## 1. 技術分析

### 1.1 這個技術解決什麼問題？

HyperFrames 解決的問題：**將一份包含時間屬性（data-*）的 HTML 靜態頁面，透過 headless Chrome 逐幀擷取 + FFmpeg 編碼，轉換為確定性（deterministic）的 MP4 影片。**

### 1.2 這個問題為什麼會發生？

| 因素 | 來源 |
|------|------|
| 傳統影音工具（After Effects / Premiere）無 headless API，無法程式化批次生成影片 | 文章明確提到 |
| Remotion 證明 headless Chrome + FFmpeg 可行，但依賴 React/JSX，對 LLM agent 不友善 | 文章明確提到 |
| LLM 訓練資料中 HTML 比例遠高於 React，agent 寫 HTML 出錯率更低 | 文章明確提到 |
| Headless Chrome 的 `BeginFrame` API + FFmpeg `image2pipe` 提供逐幀確定性 capture 的基礎設施 | 通用技術背景 |

### 1.3 這個技術是如何解決該問題的？

核心流程：

```
npx hyperframes init    →  產出 index.html（composition 骨架）
npx hyperframes preview →  啟動 Studio dev server，瀏覽器熱重載預覽
npx hyperframes lint    →  靜態 HTML 結構驗證
npx hyperframes render  →  headless Chrome 逐幀 capture → FFmpeg 編碼 → output.mp4
```

關鍵規則：

| 規則 | 說明 |
|------|------|
| 根元素 `data-composition-id` / `data-width` / `data-height` | 定義 composition 名稱與解析度 |
| 子元素 `class="clip"` + `data-start` + `data-duration` + `data-track-index` | 定義時間線上的元素 |
| GSAP timeline `{ paused: true }` 並註冊到 `window.__timelines[compositionId]` | 讓引擎可逐幀 seek 動畫狀態 |
| 無 build step | `index.html` 可直接用瀏覽器開啟預覽 |

---

## 2. AI 加速 Prompt

```
I need to create a minimal HyperFrames video project on M4 Mac (Apple Silicon).

Prerequisites already met: Node.js v24, FFmpeg installed.

Do the following step by step, waiting for my confirmation after each step:

1. Run `npx hyperframes init hf-demo --non-interactive --example blank` in the current directory
2. After init, read the generated index.html so I can see the template
3. Help me create a minimal 5-second composition: a centered title "Hello, HyperFrames!" with a GSAP fade-in + slide-up animation over a dark background
4. Run `npx hyperframes lint` to validate the HTML
5. Run `npx hyperframes render --output output.mp4` to render to MP4
6. Verify output.mp4 was created and tell me its file size

Use only the `class="clip"` and `data-*` conventions from the HyperFrames docs. GSAP timeline must be `{ paused: true }` and registered on `window.__timelines`.
```

---

## 3. Todo Checklist

- [x] **T-1: 環境最終確認** — Node.js v24.15.0 ✅, FFmpeg 7.1.1 ✅, arm64 ✅
  - 產出物：終端輸出截圖
  - 驗證標準：Node.js >= 22, ffmpeg 無報錯

- [x] **T-2: scaffold 空白專案** — `npx hyperframes init hf-demo --non-interactive --example blank`
  - 產出物：`hf-demo/` 目錄（含 `index.html`, `meta.json`）
  - 驗證標準：目錄存在、`index.html` 可讀取

- [x] **T-3: 閱讀模板 composition** — 辨識 `data-*` 屬性結構與 GSAP timeline 註冊模式
  - 產出物：對 `index.html` 每一段的注釋說明
  - 驗證標準：能辨識出根元素、clip 規則、GSAP 註冊點

- [x] **T-4: 改寫為自訂 5 秒簡單影片** — 黑色背景 + "Hello, HyperFrames!" 淡入上滑 + 淡出
  - 產出物：`index.html`
  - 驗證標準：含 `data-composition-id`, `class="clip"`, `data-start/duration/track-index`, GSAP `{ paused: true }` + `window.__timelines`

- [x] **T-5: lint 驗證** — `npx hyperframes lint`
  - 產出物：0 error, 0 warning
  - 驗證標準：error=0

- [x] **T-6: 預覽 dev server** — `npx hyperframes preview`，瀏覽器確認動畫
  - 產出物：user confirmation
  - 驗證標準：瀏覽器顯示標題文字 + 動畫效果正常

- [x] **T-7: render 輸出 MP4** — `npx hyperframes render --output output.mp4`
  - 產出物：`output.mp4` (1920x1080, 5s, 30fps)
  - 驗證標準：檔案存在、duration 約 5 秒

- [x] **T-8: 最終總結** — 清理專案、保留產出物
  - 產出物：`LEARNING-PLAN.md`, `index.html`, `README.md`
  - 驗證標準：三檔案存在，內容完整
