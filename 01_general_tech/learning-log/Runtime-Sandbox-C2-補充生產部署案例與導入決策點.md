# Runtime-Sandbox-C2-補充生產部署案例與導入決策點

## 狀況理解
使用者在前一輪看到 microVM 與 gVisor 的技術分析後，提出兩個補充需求：(1) 把兩個報告整合成一個技術報告 (2) 補充兩技術的實際生產環境運用案例以及導入時的決策點。本輪的動作重點是：網路調研生產部署資訊 → 整合報告 → 建立學習記錄。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 平行調研 gVisor 生產部署 | 取得 gVisor 的實際用戶、規模、使用場景、已知限制 | 獲得可引用的生產環境數據 | Google Cloud Run（serverless 容器全跑 gVisor）、GKE Sandbox（K8s RuntimeClass）、Google Borg（每日數百萬 sandbox）、Ant Group（10 萬+ 實例，70% app <1% overhead，雙十一驗證）、Cloudflare Pages（build sandbox，啟動從 2+ 分鐘降至 2-3 秒）、OpenAI（高風險代碼執行，PCI-DSS/SOC2）、Modal（主要 runtime）、DigitalOcean App Platform |
| 平行調研 microVM 生產部署 | 取得 Firecracker/Kata/QEMU microvm/Cloud Hypervisor 的實際用戶與規模 | 獲得可引用的生產環境數據 | AWS Lambda（每月數兆次執行）/Fargate（每週數千萬容器）、Fly.io（~300ms VM 啟動）、Kata Containers（Red Hat OpenShift、Baidu/Huawei/ZTE/金融）、Cloud Hypervisor（Microsoft Azure OpenHCL）、QEMU microvm（Red Hat 實驗，~100ms 啟動） |
| 閱讀 Ant Group 2021 生產經驗部落格 | 取得 gVisor 在超大規模金融系統中的優化經驗與效能瓶頸 | 獲得第一手生產調優數據 | KVM 平台 syscall 成本 ~830ns vs 原生 ~62ns（13x）；Go runtime 調優細節（timer buckets 64→4、GOMAXPROCS、GC 觸發）；70% app <1% overhead |
| 閱讀 GKE Sandbox 文件 | 取得 gVisor 在 GKE 中的整合方式、相容性限制、GPU 支援現狀 | 獲得 K8s 原生整合的技術限制清單 | 無 privileged container、無 hostPath、無 port-forward、無 container-level 記憶體指標；GPU 支援（L4/T4/A100/H100/TPU）；不支援 V100/P100 |
| 閱讀 Firecracker SPECIFICATION.md | 取得 AWS 在 CI 中強制執行效能承諾的實際指標 | 獲得有 CI 強制的效能數據 | 啟動 ≤125ms（從 InstanceStart 到 /sbin/init）、記憶體 ≤5MiB/VM、VMM 啟動 ≤8 CPU ms、建立速率 150 VM/s、網路 14.5 Gbps、儲存 1 GiB/s |
| 閱讀 gVisor 安全 FAQ 與效能指南 | 取得 gVisor 官方對 VM 比較的回應與效能基準 | 獲得官方立場與 benchmark 數據 | CPU-bound near-native、記憶體 ~20-50MB/Sandbox、Redis 2-10x overhead、Apache static file "predictably poor" |
| 閱讀合規相關文件 | 取得 PCI-DSS/HIPAA/FedRAMP/SOC2 下各技術的認證路徑 | 獲得合規維度的決策參考 | Firecracker（AWS 認證，審計員易理解硬體 VM 語義）、gVisor（OpenAI PCI-DSS v4.0.1 + SOC2 + ISO27001 via gVisor；Modal HIPAA + SOC2 via gVisor） |
| 整合兩份報告為 Runtime-Sandbox | 將 microVM 與 gVisor 視為同一問題域的兩種路線，合併為單一技術報告 | 產出統一的 Runtime-Sandbox 分析報告 | output/2026-05-31-Runtime-Sandbox.md，含 1-4 點標準格式 + 第 5 章生產部署與決策 |
| 建立 C1 學習記錄 | 記錄初次調研與整合過程中的決斷 | 完成 Runtime-Sandbox-C1.md | 已產出 |
| 建立 C2 學習記錄 | 記錄生產部署調研與補充過程 | 完成 Runtime-Sandbox-C2.md | 本檔案 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 報告生產部署數據完整性 | 檢查是否覆蓋主要使用者與規模 | 覆蓋 gVisor 9+ 使用者（Google/Ant Group/Cloudflare/OpenAI/Anthropic/Modal/DigitalOcean/Tailscale/Freedom of Press）+ Firecracker 8+ 使用者（AWS/Fly.io/Koyeb/Northflank/OpenNebula 等）+ Kata（Red Hat/Baidu/Huawei）+ Cloud Hypervisor（Azure） |
| 決策框架可用性 | 檢查是否提供實際可操作的選型指引 | 含決策對照表（7 方案 × 11 維度）、場景→方案流程圖、gVisor vs Firecracker 取捨分析、合規框架對照表 |
| 已知限制真實性 | 與官方文件交叉確認限制描述 | gVisor 74 個未實作 syscall、I/O 效能瓶頸、GKE 限制均來自官方文件；Firecracker 無 PCI/GPU/live migration 為設計決策非 bug |
| 數據出處可追溯 | 確認所有數字有對應來源 | 每個關鍵數字（<125ms、5MiB、150VM/s、14.5Gbps、830ns、70%<1%）均有明確官方文件/部落格出處 |
| 舊檔案清理 | 檢查 repo 根目錄是否有暫存檔 | 有待刪除的暫存調研檔（由 task agent 產出） |

## 其中的決斷點

| 決斷面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---------|------------|---------|---------|
| 生產部署章節的組織方式 | (1) 按技術分開（Firecracker/gVisor/Kata 各一節）(2) 按用戶類型分開（公有雲/自建/合規）(3) 先分技術再交集對比 | 選項 3：先按技術分列用戶與規模，再設整合對比章節 | 技術選型讀者需要「誰在用什麼、多大量」的快速索引，也需要「如果我的場景是 X 該選 Y」的決策表；先分後合能滿足兩種需求 |
| 合規資訊的處理 | (1) 僅提及有認證 (2) 詳細列出各合規框架下的認證路徑與審計友善度差異 | 選項 2：詳細列出 | 使用者要求「導入時的決策點」，合規經常是企業導入的核心阻斷點；詳細說明各框架下的認證路徑有助於實際決策 |
| 是否將 performance benchmark 細節納入報告 | (1) 僅摘要 (2) 放入完整數字 (3) 不放入，留待後續 | 選項 2：放入關鍵數字 | 導入決策需要量化數據支撐（「systrap syscall 成本 13x vs 原生」比「效能有損失」更有決策價值）；但避免變成純 benchmark 報告，只取關鍵比較點 |
| Ant Group 調優細節的保留程度 | (1) 略過 (2) 放入報告主體 (3) 放學習記錄中 | 選項 2：摘要放報告，細節留學習記錄 | 70% app <1% overhead 這個數字對 gVisor 的導入信心有重大影響，應在報告主體中出現；timer buckets/GOMAXPROCS 等細節屬調優層級，適合學習記錄 |
