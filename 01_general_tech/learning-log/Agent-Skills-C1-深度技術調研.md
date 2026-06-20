# Agent-Skills-C1-深度技術調研

## 狀況理解

使用者要求：
1. 閱讀 AGENTS.md 與目前資料夾結構
2. 調研 `https://github.com/addyosmani/agent-skills`

本專案結構：
- 根目錄三個子專案：`00_news_catchup/`、`01_general_tech/`、`02_mvps/`，各自有獨立的 AGENT(S).md 定義角色與輸出格式
- `01_general_tech/AGENTS.md`：定義「技術解析助理」角色，輸出物為「分析報告（output/）」+「分析過程報告（learning-log/）」，報告嚴格 4 點格式含 DA 表
- `01_general_tech/output/`：已有 24 份歷史分析報告（CodeGraph, HyperFrames, DeepSeek-Reasonix 等）
- `01_general_tech/learning-log/`：已有數十份過程報告，檔名規則 `<技術名>-C<自增ID>-<做的事情總結>.md`，每個技術名從 C1 起算

調研對象 addyosmani/agent-skills：
- 作者 Addy Osmani（Google Chrome 團隊）
- 63.5k stars，MIT 授權，Shell 語言標記（實際內容多為 Markdown）
- 定位「Production-grade engineering skills for AI coding agents」
- 24 個 skill + 4 個 agent persona + 5 份 reference checklist + 7 個 slash command

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `00_news_catchup/AGENT.md`、`01_general_tech/AGENTS.md`、`02_mvps/AGENTS.md` | 理解專案結構與三個子專案各自的角色定義 | 確認本次任務適用哪個 AGENTS.md | 確認 `01_general_tech/AGENTS.md` 為本次調研適用格式（4 點分析 + DA 表 + learning-log） |
| 列出根目錄與各子目錄結構 | 理解資料夾組織 | 確認 output/ 與 learning-log/ 既有檔案命名慣例 | 取得 24 份歷史 output 報告與數十份 learning-log，確認檔名規則與 C 編號獨立計算 |
| 讀取 HyperFrames 的 output 報告與 C1/C2 learning-log | 對齊既有報告的實際寫法風格 | 確認 DA 表欄位（含授權模式、是否需外接 LLM）、表格密度、圖示用法 | 確認既有風格：大量表格、ASCII 圖示、嚴格 4 點、DA 表 7 欄（含 HyperFrames 自身列） |
| 透過 gh api 取得 repo metadata | 取得 stars / 授權 / 預設分支 / 更新時間 | 確認 repo 活躍度與基本資訊 | 63.5k stars, MIT, main 分支, 2026-06-20 更新, size 325KB |
| 擷取 raw README.md | 取得整體介紹、命令對應、skill 列表、結構、設計哲學 | 理解 agent-skills 做什麼、怎麼用、為什麼 | 取得完整 README，含 7 命令 × 6 階段對應表、24 skill 列表、anatomy 圖、跨工具載入方式 |
| 擷取 `skills/using-agent-skills/SKILL.md` | 理解 meta-skill 的決策樹與 6 條核心行為 | 取得 task → skill 對應邏輯與跨 skill 共通行為 | 取得完整決策樹 ASCII 圖、6 條 operating behaviors、10 條 failure modes |
| 擷取 `skills/spec-driven-development/SKILL.md` | 理解單一 skill 的內部結構（步驟、gate、anti-rationalization 表、verification） | 作為第 3 點「核心機制」的具體範例 | 取得 4 phase gated workflow、ASSUMPTIONS 模板、三層 boundaries、rationalization 表 |
| 收斂資訊撰寫分析報告 | 產出符合 AGENTS.md 格式的 4 點報告 + DA 表 | 報告含問題、背景、核心機制、5 技術 DA 表 | 已產出 `output/2026-06-20-Agent-Skills.md` |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 報告格式合規性 | 對照 `01_general_tech/AGENTS.md` 的 4 點格式要求 | 分析報告含 4 個必要段落（問題、背景、解法、替代方案），格式符合 |
| DA 表完整性 | 確認有 2~4 個替代方案 + 7 欄（含授權、LLM） | 提供 5 個方案（Agent Skills 自身 + Cursor Rules + Claude Subagents + Aider conventions + 手寫 prompt），7 欄齊全 |
| 技術深度 | 確認核心機制涵蓋結構、生命週期對應、anatomy、範例、meta-skill、跨工具載入、設計哲學來源 | 7 個子節涵蓋結構圖、命令對應表、anatomy、spec 範例、meta-skill 行為、跨工具表、Google 工程文化對應表 |
| 資訊來源可靠性 | 資訊來自 repo 官方 README + 兩份 SKILL.md 原始檔 + gh api metadata | 所有資訊來自 addyosmani/agent-skills repo 官方檔案 |
| 模糊點標註 | AGENTS.md 要求「若問題描述含糊請指出」 | 第 1 點已註記「skill」一詞在此 repo 非 callable function 而是 Markdown workflow |
| 中文撰寫 | AGENTS.md 要求使用中文 | 報告全文中文，僅專有名詞與程式碼保留英文 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| 適用哪份 AGENTS.md | ① `00_news_catchup/AGENT.md`（Feedly 新聞助理）② `01_general_tech/AGENTS.md`（技術解析助理）③ `02_mvps/AGENTS.md`（MVP 實作教練） | ② `01_general_tech/AGENTS.md` | 調研對象是一個技術專案/repo，屬於「技術解析」範疇，非新聞 catchup 也非 MVP 實作 |
| 第 3 點深度 | ① 僅 README 概述 ② 深入到每個 skill 內部 ③ 結構 + 生命週期 + anatomy + 一個範例 skill + meta-skill | ③ 結構 + 生命週期 + anatomy + 範例 + meta-skill | 使用者要求「調研」需展現核心機制，但 24 個 skill 全部展開會失焦；用一個代表性 skill（spec-driven-development）展示內部結構即可推及其餘 |
| 範例 skill 選取 | ① using-agent-skills（meta）② spec-driven-development ③ test-driven-development ④ doubt-driven-development | ② spec-driven-development | 它是最能展現 skill anatomy 四要素（步驟、gate、anti-rationalization、verification）的範例，且是生命週期起點；using-agent-skills 雖是入口但偏決策樹而非 workflow |
| DA 表替代方案選取 | ① 僅選其他 skill 框架 ② 選不同切入角度的方案 | ② 選不同切入角度 | AGENTS.md 要求 2~4 個，本報告選 5 個（含自身）以展現「workflow-first / IDE-native / 角色分工 / Git-native / 完全客製」五種切入角度的光譜 |
| 是否 clone repo | ① clone 到本地分析原始碼 ② 僅透過 web fetch 取得文件 | ② 僅透過 web fetch | repo 主體是 Markdown，README + 兩份 SKILL.md 已足以理解核心機制；無需原始碼層級分析 |
| 跨工具載入是否全部展開 | ① 只列 Claude Code ② 列全部 8 種 | ② 列全部 8 種 | 跨工具通用性是 agent-skills 的核心賣點之一，全部列出才能展現其差異化 |