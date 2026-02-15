# Step 02: Bootstrap Project

## 任務前提＆狀況總結

我們已完成專案的基本架構搭建，並建立了 Beads 任務清單。
目前專案狀態：
- **Beads**: 專案根目錄擁有 `AGENTS.md` 規範，`.beads/` 已初始化並包含 Step 02-06 的任務規劃。
- **Directory Structure**:
    - `result/backend`: 包含 FastAPI 基礎程式碼 (`main.py`) 與 `Dockerfile`。
    - `result/docker-compose.yml`: 定義了後端服務與 SQLite Volume。

## Review紀錄（意思決定要点）

1回目: (問題)：如何確保 Agent 遵守規範？
      （答え）：建立了 `AGENTS.md`，並在專案根目錄強制要求閱讀。Beads 任務已建立並設為 Block 關係，強迫按順序執行。

2回目: (問題)：後端技術選型確認？
      （答え）：採用 FastAPI + Uvicorn (Python 3.9-slim)。資料庫暫時使用 `fake_db` (In-Memory) 用於測試路由，Step 03 將實作 SQLite 連線。

## Next Steps

- **Step 03: Backend Implementation**
    - 啟動 Docker Compose。
    - 實作真正的 SQLite/Postgres 連線。
    - 完成 CRUD API。
    - 驗證 `bd` 在開發過程中的狀態更新。
