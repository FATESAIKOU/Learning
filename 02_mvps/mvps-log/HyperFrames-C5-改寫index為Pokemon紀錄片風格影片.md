# HyperFrames-C5-改寫index為Pokemon紀錄片風格影片.md

## 狀況理解
使用者提供一段約16分鐘的 Pokemon 卡牌市場調查影片逐字稿，要求以 HyperFrames 更改 `index.html`，製作一支多場景的紀錄片風格影片。使用者選擇 50-60 秒精華版（5 場景），涵蓋天價聖杯、疫情泡沫、PSA評級、造假產業、結論等核心段落。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取現有 index.html 與 LEARNING-PLAN.md | 理解目前專案狀態與先前學習進度 | 確認起始點 | 專案已有簡易的 "Hello, HyperFrames!" 5 秒 composition |
| 讀取 design.md / house-style.md / video-composition.md / beat-direction.md / transitions.md / motion-principles.md / typography.md | 遵照 HyperFrames skill 規範，設計前先理解全套規則 | 設計不違規 | 無 design.md，採用 dark-premium palette；規則已完整理解 |
| 設計 5 場景紀錄片風格影片架構 | 將逐字稿核心摘要為 55 秒短片結構 | 5 場景 × ~11s，HOOK-breathe-BUILD-PEAK-resolve 節奏 | 場景：天價聖杯 → 疫情泡沫 → PSA評級 → 造假帝國 → 真相與結論 |
| 撰寫完整 index.html (374行) | 實作多場景 composition，含 blur crossfade transitions | 0 error lint | 0 error, 2 warning (composition_file_too_large + font_family_without_font_face) |
| 修復 visibility: hidden hard-kill (4 scenes) | 回應 lint warning: scene_layer_missing_visibility_kill | 清除所有 hard-kill 警告 | 成功修復，lint warning 只剩非阻塞項 |
| 執行 npx hyperframes lint (最終版) | 驗證 HTML 結構 | 0 error | 0 error, 2 warning (非阻塞) |
| 執行 npx hyperframes validate | WCAG AA 對比度驗證 | 全部通過 | 35 text elements pass WCAG AA，無 console errors |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| Lint 錯誤 | `npx hyperframes lint` | 0 error |
| WCAG 對比度 | `npx hyperframes validate` | 35 文字元素全部通過 AA |
| 場景轉場規則 | 檢視每個 scene 的 hard-kill 與 blur crossfade 時序 | scenes 1-4 有 visibility: hidden hard kill；scene 5 有 final fade out |
| GSAP timeline 註冊 | `window.__timelines["main"]` | 已正確註冊 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 影片時長 | 50-60秒精華版 / 90-120秒完整版 | 50-60 秒精華版 (使用者選擇) | 使用者指定 |
| 調色盤 | 9 套 dark-premium 主題 | `#0B090A` + `#161A1D` + `#660708` + `#E5383B` (血色金融) | 內容涉及金融詐騙、貪婪、深坑，用暗紅營造危險感 |
| 轉場類型 | Crossfade / Blur Crossfade / Focus Pull / Color Dip / Shader | Blur Crossfade (calm) | 紀錄片風格應使用較緩和的轉場；calm 參數適合 11 秒停留場景 |
| 字體選擇 | 多組 font pairing | Barlow Semi Condensed 800 + Newsreader 400 + JetBrains Mono | 窄體 sans 做 headline 張力，serif 做內文溫度，mono 做數據可讀性 |
| 場景結構 | 每個 scene 用 data-clip 或純 scene div | 純 scene div + opacity 控制（非 class="clip"） | 多場景 composition 使用 scene div pattern，由 GSAP 控制顯示 |
| 字體 lint warning | 添加 @font-face 或接受 fallback | 接受 fallback（Georgia/Times New Roman/Arial Narrow） | 無 design.md 約束；system font fallback 在 demo 中可接受 |
