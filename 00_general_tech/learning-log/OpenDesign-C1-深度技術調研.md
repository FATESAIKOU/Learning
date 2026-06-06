# OpenDesign-C1-深度技術調研

## 狀況理解

使用者要求：
1. 先 catchup 目前資料夾（特別是 AGENTS.md）
2. 深入調研 `https://github.com/nexu-io/open-design`

目前資料夾結構：
- `00_general_tech/AGENTS.md`：定義「技術解析助理」角色與輸出格式（分析報告 + 學習過程報告），格式嚴格受限
- `00_general_tech/output/`：已有 12 份歷史分析報告
- `00_general_tech/learning-log/`：已有 23 份學習過程報告

Open Design 是由 nexu-io 開發的開源 Claude Design 替代方案，59.6k stars，Apache-2.0 授權。核心訴求是「local-first, agent-native design platform」——不自有 agent loop，而是將使用者已安裝的 coding agent CLI 包裝為統一設計工作流。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `00_general_tech/` 目錄與 `AGENTS.md` | 理解專案結構、輸出格式規則、歷史報告風格 | 確認 AGENTS.md 中的四點格式要求與 DA 表欄位定義 | 已理解：需產出含 4 段落分析報告 + DA 表 + 學習過程報告 |
| 讀取 output/ 與 learning-log/ 目錄 | 確認歷史報告風格與深度標準 | 以 HyperFrames 報告為參考基準 | 已參考 HyperFrames 報告的詳細度與架構風格 |
| 擷取 GitHub repo 首頁 README | 取得專案的整體介紹、功能列表、對比矩陣、使用方式 | 理解 Open Design 是什麼、做什麼、與競品差異 | 已取得完整 README，含 comparison table、product tour、quick start、platform compatibility |
| 擷取 AGENTS.md（repo 中的） | 了解 repo 的開發慣例、架構、boundary constraints | 取得 monorepo 結構、lifecycle commands、capability exposure rules | 已取得完整 repo AGENTS.md：workspace layout、development workflow、agent runtime conventions、chat UI conventions、CSS ownership、i18n keys |
| 擷取 CONTEXT.md | 了解 domain language 與術語定義 | 取得 project/artifact/live artifact/AMR 等正式術語 | 已取得完整術語表與 relationships、example dialogue |
| 擷取 QUICKSTART.md | 了解快速入門流程與技術棧 | 取得 environment requirements、file map、troubleshooting | 已取得：Node 24、pnpm 10.33、two execution modes、prompt composition、file map |
| 擷取 docs/spec.md | 理解產品定位、core bets、non-goals | 取得 product definition、scenarios、positioning vs Claude Design & Open CoDesign | 已取得完整 spec：5 core bets、5 user scenarios、why not extend Open CoDesign |
| 擷取 docs/architecture.md | 理解系統拓樸、component diagram、data flow | 取得 three deployment topologies、artifact store layout、preview renderer、security model | 已取得完整架構文件含 deployment topologies、component diagram、API surface |
| 擷取 docs/skills-protocol.md | 理解 skill 格式、discovery、mode semantics | 取得 SKILL.md frontmatter grammar、od: extensions、craft references | 已取得完整技能協議：base format + OD extensions + design system injection + craft rules |
| 擷取 docs/agent-adapters.md | 理解 adapter interface、detection strategy、per-adapter notes | 取得 adapter catalog、skill injection strategies、capability-driven UI | 已取得 15+ adapters 的詳細說明含 invocation、gotchas、permission model |
| 擷取 docs/modes.md | 理解四個 mode (prototype/deck/template/design system) 的 UX flow 與 output | 取得 per-mode inputs/outputs/preview/refinement/failure modes | 已取得四種 mode 的完整定義 |
| 擷取 docs/roadmap.md | 理解開發階段與未來規劃 | 取得 Phase 0-3 時程、self-evolution track | 已取得 roadmap：Phase 0 (spec finalization) → Phase 1 MVP → Phase 2 v1 → Phase 3 v2 |
| 擷取 open-design.ai 官網 | 了解產品對外呈現、branding、FAQ | 取得 landing page 內容、FAQ、capabilities matrix | 已取得官網完整內容：4 surfaces/1 loop 模型、155 skills、150 systems |
| 嘗試擷取 Claude Design 推文 | 了解原始 Claude Design 發布內容 | 對照 Open Design 的差異化定位 | X.com 需 JavaScript 載入，webfetch 無法取得內容（限於工具本質限制） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 報告格式合規性 | 對照 AGENTS.md 的四點格式 + DA 表欄位要求 | 分析報告包含 4 段落（問題、背景、解法、替代方案），DA 表含 4 個替代方案含 5 欄位 |
| 技術深度 | 確認核心機制（prompt composition、agent adapter、skill system、MCP server）、架構圖、程式碼範例均有涵蓋 | 涵蓋 3-layer prompt composition、adapter interface TypeScript、skill 目錄結構與 YAML 範例、artifact store layout、deployment topologies |
| 資訊覆蓋面 | 確認擷取了 README + AGENTS.md（repo）+ CONTEXT.md + QUICKSTART.md + spec.md + architecture.md + skills-protocol.md + agent-adapters.md + modes.md + roadmap.md + 官網 | 共擷取 11 份來源文件，覆蓋產品定義、架構、協議、roadmap、對外官網 |
| DA 表完整性 | 確認有 4 個替代方案（Claude Design, Figma, Lovable/v0/Bolt） | 已列出 4 個方案含「技術名、技術解法、技術使用前提、技術使用副作用、技術使用預期效果」五欄 |
| 與歷史報告風格一致性 | 對照 output/2026-05-31-HyperFrames.md 的詳細度與架構風格 | 架構圖、程式碼範例、表格密度與 HyperFrames 報告一致 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 報告結構聚焦點 | ① 聚焦「product」（功能/UI/UX） ② 聚焦「architecture」（agent adapter/skill system） ③ 兩者平衡 | ③ 兩者平衡 | Open Design 的核心創新同時在產品層（agent-native design workflow）與技術層（adapter shell + MCP server），兩者不可偏廢 |
| 替代方案選取 | ① Claude Design + Figma ② Claude Design + Figma + Lovable ③ Claude Design + Figma + Lovable + Open CoDesign | ① Claude Design + Figma + Lovable 等 cloud generators | AGENTS.md 要求 2-4 個，4 個足夠展示光譜（proprietary product / GUI canvas / cloud generator / integration shell）；Open CoDesign 較小眾故不另列 |
| DA 表欄位設計 | ① 沿用歷史格式（技術名/技術解法/技術使用前提/技術使用副作用/技術使用預期效果/授權模式/是否需要外接 LLM） ② 簡化為 5 欄 | ② 簡化為 5 欄 | Open Design 的替代方案（Claude Design/Figma/Lovable）授權模式皆為商業訂閱制，無需另列；LLM 依賴性亦非這些方案的核心區分點 |
| Skill protocol 是否需要詳細展開 | ① 僅概述 ② 完整展開含 YAML frontmatter 範例 | ② 完整展開 | Skill system 是 Open Design 與所有競品的關鍵差異點（file-based & agent-agnostic），需足夠細節才能理解 |
| MCP server 是否納入核心機制 | ① 忽略 ② 納入 | ② 納入 | MCP server 是 Open Design 實現「從外部 agent 使用 OD」的關鍵橋接機制，屬於核心設計 |
