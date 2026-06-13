# context-mode-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `mksglu/context-mode` 進行深度技術調研，產出分析報告與分析過程報告。context-mode 是一個 MCP server plugin，宣稱能將 AI 編碼代理的 context window 使用量縮減 98%（315 KB → 5.4 KB），透過 sandbox 隔離工具輸出、FTS5/BM25 知識庫索引、session continuity 機制、以及「Think in Code」範式強制。支援 15+ 平台（Claude Code、Cursor、OpenCode、Gemini CLI、VS Code Copilot、JetBrains Copilot、Codex CLI 等）。GitHub stars 17.3k，被 Microsoft、Google、Meta、Amazon 等企業團隊使用。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 讀取 AGENTS.md 與資料夾結構 | 理解任務規範與現有 output/learning-log 格式 | 確認輸出格式要求與目錄結構 | 確認需產出 `output/<日期>-<技術名>.md` 與 `learning-log/<技術名>-C1-<總結>.md`；現有 18 個 output 與 31 個 learning-log |
| WebFetch GitHub repo 首頁 | 取得 README 全貌（安裝、架構、功能說明） | 理解技術全貌 | README 被截斷（~55528 bytes），取得前半段包含 Problem、How It Solves、Install（15+ 平台）、Tools 等核心章節 |
| WebFetch `llms.txt` | 取得專為 LLM 設計的導覽索引 | 快速定位核心檔案與架構 | 取得完整架構導覽：Core Architecture（server/store/executor/security/runtime）、Hook System、Skills、Configuration、API Reference |
| WebFetch `llms-full.txt` | 取得完整 API 參考與技術細節 | 深入理解工具簽名、參數、知識庫、安全模型 | 取得完整技術文件：11 個 MCP 工具完整簽名與參數、FTS5/BM25 知識庫 schema 與三層 fallback 搜尋、12 語言 polyglot sandbox、安全模型、hook 系統、benchmark 數據 |
| WebFetch `BENCHMARK.md` | 取得效能基準測試數據 | 驗證 98% 縮減宣稱的實證基礎 | 取得 21 場景 benchmark：Part 1 `ctx_execute_file` 14 場景 98% savings、Part 2 `ctx_index`+`ctx_search` 6 場景 82% savings、Part 3 大型輸出 externalization、full debugging session 94% context 節省 |
| WebFetch `src/server.ts` | 取得核心實作細節 | 理解 MCP server 架構、工具註冊、session 統計、安全檢查 | 取得 server.ts 完整原始碼（~2500 行），包含工具註冊邏輯、OpenCode/KiloCode 原生 plugin 路徑、session stats 追蹤、安全 deny policy、project dir 解析 |
| Task agent 讀取截斷的 README 後半 | 取得被截斷的 README 剩餘內容 | 補全 README 資訊 | 取得後半內容：Session Continuity 詳細機制（5 種 Hook 協同）、Platform Compatibility 矩陣、Utility Commands、Benchmarks、Privacy、Security、License |
| Task agent 搜尋替代方案 | 尋找解決類似問題的其他技術 | 為 DA 表蒐集 2-4 個替代方案 | 取得 4 個替代方案：LeanCTX（最接近競爭者）、smart-mcp（tool schema 縮減）、Repomix（codebase 預壓縮）、code2prompt（codebase 預壓縮） |
| 讀取現有 LeanCTX 分析報告 | 參考現有報告格式與 LeanCTX 作為對照 | 確保格式一致性並理解相近技術 | LeanCTX 報告格式為 4 點結構（問題/背景/解法/替代方案+DA表），與 context-mode 問題域高度重疊 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 技術全貌理解 | 交叉比對 README、llms-full.txt、BENCHMARK.md、server.ts | 完整理解四大機制：Context Saving（sandbox + FTS5）、Session Continuity（SQLite events + BM25 resume）、Think in Code（強制 script 執行）、No prose-style enforcement（不干預模型輸出風格） |
| 平台覆蓋範圍 | README Install 章節 + server.ts 平台偵測邏輯 | 15+ 平台：Claude Code、Gemini CLI、VS Code Copilot、JetBrains Copilot、Cursor、OpenCode、KiloCode、OpenClaw/Pi、Codex CLI、Kimi Code、Qwen Code、Antigravity、Kiro、Zed、OMP |
| 替代方案完整性 | Task agent 搜尋 + 手動比對 LeanCTX | 4 個替代方案涵蓋不同切入點：tool output sandbox（LeanCTX）、tool schema 縮減（smart-mcp）、codebase 預壓縮（Repomix、code2prompt） |
| 輸出格式合規 | 比對 AGENTS.md 規範與現有 output 檔案 | 分析報告符合 4 點結構（問題/背景/解法/替代方案+DA表+切入點差異圖）；分析過程報告符合指定格式（狀況理解/動作與結果/現狀/決斷點） |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 替代方案選擇 | (a) 僅列 LeanCTX 一個替代方案；(b) 列 LeanCTX + smart-mcp + Repomix + code2prompt 四個；(c) 列 MemGPT/Letta、RTK、Context+ 等（沿用 LeanCTX 報告的 DA 表） | 選擇 (b)：LeanCTX + smart-mcp + Repomix + code2prompt | LeanCTX 報告已涵蓋 MemGPT/Letta、RTK、Context+ 等方案，且那些方案與 context-mode 的切入點差異較大（MemGPT 為通用對話記憶、RTK 為雲端快取）。本次選擇與 context-mode 直接相關的四個方案：LeanCTX（最接近競爭者）、smart-mcp（MCP 代理方案）、Repomix/code2prompt（codebase 預處理方案），使 DA 表更具針對性 |
| DA 表欄位設計 | (a) 沿用 AGENTS.md 規範的 5 欄（技術名/技術解法/技術使用前提/技術使用副作用/技術使用預期效果）；(b) 自行擴充欄位 | 選擇 (a) | AGENTS.md 明確規範 DA 表欄位，且現有所有 output 報告均遵循此格式 |
| 分析報告是否加入「Think in Code」與「No prose-style enforcement」的詳細說明 | (a) 僅簡述；(b) 詳細展開含虛擬碼 | 選擇 (b) | README 明確將此列為四大解決機制之一，且 llms-full.txt 提供完整技術細節，應忠實呈現 |
| 是否在分析報告中提及 context-mode 與 LeanCTX 的對比 | (a) 在 DA 表中簡述；(b) 在正文中額外展開對比 | 選擇 (a) | AGENTS.md 規範分析報告僅回答 4 點，不額外延伸；對比資訊置於 DA 表與切入點差異圖中即足夠 |
