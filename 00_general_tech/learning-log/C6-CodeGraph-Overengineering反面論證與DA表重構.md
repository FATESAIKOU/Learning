# CodeGraph-C6-Overengineering反面論證與DA表重構

## 狀況理解
使用者要求對 CodeGraph 與 GitNexus 進行 2×2 overengineering 判定（自身問題 × 導入 SaaS 團隊），且須從反面論證出發——即針對兩個技術的四個面向各別蒐集反對證據，收斂後才做判定。結果須反映到分析報告的 DA 表，且比較技術限縮至最多 4 個。最後產出本篇學習紀錄。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 查閱 CodeGraph open issues | 蒐集反面證據：確認 CodeGraph 實際存在的維護負擔與邊緣案例 | 取得具體 issue 編號與問題描述 | 取得 #579（inotify 90k watches）、#584（Go interface 不偵測）、#578（Python module-attribute call 遺漏）等實例 |
| 查閱 GitNexus open issues | 蒐集反面證據：確認 GitNexus 自幹基礎設施的品質風險 | 取得具體 issue 編號與規模 | 取得 #1927-#1936 共 10 個語言的 parsing coverage gaps（合計 67 項缺失），加上 #1938（hook 仍未修正）、#1939（npm 11.x crash） |
| 查閱 SQLite 官方使用指南（whentouse.html） | 驗證 CodeGraph 使用 SQLite 是否對應其宣稱場景 | 確認 SQLite 適用於 CodeGraph 的查詢模式 | SQLite WAL 模式適用於單機多讀者（CodeGraph 的使用場景），不適用於多寫者（非 CodeGraph 場景）。GitNexus 自幹 LadybugDB 的原因不成立 |
| 對 CodeGraph 進行反面論證（立場 A vs 立場 B） | 建構客觀證據矩陣 | 取得是否 overengineering 的證據收斂 | 收斂：不是 overengineering——工程投入與問題規模成比例，使用成熟組件 |
| 對 GitNexus 進行反面論證（立場 A vs 立場 B） | 建構客觀證據矩陣 | 取得是否 overengineering 的證據收斂 | 收斂：功能面不是、工程面效率不佳——功能合理但自幹過多基礎設施 |
| 對導入 SaaS 團隊進行反面論證（CodeGraph + GitNexus） | 從運維/授權/品質/方案對比四個維度評估導入合理性 | 取得導入 SaaS 團隊是否 overengineering 的證據收斂 | CodeGraph：否（零成本導入、風險可控）；GitNexus：是（通用需求不如 CodeGraph、特化需求覆蓋面窄） |
| 重構分析報告 section 4 | 將反面論證結果融入 DA 表，剔除不重要方案，上限 4 個 | DA 表僅含 4 個技術（CodeGraph/GitNexus/Aider/SCIP），外加 overengineering 判定補充表 | 完成：DA 表 4 行 × 5 欄 + 2×2 overengineering 判定表 + 4 句切入點差異 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| DA 表方案數量 | 讀取報告 section 4 | 4 個：CodeGraph、GitNexus、Aider repomap、LSIF/SCIP。剔除 SonarQube（不同問題域）、Ctags（過於基礎）、LSP wrapper（未實現） |
| Overengineering 判定是否基於反面論證 | 對照本文中「立場 A vs 立場 B」證據蒐集與對話回覆的一致性 | 一致：每個判定均先列出反對證據，再列出支持證據，最後收斂 |
| 證據來源可追溯性 | 檢查引用來源 | CodeGraph issues（3 個）、GitNexus issues（13 個）、SQLite 官方文檔、兩者架構文件、benchmark README |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| DA 表保留 4 個方案的選取邏輯 | 從原本 7 個方案中篩選出 4 個 | CodeGraph、GitNexus、Aider repomap、LSIF/SCIP | 剔除 SonarQube（不同問題域：SAST vs code intelligence）、Ctags+grep（過於基礎，非成熟方案）、LSP wrapper（未實際存在於市場）。保留的 4 個均屬「提供 agent 程式碼結構理解的工具」 |
| Overengineering 判定表的格式 | 1. 融入 DA 表新增欄位；2. 獨立補充表 | 2. 獨立補充表 | 2×2 判定涉及兩個技術 × 兩個維度的交叉分析，新增欄位會使 DA 表過寬難以閱讀。獨立補充表結構更清晰 |
| GitNexus 的整體定性措辭 | 1. 「overengineering」；2. 「效率不佳的設計選擇」 | 2. 「否（功能面）/ 效率不佳（工程面）」 | 反面論證顯示功能本身合理（communities/processes/contract bridge 回應了更宏大的問題），問題在實現手段（自幹 DB/scope resolver/embedding）。用「效率不佳」比「overengineering」更精準地反映技術事實 |
