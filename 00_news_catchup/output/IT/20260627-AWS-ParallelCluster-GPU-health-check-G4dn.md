# 6. AWS ParallelCluster の GPU ヘルスチェックを G4dn インスタンスで試してみた

**Source**: https://dev.classmethod.jp/articles/aws-parallelcluster-gpu-healthcheck/
**Author**: DevelopersIO (Classmethod)
**Date**: 2026-06-27
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

GPU 叢集上執行長時間訓練 job 時，GPU 硬體故障（記憶體錯誤、PCIe 異常、NVLink 斷線）會導致 job 中途失敗。傳統做法是：job 失敗 → 手動排查 → 手動隔離故障節點 → 重新提交 job。這個流程耗時且容易在人為疏失下將 job 再次分配到同一故障節點。

AWS ParallelCluster 3.6.0+ 的 GPU 健康檢查功能，在每個 job 執行前自動執行 DCGM（Data Center GPU Manager）診斷，故障節點自動 DRAIN 並將 job 重新分配到健康節點。

## 2. 這個問題為什麼會發生?(背景)

| 根因 | 說明 |
|------|------|
| GPU 硬體故障率 | 大規模 GPU 叢集中，GPU 記憶體 ECC error、PCIe link 降級、NVSwitch 故障是已知的常態性問題 |
| 訓練 job 成本高 | 深度學習訓練 job 可能執行數小時至數天，中途失敗的代價是 GPU 時間與人力成本的雙重浪費 |
| Slurm 原生缺乏 GPU 診斷 | Slurm 作為 HPC 排程器，原生 prolog/epilog 機制僅檢查節點可用性，不檢查 GPU 健康狀態 |
| AWS 責任分界 | AWS 提供 GPU 執行個體但不主動監控 GPU 內部健康狀態，使用者需自行實作 |

推測: AWS 推出此功能是為了與 HyperPod 的 Deep Health Check 形成差異化。ParallelCluster 的 GPU 健康檢查較輕量（DCGM level 2），HyperPod 的 Deep Health Check 更全面（含 NCCL 測試、stress test），但 ParallelCluster 的 1 行設定即可啟用，進入門檻更低。

**GPU 健康檢查架構**：

```
Job 提交 → Slurm 排程 → prolog 觸發
                          ↓
              90_pcluster_health_check_manager
                          ↓
              DCGM dcgmi level 2 診斷
              ├── software (驅動/軟體棧)
              ├── memory (GPU 記憶體)
              ├── pcie (PCIe 狀態)
              └── memory bandwidth (記憶體頻寬)
                          ↓
              Pass ──→ Job 本體執行
              Fail ──→ 節點 DRAIN → Job 重新排隊 → 健康節點執行
```

## 3. 這個技術/政策是如何解決該問題的?

**實作細節**（基於 g4dn.xlarge 實測）：

| 項目 | 結果 |
|------|------|
| 驗證版本 | AWS ParallelCluster v3.15.1 (ap-northeast-1, Ubuntu 24.04) |
| 啟用方式 | `HealthChecks.Gpu.Enabled: true`（1 行 YAML 設定） |
| 執行時機 | Slurm prolog（job 開始直前） |
| 診斷工具 | NVIDIA DCGM level 2 |
| 診斷耗時 | g4dn.xlarge (Tesla T4, 單 GPU): 約 18 秒 |
| 診斷項目 | software / memory / pcie（全 Pass） |
| 失敗處理 | 節點 DRAIN → job 重新排隊 → 健康節點執行 |
| 日誌位置 | `/var/log/parallelcluster/slurm_health_check.log` + CloudWatch Logs |

**設定方式**（二擇一）：
```yaml
# 佇列層級（所有 compute resource 適用）
SlurmQueues:
  - Name: gpu
    HealthChecks:
      Gpu:
        Enabled: true

# 或個別 compute resource 層級（覆寫佇列設定）
SlurmQueues:
  - Name: gpu
    ComputeResources:
      - Name: g4dn
        HealthChecks:
          Gpu:
            Enabled: true
```

**注意事項**：

| 限制 | 說明 |
|------|------|
| 僅 NVIDIA GPU | 非 NVIDIA GPU 會跳過檢查 |
| prolog 逾時 | `BatchStartTimeout` 預設 180 秒，p4d.24xlarge 約 3 分鐘，p5.48xlarge (H100 x8) 約 5 分鐘可能逾時 |
| 大記憶體 GPU | 合計 GPU 記憶體 > 327,680 MiB (~320 GB) 不建議啟用 |
| 短 job 開銷 | 每次 job 啟動都執行診斷，短時間大量 job 時 overhead 顯著 |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 平台 | 機制 | 差異 |
|------|------|------|------|
| AWS ParallelCluster GPU Health Check | AWS (Slurm) | DCGM level 2 prolog | 1 行設定，輕量，僅 NVIDIA GPU |
| AWS HyperPod Deep Health Check | AWS (Slurm) | DCGM + NCCL test + stress test | 更全面但設定複雜，適合大規模訓練 |
| NVIDIA DCGM 獨立部署 | 自建/K8s | DCGM daemon + Prometheus exporter | 持續監控而非 job 前檢查，需自行整合排程器 |
| K8s GPU Health Check (NVIDIA GPU Operator) | K8s | GPU Feature Discovery + MIG Manager | K8s-native，適合容器化訓練 job |
| GCP GPU 健康監控 | GCP (GKE) | Cloud Monitoring + NVIDIA DCGM | GCP 原生整合，與用戶的 GKE 環境直接相關 |
| Slurm node health check (通用) | Slurm | 自訂 prolog script | 可擴展至非 GPU 檢查（磁碟、網路、記憶體） |

**對用戶的啟示**：
- 用戶技術棧為 GCP GKE，若團隊有 GPU 訓練需求（如 AI/ML 模型訓練），GCP 對應方案為 GKE + NVIDIA GPU Operator 的 GPU 健康監控，或使用 GCP Vertex AI 的託管訓練服務。
- 用戶正在學習 K8s CRD，NVIDIA GPU Operator 透過 CRD 管理 GPU 驅動、device plugin、DCGM exporter 等元件，是理解 K8s operator 模式的絕佳案例。
- 作為即將轉管理者，此文章展示的自動化故障轉移模式（detect → drain → reschedule）可應用於一般服務的 health check 與 auto-healing 設計。
