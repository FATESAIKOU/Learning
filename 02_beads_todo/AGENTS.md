# AGENTS.md

## 專案工作守則 (Project Rules)

**此專案使用 [Beads (bd)](https://github.com/steveyegge/beads) 作為唯一的長期記憶與任務管理系統。**

所有參與開發的 Agent 與人類必須遵守以下規範：

### 1. 任務管理 (Task Management)
*   **唯一真理 (Source of Truth):** 禁止使用 `TODO.md` 或 `plan.md` 來追蹤進度。所有任務狀態必須反映在 `bd` 中。
*   **啟動工作 (Starting Work):**
    *   在開始任何工作前，執行 `bd ready` 尋找當前可執行的任務。
    *   使用 `bd update <id> --status in_progress` 認領任務。
*   **完成工作 (Finishing Work):**
    *   工作完成後，使用 `bd update <id> --status done` 關閉任務。
    *   若發現新任務，使用 `bd create` 建立並設定適當的依賴 (`bd dep add`)。

### 2. 決策紀錄 (Decision Records)
*   重大技術決策必須記錄在 `bd` 的 issue comment 或獨立的決策 issue 中。
*   每個階段 (Step) 結束時，必須產出對應的 `report/step-xx-name.md` 報告。

### 3. 環境與工具 (Environment & Tools)
*   本專案採用 Docker 化開發，除 `bd` CLI 外，盡量不依賴 Host 環境。
*   後端資料庫預設使用 SQLite (檔案模式)，以簡化配置。

---
*這是一份強制性文件，請確保在每次 Session 開始時閱讀。*
