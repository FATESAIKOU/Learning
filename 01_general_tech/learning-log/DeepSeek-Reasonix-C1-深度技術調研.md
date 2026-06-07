# DeepSeek-Reasonix-C1-深度技術調研.md

## 狀況理解

使用者要求對 GitHub 專案 `esengine/deepseek-reasonix` 進行深入技術調研，產出格式需遵循 `AGENTS.md` 規範。此專案為 2026 年 4-5 月快速崛起的開源 AI coding agent（14.7k stars），以 DeepSeek 原生、cache-first loop 為核心賣點，目標是「低到可以一直開著」的終端 coding agent。需從專案 README、ARCHITECTURE.md、REASONIX.md、CLI-REFERENCE.md、benchmarks 以及 DeepSeek 官方 API 文件等多個來源整合資訊。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md 確認輸出格式規範 | 確保產出符合專案約定 | 取得 4 點報告結構 + 學習紀錄格式 | 已完整確認：分析報告 4 點 + DA 表、學習紀錄含 4 區塊 |
| 讀取 repo root 與現有 output/ learning-log/ 目錄 | 理解專案狀態，確認是否有既有分析 | 決定使用新技術名 `DeepSeek-Reasonix` | 確認無既有檔案，技術名無衝突 |
| 從 GitHub web fetch README（英文版） | 取得專案總覽、安裝方式、feature 對比 | 掌握核心定位與行銷主張 | 取得完整 README，含 Pillar 概述、對比表、benchmarks 連結 |
| 從 GitHub web fetch ARCHITECTURE.md | 深入了解三支柱架構設計 | 取得 cache-first loop 技術細節 | 取得完整架構文檔：ImmutablePrefix/AppendOnlyLog/VolatileScratch 分區設計、Tool-Call Repair 四 pass、Cost Control 四機制、parallel dispatch |
| 從 GitHub web fetch REASONIX.md | 了解專案技術棧、目錄結構、開發慣例 | 補充實作層面的技術資訊 | 取得 TS 5.6+/ESM/Ink 5/Commander.js 技術棧、目錄 layout、npm scripts |
| 從 GitHub web fetch README.zh-CN.md | 取得中文版說明輔助理解 | 補充中文使用者視角的資訊 | 確認中文社群（QQ 通道）、中國本地化的 web search engine 支援 |
| 從 GitHub web fetch CLI-REFERENCE.md | 了解完整的 CLI 命令與快捷鍵生態 | 取得 feature 全貌 | 取得 shell subcommands + slash commands + keybindings + mouse 操作 |
| 從 GitHub web fetch benchmarks/real-world-cache/README.md | 取得真實用戶 cache hit 數據 | 驗證 cache-first 設計的量化效果 | 取得 2026-05-01 單日數據：99.82% hit rate、$1.38 vs $61.06、97.7% cost saving |
| 從 DeepSeek API 官方文件取得 KV cache 說明 | 理解 DeepSeek 端的前綴快取機制 | 區分「DeepSeek 提供的 cache」與「Reasonix 如何維持 cacheable」 | 取得 disk cache 持久化規則（三種時機）、cache hit 條件（byte-exact match）、使用 best-effort 非保證 |
| 嘗試 fetch 官方網站 docs | 取得更多配置與使用文件 | 增加資訊完整度 | 404 失敗，不影響主分析 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 技術被解決問題的明確性 | 對照 README、ARCHITECTURE.md、benchmarks 中的量化數據 | 問題定義清晰：通用 agent 因 byte drift 導致 DeepSeek cache miss（<20%），目標是維持 >99% hit rate |
| 問題背景的完整性 | 對照 DeepSeek 官方文件理解 KV cache 機制 vs Reasonix 的 client-side 策略 | 區分明確：DeepSeek 端的 cache 是基礎設施（3 種持久化時機），Reasonix 端是維持 byte stability 的策略層 |
| 技術解法的具體性 | 對照 ARCHITECTURE.md 的三支柱+四機制描述 | 具體：ImmutablePrefix / AppendOnlyLog / VolatileScratch / Auto-compact，每項都有明確實作位置（src/memory.ts 等） |
| 替代方案的完整性 | 對比 Claude Code、Cursor、Aider 的文件與社群資訊 | 四選項涵蓋主要競爭格局：成本導向（Reasonix）、品質導向（Claude Code）、IDE 整合（Cursor）、靈活導向（Aider） |
| DA 表格式正確性 | 對照 AGENTS.md 要求的欄位 | 五欄位完備：技術名、技術解法、技術使用前提、技術使用副作用、技術使用預期效果 |
| 輸出物產出 | 確認兩個 markdown 檔案已寫入 | output/2026-05-31-DeepSeek-Reasonix.md + learning-log/DeepSeek-Reasonix-C1-深度技術調研.md 已建立 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 替代方案對比對象選擇 | (A) 只比 Claude Code 和 Cursor (B) 加入 Aider (C) 加入更多（Continue、Cline、Windsurf 等） | (B) 加入 Aider | Reasonix 的 README 自身列出了 Claude Code、Cursor、Aider 三個對比對象，與此對齊可保持論述一致性。Continue 和 Cline 在 benchmarks/real-world-cache 中被提到作為 cache-miss 範例，但非完整產品級對比 |
| DA 表數量 | (A) 2-3 個 (B) 4 個 | (B) 4 個 | AGENTS.md 要求 2-4 個，選 4 個以覆蓋最大差異化維度 |
| 是否納入 cache hit 量化數據 | (A) 只引用數字 (B) 不引用數字 | (A) 引用數字 | benchmarks/real-world-cache 提供了公開的真實用戶數據，對驗證技術效果有直接說服力 |
| 分析報告的語言風格 | (A) 評價性語言 (B) 純描述性語言 | (B) 純描述性 | AGENTS.md 明確要求「不評論好壞、不延伸設計哲學」「不使用情緒性語言」「不寫可能、也許、我認為」 |
