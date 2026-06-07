# HyperFrames-C3-清理目錄與產出最終文件

## 狀況理解

使用者回報 T-6 (preview) 與 T-7 (render) 均已通過。要求：
1. 刪除 `hf-demo/` scaffold 目錄
2. `2026-05-31-HyperFrames/` 僅保留三個檔案：`LEARNING-PLAN.md`、`index.html`、`README.md`
3. `README.md` 內含 lint / preview / render 三個 npx 指令整理

同時 AGENTS.md 已被使用者修改，刪除了關於 README.md 的定義（現僅保留 LEARNING-PLAN.md 的格式要求）。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取最新 `02_mvps/AGENTS.md` | 確認使用者修改後的規則 | 確認 README.md 定義已被刪除，僅保留 LEARNING-PLAN.md | 確認：AGENTS.md 中無 README.md 相關格式要求 |
| 刪除 `hf-demo/` 目錄 | 清理 scaffold 殘留 | `hf-demo/` 不存在 | `rm -rf` 成功 |
| 寫入 `index.html` 到 output 目錄根層 | 保留最終 composition 產出物 | 可直接複用於 lint/preview/render | 寫入到 `2026-05-31-HyperFrames/index.html` |
| 更新 `LEARNING-PLAN.md` 全部勾選完成 | 標記所有 T-1 ~ T-8 完成 | Checklist 全 `[x]` | 8 步驟全數標記完成 |
| 撰寫 `README.md`（指令整理） | 產出 lint/preview/render 三個 npx 指令 | 含指令 + 簡短說明 + composition 規則 + 指向 index.html | 寫入完成 |
| 驗證目錄結構 | `ls` 確認僅 3 個檔案 | `index.html` + `LEARNING-PLAN.md` + `README.md` | 3 檔案，無多餘項目 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 目錄殘留 | `ls 02_mvps/output/2026-05-31-HyperFrames/` | 僅 3 個檔案：index.html, LEARNING-PLAN.md, README.md |
| hf-demo 已刪除 | `ls hf-demo` | 不存在 |
| LEARNING-PLAN.md | Checklist 全部勾選 + 技術分析完整 | ✅ |
| README.md | 含 lint / preview / render 三命令 + 規則表 | ✅ |
| index.html | 含 data-* 屬性 + GSAP fromTo + window.__timelines | ✅ |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| index.html 放置位置 | ① 留在 hf-demo/ 中 ② 直接放 output 目錄根層 | ② output 目錄根層 | 使用者要求刪除 hf-demo/，但 index.html 是關鍵產出物需保留 |
| README.md 內容範圍 | ① 只放指令 ② 指令 + 規則 + 範例參考 | ② 指令 + 規則 + 範例參考 | 使用者要求「指令整理」，但無範例 context 的指令無法獨立使用 |
| 指令格式 | ① 用 npm run ② 用 npx | ② npx | 使用者明確要求「三個都要用 npx」 |
