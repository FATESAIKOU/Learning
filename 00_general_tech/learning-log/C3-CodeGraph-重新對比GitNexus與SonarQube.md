# CodeGraph-C3-重新對比GitNexus與SonarQube

## 狀況理解
使用者指出第一次比較時誤將「gitnexus」理解為 Sonatype Nexus 而非 GitNexus（https://github.com/abhigyanpatwari/GitNexus）。User 明確指出後，需重新調研 GitNexus，並與 CodeGraph、SonarQube 做正確的三方對比。GitNexus 是一個面向 AI agent 的 zero-server code intelligence engine（40.8k stars），與 CodeGraph 在同一問題域中，而 SonarQube 則是完全不同的問題域（SAST）。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 GitNexus GitHub repo README | 取得 GitNexus 完整定位、功能列表、安裝方式、支援 agent、兩模式（CLI+MCP / Web UI）說明 | 理解 GitNexus 與 CodeGraph 的核心差異 | 取得完整 README，含 16 MCP tools、4 agent skills、Leiden community detection、process extraction、group/contract bridge、hybrid search、hooks 整合等細節 |
| 讀取 GitNexus ARCHITECTURE.md | 深入了解 12-phase pipeline DAG、LadybugDB schema、call-resolution DAG（6-stage）、scope-resolution pipeline（RFC#909） | 取得與 CodeGraph 4-stage pipeline 的對比基礎 | 取得 12-phase DAG（scan→structure→markdown→cobol→parse→routes→tools→orm→crossFile→mro→communities→processes）、44 node types + 21 relationship types、3-tier name lookup + MRO walk、C3 linearization、scope-resolution pipeline for C#/Python 細節 |
| 讀取 GitNexus package.json | 了解技術堆疊 | 確認框架選型 | TypeScript monorepo（gitnexus/ + gitnexus-web/ + gitnexus-shared/），PolyForm Noncommercial license |
| 重新閱讀 CodeGraph 報告現有內容 | 確認要替換的部分準確 | 確保編輯範圍正確 | 報告原有 section 5 比較 CodeGraph vs SonarQube vs Sonatype Nexus（後者不正確），需替換為 CodeGraph vs GitNexus vs SonarQube |
| 替換分析報告 section 5 | 將錯誤對比資訊替換為正確的三方對比 | 使用者能獲得 CodeGraph/GitNexus/SonarQube 的正確定位區分 | 完成替換：含定位圖、13維度完整對比表、CodeGraph vs GitNexus 核心差異詳析、使用場景對比、可否互補搭配分析 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| GitNexus 核心機制理解 | 對比 README + ARCHITECTURE.md 的一致性 | 一致：12-phase DAG（含 tree-sitter parsing、Leiden community detection、process extraction）、LadybugDB graph DB、BM25+vector hybrid search、MCP tools/skills/hooks/resources 完整覆蓋 |
| GitNexus 與 CodeGraph 定位差異 | 對比兩者的 pipeline 階段、圖資料深度、MCP 工具數、agent 整合層級 | GitNexus 是 CodeGraph 的功能超集：更深圖資料（44 vs 20 node types）、更多工具（16 vs 10）、agent hooks + skills + prompts、Leiden communities + processes + group/contract bridge。CodeGraph 更輕量、auto-sync 原生化、install 更簡單 |
| GitNexus 與 SonarQube 定位差異確認 | 確認兩者問題域 | 無重疊：GitNexus 解決「agent 理解程式碼架構」；SonarQube 解決「程式碼品質與安全審查」 |
| 報告替換完整性 | 確認 section 5 已完整替換且不殘留 Sonatype Nexus 內容 | 舊 Sonatype Nexus 內容已完全移除，新 section 5 含定位圖、13維度對比表、CodeGraph vs GitNexus 核心差異表、場景對比、可否互補建議 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 比較框架選擇 | 1. 僅比較 CodeGraph vs GitNexus；2. 同時比較 CodeGraph vs GitNexus vs SonarQube | 2. 三方同時比較 | 使用者一開始要求比較「CodeGraph vs SonarQube/gitnexus」，經澄清 gitnexus=GitNexus 後，仍應保留 SonarQube 作為不同維度的對照，避免報告僅限於同質比較 |
| GitNexus 描述深度 | 1. 僅從 README 層次；2. 深入 ARCHITECTURE.md 的 pipeline/schema/resolution 細節 | 2. 深入 ARCHITECTURE.md | GitNexus 與 CodeGraph 屬於同一問題域，需要同等深度的技術細節才能做出有意義的差異對比 |
| CodeGraph vs GitNexus 關係定性 | 1. 「競爭對手」；2. 「GitNexus 是 CodeGraph 的功能超集」；3. 「可互補」 | 2. 「GitNexus 是功能超集，通常二選一」 | GitNexus 涵蓋了 CodeGraph 的核心能力（tree-sitter parsing/圖查詢/MCP）並額外增加 communities/processes/group/embed/rename/skills/hooks，兩者為同一問題域的工具，通常擇一而非並存 |
| SonarQube 在新報告中的位置 | 1. 移除 SonarQube；2. 保留並調整重點 | 2. 保留作為不同維度對照 | SonarQube 是 user 原始要求中的一部分，且作為 SAST 代表能清楚展示「code intelligence」與「code quality」是兩個獨立維度 |
