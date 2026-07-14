# Strix AI 滲透測試 — 能力邊界分析

> 日期：2026-07-14
> LLM：Ollama Cloud (deepseek-v4-flash / deepseek-v4-pro)
> Strix 版本：1.0.4

---

## 一、掃描執行摘要

| 面向 | Run 1 (flash) | Run 2 (pro) |
|---|---|---|
| Model | `ollama_chat/deepseek-v4-flash` | `ollama_chat/deepseek-v4-pro` |
| Token 消耗 | 42.9M input | 17M input (中斷) |
| 執行時間 | ~24 分鐘 (後卡住) | ~16 分鐘 (後中斷) |
| 漏洞數量 | 8 (1H/7M) | 7 (2C/4M/1L) |
| 終止原因 | Agent hang (sub-agent 持續 waiting) | Ollama Cloud session usage limit |
| 產出品質 | 完整 PoC + CVSS + 修復建議 | 完整 PoC + CVSS + 修復建議 |

---

## 二、Strix 能做到什麼（能力）

### 2.1 自動化 API 偵查

Strix 成功自動發現了目標的多個 API 端點 (`/configs`, `/users/{id}`, `/courses`, `/signup`, `/sessions`, `/password_reset`)，無需手動提示。其內部使用的工具鏈 (Caido Proxy + Playwright Browser + nuclei scanner) 能有效進行攻擊面映射。

### 2.2 多類型漏洞檢測

Strix 在 Quick Mode 下成功識別了以下漏洞類型：

| 漏洞類型 | 是否檢出 | 備註 |
|---|---|---|
| CSRF | 是 | 發現 3 個 CSRF 端點 |
| Information Disclosure | 是 | /configs, /users, /courses |
| Open Redirect | 是 | NextAuth callbackUrl |
| User Enumeration | 是 | /users/{id} |
| Input Validation | 是 | Registration bypass (pro only) |
| Rate Limiting | 是 | 所有 auth 端點 |
| Race Condition | 是 | Registration TOCTOU (pro only) |
| Weak Password Policy | 是 | (pro only) |
| Injection (SQLi/XSS) | **否** | 未檢出 |
| SSRF | **否** | 未檢出 |
| Auth Bypass | **否** | 未檢出 |

### 2.3 結構化報告產出

每個漏洞皆包含：
- PoC 描述 + 可執行 Python/curl 程式碼
- CVSS 3.x 評分 + 細項拆解
- CWE 分類
- 具體修復建議

---

## 三、Strix 做不到什麼（能力邊界）

### 3.1 高度依賴 LLM 品質 — 不同模型結果差異大

同一目標、同一 scan mode，flash 與 pro 的結果**重疊率僅 ~40%**：

| 類型 | flash only | 重疊 | pro only |
|---|---|---|---|
| 漏洞數量 | 4 | 4 | 3 |

- flash 發現了 `/configs` 資訊洩漏（HIGH）和 `/courses` 洩漏，pro 完全沒發現
- pro 發現了 Registration Bypass（CRITICAL）和 Race Condition（LOW），flash 完全沒發現
- 嚴重度判斷也不同：flash 評 Rate Limiting 為 MEDIUM（CVSS 5.3），pro 評為 CRITICAL（CVSS 8.6）

**結論**：Strix 的結果極大取決於底層 LLM。單一模型掃描會產生漏報。實際上需要多模型交叉驗證。

### 3.2 Ollama Cloud API 不是 Strix 官方支援的 Provider

Ollama 在 Strix 中被歸類為 "Local Models"，官方明確警告：**「Most local models struggle with complex agentic tasks」**。

本次實測遇到的具體問題：
- **Flash 模型**：sub-agent 陷入永久 waiting 狀態，無法完成多步驟 tool calling 鏈
- **Pro 模型**：出現 5 次連續 streaming retry 後恢復，但最終因 session usage limit 被切斷
- 兩次掃描都沒有**正常完成** Quick Mode（理論上應在 5-15 分鐘內結束），都是在異常狀態下終止

### 3.3 Token 消耗失控 — Quick Mode 吃掉 17M~43M tokens

