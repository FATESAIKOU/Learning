# CLI-Anything 分析報告

> 分析日期：2026-05-31（revised with counterfactual analysis）
> 專案倉庫：https://github.com/HKUDS/CLI-Anything (HKUDS, 41.4k stars)

---

## 1. 這個技術解決什麼問題？

**AI Agent 無法直接操作缺乏結構化 API 的桌面軟體。**

CLI-Anything 提供一套標準化方法論與工具鏈，將任意 GUI 軟體轉換為 AI Agent 可直接調用的 CLI 工具。

### 被解決的具體問題：

| 問題面向 | 具體描述 |
|---------|---------|
| **操作介面不匹配** | Agent 的文字推理能力 vs GUI 的視覺/點擊操作 |
| **缺乏結構化介面** | 大多數桌面軟體沒有 machine-readable API |
| **Agent 無法做視覺回饋閉環** | Agent 無法看見渲染結果、無法迭代修正 |
| **社群生態碎片化** | 每個 Agent 平台各自為政，缺乏統一的軟體操作標準 |
| **跨軟體預覽格式不一致** | 不同軟體的預覽/中間輸出格式不統一 |

### 反面論證：這個問題的範圍被誇大了嗎？

**論點 1：這個問題僅存在於軟體缺乏結構化 API 時。** 對於 Web-based 工具（Figma、Google Docs、Notion），它們普遍提供 REST API 或已有完整的 MCP/Playwright 整合。對這些情境導入 CLI-Anything 的 7-phase SOP + Preview Protocol + CLI-Hub 生態鏈屬於 overengineering。

**論點 2：問題的真實規模可能小於專案聲稱。** 在 GitHub issue tracker 中，目前 open issue 僅 27 個，open PR 29 個，其中多數是新 harness 的提交而非 bug 修復。這表明實際使用者在生成 harness 後的「使用與維護」階段的回饋量並不高——可能是因為生成的 CLI 品質不足以進入生產使用，或者使用者基數尚未達到自驅動的社群規模。

**論點 3：問題的定義隱含了「Agent 必須透過 CLI 操作軟體」的前提。** 這個前提本身有爭議：如果 Agent 直接透過軟體的原生 API/SDK 操作（例如直接調用 Blender Python API、直接使用 LibreOffice UNO），則不需要 CLI 中間層。CLI-Anything 額外增加了一層 Python Click CLI 包裝，引入了額外的維護負擔與故障面。

**論點 4：適用範圍受限於軟體能否被分析。** 對於閉源且無公開 API/SDK 的軟體，Phase 1 的原始碼分析無法執行，整個方案失效。專案中已收錄的非開源軟體（Zoom、iTerm2、Safari、NotebookLM）依賴的是公開 API/SDK 而非原始碼分析，這與 `/cli-anything ./gimp` 的標準流程有本質差異。

### 收斂結論

問題真實存在，但範圍被敘事放大。CLI-Anything 的適用領域核心是 **「具備 headless/scripting 模式的桌面軟體」**——這是一個真實但有限的問題空間。對於已有良好 API 的 Web 服務或原生支援 CLI 的工具，此方案為 overengineering。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景因素

- **CLI 是 Agent 的通用介面**：文字命令與 LLM 的 token-based 推理匹配
- **Claude Code 已證明 CLI 可行性**：每天執行數千個真實工作流
- **GUI 軟體通常有 CLI/Headless 模式但未被結構化封裝**：LibreOffice `--headless`、Blender `--background --python`、GIMP `-i -b` 等底層介面對於 Agent 過於原始
- **現有軟體的設計目標是人類而非 Agent**：GUI 操作映射為底層 API 需被標準化

### 通用技術背景（補充）

| 背景因素 | 說明 |
|---------|------|
| **LLM Token 介面限制** | LLM 的輸入僅限文字/圖片 token，無法直接產生滑鼠事件或接收 GUI 事件流 |
| **MCP / Function Calling 的興起** | Agent 生態正快速向結構化工具呼叫收斂 |
| **Headless 渲染的普及** | 現代軟體普遍支援 headless 模式（CI/CD 驅動） |
| **PEP 420 namespace package** | 多個獨立 PyPI 包可共存於同一 `cli_anything` 命名空間下 |

