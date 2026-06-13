# planning-with-files-C1-完整技術調研與深度分析

## 狀況理解
使用者要求對 GitHub repo `othmanadi/planning-with-files` 進行完整深度調研，涵蓋 README、SKILL.md、docs/、templates/、scripts/、commands/、examples/ 全部目錄，以及外部網路資料（Manus 官方部落格、TechCrunch 收購報導）。目標是理解該技術解決的問題、核心機制、架構決策、benchmark 結果，並與其他 planning 方法做對比。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 透過 GitHub API 列舉 docs/、templates/、scripts/、commands/、examples/ 目錄結構 | 了解 repo 完整檔案組織 | 取得所有檔案清單與 download URL | 成功取得 5 個目錄的完整檔案列表（docs 含 30+ 檔案、templates 含 7 個、scripts 含 25 個、commands 含 12 個、examples 含 2 個） |
| Fetch README.md（master branch） | 取得完整 README 內容（含 v3 新功能、benchmark、17+ IDE 支援等） | 理解專案全貌與版本演進 | 成功取得完整 README（含 v3.0.0/v3.1.0 release notes、benchmark badges、community forks、session recovery 說明） |
| Fetch SKILL.md（skills/planning-with-files/ 路徑） | 取得核心 skill 定義（hooks、rules、templates、scripts 說明） | 理解 hook 系統、7 條 critical rules、security boundary | 成功取得完整 SKILL.md（含 5 個 hook 定義、7 條 rules、3-strike error protocol、autonomous/gated mode 完整說明、anti-patterns） |
| Fetch docs/quickstart.md, docs/workflow.md, docs/installation.md | 取得使用指南、工作流程圖、安裝說明 | 理解 5-step quickstart、visual workflow、4 種安裝方式 | 成功取得 3 份文件（quickstart 含 topic handoff pattern、workflow 含 ASCII diagram 與 5-question reboot test、installation 含 plugin/manual/legacy/one-line 四種方式） |
| Fetch docs/evals.md | 取得 benchmark 方法論與完整數據 | 理解 96.7% pass rate 的測試設計 | 成功取得完整 evals 文件（5 eval types、30 assertions、10 parallel subagents、3 blind A/B comparisons、token/time cost analysis） |
| Fetch docs/attestation-locking.md | 取得 SHA-256 鎖定機制的 write path 與 fallback 行為 | 理解 atomic rename、flock、platform behavior | 成功取得（含 Linux/macOS/Windows Git Bash/WSL 四平台行為表、slug-mode 推薦） |
| Fetch docs/article.md + docs/article-v2.md | 取得作者的安全審計故事與修復過程 | 理解 prompt injection amplification 漏洞與 v2.21.0 修復 | 成功取得兩篇文章（含 vulnerability flow、fix、eval verification） |
| Fetch docs/perf-notes.md | 取得 SHA cache 的效能設計細節 | 理解 cache location、keying、container 行為 | 成功取得（含 XDG_CACHE_HOME/pwf-sha 路徑、mtime-keyed cache、gated mode always rehash） |
| Fetch templates/task_plan.md, findings.md, progress.md, loop.md | 取得 3-file pattern 的模板結構 | 理解各檔案的 section 設計與註解說明 | 成功取得 4 個模板（task_plan 含 Goal/Phases/Decisions/Errors、findings 含 Requirements/Research/Decisions/Issues/Resources/Visual、progress 含 Session/Phase log/Test Results/Error Log/5-Question Reboot、loop 含 planning-aware tick prompt） |
| Fetch scripts/init-session.sh | 取得 session 初始化腳本的完整邏輯 | 理解 legacy/slug/autonomous/gated 四種 mode 的初始化流程 | 成功取得完整腳本（含 slugify、short_uuid、gen_nonce、apply_v3_mode、template 選擇、.mode/.nonce/.stop_blocks 寫入） |
| Fetch scripts/check-complete.sh | 取得 completion check 腳本的完整邏輯 | 理解 phase status 解析、gate decision table、5 個 guard conditions | 成功取得完整腳本（含 primary/inline status 雙格式支援、gate 五條件判斷、block counter、stall detection、JSON block decision 輸出） |
| Fetch scripts/attest-plan.sh | 取得 attestation 腳本的完整邏輯 | 理解 SHA-256 計算、atomic rename、flock、read-back verification | 成功取得完整腳本（含 resolve→hash→temp file→atomic rename→verify 流程、integrity gap fix、concurrent writer detection） |
| Fetch scripts/inject-plan.sh | 取得 plan injection dispatcher 的完整邏輯 | 理解 context mode（userprompt/pretool/precompact）、attestation check、v3 mode 行為差異 | 成功取得完整腳本（含 resolution order、containment guard、SHA cache、nonce delimiters、tamper detection、ledger summary vs raw progress tail） |
| Fetch scripts/gate-stop.sh | 取得 Stop hook dispatcher | 理解 thin wrapper 如何發現 check-complete.sh 並傳遞 --gate | 成功取得（含 script discovery pattern、stdin passthrough） |
| Fetch scripts/ledger-append.sh + ledger-summary.sh | 取得 run ledger 的寫入與讀取邏輯 | 理解 JSONL 格式、tick monotonic counter、fixed-shape summary | 成功取得兩個腳本（ledger-append 含 event allowlist、agent sanitization、flock-protected append、max_tick_in_dir；ledger-summary 含 phase count、per-agent last event、KV-cache stable output） |
| Fetch scripts/resolve-plan-dir.sh | 取得 plan directory 解析邏輯 | 理解 4-step resolution order、containment guard、portable mtime | 成功取得（含 PLAN_ID→.active_plan→newest mtime→legacy 順序、canonicalize、is_within_root、mtime_of 多平台 fallback） |
| Fetch scripts/session-catchup.py | 取得 session recovery 邏輯 | 理解 Claude Code JSONL 與 OpenCode SQLite 兩種 backend | 成功取得完整 Python 腳本（含 detect_ide、scan_for_planning_update、extract_messages_from_session、opencode_catchup with sqlite3） |
| Fetch scripts/phase-status.sh + set-active-plan.sh | 取得 phase status 寫入與 active plan 切換邏輯 | 理解 concurrent-safe write（flock + atomic temp+mv）與 active plan pointer 機制 | 成功取得兩個腳本（phase-status 含 awk rewrite、status allowlist；set-active-plan 含 show/set 雙模式） |
| Fetch commands/plan.md, plan-goal.md, plan-loop.md, plan-attest.md, status.md | 取得 slash command 定義 | 理解 plugin 命令的觸發邏輯與 Claude Code turn-loop 整合 | 成功取得 5 個 command 定義（plan-goal 含 /goal bridge、plan-loop 含 /loop bridge、plan-attest 含 attestation workflow、status 含 compact status display） |
| Fetch examples/README.md | 取得完整 walkthrough 範例 | 理解 3-file pattern 在實際任務中的演進過程 | 成功取得完整範例（含 Phase 1→4 的四階段檔案狀態展示、error handling 範例、key takeaways） |
| Fetch Manus 官方部落格《Context Engineering for AI Agents》 | 取得 Manus 的 context engineering 原始設計理念 | 理解 KV-cache、mask don't remove、filesystem as context、recitation、error persistence 五大原則 | 成功取得完整文章（含 5 個 principles 的詳細說明、Manus 的 agent loop 設計、todo.md 的 attention manipulation 機制） |
| Fetch TechCrunch《Meta just bought Manus》 | 取得 Manus 被收購的背景資訊 | 理解 Manus 的商業價值（$2B acquisition、$100M+ ARR、millions of users） | 成功取得（含 acquisition timeline、Benchmark $75M round、Meta 整合計劃） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 檔案覆蓋完整性 | 對照使用者要求的 10 個調研項目，逐一確認是否取得對應原始碼/文件 | 全部 10 項均已取得完整內容（README、SKILL.md、docs/*、templates/*、scripts/*、commands/*、examples/*、外部文章） |
| 核心機制理解 | 交叉比對 SKILL.md 的 hook 定義與 scripts/ 中的實際實作 | hook 定義與 dispatcher 腳本邏輯一致；inject-plan.sh 集中管理原本散落在 14 個 SKILL.md 變體中的 injection 邏輯 |
| v3 新功能理解 | 對照 README release notes 與 SKILL.md/scripts 中的實作 | autonomous mode（丟棄 per-tool-call injection、default-on attestation、ledger summary）與 gated mode（5-condition gate、runaway guards、host capability tiers）的設計意圖與實作一致 |
| Benchmark 數據可信度 | 閱讀 evals.md 的完整方法論（assertion 定義、test cases、A/B blind comparison 設計） | 方法論透明：30 assertions 均為 objectively verifiable（file existence、section headers）；3 blind A/B comparisons 由 independent comparator agents 執行；token/time cost 有量化 |
| 安全性設計 | 閱讀 article.md 的 vulnerability 分析 + SKILL.md security boundary + attestation 機制 | 三層防禦：(1) delimiter framing (2) hash attestation (3) v3 nonce + attested injection refusal + structured ledger；v2.21.0 移除了 WebFetch/WebSearch 從 allowed-tools |
| 跨平台支援 | 檢查 scripts/ 中 sh + ps1 雙版本、docs/ 中 17+ IDE 設定指南 | 每個核心腳本均有 bash 與 PowerShell 版本；每個支援的 IDE 有獨立 docs/<ide>.md 設定指南 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| SKILL.md 路徑 | (a) repo root 的 SKILL.md (b) skills/planning-with-files/SKILL.md | 選擇 (b) skills/planning-with-files/SKILL.md | repo root 無 SKILL.md（404）；skills/ 子目錄下的才是實際被 Claude Code 載入的 skill 定義，含完整 frontmatter hooks |
| 外部資料範圍 | (a) 僅 repo 內文件 (b) 加入 Manus 官方部落格 (c) 加入更多第三方評論 | 選擇 (b) | Manus 部落格是 planning-with-files 設計理念的直接來源（README 明確引用）；第三方評論在 web search 中未找到獨立技術分析 |
| 分析報告深度 | (a) 僅回答 4 點格式 (b) 加入架構圖與程式碼片段 | 選擇 (b) | AGENTS.md 要求「善用圖示、程式碼或虛擬碼做舉例」；3-file pattern 與 hook 系統的本質適合用 ASCII diagram 與 script 邏輯摘要呈現 |
| DA 表對照技術選擇 | (a) TodoWrite + spec-driven + context compression (b) 加入更多如 LangGraph、AutoGPT | 選擇 (a) | TodoWrite 是 Claude Code 內建 direct alternative；spec-driven 與 context compression 是不同切入點的同類問題解法；LangGraph/AutoGPT 是 agent framework 層級，非 planning 層級 |
