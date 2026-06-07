# HyperFrames-C2-模板解析改寫與Lint驗證

## 狀況理解

T-1、T-2（環境確認 + scaffold）已在 C1 對話中完成。本輪專注於 T-3、T-4、T-5：
- T-3：閱讀空白模板 index.html，辨識 data-\* 與 GSAP 結構
- T-4：改寫為 5 秒淡入淡出自訂影片
- T-5：執行 lint 並修復全部錯誤

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `hf-demo/index.html`（空白模板） | T-3: 理解模板的 composition 結構 | 辨識出根元素屬性、clip 規則、GSAP 註冊點 | 模板含 `<div data-composition-id="main">` + 根容器 + paused tl |
| 分析模板結構並產出圖示 | T-3: 幫助使用者建立心智模型 | 以樹狀圖 + 表格說明每個區塊作用 | 產出結構樹 + 三規則表 |
| 改寫 `index.html` 為 5 秒淡入淡出影片 | T-4: 產出實作 composition | 黑色背景 + "Hello, HyperFrames!" 標題淡入上滑 + 淡出 | 寫入完成 |
| 執行 `npx hyperframes lint` | T-5: 靜態驗證 HTML | 預期 lint 通過 | 初始 1 error + 2 warning |
| 修復 `opacity: 0` CSS + `gsap.from({opacity:0})` 衝突 | T-5: 解決 error | 移除 CSS opacity，改用 fromTo | error 修復 |
| 修復 CSS `transform` + GSAP `y` 衝突 | T-5: 解決 warning | 移除 CSS transform，改用 GSAP xPercent/yPercent | warning 修復 |
| 修復 `-apple-system` 無 @font-face | T-5: 解決 warning | 移除 -apple-system | warning 修復 |
| 使用者重新執行 lint | T-5: 驗證修復 | lint 零錯誤 | 通過 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| index.html 結構正確性 | 對照 HyperFrames composition 規範 | ✅ 含 data-composition-id, class="clip", data-start/duration/track-index |
| GSAP timeline 註冊 | `{ paused: true }` + `window.__timelines["main"]` | ✅ |
| lint 結果 | `npx hyperframes lint` | ✅ 0 error |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| CSS centering 方式 | ① 保留 CSS `transform: translate(-50%,-50%)` + 放棄 GSAP y 動畫 ② 改用 GSAP xPercent/yPercent | ② GSAP xPercent/yPercent | GSAP 會 overwrite 整個 transform，且 fromTo 不受此 lint rule 限制 |
| opacity 初始值 | ① 保留 CSS `opacity: 0` + 改用 `gsap.to()` ② 移除 CSS opacity + 用 `gsap.fromTo()` 明確定義起終 | ② fromTo | fromTo 明確定義起終點，可排除 lint error 且意圖更清晰 |
| 字體選擇 | ① 保留 `-apple-system` 不理會 warning ② 移除 | ② 移除 | warning 非 fatal 但 lint 規範要求無 warning，移除不影響本機預覽 |