### 反面論證：背景因素的弱點與遺漏

**論點 1：「CLI 是 Agent 通用介面」的前提不完整。** 這個論述預設 Agent 的最佳互動模式是文字 CLI。然而 MCP 的結構化 JSON tool call、直接 SDK 呼叫、甚至 vision-based 截圖分析也是可行的互動模式。CLI 作為通用介面的優勢需要依情境評估，不是絕對命題。

**論點 2：Headless 模式的存在不能推導出「Agent 化」的必要性。** 軟體有 headless 模式（如 LibreOffice `--headless`）說明它已經可以被 CLI 腳本呼叫，但這些軟體的使用者主要是人類透過 GUI 互動。Agent 是否需要一個「額外的 CLI 包裝層」來調用這個 headless 模式本身就有爭議——直接呼叫 `libreoffice --headless --convert-to pdf file.odt` 已經是有效的 Agent 操作，不需要 `cli-anything-libreoffice document export render` 的多層抽象。

**論點 3：專案強調「軟體為人類設計」作為問題根源，但迴避了「誰應該負責提供機器介面」的責任歸屬。** 傳統上，軟體開發者（不是第三方 Agent 工具鏈開發者）應該負責提供結構化 API。CLI-Anything 將這個責任轉移到 Agent 與社群上，造成了生成品質不可控、上游更新後 harness 可能失效等維護問題。

**論點 4：生態碎片化是真實但有限的問題。** Claude Code 的 plugin、Pi 的 extension、Codex 的 skill、Opencode 的 command——這些確實是不同的整合點。但 CLI-Anything 並未解決碎片化，而是增加了一個新的統一層：它使每個 Agent 平台都必須實作對 CLI-Anything 的支援。這將碎片化問題從「各平台與各軟體的整合」轉為「各平台與 CLI-Anything 的整合」，僅是轉移了問題層級，未根本解決。

### 收斂結論

背景因素真實存在，但 CLI-Anything 對這些因素的回應存在邏輯跳躍：headless 模式的存在不代表需要一個額外的 CLI 包裝層；軟體設計以人類為中心不代表第三方應負擔機器介面的建構責任。專案的背景立論將「CLI 是通用介面」的陳述過度絕對化。

---

## 3. 這個技術是如何解決該問題的？

CLI-Anything 提供一個 **7 階段的標準作業程序（SOP）**，由 AI Agent 執行，將任意 GUI 軟體轉換為結構化 CLI 工具。

### 核心機制圖示

```
軟體原始碼/文檔
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: 程式碼分析                                  │
│  - 找出核心引擎/後端（如 Shotcut→MLT, GIMP→Script-Fu） │
│  - 映射 GUI 操作 → API 呼叫                           │
│  - 識別資料模型（XML/JSON/二進位）                      │
│  - 找出既有 CLI 工具（如 melt, ffmpeg, convert）        │
│  - 約束：需有可分析的原始碼或公開文檔；閉源+無API→不可行  │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2: CLI 架構設計                                │
│  - 互動模式：Stateful REPL + Subcommand CLI           │
│  - 命令分組：專案管理 / 核心操作 / 匯入匯出 / 設定 / 狀態 │
│  - 狀態模型：in-memory (REPL) + file-based (CLI)      │
│  - 輸出格式：人類可讀 + --json 機器輸出                 │
│  - 盲點：Agent 自行設計命令分組，無人機審查設計合理性       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: 實作                                       │
│  - 資料層：直接操作原生格式（MLT XML, ODF, SVG, .blend）│
│  - 後端層：utils/<軟體>_backend.py 包裝真實軟體的 CLI    │
│  - 渲染層：產生有效中間檔 → 呼叫真實軟體渲染              │
│  - REPL 層：統一 ReplSkin 介面 + prompt_toolkit        │
│  - Session 管理：undo/redo + 檔案鎖定                  │
└────────────────────────┬────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────────┐
│ Phase 4    │  │ Phase 5    │  │ Phase 6        │
│ 測試計畫   │  │ 測試實作   │  │ 測試文件       │
│ TEST.md    │  │ unit+E2E   │  │ (寫入結果)     │
│ (先寫計畫) │  │ +subprocess│  │                │
└────────────┘  └────────────┘  └────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 6.5: SKILL.md 產生                            │
│  - AI-discoverable skill 定義（YAML frontmatter）     │
│  - npx skills add HKUDS/CLI-Anything --skill <name>  │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Phase 7: PyPI 發布                                  │
│  - PEP 420 namespace package (cli_anything/<軟體>/)  │
│  - pip install cli-anything-<軟體>                   │
│  - 註冊至 registry.json / public_registry.json       │
└─────────────────────────────────────────────────────┘
```

