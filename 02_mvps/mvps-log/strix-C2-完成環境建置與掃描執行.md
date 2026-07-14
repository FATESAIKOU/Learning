# strix-C2-完成環境建置與掃描執行

## 狀況理解

使用者在 fh-l (Linux x86_64) 上透過 tmux sysinfo session 執行 Strix 安裝與掃描。初步使用 Anthropic API 的計劃因費用問題改為 Ollama Cloud。掃描過程遭遇多次 LLM 層問題，最終完成兩次 Quick Mode 掃描並產出完整報告。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 在 fh-l tmux sysinfo 安裝 Strix | 避開本機 M4 Mac 網路問題 | curl 安裝 + Docker sandbox pull | 成功，Strix 1.0.4 + sandbox image 就緒 |
| 配置 Ollama Cloud env vars | 讓 Strix 使用 Ollama Cloud API | `STRIX_LLM=ollama_chat/deepseek-v4-flash` | 驗證通過 |
| 執行 Quick Mode (flash) | 快速驗證工具可用性 | 5-10 分鐘產出初步漏洞 | 24 分鐘後 sub-agent hang，8 漏洞 (1H/7M) |
| 診斷 flash 卡住原因 | 判斷是工具問題還是 LLM 問題 | 確認死因 | sub-agent 8b68be24 卡在 waiting，Ollama Cloud API 無回應 |
| 改回 pro 重跑 Quick Mode | 測試不同模型的效果差異 | pro 模型能更穩定完成 | 17M tokens 時 Ollama Cloud session limit 中斷，7 漏洞 (2C/4M/1L) |
| 手動 Recon 目標網站 | 收集目標技術棧與攻擊面 | 產出 target-recon.md | Next.js + Rails API + NextAuth.js 架構，7 個 API 端點 |
| 拉取遠端結果 | 將 fh-l 上的掃描結果複製到本機 | scp strix_runs/ | 成功拉取 2 組 vulnerabilities.json + md 詳細報告 |
| 撰寫綜合滲透報告 | 彙整兩次掃描結果 | 結構化 pentest-report.md | 11 個漏洞、含 Executive Summary、Risk Matrix |
| 撰寫能力邊界分析 | 記錄 Strix 的實際能力與限制 | 至少 3 條邊界觀察 | 7 條觀察，含模型對比、token 效率、Ollama Cloud 極限 |
| 撰寫指令參考表 | 記錄完整操作歷程 | command-reference.md | 4 個 Phase、12 個指令、附環境變數表 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| fh-l 環境 | Docker + Strix + sandbox image | 全部就緒，可重複使用 |
| 掃描結果 | 兩組 strix_runs/ 目錄 | 已拉取到本機 output/ 目錄 |
| 產出文件 | pentest-report.md, capability-boundary.md, command-reference.md, target-recon.md | 全部存在 |
| LEARNING-PLAN.md | 所有 C1-C9 步驟 | 全部標記為 [x] |
| 漏洞總數 | 兩次掃描合併去重 | 11 個獨立漏洞 (2 CRITICAL, 1 HIGH, 8 MEDIUM/LOW) |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| LLM provider | ① Anthropic Claude API ② Ollama Cloud | 選擇 Ollama Cloud | 使用者反映 Anthropic API 費用過高，Ollama Cloud 已有訂閱 |
| 模型選擇 | ① deepseek-v4-flash ② deepseek-v4-pro ③ llama4 | 先 flash 後 pro | 使用者指定 flash 開局，卡住後改 pro 驗證差異 |
| flash 卡住後的行動 | ① 等自然結束 ② 中斷寫報告 ③ 換模型重跑 | 中斷後換 pro 重跑 | flash 已卡 1.5 小時，繼續等無意義 |
| Deep Mode 是否執行 | ① 照計畫執行 ② 跳過 | 跳過，改為 pro 版 Quick Mode | Ollama Cloud session limit 無法支撐 Deep Mode (>100M tokens) |
| 執行環境 | ① M4 Mac 本機 ② fh-l 遠端 | fh-l 遠端 | M4 Mac 網路差，Docker image 無法下載 |
| 結果彙整方式 | ① 只用一組結果 ② 合併兩組結果 | 合併兩組 | flash 與 pro 發現的漏洞重疊率僅 40%，合併可得到更完整圖像 |