| 指標 | 數值 |
|---|---|
| Flash Quick Mode | 42.9M input tokens |
| Pro Quick Mode | 17M input tokens（中斷時） |
| 預期 Quick Mode | ~5M~10M tokens |

Strix 官方建議用 `gpt-5.4` 或 `claude-sonnet-4-6`。使用非推薦模型時，Agent 可能會做大量無效推理，導致 token 消耗爆炸。對於 `deepseek-v4-flash` 而言，42.9M tokens 卻沒完成 Quick Mode scan，效率極低。

### 3.4 誤報風險 — PoC 未手動驗證

Strix 產出的 PoC 程式碼是 AI 生成的，**未經實際測試環境驗證**。例如：
- `vuln-0001` (CSRF on Registration)：PoC 說 `{"result":"success"}`，但如果該 email 已被 flash scan 中的 CSRF test 註冊過，實際結果可能是 email duplicate error 而非 CSRF 成功
- PoC 中的 `csrf_test@test.com` 等測試用 email 可能在第一次掃描中已被消耗

### 3.5 Caido Proxy 穩定性問題

兩次掃描都出現 `strix.tools.proxy.tools: view_request failed` 和 `Connector is closed` 錯誤。這是 Strix 內部的 HTTP proxy 工具不穩定，可能影響對需要攔截/修改 HTTP 流量的測試（如 CSRF 深度測試）。

### 3.6 無認證測試（Black-box 限制）

本次為黑箱掃描（無帳號）。Strix 支援 `--instruction "Use credentials: user:pass"` 的灰箱測試，但未測試。黑箱掃描無法檢測：
- 已登入後的權限提升 (IDOR 深度)
- Session 管理漏洞
- 商業邏輯漏洞（如付款流程）
- 內部 API 端點

### 3.7 Ollama Cloud 的 Session Usage Limit

```
you (tsungfuchiang) have reached your session usage limit
```

Ollama Cloud 的免費/低價方案有 session 用量上限。一次 Quick Mode 掃描就耗盡了配額。Strix 的 Deep Mode 預計消耗 50M~200M tokens，在 Ollama Cloud 上根本無法完成。

---

## 四、模型對比矩陣

| 評估面向 | deepseek-v4-flash | deepseek-v4-pro |
|---|---|---|
| 漏洞發現數量 | 8 | 7 (中斷前) |
| CRITICAL 發現 | 0 | 2 |
| Token 效率 | 低 (42.9M / 8 vulns = 5.4M/vuln) | 中 (17M / 7 vulns = 2.4M/vuln) |
| Agentic 穩定性 | 差（sub-agent hang） | 中（streaming retry 後恢復） |
| 發現獨特漏洞 | /configs, /courses disclosure | Registration bypass, race condition, weak password |
| 適合 Strix？ | 否 | 勉強可用但不穩定 |

---

## 五、最終結論

### Strix 的使用前提

| 條件 | 本次是否滿足 |
|---|---|
| Docker 環境 | 是 (fh-l) |
| 官方推薦 LLM (GPT-5.4 / Claude-4.6) | **否** — 使用 Ollama Cloud deepseek |
| 穩定的 API 連線 | **否** — streaming retry / usage limit |
| 充足的 token 預算 | **否** — Ollama Cloud 配額不足 |

### 一句話總結

**Strix 是有潛力的工具，但它對底層 LLM 的依賴極深。使用非官方推薦的 LLM provider (Ollama Cloud + deepseek 系列) 會遇到：agent 卡死、streaming 不穩、token 消耗爆炸、用量上限中斷。產出的報告有參考價值，但需要人工交叉驗證。**

### 若要用 Strix 做正式滲透測試的必要條件

1. 使用 OpenAI GPT-5.4 或 Anthropic Claude Sonnet 4.6（官方推薦模型）
2. 準備 100M~500M token 預算（Deep Mode）
3. 執行至少 2 次不同模型的掃描做交叉驗證
4. 人工驗證所有 PoC
5. 搭配灰箱測試（提供測試帳號）