### 使用者輸入的角色：use case 定義到 Agent 開發的流程

```
觸發階段（一次性）：
  /cli-anything ./gimp
  → Agent 分析 GIMP 完整程式碼/文檔
  → Agent 自動設計並實作包含「所有可發現操作」的 CLI
  → 使用者未定義 use case，Agent 自行決定覆蓋範圍

迭代階段（可重複）：
  /cli-anything:refine ./gimp "加強圖片批次處理與濾鏡"
  → Agent 比較軟體完整能力 vs 當前 CLI 覆蓋率（gap analysis）
  → 加入使用者指定的 use case 相關命令
  → 增量更新，不破壞既有命令

未解決的缺失：
  - 初始階段無 use case 輸入，Agent 可能：
    ✓ 產生使用者不需要的命令（覆蓋率過廣）
    ✗ 遺漏使用者真正需要的命令（無需求導向的優先級）
  - refine 只能「增量補充」而非「刪減無用命令」
  - 使用者必須在事後（而非事前）參與需求定義
```

### 本質分析：是否為「將整個介面開發外包給 Agent」

```
┌──────────────────────────────────────────────────────────────────┐
│  傳統軟體開發分工                                                  │
│  ─────────────                                                    │
│  人類 PM：定義需求、use case                                       │
│  人類 Developer：分析 API、設計介面、撰寫實作、寫測試               │
│  人類 QA：驗證功能完整性                                           │
│                                                                  │
│  CLI-Anything 模式                                                │
│  ────────────────                                                 │
│  人（觸發）：/cli-anything ./gimp                                  │
│  Agent（需求定義）：Phase 1 掃描程式碼 → 推斷「需要哪些命令」        │
│  Agent（架構設計）：Phase 2 設計命令分組與狀態模型                   │
│  Agent（實作）：Phase 3 撰寫 Python Click CLI 程式碼                │
│  Agent（測試）：Phase 4-6 撰寫 unit + E2E 測試並執行                │
│  Agent（文件）：Phase 6.5 產生 SKILL.md                            │
│  Agent（發布）：Phase 7 PyPI 打包                                  │
│  ─────────────────────────────                                    │
│  人類角色：觸發者 + 事後 refine 的指導者                            │
│  Agent 角色：PM + Developer + QA + DevOps                          │
│                                                                  │
│  本質：將「需求定義 → 架構設計 → 實作 → 測試 → 發布」全鏈路        │
│        交由 Agent 獨立完成，人類僅在觸發與 refine 階段介入。         │
│        這就是「把整個介面開發外包給 Agent」。                        │
└──────────────────────────────────────────────────────────────────┘
```

### 關鍵技術決策

#### 1. 必須使用真實軟體渲染（#1 規則）

```
✅ 正確做法（HARNESS.md 規範）：
   1. 產生有效的中間檔（ODF, MLT XML, .blend-cli.json, SVG）
   2. 呼叫真實軟體進行渲染
   3. 程式化驗證輸出（magic bytes, ZIP 結構, pixel-level 分析）

❌ 反模式（HARNESS.md 明確禁止）：
   用 Pillow 模擬 GIMP、用 ffmpeg concat 丟棄濾鏡效果
```

#### 2. 預覽協議（Preview Protocol）

