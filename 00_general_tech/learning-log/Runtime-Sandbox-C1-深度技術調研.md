# Runtime-Sandbox-C1-深度技術調研

## 狀況理解
使用者要求對 microVM 與 gVisor 進行深度技術調研。初次產出兩份獨立報告（microVM 與 gVisor 各一份）。後續使用者指示：(1) 將兩份報告整合為一個技術名 Runtime-Sandbox (2) 補充兩者在實際生產環境的部署案例與導入時的決策點。目標是產出整合的分析報告、補充生產部署資訊、並建立完整的學習過程記錄。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 AGENTS.md | 確認報告格式規範（4 點格式、DA 表欄位、中文輸出、圖示強化） | 輸出符合規範的整合報告 | AGENTS.md 規範：問題→背景→解法→替代方案+DA表，中文，ASCII art 圖示 |
| 平行調研 microVM 技術 | 取得 Firecracker/Kata/QEMU microvm/Cloud Hypervisor 的設計目標、核心機制、效能指標 | 獲得 microVM 生態全景 | Firecracker 5 設備模型、<125ms 啟動、Rust 實作、KVM 底層；Kata OCI 整合；QEMU microvm 精簡 machine type；Cloud Hypervisor 中長期 workload 定位 |
| 平行調研 gVisor 技術 | 取得 Sentry/Gofer/Platform 三大元件的設計、安全模型、效能數據 | 獲得 gVisor 完整架構 | Sentry（Go kernel 重寫）、Gofer（9P 檔案代理）、Platform（systrap/KVM）、runsc OCI runtime、netstack、VFS、安全模型 |
| 平行調研生產部署案例與決策 | 取得 gVisor 與 microVM 的實際用戶、規模數據、導入決策框架 | 獲得生產環境全景與決策對照 | gVisor：Google Cloud Run/GKE Sandbox/Borg（百萬級）、Ant Group（10 萬+）、OpenAI/Anthropic/Modal；Firecracker：AWS Lambda（兆次/月）/Fargate、Fly.io；Kata：Red Hat OpenShift、Baidu/Huawei |
| 合併兩份獨立報告為整合報告 | 以 Runtime-Sandbox 為統一名稱，整合兩技術為同一問題域的兩種路線 | 產出單一技術報告，同時保留兩路線的微觀機制差異 | 以「隔離技術光譜」框架統合，第 3 點分為 microVM 路線與 gVisor 路線兩節 |
| 補充第 5 章節：實際生產環境與導入決策點 | 新增不在 AGENTS.md 4 點規範內的實用資訊 | 提供可操作的技術選型框架 | 含 5 節：各技術實際用戶、決策對照表、場景→方案流程、gVisor vs Firecracker 取捨、合規考量、已知限制 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|---------------|---------|
| 報告格式 | 比對 output/2026-05-31-Runtime-Sandbox.md 與 AGENTS.md 規範 | 1-4 點嚴格符合規範；第 5 章為使用者額外要求，不在規範範圍內但合併於同一報告 |
| DA 表格式 | 比對 AGENTS.md 要求的 DA 表欄位（技術名、技術解法、技術使用前提、技術使用副作用、技術使用預期效果） | 欄位完整，包含 runc、seccomp、Unikernel、傳統 VM 四個替代方案 |
| 生產數據真實性 | 與官方文件、技術部落格、公開演講交叉確認 | 所有數據與用戶名稱皆有出處；未使用的數據不納入 |
| 報告完整性 | 檢查涵蓋的技術範圍 | microVM（Firecracker/Kata/QEMU microvm/Cloud Hypervisor）+ gVisor（Sentry/Gofer/Platform/runsc）+ 底層技術（KVM/virtio）+ 替代方案（runc/seccomp/Unikernel/傳統VM）+ 生產部署 + 決策框架 |
| 舊檔案清理 | 確認暫存研究檔案位置 | gVisor-production-research.md 與 microVM-production-research.md 為 task agent 輸出的暫存檔，位於 repo 根目錄，需手動刪除 |

## 其中的決斷點

| 決斷面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---------|------------|---------|---------|
| 技術命名 | (1) 保持 microVM 與 gVisor 分開 (2) 合併為 Runtime-Sandbox (3) 命名為 Container-Isolation | 選項 2：Runtime-Sandbox | 使用者明確要求「把兩個報告整合成一個技術」；以運行時沙箱隔離為上位概念，能涵蓋兩條路線的共性而不失各自細節 |
| 整合方式 | (1) 只留共同問題+解法，刪減差異 (2) 先寫共通框架再分路線詳述各自機制 (3) 兩篇並列，加一個總覽 | 選項 2：先寫共通框架再分路線 | 兩技術解決同一問題但機制截然不同；先以光譜圖建立心智模型，再分路線詳述，讀者能理解「為什麼會有兩種路線」 |
| 報告結構擴充（第 5 章） | (1) 嚴格只寫 4 點 (2) 在第 4 點內塞入生產部署資訊 (3) 獨立第 5 章但不破壞 1-4 點格式 | 選項 3：獨立第 5 章 | 使用者要求補充的內容（生產部署、決策點）本質上不是 AGENTS.md 規範的 4 點結構能涵蓋的；獨立章節能滿足使用者需求而不破壞原有格式 |
| 暫存研究檔案的處理 | (1) 保留供後續參考 (2) 刪除避免混淆 | 選項 2：刪除 | 暫存檔位於 repo 根目錄，非 output/ 或 learning-log/，不符合目錄結構規範；其內容已收斂至正式報告中 |
