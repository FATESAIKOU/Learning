# Strix AI 滲透測試工具 — 學習計畫

> 日期：2026-07-14
> 目標工具：Strix (https://github.com/usestrix/strix)
> 目標網站：https://axross-recipe.com/
> 可用 AI 資源：Ollama Cloud、Claude Pro (Anthropic API)

---

## 一、技術分析

### 1. 這個技術解決什麼問題？

Strix 解決的是「手動滲透測試耗時長、成本高、難以持續執行」的問題。
傳統滲透測試需要專業資安人員花費數天至數周手動探測漏洞，且難以在每次程式碼變更時重複執行。Strix 透過 AI Agent 自動化執行偵查(Recon)、漏洞利用(Exploit)、驗證(Validation) 的完整流程，產出含 PoC 的滲透報告。

### 2. 這個問題為什麼會發生？（背景）

- **手動測試成本**：專業滲透測試人員稀缺，單次測試費用高（數千至數萬美元），且排程需數週。
- **CI/CD 速度需求**：現代開發流程每日部署多次，傳統滲透測試速度無法跟上。
- **SAST/DAST 工具限制**：靜態分析工具誤報率高，缺乏實際利用驗證（PoC）；動態掃描工具覆蓋範圍有限。
- **LLM 技術成熟**：GPT-5.4、Claude Sonnet 4.6 等模型具備足夠的推理能力，能模擬攻擊者思維進行多步驟滲透。

### 3. 這個技術是如何解決該問題的？

- **多 Agent 協作架構**：使用 Graph of Agents 模式，不同 Agent 負責不同階段（偵查、利用、後利用），共享發現結果。
- **Docker 沙箱隔離**：所有滲透行為在 Docker 容器內執行，內建 Caido Proxy、Playwright 瀏覽器、Python 沙箱、終端等完整工具鏈。
- **LiteLLM 抽象層**：支援 100+ LLM Provider（OpenAI、Anthropic、Ollama 等），使用 `provider/model` 格式切換。
- **實際漏洞驗證**：不只掃描，而是實際發動攻擊並產生 PoC，降低誤報率。
- **CLI 輸出**：以文字或 TUI 介面輸出結構化漏洞報告，含 CVSS 評分與修復建議。

---

## 二、AI 加速 Prompt

> 以下 Prompt 可直接貼給支援程式碼生成的 AI，用於快速搭建專案基礎環境或分析掃描結果。

```
You are a cybersecurity expert familiar with Strix (https://github.com/usestrix/strix), 
an open-source AI penetration testing tool.

I need you to:

1. Help me install Strix on macOS (Apple Silicon M4) using:
   - pipx install strix-agent
   OR
   - curl -sSL https://strix.ai/install | bash

2. Help me configure Strix to use Anthropic Claude API:
   export STRIX_LLM="anthropic/claude-sonnet-4-6"
   export LLM_API_KEY="<my-anthropic-api-key>"

3. After I run a scan on a target web app, I will provide you the raw output 
   (from strix_runs/ directory). Your job is to:
   - Parse and summarize all findings
   - Categorize vulnerabilities by OWASP Top 10 category
   - Rate severity (Critical/High/Medium/Low)
   - Extract the PoC (Proof of Concept) for each finding
   - Generate a professional penetration test report in Markdown format

4. Also help me understand what each finding means in plain language, 
   and suggest remediation steps for the development team.

Please confirm you understand before I proceed.
```

---

## 三、Todo Checklist

> 總預計時間：60 分鐘
> 每一步都必須有明確的「產出物」或「驗證標準」

### Phase 1: 環境準備 (預計 10 分鐘)

- [x] **C1. 確認 Docker 運行狀態**
  - 執行 `docker info` 確認 Docker daemon 正常運行。
  - **驗證標準**：輸出 `Server Version: ...` 且無錯誤訊息。
  - **實際結果**：Docker 27.4.1 (local) / 29.2.0 (fh-l)，正常運作。

- [x] **C2. 安裝 Strix CLI**
  - 使用 `pipx install strix-agent` 或 curl 腳本安裝。
  - **驗證標準**：執行 `strix --help` 顯示 CLI 說明。
  - **實際結果**：curl 安裝法成功，Strix 1.0.4 部署於 fh-l。

- [x] **C3. 配置 LLM Provider**
  - 設定 Ollama Cloud 為 LLM backend。
  - **驗證標準**：`echo $STRIX_LLM` 輸出正確 provider/model 格式；`echo $LLM_API_KEY` 顯示已設定。
  - **實際結果**：`ollama_chat/deepseek-v4-flash` 及 `ollama_chat/deepseek-v4-pro`，API 端點 `https://ollama.com`。

### Phase 2: 目標分析與掃描執行 (預計 25 分鐘)

- [x] **C4. 對 axross-recipe.com 進行 Recon（手動資訊收集）**
  - 瀏覽目標網站，記錄：使用的技術棧、表單、登入頁面、API 端點、Cookie/Header 特徵。
  - 產出物：`output/2026-07-14-strix/target-recon.md`（簡易的目標情報筆記）。
  - **實際結果**：完成，識別出 Next.js + Rails API + NextAuth.js 架構。

- [x] **C5. 執行第一次 Strix 掃描（Quick Mode - flash）**
  - 指令：`strix -n --target https://axross-recipe.com --scan-mode quick`
  - **實際結果**：42.9M tokens，8 漏洞 (1H/7M)，因 agent hang 未正常結束。

- [x] **C6. 執行第二次 Strix 掃描（Quick Mode - pro，取代原規劃的 Deep Mode）**
  - 指令：`strix -n --target https://axross-recipe.com --scan-mode quick`（改用 pro 模型）
  - **實際結果**：17M tokens 時 Ollama Cloud session usage limit 中斷，7 漏洞 (2C/4M/1L)。
  - Deep Mode 未執行原因：Ollama Cloud 配額不足，不適合跑 Deep Mode (>100M tokens)。

### Phase 3: 結果分析與報告產出 (預計 20 分鐘)

- [x] **C7. 分析掃描結果**
  - 讀取 `strix_runs/` 下的 JSON/Markdown 輸出。
  - 分類漏洞：依 OWASP Top 10、CVSS 分數。
  - **驗證標準**：能列出至少一個具體的漏洞類別與其 PoC 描述。
  - **實際結果**：11 個獨立漏洞，含完整 PoC、CVSS、CWE 分類。

- [x] **C8. 產出滲透報告**
  - 基於掃描結果，編寫結構化滲透報告。
  - 產出物：`output/2026-07-14-strix/pentest-report.md`。
  - **實際結果**：含 Executive Summary、Findings Table、11 個 Detailed Findings、Risk Matrix。

### Phase 4: 反思與總結 (預計 5 分鐘)

- [x] **C9. 撰寫 Strix 能力邊界分析**
  - 記錄：Strix 掃描到了什麼 / 沒掃到什麼 / 掃描過程中的限制 / AI 判斷準確度 / 與手動測試的差距。
  - 產出物：`output/2026-07-14-strix/capability-boundary.md`。
  - **驗證標準**：至少 3 條具體的能力邊界觀察。
  - **實際結果**：7 條能力邊界觀察，含模型對比矩陣、token 效率分析。