```
Preview Bundle (preview-bundle/v1)
  ├── manifest.json    (機器契約)
  ├── summary.json     (人類/Agent摘要)
  └── artifacts/
      ├── hero.png     (主力預覽圖)
      ├── gallery_*.png
      ├── preview.mp4
      └── pipeline_diff.json

Live Session:
  session.json     ← 可變的當前頭
  trajectory.json  ← 不可變的 append-only 命令→預覽歷史
```

#### 3. 生態系統架構

```
CLI-Hub (cli-hub)
├── pip install cli-anything-hub
├── list / search / info / install / update / uninstall / launch
└── previews inspect / html / watch / open

cli-anything-plugin (SOP 文件與 Agent 整合)
├── Claude Code: /cli-anything <path>
├── Pi: .pi-extension/cli-anything/
├── OpenClaw / OpenCode / Codex / Qodercli

Skills (repo-root skills/)
└── npx skills add HKUDS/CLI-Anything --skill <name> -g -y
```

### 反面論證：解決方案的根本缺陷

**缺陷 1：Phase 1 的原始碼分析依賴不現實。** `/cli-anything ./gimp` 假設 GIMP 原始碼目錄在本地可用且結構良好。實際上，大型開源專案（GIMP、Blender、LibreOffice）的原始碼結構複雜，Agent 能否正確分析並映射 GUI 操作到 API 是一個未被證實的假設。HARNESS.md 未提供任何關於 Phase 1 分析正確率的數據或驗證方法。

**缺陷 2：額外的 CLI 抽象層增加了延遲與複雜度。** 以 LibreOffice 為例：

```python
# 直接呼叫（無 CLI-Anything 時 Agent 也可以這樣做）：
subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", file.odt])

# 透過 CLI-Anything（增加了多層中間轉換）：
cli-anything-libreoffice document new --type writer
cli-anything-libreoffice writer add-heading -t "Title"
cli-anything-libreoffice export render output.pdf -p pdf --overwrite
```

對於已支援 headless 模式的軟體，CLI-Anything 額外引入的 Click CLI 層、ReplSkin、session 管理等機制並非必要，反而增加了維護負擔。

**缺陷 3：生成的 CLI 品質不可控。** 60+ harness 由不同的 Agent 或社群貢獻者生成。雖然有 HARNESS.md 的規範約束和社群 PR review，但沒有機制保證每個 harness 的命令覆蓋率、正確性或設計一致性。不同 harness 的品質可能差異極大。

**缺陷 4：Preview Protocol 的複雜度超出多數情境所需。** bundle/session/trajectory 的三層模型、manifest.json 的豐富欄位、live session 的 poll-first 機制——這些對於僅需要「產生一個截圖給 Agent 看」的情境而言是過度設計。

**缺陷 5：上游軟體更新時 harness 的維護責任不明。** GIMP 3.0 改變 Script-Fu API 時，`cli-anything-gimp` 誰來更新？Blender 4.0 改變 Python API 時，`cli-anything-blender` 誰來修？CLI-Anything 專案本身未定義 harness 的生命週期管理策略。這使生成的 CLI 面臨快速朽化的風險。

### 收斂結論

