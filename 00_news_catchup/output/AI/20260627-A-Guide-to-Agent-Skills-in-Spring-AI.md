# 1. A Guide to Agent Skills in Spring AI

**Source**: https://feeds.feedblitz.com/~/958380014/0/baeldung
**Author**: Baeldung
**Date**: 2026-06
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

Agent Skills 解決的是 **輕量級 AI Agent 能力擴展的過度工程化問題**。

在 Spring AI 生態中，要讓 AI Agent 具備呼叫外部工具的能力，標準做法是建立 MCP (Model Context Protocol) Server。但 MCP Server 需要獨立的服務進程、生命週期管理、傳輸層配置，對於以下場景明顯 overkill：

| 場景 | MCP Server 的痛點 |
|------|------------------|
| 單一 Agent 的本地自動化任務 | 需要啟動/維護獨立服務 |
| 簡單的 shell script 或檔案操作 | 需要包裝成 MCP tool 介面 |
| 快速原型驗證 | 基礎設施成本高於業務邏輯 |

Agent Skills 提供了一種 **目錄級別的宣告式能力定義**，讓開發者只需在 `.openai/skills/` 下建立一個含 `SKILL.md` 的目錄，就能讓 Agent 發現並呼叫該能力，無需啟動任何外部服務。

## 2. 這個問題為什麼會發生?(背景)

**MCP 的設計初衷是跨進程/跨網路的工具整合**，而非本地輕量任務。

MCP 協議定義了 client-server 架構，透過 stdio 或 HTTP SSE 傳輸，這對以下場景是合理的：
- 多個 Agent 共享同一組工具
- 工具需要獨立擴展、獨立部署
- 工具提供方與 Agent 開發方是不同團隊

但 Spring AI 2.x 開始支援 Agent 模式後，開發者頻繁遇到「只想讓 Agent 跑一個 Python script 或讀一個本地檔案」的需求。每次都建 MCP Server 的成本（建立專案、配置傳輸、管理生命週期）遠超實際業務邏輯。

Agent Skills 規範的出現，填補了 **「MCP Server 太重、直接寫死 code 太不靈活」** 之間的中間地帶。它本質上是將 Anthropic 的 Agent Skills 開放規範整合進 Spring AI 生態。

## 3. 這個技術/政策是如何解決該問題的?

Spring AI 透過三個 Tool 的組合實現 Agent Skills：

```
ChatClient
  ├── SkillsTool        ← 掃描 .openai/skills/ 目錄，註冊所有 skill 的 name + description
  ├── FileSystemTools   ← 讓 Agent 能讀取 SKILL.md 中的指令與資源檔案
  └── ShellTools        ← 讓 Agent 能執行 skill 中定義的 script（Python/Bash 等）
```

**運作流程**：

1. **註冊階段**：`SkillsTool` 掃描 `.openai/skills/` 下所有子目錄，讀取每個 `SKILL.md` 的 frontmatter（name + description），作為 tool description 提供給 LLM
2. **匹配階段**：使用者發送請求時，LLM 根據所有 skill 的 description 判斷哪個 skill 相關
3. **載入階段**：LLM 透過 `FileSystemTools` 讀取匹配 skill 的 `SKILL.md` 完整內容（含自然語言指令）
4. **執行階段**：LLM 依照指令透過 `ShellTools` 執行 script（如 `uv run scripts/fetch_article.py <url>`），讀取 stdout 作為輸入
5. **回應階段**：LLM 依照 `SKILL.md` 中定義的輸出格式（如 TL;DR / Key Points / Bottom Line）結構化回應

**目錄結構範例**：

```
.openai/skills/
└── article-summarizer/
    ├── SKILL.md          ← frontmatter (name, description) + 自然語言指令
    └── scripts/
        └── fetch_article.py  ← 實際執行的邏輯
```

**SKILL.md 範例**：

```yaml
---
name: article-summarizer
description: Summarizes articles into concise digests.
---
# Article Summarizer
## Instructions
1. If given a URL: Run `uv run scripts/fetch_article.py <url>`
2. Extract main thesis, key points, and conclusion
3. Structure output as TL;DR, key points, and bottom line
```

**關鍵設計決策**：
- Skill 的 description 是 LLM 判斷是否匹配的唯一依據，需精確描述觸發條件
- `ShellTools` 無 sandbox，直接在本地機器執行，需審查 script 內容或容器化
- Skill 支援任意語言的 script（Python/Bash/Node 等），只要執行環境預裝對應 runtime

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 與 Agent Skills 的差異 |
|------|---------|----------------------|
| **MCP Server** (Spring AI 原生) | 多 Agent 共享、跨進程工具 | 需獨立服務，適合正式環境；Agent Skills 適合本地輕量任務 |
| **LangChain Tools** | Python 生態的 Agent 工具 | 以 Python decorator 定義 tool，與 Spring AI/Java 生態不同 |
| **OpenAI Function Calling** | 直接定義 JSON Schema | 無檔案系統/Shell 執行能力，僅定義介面，實作需自行處理 |
| **Anthropic Tool Use** | Claude 原生 tool | 與 Agent Skills 規範同源，但 Spring AI 的實作整合了 FileSystem + Shell |
| **直接寫死 ChatClient 邏輯** | 最簡單的單一任務 | 無重用性，每次改需求要改 code；Agent Skills 是宣告式、可複用 |

**對用戶（Spring+AI 學習中、即將轉管理者）的啟示**：

- Agent Skills 降低了 AI Agent 功能擴展的門檻，適合在 AxrossRecipe 內部快速原型驗證 AI 功能
- 從 MCP Server 到 Agent Skills 的選擇，本質是 **「基礎設施成本 vs 靈活性」** 的取捨，作為管理者需能判斷何時用哪種方案
- `ShellTools` 無 sandbox 的安全風險，在企業環境中需特別注意，容器化是推薦的 mitigation
- 這個模式與用戶正在學習的 Spring+AI + MCP 直接相關，是 Spring AI 2.x 的關鍵新特性
