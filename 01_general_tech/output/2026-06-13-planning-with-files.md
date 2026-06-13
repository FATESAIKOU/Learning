# planning-with-files 技術分析報告

## 1. 這個技術解決什麼問題？

AI agent（如 Claude Code、Cursor、Codex 等）在執行長時間、多步驟任務時，面臨四個具體問題：

| 問題 | 具體表現 |
|------|----------|
| **揮發性記憶（Volatile Memory）** | TodoWrite 工具在 `/clear` 或 context reset 後消失，所有規劃狀態遺失 |
| **目標漂移（Goal Drift）** | 經過 50+ 次 tool call 後，agent 忘記原始目標，偏離任務方向 |
| **隱藏錯誤（Hidden Errors）** | 失敗未被追蹤記錄，導致相同錯誤重複發生 |
| **上下文膨脹（Context Stuffing）** | 所有資訊塞進 context window，而非持久化儲存，導致 context 快速耗盡 |

planning-with-files 透過**檔案系統作為持久化記憶**的模式，將 agent 的工作狀態從揮發性 context window 遷移到磁碟上的 markdown 檔案，使 agent 在 context 重置後仍能恢復工作狀態。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

- **Manus AI 的 context engineering 實踐**：Manus（2025/12 被 Meta 以 $2B 收購）在其官方部落格《Context Engineering for AI Agents》中揭示了 agent 系統的核心困境：
  - LLM 的 context window 雖達 128K tokens，但在真實 agentic 場景中仍不足
  - 模型效能隨 context 長度增加而衰減（lost-in-the-middle 問題）
  - 長輸入即使有 prefix caching 仍然昂貴（prefill 成本高）
  - 任何不可逆的 context 壓縮都伴隨資訊遺失風險
- **Manus 的解決方案**：將檔案系統視為「終極 context」——無大小限制、天然持久、agent 可直接操作。模型學會按需讀寫檔案，將檔案系統用作結構化的外部記憶。

### 通用技術背景（自行補充）

| 因素 | 說明 |
|------|------|
| Context window 限制 | Claude 200K / GPT-4 128K token context 看似大，但在真實 agentic 任務中（程式碼庫操作、多輪研究、大量 tool call）仍快速耗盡 |
| Lost-in-the-middle | LLM 對 context 中段的注意力衰減，導致早期指令被遺忘 |
| KV-cache 壓力 | 長 context 使 KV-cache 膨脹，影響延遲與成本 |
| Agent 無狀態設計 | 多數 agent framework 將狀態存在 context 中，context 揮發導致狀態丟失 |

---

## 3. 這個技術是如何解決該問題的？

### 核心機制：3-File Pattern

```
Agent 任務執行流程
        │
        ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ task_plan.md  │     │ findings.md  │     │ progress.md  │
│              │     │              │     │              │
│ • Phase 追蹤  │     │ • 研究發現    │     │ • Session log │
│ • Checkboxes  │     │ • 調查結果    │     │ • Test results│
│ • 決策記錄    │     │ • 收集的資訊  │     │ • Error log   │
│ • 錯誤清單    │     │ • 參考資料    │     │ • 時間戳記    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │      Hook 系統 (5 hooks)    │
              │                           │
              │ SessionStart → 初始化       │
              │ PreToolUse → re-read plan  │
              │ PostToolUse → 提醒更新      │
              │ Stop → 驗證完成             │
              │ PreCompact → flush progress│
              └───────────────────────────┘
```

### 3.1 Hook 系統

| Hook | 觸發時機 | 行為 |
|------|---------|------|
| **SessionStart** | Agent session 啟動 | 初始化 planning files；檢查前次 session 遺留；支援 `--autonomous` / `--gated` 模式 |
| **PreToolUse** | 每次 tool call 前（legacy）/ session start + phase transitions（autonomous） | 注入 plan 內容到 context，確保 agent 記得當前階段 |
| **PostToolUse** | 每次 tool call 後 | 提醒 agent 更新 progress.md |
| **Stop** | Agent 嘗試停止時 | 檢查所有 phase 是否完成；gated mode 下 block stop |
| **PreCompact** | Context 壓縮前 | Flush progress，確保壓縮後重要資訊不遺失 |

### 3.2 Session Recovery 機制

當 `/clear` 執行後，skill 自動從 previous session 恢復：

1. 檢查 active IDE 的 session store（`~/.claude/projects/` for Claude Code, `~/.codex/sessions/` for Codex）
2. 找到 planning files 最後更新時間點
3. 提取該時間點之後的對話（potentially lost context）
4. 生成 catchup report

虛擬碼：
```python
def session_recovery():
    planning_sessions = scan_planning_files()
    last_update = max(s.modified_at for s in planning_sessions)
    
    previous_session = get_previous_session_data()
    lost_context = previous_session.get_conversation_after(last_update)
    
    if lost_context:
        print_catchup_report(lost_context)
```

### 3.3 v3 關鍵創新