CLI-Anything 的技術方案在「讓 Agent 能夠呼叫桌面軟體」的目標上是可行的，但方案引入的多層抽象（Click CLI 包裝層 + ReplSkin + session + Preview Protocol + CLI-Hub）中，部分層次是 overengineering。對於已有 CLI/headless 模式的軟體，直接呼叫底層命令比透過 CLI-Anything 更簡潔。此方案最適合的情境是「軟體有 headless 模式但使用極度複雜，Agent 需要一個結構化且有 state management 的高階介面」。

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 決策分析表 (DA Table)

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|---------|-------------|---------------|----------------|
| **CLI-Anything** | Agent 遵循 7-phase SOP，自動生成 Python Click CLI + REPL，包裝軟體的 headless 模式 | 目標軟體有 headless/scripting 介面或被分析的原始碼/文檔；Python 3.10+；支援的 AI Agent 平台 | 每個軟體獨立生成並維護 harness；依賴真實軟體安裝（硬依賴）；生成品質取決於 Agent 分析能力；增加中間抽象層、額外維護負擔 | Agent 可透過文字命令操作桌面軟體；產生真實渲染輸出；支援預覽、session、undo/redo |
| **MCP (Model Context Protocol)** | 軟體開發者手動實作 MCP Server，定義 tools，Agent 透過 MCP Client 呼叫 | 軟體開發者需手動實作 MCP Server；需遵循 MCP 規範 | 每個軟體需開發者手動撰寫 server；工具定義可能不完整 | Agent 透過標準化協議呼叫軟體功能；工具定義具型別安全 |
| **Browser Use / Playwright MCP** | Agent 透過瀏覽器自動化操作 Web-based GUI，使用 DOM 選擇器定位元素 | 目標軟體必須是 Web-based；需要瀏覽器 | 依賴 DOM 穩定性（UI 改版失效）；視覺定位不可靠；無法操作原生桌面軟體 | Agent 可操作 Web 應用 GUI；適合 SaaS |
| **Direct API / SDK 呼叫** | Agent 直接調用軟體的原生 API（Blender Python API、LibreOffice UNO、GIMP Script-Fu） | 軟體有公開的程式化 API/SDK | Agent 需要深入理解特定 API；不具跨軟體統一性；無預覽/測試自動化 | 最直接高效的 Agent-軟體互動路徑；零中間層開銷 |
| **Open Interpreter** | LLM 在本地執行任意程式碼，由 LLM 自行撰寫腳本操作軟體 | LLM 了解軟體的程式化 API；需要 sandbox | LLM 生成的腳本品質不穩定；無結構化測試；安全風險高 | LLM 快速嘗試調用軟體的 API/CLI；適合探索性任務 |
| **Custom Plugin / API Wrapper** | 人工為特定軟體撰寫 REST API 或 SDK 包裝層 | 需人工開發資源；軟體有 SDK 或內部 API | 開發成本高；僅適用於單一軟體；需持續維護 | 精確可控的軟體操作介面；適合企業級整合 |

### 各方案切入點差異

```
問題：Agent 如何操作軟體？

CLI-Anything ──────► Agent 自動生成 CLI（外包整個開發鏈）
                      前提：軟體有 headless 模式 或 可分析的原始碼
                      代價：增加中間層、品質不可控、維護歸屬不明
                      適合：缺乏 API 的桌面軟體的自動化

MCP ───────────────► 開發者手動定義結構化工具
                      前提：開發者願意投入實作
                      代價：人工成本高
                      適合：開發者維護的重要軟體

Browser Use ───────► DOM 操作 + 視覺模擬
                      前提：目標為 Web-based 工具
                      代價：DOM 脆弱、無法操作原生桌面
                      適合：Web SaaS 的自動化

Direct API/SDK ────► 直接呼叫軟體原生 API
                      前提：軟體有公開 API（如 Blender Python API）
                      代價：無跨軟體統一性
                      適合：對單一軟體深度整合的情境

Open Interpreter ──► LLM 自行生成腳本
                      前提：LLM 了解軟體 API
                      代價：品質不穩定、無結構化保證
                      適合：一次性探索任務

Custom Wrapper ────► 人工開發專用包裝
                      前提：有人工開發資源
                      代價：開發成本高
                      適合：企業關鍵軟體內部署
```

### overengineering 的判定矩陣

```
                      軟體有 REST API / GraphQL    軟體有 CLI/headless     軟體僅有 GUI，無任何 API
                      ────────────────────────    ────────────────────    ────────────────────────
使用 CLI-Anything     Overengineering              過度抽象層               合理選擇（唯一的 Agent 化路徑）
                      （直接調 API 更簡潔）         （直接 call CLI 更簡潔）

使用 MCP              可接受                        可接受                  不可行（無 API 可包裝）
                      （API → MCP 是自然映射）       （CLI → MCP 可行）

使用 Browser Use      可接受                        不適用                  可接受
                      （如已有 Web UI）             （非 Web 軟體）          （GUI → DOM 操作）

使用 Direct API/SDK   最佳選擇                      最佳選擇                不可行
                      （零中間層）                  （零中間層）              （無 API 可用）

使用 Open Interpreter 可接受                        可接受                  風險高但可用
                      （LLM 直接寫 API 呼叫）        （LLM 直接寫 shell）     （LLM 需猜測操作邏輯）
```

