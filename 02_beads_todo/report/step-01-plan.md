# step-01-plan.md

## 任務前提＆狀況總結

我們目前正在進行 Beads (bd) 學習專案，目標是建立一個 ToDo 應用程式並演練使用 `bd` 作為唯一的長期記憶與任務管理工具。

**專案狀態：**
1.  已安裝 `bd` CLI (Beads 0.50.3)。
2.  已建立專案目錄 `02_beads_todo` 並初始化 `bd` (`.beads/` 已生成)。
3.  已建立 `report` 和 `result` 目錄。

**後續執行計畫：**
- **Step 02: Bootstrap**
    - 建立 `AGENTS.md` (Beads Policy)。
    - 設定 `docker-compose.yml` (包含 DB: SQLite 或 Postgres)。
    - 設定 `.gitignore` 等基礎配置。
    - 使用 `bd` 登記初始任務。

- **Step 03: Backend**
    - 實作 ToDo CRUD API (選擇語言：Python FastAPI 或 Go Gin/Echo?)。
    - 確保資料庫連線與遷移 (Migration)。
    - 測試 API 功能。
    - 使用 `bd` 記錄所有開發任務。

- **Step 04: Pause & Restart**
    - 停止所有 Container。
    - 模擬「失憶」：清除 Session 上下文 (實際上是重新檢視 `bd` 狀態)。
    - 驗證能否僅透過 `bd` 恢復工作狀態。

- **Step 05: Frontend**
    - 實作簡易前端 (HTML/JS 或 React/Vue)。
    - 整合後端 API。
    - 完成 ToDo 列表顯示與操作。

- **Step 06: Wrapup**
    - 總結學習心得。
    - 清理環境。

## Review紀錄（意思決定要点）

1回目: (問題)：語言選擇？
      （答え）：User 未指定後端語言。建議使用 Python (FastAPI) 或 Node.js (Express)，因其輕量且易於 Dockerize。鑑於「學習 Beads」是重點，後端越簡單越好。預設採用 Python FastAPI + SQLite。

2回目: (問題)：DB 選擇？
      （答え）：規格提到「DB 可用 SQLite（最簡化）或 Postgres」。為了降低環境複雜度並專注於 Beads 流程，建議初期使用 SQLite (儲存於 Volume 或檔案)，若有需要再遷移至 Postgres。

**請確認上述計畫，若無異議將開始 Step 02。**