#### Autonomous Mode（自主模式）

- 丟棄 per-tool-call plan re-injection（減少 +68% token overhead）
- 保留 turn-start injection
- Default-on attestation（未驗證的 plan 內容拒絕注入）
- Structured run ledger 取代 raw progress.md tail

#### Gated Mode（閘控模式）

5-condition completion gate：
1. Gated mode marker 存在
2. 有 `in_progress` 狀態的 phase
3. `stop_hook_active` = false
4. Block count < cap (default 20)
5. Ledger 自上次 block 以來有進展

Runaway guards：block counter、stall detection、cap 限制

Host capability tiers：
| Tier | 能力 | 適用場景 |
|------|------|---------|
| Tier 1 | Hard block（強制阻擋 stop） | Claude Code, Cursor |
| Tier 2 | Follow-up inject（注入提醒） | Codex, Gemini CLI |
| Tier 3 | Notify only（僅通知） | OpenCode, Continue |

#### Attestation（認證鎖定）

- SHA-256 鎖定 `task_plan.md`
- Hook 端比對 hash，mismatch 時 block injection
- v3 增加 nonce delimiters 防止 replay
- SHA cache 移至 `$XDG_CACHE_HOME/pwf-sha`

#### Run Ledger

- Append-only JSONL 格式（`ledger-<agent>.jsonl`）
- Fixed-shape summary（無 timestamps → KV-cache stable）
- 相對於 raw progress.md tail 更適合 structured parsing

### 3.4 Parallel Plan Isolation（並行隔離）

```
.planning/
├── 2026-01-15-feature-x/       ← session 1
│   ├── task_plan.md
│   ├── findings.md
│   └── progress.md
├── 2026-01-15-bug-fix-y/       ← session 2
│   ├── task_plan.md
│   ├── findings.md
│   └── progress.md
└── .active_plan                ← current session pointer
```

- Slug mode：`.planning/YYYY-MM-DD-slug/`
- `resolve-plan-dir.sh` 4-step resolution（slug → active_plan → legacy root → create）
- Containment guard 防 symlink traversal

### 3.5 平台支援（17+）

| 等級 | IDE |
|------|-----|
| **Enhanced Support**（hooks + lifecycle automation） | Claude Code, Cursor, GitHub Copilot, Mastra Code, Gemini CLI, Kiro, Codex, Hermes Agent, CodeBuddy, FactoryAI Droid, OpenCode |
| **Standard Agent Skills**（via `npx skills add`） | Continue, Pi Agent, OpenClaw, Antigravity, Kilocode, AdaL CLI |
| **Sandbox Runtime** | BoxLite（via ClaudeBox） |

### 3.6 Benchmark 結果（v2.21.0, claude-sonnet-4-6）

| Test | with_skill | without_skill |
|------|-----------|---------------|
| Pass rate (30 assertions) | **96.7%** (29/30) | 6.7% (2/30) |
| 3-file pattern followed | 5/5 evals | 0/5 evals |
| Blind A/B wins | **3/3 (100%)** | 0/3 |
| Avg rubric score | **10.0/10** | 6.8/10 |

Cost: +68% tokens, +17% time（structured output 的代價）

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（Decision Analysis）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|---------|-------------|---------------|----------------|
| **Claude Code TodoWrite** | 內建 TodoWrite 工具追蹤 task list | 僅在單一 session context 內有效 | `/clear` 或 session 中斷後完全遺失；無跨 session 持久化；無 completion gate | 短期任務的簡單進度追蹤 |
| **Spec-Driven Development** | 先撰寫完整 spec，agent 按 spec 執行 | 需 upfront 撰寫規格文件 | Spec 為靜態文件，缺乏 runtime adaptation；不追蹤執行進度；無錯誤持久化 | 需求明確、變更少的專案 |
| **Context Compression** | 壓縮/摘要 context 以節省空間 | 模型需支援 context compaction | 不可逆壓縮導致資訊遺失；無法精確恢復任務狀態；壓縮後的摘要可能遺漏關鍵細節 | 延長單一 session 的有效執行時間 |
| **Multi-Agent Orchestration** | 任務分解為子任務，多 agent 平行處理 | 任務可分解為獨立子任務 | 協調 overhead；子任務間狀態同步複雜；解決規模問題而非記憶問題 | 大規模任務的平行執行 |

### 各方案切入點差異

| 方案 | 核心切入點 |
|------|-----------|
| **planning-with-files** | 以**檔案系統作為 agent 的持久化記憶**，解決 volatile memory + goal drift + hidden errors + context stuffing 四個根本問題 |
| **Claude Code TodoWrite** | context 內 task list，快速簡單但無持久化 |
| **Spec-Driven Development** | upfront 規格定義，適合需求穩定的專案 |
| **Context Compression** | 減少 context 體積以延長 session 壽命，但伴隨資訊遺失 |
| **Multi-Agent Orchestration** | 任務分解與平行處理，解決規模問題而非記憶問題 |
