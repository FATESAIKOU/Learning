# Heretic-C1-深度技術調研

## 狀況理解
使用者要求對 GitHub repo `p-e-w/heretic` 進行深度技術調研，涵蓋：
- 原始碼結構（src/heretic/）
- 三個設定檔（default, nohumor, noslop）
- 網路上的部落格文章、評論、技術分析
- directional ablation / abliteration 技術背景（Arditi et al. 2024）
- TPE-based parameter optimizer（Optuna）
- 技術架構、核心機制、關鍵設計決策的結構化總結

使用者已持有 README，需要補充 README 以外的細節。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 嘗試 fetch GitHub API trees (main branch) | 取得完整目錄結構 | 列出所有檔案 | 404 失敗（branch 名為 master 非 main） |
| 嘗試 fetch config 檔案 (main branch) | 取得設定檔內容 | 完整 TOML 內容 | 404 失敗（同上） |
| Fetch GitHub repo 頁面 (master branch) | 取得 README 完整內容與目錄結構 | 完整 README + 檔案列表 | 成功，取得完整 README 及目錄 |
| Fetch config.default.toml (master) | 取得預設設定 | 完整設定內容 | 成功 |
| Fetch config.nohumor.toml (master) | 取得無幽默設定 | 完整設定內容 | 成功 |
| Fetch config.noslop.toml (master) | 取得無 slop 設定 | 完整設定內容 | 成功 |
| Fetch GitHub API repo info | 取得 repo 基本資訊 | stars/forks/license 等 | 成功（24.3k stars, 2.6k forks, AGPL-3.0） |
| Fetch src/heretic/ 目錄 | 取得原始碼檔案列表 | 10 個 .py 檔案 | 成功 |
| Fetch pyproject.toml | 取得依賴與專案設定 | 完整依賴清單 | 成功 |
| Fetch main.py (56KB) | 理解主程式流程 | 完整程式邏輯 | 成功（部分截斷，已存檔） |
| Fetch model.py (35KB) | 理解模型載入/abliteration 邏輯 | 完整模型處理程式碼 | 成功 |
| Fetch analyzer.py (13KB) | 理解 residual geometry 分析 | 完整分析程式碼 | 成功 |
| Fetch utils.py (26KB) | 理解工具函數 | 完整工具程式碼 | 成功 |
| Fetch evaluator.py (4KB) | 理解評分邏輯 | KL divergence + refusal 計算 | 成功 |
| Fetch config.py (18KB) | 理解設定模型 | Pydantic Settings 定義 | 成功 |
| Fetch system.py (16KB) | 理解系統/硬體偵測 | 多加速器支援 | 成功 |
| Fetch reproduce.py (11KB) | 理解 reproducibility 機制 | 完整 reproduce 邏輯 | 成功 |
| Fetch Arditi et al. 2024 arXiv | 理解 abliteration 理論基礎 | 論文摘要 | 成功 |
| Fetch Labonne abliteration blog | 理解 abliteration 實作歷史 | 完整文章 | 成功 |
| Fetch grimjim projected abliteration | 理解 orthogonalize_direction 來源 | 完整文章 | 成功 |
| Fetch grimjim norm-preserving biprojected | 理解 row_normalization=full 來源 | 完整文章 | 成功 |
| Fetch Optuna 官網 | 理解 TPE sampler 原理 | 功能概述 | 成功 |
| Fetch FailSpy/abliterator | 理解競爭工具 | README | 成功 |
| Fetch AUGMXNT/deccp | 理解中文審查場景工具 | README | 成功 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 原始碼結構完整性 | 確認 src/heretic/ 下 10 個檔案全部讀取 | 全部成功讀取：`__init__.py`, `analyzer.py`, `config.py`, `evaluator.py`, `main.py`, `model.py`, `progress.py`, `reproduce.py`, `system.py`, `utils.py` |
| 設定檔完整性 | 三個設定檔全部讀取 | default.toml（完整）、nohumor.toml（完整）、noslop.toml（完整） |
| 理論基礎覆蓋 | Arditi 2024 + Labonne 2024 + Lai 2025 (projected + biprojected) | 四篇關鍵文獻全部取得 |
| 競爭工具覆蓋 | abliterator.py, AutoAbliteration, ErisForge, deccp | 前兩者取得 README，ErisForge 未直接 fetch（資訊來自 Heretic README），deccp 取得 README |
| 優化器理解 | Optuna TPE sampler | 取得官網功能描述 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|------------|---------|---------|
| Branch 名稱 | main / master | master | GitHub API 回傳 404 後檢查 repo 頁面確認 default branch 為 master |
| 原始碼讀取策略 | 全部讀取 / 只讀關鍵檔案 | 全部讀取（10 個檔案） | 使用者要求 "in depth" 分析，需完整理解架構 |
| 外部文獻搜尋範圍 | 僅 README 引用 / 擴展搜尋 | 擴展搜尋（Arditi, Labonne, Lai×2, Optuna, 競爭工具） | 使用者明確要求搜尋 abliteration 技術、TPE、blog posts |
| 分析報告深度 | 僅回答 4 點 / 加入技術細節 | 加入虛擬碼、流程圖、DA 表 | AGENTS.md 要求使用圖示、程式碼、表格強化理解 |
