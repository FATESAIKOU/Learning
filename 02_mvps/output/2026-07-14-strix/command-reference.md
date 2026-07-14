# Strix AI 滲透測試 — 完整指令表

> 執行環境：fh-l (Linux x86_64, Ubuntu 24.04, Docker 29.2.0)
> 控制端：M4 Mac Pro via SSH + tmux sysinfo session
> 目標：https://axross-recipe.com/
> LLM：Ollama Cloud (deepseek-v4-flash)

---

## Phase 1: 環境準備

### 1-1. 確認遠端 Docker 狀態

```bash
ssh fh-l "docker info 2>&1 | head -15"
```

- **說明**：確認目標機器 Docker daemon 正常運行。Strix 的所有滲透行動都在 Docker 沙箱內執行。
- **驗證**：輸出 `Server Version`, `Containers`, `Images` 統計資訊，無錯誤。

### 1-2. 確認 tmux session

```bash
ssh fh-l "tmux list-sessions"
```

- **說明**：確認 sysinfo session 存在且已 attached，後續所有指令透過 `tmux send-keys` 發送至此 session。

### 1-3. 安裝 Strix CLI（curl 安裝法）

```bash
ssh fh-l 'tmux send-keys -t sysinfo "curl -sSL https://strix.ai/install | bash" Enter'
```

- **說明**：透過官方一鍵安裝腳本 (curl → bash) 安裝 Strix。腳本會：
  1. 偵測作業系統與 CPU 架構
  2. 下載適合的 binary → `/home/<user>/.strix/bin/strix`
  3. 寫入 PATH 到 `~/.zshrc`
  4. 自動拉取 Docker sandbox image `ghcr.io/usestrix/strix-sandbox:1.0.0`
- **替代方案**：`pipx install strix-agent`（但本次因網路問題逾時失敗）
- **驗證**：Shell 輸出 `"Strix X.Y.Z ready"` + `"Sandbox image pulled successfully"`

### 1-4. 驗證安裝

```bash
ssh fh-l "/home/fatesaikou/.strix/bin/strix --version"
```

- **說明**：確認 strix binary 可執行且版本正確。
- **驗證**：輸出 `strix 1.0.4`

### 1-5. 設定 LLM Provider 環境變數

```bash
tmux send-keys -t sysinfo 'export STRIX_LLM="ollama_chat/deepseek-v4-flash"' Enter
tmux send-keys -t sysinfo 'export LLM_API_BASE="https://ollama.com"' Enter
tmux send-keys -t sysinfo 'export LLM_API_KEY="<OLLAMA_CLOUD_API_KEY>"' Enter
```

- **說明**：設定三個必要的環境變數：
  | 變數 | 值 | 用途 |
  |---|---|---|
  | `STRIX_LLM` | `ollama_chat/deepseek-v4-flash` | 指定 LLM provider/model，`ollama_chat` prefix 使用 `/api/chat` 端點（支援 tool calling） |
  | `LLM_API_BASE` | `https://ollama.com` | Ollama Cloud 的 API 端點（非本地 localhost） |
  | `LLM_API_KEY` | `<key>` | Ollama Cloud 認證金鑰，格式為 `<hex>.<jwt>` |
- **驗證**：`echo $STRIX_LLM` 輸出不為空

---

## Phase 2: 目標偵查與掃描

### 2-1. 手動 Recon（可選，本機執行）

使用瀏覽器 DevTools 或 curl 收集目標資訊：
```bash
# 檢查 HTTP headers
curl -sI https://axross-recipe.com/

# 檢查 API 端點
curl -s https://api.axross-recipe.com/configs | python3 -m json.tool
```

- **說明**：手動收集目標的技術棧、API 端點、認證機制、安全 headers。產出 `output/<date>-strix/target-recon.md`。
- **驗證**：產出 recon 報告含技術棧、API 列表、攻擊面分析。

### 2-2. 執行 Quick Mode 掃描

```bash
tmux send-keys -t sysinfo 'strix -n --target https://axross-recipe.com --scan-mode quick' Enter
```

- **說明**：非互動模式 (`-n`) 的快速掃描，約 5-15 分鐘。Strix 會：
  1. 在 Docker 中啟動 sandbox 容器
  2. 內部啟動 Caido Proxy、Playwright Browser、nuclei scanner、Python runtime
  3. LLM Agent 進行自動化偵查 → 利用 → 驗證 → 回報
- **驗證**：`strix_runs/<target>-<hash>/vulnerabilities.csv` 產生，含漏洞清單

### 2-3. 檢視掃描輸出

```bash
# 列出 run 目錄
ssh fh-l "ls -la ~/strix_runs/axross-recipe-com_*/"

# 檢視漏洞 CSV
ssh fh-l "cat ~/strix_runs/axross-recipe-com_*/vulnerabilities.csv"

# 檢視完整 JSON
ssh fh-l "cat ~/strix_runs/axross-recipe-com_*/vulnerabilities.json"
```

