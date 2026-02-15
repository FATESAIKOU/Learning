# Step 03: Backend Implementation

## 任務回顧

本階段目標是完成 ToDo 後端 API 的實作，並確保資料能持久化儲存於 SQLite 資料庫中。

**完成項目：**
1.  **Database Integration**:
    -   新增 `database.py` 處理 SQLite 連線 (`sqlalchemy`)。
    -   新增 `models.py` 定義 `Todo` 資料表結構。
    -   修正 `docker-compose.yml` 中的 `DATABASE_URL` 路徑問題 (從 `sqlite:///data/todos.db` 改為 `sqlite:////data/todos.db` 以確保絕對路徑正確對應 Volume)。

2.  **API Implementation**:
    -   更新 `main.py`，移除 `fake_db`，全面改用 Database Session。
    -   實作完整 CRUD (Create, Read, Update, Delete) 路由。
    -   新增 Pydantic Schemas (`TodoCreate`, `TodoUpdate`, `TodoResponse`) 進行資料驗證。

3.  **Verification**:
    -   成功啟動 Docker Container (`result_backend_1`)。
    -   透過 `curl` 驗證 API 功能正常 (新增、讀取)。
    -   確認資料庫檔案 `data/todos.db` 建立於 Volume 中。

## Review紀錄（意思決定要点）

1回目: (問題)：Database URL Path Issue
      （答え）：在 `docker-compose.yml` 設定 `sqlite:///data/todos.db` 時，SQLAlchemy 解讀為相對路徑 `/app/data/todos.db`，導致 `OperationalError: unable to open database file`。解決方案是使用 `sqlite:////data/todos.db` (4個斜線) 指定絕對路徑，或是調整路徑對應。最終採用絕對路徑修正。

2回目: (問題)：Module Imports
      （答え）：為了避免 `uvicorn` 執行時的 package 結構問題，採用了直接 import (`import models`, `from database import ...`) 而非相對 import (`from . import models`)，確保單檔執行與 Docker 啟動的相容性。

## Next Steps

- **Step 04: Pause & Restart (模拟失憶)**
    -   停止所有 Containers。
    -   清理 Session / Memory (Agent 視角)。
    -   重新讀取 `bd` 狀態，並繼續 Step 05 (Frontend)。
