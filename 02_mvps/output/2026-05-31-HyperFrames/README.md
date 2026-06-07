# HyperFrames CLI 快速操作

> 環境：M4 Mac Pro · Node.js >= 22 · FFmpeg 已安裝

---

## Commands

### 1. Lint（靜態 HTML 驗證）

檢查 `index.html` 的 data-\* 屬性結構、GSAP 用法、字體宣告等是否符合規範。

```bash
npx hyperframes lint
```

### 2. Preview（啟動 dev server）

啟動 Studio dev server，瀏覽器熱重載預覽 composition。**此命令為長駐伺服器，會 blocking 終端。**

```bash
npx hyperframes preview
```

開啟瀏覽器後，編輯 `index.html` 會自動熱重載。

### 3. Render（輸出 MP4）

headless Chrome 逐幀 capture 後 FFmpeg 編碼為 MP4。

```bash
npx hyperframes render --output output.mp4
```

---

## 最小 Composition 規則

| 規則 | 說明 |
|------|------|
| 根元素 | `data-composition-id` + `data-width` + `data-height` |
| clip 元素 | `class="clip"` + `data-start` + `data-duration` + `data-track-index` |
| GSAP timeline | `{ paused: true }` 並註冊到 `window.__timelines[compositionId]` |

範例：`index.html`