- **說明**：Strix 將結果輸出到 `~/strix_runs/<run-name>/`，包含：
  | 檔案 | 內容 |
  |---|---|
  | `vulnerabilities.csv` | 漏洞清單 (id, title, severity, timestamp, file) |
  | `vulnerabilities.json` | 完整的結構化漏洞報告 (含 PoC, CVSS, remediation) |
  | `vulnerabilities/vuln-XXXX.md` | 個別漏洞的 Markdown 報告 |
  | `run.json` | 完整的執行記錄 |
  | `strix.log` | 除錯日誌 |
- **驗證**：`vulnerabilities.csv` 中包含漏洞條目

### 2-4. 執行 Deep Mode 掃描

```bash
tmux send-keys -t sysinfo 'strix -n --target https://axross-recipe.com --scan-mode deep --instruction "Focus on web application vulnerabilities: XSS, CSRF, IDOR, SQLi, auth bypass, business logic flaws"' Enter
```

- **說明**：深度掃描，預計 1-4 小時。`--instruction` 參數指定掃描方向（可選）。
- **與 Quick Mode 的差異**：
  | 面向 | Quick | Deep |
  |---|---|---|
  | 時間 | 5-15 分鐘 | 1-4 小時 |
  | LLM 推理深度 | 淺 | 深 (chained vulns, edge cases) |
  | SAST/DAST | 基礎 | semgrep + AST + 動態驗證 |
  | Token 消耗 | ~50M | 可能 >200M |

### 2-5. 追蹤掃描進度

```bash
# 即時查看 TUI 進度
ssh fh-l "tmux capture-pane -t sysinfo:1 -p" | tail -20

# 監控 Docker 容器狀態
ssh fh-l "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' | grep strix"
```

---

## Phase 3: 結果分析與報告產出

### 3-1. 彙整結果

```bash
# 將遠端結果拉到本機
scp -r fh-l:~/strix_runs/axross-recipe-com_*/ ./output/2026-07-14-strix/raw-output/
```

- **說明**：將 fh-l 上的掃描結果複製到本機的 `output/` 目錄做進一步處理。

### 3-2. 分析與分類漏洞

```bash
# 依嚴重性排序
ssh fh-l "python3 -c \"
import json
with open('strix_runs/axross-recipe-com_XXXX/vulnerabilities.json') as f:
    vulns = json.load(f)
for v in sorted(vulns, key=lambda x: x['cvss'], reverse=True):
    print(f\\\"{v['severity']:5} | CVSS {v['cvss']:.1f} | {v['title']}\\\")\""
```

### 3-3. 產出滲透報告

- 基於 `vulnerabilities.json` 和 `vulnerabilities/*.md` 撰寫結構化報告
- 格式：Executive Summary → Findings Table → Detailed Findings (含 PoC, CVSS, 修復建議)
- 產出：`output/<date>-strix/pentest-report.md`

### 3-4. 能力邊界分析

- 撰寫獨立的能力邊界分析文件
- 內容：Strix 掃描到什麼 / 沒掃到什麼 / AI 判斷準確度 / Token 消耗 / 成本
- 產出：`output/<date>-strix/capability-boundary.md`

---

## Phase 4: 清理

### 4-1. 停止 Strix（若需手動中斷）

```bash
tmux send-keys -t sysinfo '^C'  # Ctrl+C
```

### 4-2. 清理 Docker 資源

```bash
ssh fh-l "docker rm -f \$(docker ps -a --filter 'ancestor=ghcr.io/usestrix/strix-sandbox' -q)"
```

---

## 附錄：環境變數參考

| 變數 | 必填 | 範例值 | 說明 |
|---|---|---|---|
| `STRIX_LLM` | 是 | `ollama_chat/deepseek-v4-flash` | provider/model 格式 (LiteLLM) |
| `LLM_API_KEY` | 是 | `717d34...` | Ollama Cloud API key |
| `LLM_API_BASE` | 否 | `https://ollama.com` | 自訂 API endpoint (非 localhost 時必填) |
| `STRIX_REASONING_EFFORT` | 否 | `high` / `medium` | 推理深度 (預設 high，quick scan 為 medium) |
| `PERPLEXITY_API_KEY` | 否 | — | 搜尋增強功能（可選） |
| `STRIX_MAX_LOCAL_COPY_MB` | 否 | `1024` | 本地目錄掃描的檔案大小上限 (MB) |
| `LLM_MODEL` | 否 | — | 部分 provider 的替代模型指定方式 |

---

## 附錄：目錄結構說明

```
output/2026-07-14-strix/
├── LEARNING-PLAN.md          # 學習計畫 (含技術分析 + Checklist)
├── target-recon.md           # 手動偵查報告 (目標網站情報)
├── raw-output/               # Strix 原始輸出 (從 fh-l 拉取的 strix_runs/)
├── pentest-report.md         # 最終滲透報告 (綜合分析)
└── capability-boundary.md   # Strix 能力邊界分析

fh-l ~/strix_runs/
└── axross-recipe-com_XXXX/
    ├── run.json              # 完整執行記錄
    ├── strix.log             # 除錯日誌
    ├── vulnerabilities.json  # 結構化漏洞報告
    ├── vulnerabilities.csv   # 漏洞摘要表
    ├── vulnerabilities/      # 個別漏洞詳細報告 (*.md)
    └── .state/               # 內部狀態 (strix 內部使用)
```