判準：CLI-Anything 的 overengineering 程度與「目標軟體的 API 成熟度」成反比。

- API 成熟度高（REST/GraphQL/SDK）→ CLI-Anything 是 overengineering
- 僅有 headless CLI 但操作複雜 → CLI-Anything 提供價值（結構化 + session + preview）
- 僅有 GUI，無任何程式化介面 → CLI-Anything 是唯一可行的 Agent 化路徑（但 Phase 1 可能也無法分析）

### 對軟體工程師的導入意義分析

```
┌─────────────────────────────────────────────────────────────────┐
│ 正向意義                                                         │
│                                                                 │
│  1. 加速原型開發：對於無 API 的桌面工具，可快速取得一個初步可用的   │
│     CLI 包裝，作為後續精煉的起點                                   │
│                                                                 │
│  2. 跨軟體 workflow 整合：透過統一的 CLI 介面 + JSON 輸出，         │
│     可將多個工具串接為 Agent 工作流（如 LibreOffice 產生文件 →     │
│     GIMP 裁切圖片 → Shotcut 組裝影片）                            │
│                                                                 │
│  3. 測試自動化：Phase 4-6 的自動測試生成降低了 CI/CD 整合門檻      │
│                                                                 │
│  4. Preview Protocol 的 CI/CD 價值：標準化預覽 Bundle 可作為       │
│     CI 中的視覺回歸測試基礎                                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 反向限制                                                         │
│                                                                 │
│  1. 生成的程式碼不是 production-grade：Agent 生成的 Click CLI      │
│     和 ReplSkin wrapper 需要工程師審查、重構和維護                 │
│                                                                 │
│  2. 維護歸屬不明：誰負責在上游軟體更新後更新 harness？              │
│     如果依賴社群貢獻，更新速度無法保證                             │
│                                                                 │
│  3. 學習成本：工程師需要理解 CLI-Anything 生態（7-phase SOP、       │
│     HARNESS.md、Preview Protocol、CLI-Hub、SKILL.md），            │
│     這是一套額外的知識體系                                        │
│                                                                 │
│  4. Vendor lock-in 風險：一旦 workflow 依賴 cli-anything-*         │
│     生態，遷移成本變高                                            │
│                                                                 │
│  5. 對已有良好 API 的軟體是多餘的：工程師直接使用軟體的官方 SDK     │
│     或 API 通常更高效、更可靠                                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 工程師最合理的導入策略                                             │
│                                                                 │
│  1. 先評估目標軟體的 API 成熟度：                                  │
│     - 有 REST API / SDK → 跳過 CLI-Anything，直接整合              │
│     - 有 headless CLI 但操作複雜 → 可考慮 CLI-Anything             │
│     - 無 API + 無 CLI → CLI-Anything 是少數選擇之一                │
│                                                                 │
│  2. 若決定使用 CLI-Anything：                                      │
│     - 利用 /cli-anything 快速生成初始版本                          │
│     - 以 refine 迭代補充                                          │
│     - 將生成的程式碼視為「MVP 原型」而非最終產品                    │
│     - 建立內部 fork 進行品質控制與長期維護                          │
│                                                                 │
│  3. 若 Web-based workflow：直接選用 MCP 或 Playwright，             │
│     不考慮 CLI-Anything                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 補充說明：Preview Protocol 的替代思路

| 方案 | 做法 | 差異 |
|------|------|------|
| 各 CLI 自定義預覽格式 | 每個 harness 自行定義預覽輸出 | 缺乏互操作性，agent 無法統一消費 |
| 即時畫面串流（VNC/RDP）| 將 GUI 畫面即時串流給 agent 判斷 | 頻寬大、延遲高、需 GUI 環境 |
| Screenshot-based 閉環 | Agent 發送指令後截圖、用 vision model 判斷結果 | 視覺判斷不可靠、無法結構化驗證 |
| CLI-Anything Preview Protocol | 標準化 bundle 契約，真實軟體渲染後封裝為 manifest.json + artifacts/ | 需 harness 實作 preview 命令；對簡單情境是 overengineering |
