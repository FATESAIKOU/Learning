# LingBot-Map-C1-深度技術調研

## 狀況理解

使用者要求對 `https://github.com/robbyant/lingbot-map` 做深入技術調研，並依據 AGENTS.md 的規範產出兩個文檔：
1. 分析報告：`output/<日期>-<分析技術名>.md`
2. 分析過程報告：`learning-log/<分析技術名>-C1-<做的事情總結>.md`

該專案為 2026 年 4 月發表的「Geometric Context Transformer for Streaming 3D Reconstruction」（LingBot-Map），是一個 feed-forward 3D foundation model，用於從 streaming video 中即時重建 3D 場景。GitHub stars 6.9k，由 Robbyant 團隊維護，在 benchmark/README.md 中也明確引用了多個同領域的對比方法（VGGT、Fast3R、DROID-SLAM、MegaSaM、StreamVGGT、TTT3R 等）。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取工作目錄 `01_general_tech/AGENTS.md` | 確認輸出物格式、分析報告 4 點結構、DA 表欄位 | 取得精確的輸出規範 | 成功取得，確認 4 點問答格式、DA 表需 5 個欄位（技術名、技術解法、技術使用前提、技術使用副作用、技術使用預期效果） |
| 讀取 `learning-log/` 目錄 | 確認過往學習紀錄的命名與格式慣例 | 遵循一致的檔名與結構 | 取得 7 篇歷史紀錄，確認檔名規則為 `<技術名>-C<自增ID>-<總結>.md` |
| WebFetch 取得 GitHub README（主要頁面） | 取得專案的完整說明、架構、API、安裝指南 | 理解模型設計理念、使用方式、benchmark 框架 | 成功取得完整 README（含安裝、demo、offline rendering pipeline、benchmark 架構詳解） |
| WebFetch 取得 arxiv 論文摘要 (2604.14141) | 取得論文 formal description | 確認核心貢獻與技術名詞定義 | 成功取得：定義 GCT 三種 attention（anchor context、pose-reference window、trajectory memory），~20 FPS，10,000+ 幀 |
| WebFetch 探索 repo 目錄結構 | 了解程式碼組織與核心模組 | 確認 implement 細節（如 models/gct_stream.py、heads/、layers/、aggregator/） | 成功取得目錄樹：`lingbot_map/` 下有 aggregator、heads、layers、models、utils、vis 六個子模組 |
| WebFetch 讀取 `benchmark/README.md` | 了解 benchmark 框架設計與支援的評估指標 | 掌握評估體系（ATE、AUC、depth metrics、point cloud metrics）與 BSS 儲存格式 | 成功取得詳細的 benchmark 文檔，含 BSS 目錄結構、三層 aggregation、支援的 datasets (KITTI、Oxford Spires、VBR、DROID-W 等) |
| WebFetch 取得 VGGT 專案 README | 對比研究：理解 batch-mode feed-forward 模型的設計 | 取得 VGGT 的架構概述（CVPR 2025 Best Paper） | 成功取得：VGGT 為 batch-mode，一次性處理所有視圖，用 Alternating-Attention，無 streaming 設計 |
| WebFetch 取得 arxiv VGGT 摘要 (2503.11651) | 取得 formal abstract | 交叉確認 VGGT 設計哲學 | 成功取得，確認其為 feed-forward、處理 1 到數百張視圖、輸出 camera/depth/point/track |
| WebFetch 取得 DROID-SLAM 專案 README | 對比研究：了解 recurrent iterative + DBA 的 streaming SLAM | 確認其架構與計算瓶頸 | 成功取得：GRU-based recurrent update + DBA layer，支援 mono/stereo/RGB-D，推理約 3 FPS |
| 搜尋 MegaSaM、Fast3R 等其他對比項目 | 擴充 DA 表的對比基礎 | 蒐集足夠的替代方案做比較 | MegaSaM URL 404（正確 repo 可能在其他位置），Fast3R URL 404；轉以 benchmark/README 中的方法列表為基礎 |
| 搜尋 arxiv 2412.07496 (誤打，應為 MegaSaM paper) | 嘗試取得 MegaSaM paper | 交叉確認 | 返回的是不相關的量子物理論文（錯誤的 arxiv ID），需使用正確的 MegaSaM paper ID |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| 核心技術理解 | 論文 abstract + README 的交叉比對 | 已確認 GCT 三層 attention 的設計與目的，以及 paged KV cache、keyframe interval、windowed mode 等 streaming 優化技術 |
| 程式碼架構 | 目錄樹瀏覽確認模組職責 | 已確認 `models/`（gct_base/stream/window）、`heads/`（camera/dpt）、`aggregator/`（stream）、`layers/`（attention/flashinfer_cache/rope）的分工 |
| 基準比較方法 | 從 benchmark/README 的方法列表與外部搜尋交叉確認 | 已取得 VGGT、DROID-SLAM、ORB-SLAM3 的足夠資訊；MegaSaM 和 Fast3R 的 repo URL 需要修正 |
| Benchmark 評估體系 | benchmark/README.md 完整閱讀 | 已確認 ATE/RPE/AUC/depth/point cloud 指標、BSS 儲存格式、三層 aggregation 設計 |
| 輸出文件完整性 | 檢查分析報告是否覆蓋 AGENTS.md 要求的 4 點 | 已覆蓋：1) 解決問題、2) 問題原因、3) 解決機制、4) DA 表格與替代方案 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| DA 表中對比方法的數量 | 1) 只放 2 個（VGGT + DROID-SLAM）/ 2) 放 4 個（含 ORB-SLAM3）/ 3) 放 6 個（含 MegaSaM、Fast3R） | 選擇 4 個（VGGT、DROID-SLAM、ORB-SLAM3、DUSt3R/MASt3R） | AGENTS.md 要求 2-4 個替代方案；MegaSaM 和 Fast3R 的公開 repo 無法確認（404），不宜放入 DA 表以免資訊不完整 |
| 是否用 CDP 繞過 GitHub 反爬 | 1) 使用 CDP / 2) 放棄該資料來源 | 放棄使用 CDP | GitHub 頁面透過 WebFetch 即可正常取得內容（未觸發 CAPTCHA），無需 CDP |
| DA 表的第四項選擇 | 1) ORB-SLAM3 / 2) MegaSaM / 3) DUSt3R | 選擇 DUSt3R/MASt3R | ORB-SLAM3 和 DROID-SLAM 同為經典 SLAM 路線（雖然一個 optimization-based 一個 learning-based），DA 表需要展現不同設計哲學的對比；DUSt3R 作為 dense pairwise reconstruction 基礎模型代表另一種路線 |
| Windowed mode 的解釋深度 | 1) 只提概念 / 2) 附上程式碼對照 | 選擇附程式碼對照 | AGENTS.md 要求「說明時善用程式碼或虛擬碼做舉例」 |
