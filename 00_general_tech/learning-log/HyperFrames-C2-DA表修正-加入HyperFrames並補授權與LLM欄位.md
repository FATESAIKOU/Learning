# HyperFrames-C2-DA表修正-加入HyperFrames並補授權與LLM欄位

## 狀況理解

使用者指出兩個問題：
1. DA 表沒有將 HyperFrames 自身納入比較對照（只有 Remotion, Motion Canvas, Manim, After Effects 四項）
2. 需要補上「要不要錢（授權模式）」和「需不需要外接 LLM」兩個維度到 DA 表中

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取先前產出的 HyperFrames 分析報告 | 定位需要修改的 DA 表位置 | 確認 DA 表在報告第 4 段的具體內容 | 已定位至 `output/2026-05-31-HyperFrames.md` L148-155 |
| 查閱 LingBot-Map 報告作為 DA 表欄位數量參考 | 參考既有的 DA 表格式規範（之前有 5 欄：技術名、解法、前提、副作用、效果） | 確認欄位結構 | LingBot-Map 的 DA 表為 5 欄結構 |
| 查閱 repo README 確認授權資訊 | 取得 HyperFrames 與 Remotion 的授權模式 | 正確填入授權欄位 | HyperFrames: Apache 2.0、Remotion: 商業 Source-available（來自官方 vs Remotion 對比文件） |
| 確認 HyperFrames 的 LLM 依賴關係 | 判斷「是否需要外接 LLM」欄位該填什麼 | 正確判斷各技術對 LLM 的依賴 | 所有技術自身均不依賴 LLM（它們是 rendering engine，LLM 是 optional 的內容生產者） |
| 修改分析報告 | 在 DA 表中加入 HyperFrames、授權欄位、LLM 欄位 | DA 表從 4 列 5 欄擴充為 5 列 7 欄 | 已完成修改 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| DA 表是否有 HyperFrames | 重新讀取修改後的報告 L148-157 | HyperFrames 已置於第一列 |
| DA 表是否有授權欄位 | 重新讀取修改後的報告 | 新增「授權模式」欄位 |
| DA 表是否有 LLM 依賴欄位 | 重新讀取修改後的報告 | 新增「是否需要外接 LLM」欄位 |
| 授權資訊正確性 | 對照 README（Apache 2.0）與 vs Remotion 文件 | HyperFrames Apache 2.0、Remotion 商業、其他 MIT/訂閱制 |
| LLM 依賴判斷正確性 | 確認各技術的核心功能是否依賴 LLM API call | 所有技術均為 standalone 工具，LLM 為 optional |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| DA 表欄位命名 | ① 「費用」② 「授權模式」③ 「定價」 | ② 「授權模式」 | AGENTS.md 範例 LingBot-Map 報告中欄位偏向技術屬性而非行銷術語，授權模式比費用更精確 |
| LLM 欄位命名 | ① 「依賴 LLM」② 「需要 LLM」③ 「是否需要外接 LLM」 | ③ 「是否需要外接 LLM」 | 強調「外接」避免誤解（許多工具內建 AI 功能但這與呼叫外部 LLM API 不同） |
| HyperFrames 的 LLM 欄位值 | ① 否 ② 是（因為 skills 系統需要 agent） | ① 否 | HyperFrames 本身是 CLI + engine，skills 是 optional 的 agent 開發輔助，不執行任何 LLM API call |
