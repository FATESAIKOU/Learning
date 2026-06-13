# Odysseus-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `pewdiepie-archdaemon/odysseus` 進行深度技術調研，已持有 README，需補充：
- docs/ 目錄架構細節
- ROADMAP.md / THREAT_MODEL.md
- core/ 與 src/ 目錄結構
- 網路上的技術分析與評論
- 各核心組件（Chat, Agent, Cookbook, Deep Research, Compare, Documents, Memory/Skills, Email, Notes/Tasks, Calendar）的技術實作
- Agent 迴圈機制（基於 opencode）
- MCP 整合方式
- Cookbook 本地模型伺服方式
- 安全模型
- 與 Open WebUI / LibreChat / AnythingLLM 等競品比較

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 從 GitHub raw 取得 README.md | 確認已持有的 README 內容與最新版本一致 | 取得完整 README 作為分析基礎 | 成功取得，內容與使用者持有的相符 |
| 從 GitHub raw 取得 ROADMAP.md | 了解專案當前優先事項與技術債務 | 取得開發路線圖 | 成功取得，包含 High Priority bugs、Refactor Targets、Frontend/Backend 改進清單 |
| 從 GitHub raw 取得 THREAT_MODEL.md | 了解安全信任邊界、角色權限、已知缺口 | 取得完整威脅模型 | 成功取得，包含角色能力矩陣、認證機制、Internal Tool Loopback、提示注入防護、Security Headers、4 個已知安全缺口 |
| 嘗試取得 ARCHITECTURE.md | 尋找專用架構文檔 | 取得架構說明 | 404 不存在，架構資訊僅在 README 末尾簡述 |
| 取得 docs/ 目錄內容 | 了解文檔結構 | 取得所有文檔清單 | 成功取得，docs/ 主要為 demo 媒體檔 (gif/webm) + landing page + email-outlook.md + security-ci.md + pr-blocker-audit.md |
| 取得 core/ 目錄內容 | 了解核心基礎設施 | 取得模組清單 | 成功取得：auth.py(25KB), database.py(99KB), middleware.py(6KB), session_manager.py(27KB), atomic_io.py, constants.py, models.py, platform_compat.py |
| 取得 src/ 目錄內容 | 了解業務邏輯層 | 取得模組清單 | 成功取得 60+ 檔案，關鍵：agent_loop.py(187KB), llm_core.py(102KB), mcp_manager.py(29KB), deep_research.py(40KB), context_compactor.py(18KB), prompt_security.py, tool_security.py |
| 取得 routes/ 目錄內容 | 了解 API 路由結構 | 取得路由清單 | 成功取得 50+ 路由模組，關鍵：cookbook_routes.py(161KB), email_routes.py(156KB), chat_routes.py(80KB), document_routes.py(76KB), skills_routes.py(76KB) |
| 取得 services/ 目錄內容 | 了解可插拔服務層 | 取得服務清單 | 成功取得：hwfit, search, memory, docs, shell, stt, tts, research, youtube, faces |
| 取得 static/ 目錄內容 | 了解前端架構 | 取得前端檔案清單 | 成功取得：index.html(208KB SPA), app.js(175KB), style.css(1.15MB), login.html, manifest.json, sw.js(PWA) |
| 取得 src/agent_tools/ 內容 | 了解工具定義 | 取得工具清單 | 成功取得：__init__.py(5KB), document_tools.py(27KB), filesystem_tools.py(17KB), subprocess_tools.py(5KB), web_tools.py(4KB) |
| 取得 src/search/ 內容 | 了解搜尋模組 | 取得搜尋模組清單 | 成功取得：core.py, providers.py, analytics.py, cache.py, content.py, query.py, ranking.py（多為 alias 指向 services/search） |
| 深入讀取 agent_loop.py | 理解 Agent 迴圈核心機制 | 取得完整 Agent 迴圈邏輯 | 成功取得（187KB），包含 fenced code block 工具呼叫、domain-based rules、tool sections、context compaction、plan mode 等 |
| 深入讀取 mcp_manager.py | 理解 MCP 整合機制 | 取得 MCP 管理邏輯 | 成功取得（29KB），包含 stdio/SSE/Streamable HTTP 三種傳輸、OAuth 流程、工具 schema sanitize、readonly 分類、auto-reconnect |
| 深入讀取 prompt_security.py | 理解提示注入防護 | 取得防護機制 | 成功取得，包含 UNTRUSTED_CONTEXT_POLICY、guard markers、escape 機制 |
| 深入讀取 tool_security.py | 理解工具權限控管 | 取得權限模型 | 成功取得，包含 NON_ADMIN_BLOCKED_TOOLS(40+)、PLAN_MODE_READONLY_TOOLS、plan_mode_disabled_tools() |
| 深入讀取 context_compactor.py | 理解上下文壓縮機制 | 取得壓縮邏輯 | 成功取得，包含 85% 閾值觸發、SELF_SUMMARY_SYSTEM_PROMPT、tool message sanitize、trim_for_context |
| 深入讀取 deep_research.py | 理解深度研究引擎 | 取得 IterResearch 實作 | 成功取得（40KB），包含 Planning→Think→Search→Extract→Synthesize→Decide→Final Report 完整流程 |
| 搜尋網路評論與技術分析 | 補充社群觀點 | 取得外部評價 | Google 搜尋遭 429 阻擋；GitHub repo 頁面顯示 69.5k stars / 8.8k forks / 1150 commits，活躍社群 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 架構完整性 | 對比 README 架構圖與實際目錄結構 | 一致：app.py → core/ → src/ → routes/ → services/ → static/ |
| Agent 迴圈機制 | 閱讀 agent_loop.py 原始碼 | 確認使用 fenced code block 工具呼叫模式，非 OpenAI function calling；支援 plan mode、domain-based rules、context compaction |
| MCP 整合深度 | 閱讀 mcp_manager.py 原始碼 | 確認支援 stdio/SSE/Streamable HTTP 三種傳輸，含 OAuth 流程、工具 schema sanitize、readonly 分類 |
| 安全模型完整性 | 閱讀 THREAT_MODEL.md + prompt_security.py + tool_security.py | 確認多層防護：認證(2FA)、授權(admin/non-admin)、提示注入防護(guard markers)、工具 denylist、internal loopback token |
| 深度研究引擎 | 閱讀 deep_research.py 原始碼 | 確認 IterResearch 模式，支援多搜尋提供者 fallback、自動分類、報告擴展、合成失敗 fallback |
| Cookbook 模型管理 | 閱讀 README Cookbook 章節 + cookbook_serve_lifecycle.py | 確認基於 llmfit 硬體掃描、tmux 背景管理、SSH 遠端伺服、Docker GPU passthrough 診斷 |
| 競品對比 | 基於對 Open WebUI / LibreChat / AnythingLLM / Msty 的已知資訊 | Odysseus 的差異化在於 Agent 迴圈 + Cookbook + Deep Research + 郵件/行事曆整合的 all-in-one 定位 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 架構文檔來源 | (a) 僅依賴 README 架構段 (b) 深入讀取各目錄原始碼 | 選擇 (b) | README 架構段僅 6 行概述，不足以理解技術細節；ARCHITECTURE.md 不存在 |
| Agent 迴圈分析深度 | (a) 僅依賴 README 描述 (b) 完整讀取 agent_loop.py 原始碼 | 選擇 (b) | Agent 迴圈是 Odysseus 核心差異化能力，需理解其實際實作而非表面描述 |
| 網路評論搜尋 | (a) Google 搜尋 (b) GitHub Discussions/Issues (c) 放棄外部評論 | 選擇 (a) 後遭 429，改以 GitHub repo 數據替代 | Google 搜尋遭 rate limit；GitHub repo 頁面提供足夠社群活躍度指標 (69.5k stars, 1150 commits) |
| 競品對比範圍 | (a) 僅列舉 (b) 含 DA 表 | 選擇 (b) | 依 AGENTS.md 規範，需提供 DA 表（技術名/技術解法/技術使用前提/技術使用副作用/技術使用預期效果） |
| 分析報告深度 | (a) 僅回答 4 點 (b) 加入架構圖與程式碼片段 | 選擇 (b) | 技術複雜度高，純文字難以表達架構層次；架構圖與虛擬碼有助於心智模型建立 |
