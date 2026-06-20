# Apple Container（apple/container）技術分析

> 調研來源：[apple/container](https://github.com/apple/container) README、`docs/technical-overview.md`、底層 [apple/containerization](https://github.com/apple/containerization) README
> 專案狀態：1.0.0 已於 2026-06-09 發布（Apache-2.0，38.9k stars）

---

## 1. 這個技術解決什麼問題？

**在 macOS 上原生、安全且高效地建立與執行 Linux 容器。**

具體被解決的問題：

| 問題面向 | 被解決的具體問題 |
|---|---|
| 隔離強度 | 傳統 macOS 容器方案把多個容器塞進單一共享 Linux VM，容器之間僅靠 Linux namespace 隔離；`container` 為每個容器起一個獨立輕量 VM，達到 VM 級隔離 |
| 隱私 / 資料曝露 | 共享 VM 模型需把「未來可能用到」的資料全掛進 VM 再選擇性掛給容器；`container` 只把必要資料掛進各 VM，縮小曝露面 |
| 映像檔相容性 | 過去 macOS 容器工具常綁定私有格式或特定 registry；`container` 完全消費 / 產出 OCI 標準映像檔，與任何 OCI registry 與 OCI runtime 互通 |
| macOS 原生整合 | 既有多為 Go 生態跨平台工具，與 macOS 系統服務整合淺；`container` 以 Swift 撰寫，整合 Virtualization.framework、vmnet、XPC、Launchd、Keychain、unified logging |

**模糊點註記**：README 對「lightweight VM」的具體資源佔用（CPU、固定記憶體底線）未給出數字，僅以「sub-second boot」「less memory than full VMs」描述。

---

## 2. 這個問題為什麼會發生？（背景）

### 明確提到（來自 README / technical-overview）

- **macOS 核心不支援 Linux container**：macOS 核心為 XNU，不提供 Linux 的 namespace / cgroup；要跑 Linux container 必須先跑 Linux 核心。technical-overview 原文：*「the typical way to run Linux containers is to launch a Linux virtual machine (VM) that hosts all of your containers.」*
- **macOS 26 帶來新能力**：README 與 technical-overview 皆明確指出 `container`「takes advantage of new features and enhancements to virtualization and networking in this release」，且明示不支援舊版 macOS。macOS 26 對 Virtualization.framework 與 vmnet 的強化是 per-container VM 模型可行的前提。
- **共享 VM 模型的固有權衡**：technical-overview 直接點名共享 VM 在 security、privacy、performance 三面向的取捨，作為 `container` 改採 per-container VM 的動機。

### 通用技術背景（作者未明說，自行補充）

- Linux container 生態（Docker、OCI、Kubernetes）以 Linux 核心能力為基礎，macOS 長期以來是「二等公民」，需透過 VM 包一層。
- 蘋果自家 Virtualization.framework（macOS 11+ 引入，Swift API）讓「原生起 ARM64 Linux VM」變可行，但早期版本功能不足以支撐 per-container 級別的輕量 VM。
- Apple Silicon（M 系列）統一 ARM64 架構，使 Apple 自家 VM 跑 ARM64 Linux 容器不再需要指令集翻譯；Rosetta 2 for Linux 則補足 x86_64 容器需求。

---

## 3. 這個技術是如何解決該問題的？

### 3.1 分層架構

```
┌──────────────────────────────────────────────────────────────┐
│  container CLI（使用者介面）                                  │
└───────────────┬──────────────────────────────────────────────┘
                │ client library
                ▼
┌──────────────────────────────────────────────────────────────┐
│  container-apiserver（Launch agent，container system start） │
│  對外提供管理 API                                              │
└──┬─────────────────────────────────┬─────────────────────────┘
   │ XPC                              │ XPC
   ▼                                  ▼
┌────────────────────┐         ┌──────────────────────┐
│ container-core-    │         │ container-network-   │
│ images             │         │ vmnet                │
│ (映像檔管理 /       │         │ (虛擬網路 vmnet)      │
│  本地 content store)│         └──────────────────────┘
└────────────────────┘
   │ 每建立一個 container
   ▼
┌──────────────────────────────────────────────────────────────┐
│  container-runtime-linux（per-container runtime helper）      │
│  └─ 該 container 專屬的輕量 Linux VM                          │
│      └─ vminitd（init 系統，gRPC over vsock）                 │
│          └─ 容器化行程                                         │
└──────────────────────────────────────────────────────────────┘
```

關鍵點：**每建立一個 container，`container-apiserver` 就啟動一個 `container-runtime-linux` 與其專屬 VM**，而非把容器塞進共享 VM。

### 3.2 底層機制（來自 containerization package）

| 機制 | 做法 |
|---|---|
| 輕量 VM | 以 Virtualization.framework 起 ARM64 Linux VM，每容器一個 |
| 快速開機 | 使用優化的 minimal Linux kernel config（containerization/kernel 目錄提供），sub-second boot |
| init 系統 | `vminitd`：VM 內 PID 1，對外透過 **vsock** 暴露 **gRPC** API，供 host 設定 runtime 環境、啟動行程、收發 I/O / signal / event |
| 映像檔 | 完全 OCI 相容：`ContainerizationOCI` 處理映像檔格式、registry client；`ContainerizationEXT4` 建立 ext4 rootfs；`ContainerizationNetlink` 操作 netlink |
| 網路 | vmnet framework 提供虛擬網路，每容器可配獨立 IP（macOS 26），不需逐一 port forwarding |
| 跨架構 | Rosetta 2 for Linux 跑 linux/amd64 容器 |
| 系統整合 | XPC（IPC）、Launchd（服務管理）、Keychain（registry 認證）、unified logging（日誌） |

### 3.3 使用流程示意

```bash
# 1. 啟動系統服務（Launch agent 載入 container-apiserver）
container system start

# 2. 拉取 OCI 映像檔（container-core-images 透過 OCI client 從 registry 拉）
container pull docker://nginx:latest

# 3. 執行 → 起一個專屬輕量 VM → vminitd → 容器行程
container run --rm nginx:latest

# 4. 建立映像檔 → 產出 OCI 格式 → 可推回任何 registry
container build -t myapp .
container push docker://registry/myapp:1.0
```

### 3.4 已知限制（technical-overview 明列）

- **記憶體回收不全**：macOS Virtualization.framework 對 memory ballooning 僅部分支援；容器內釋放的記憶體頁不會歸還 host，多個高記憶體容器需定期重啟。
- **macOS 15 降級限制**：網路隔離（容器間無法互通）、無多網路、IP 位址可能與 vmnet subnet 不一致導致斷網。

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

> macOS 上執行 Linux 容器的同類方案，依「VM 模型」分兩派：
> - **共享 VM 派**：一個 Linux VM 內跑多個容器（Docker Desktop、Colima、OrbStack、Lima）
> - **per-container VM 派**：每容器一個 VM（Apple Container、Kata Containers 概念）

### DA 表（定性定量評估）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|---|---|---|---|---|
| **Apple Container** | 每容器一個輕量 Linux VM（Virtualization.framework + vminitd + vsock gRPC），OCI 相容 | Apple Silicon Mac、macOS 26、需安裝系統服務 | 記憶體回收受 macOS ballooning 限制；僅 macOS 26 完整支援；macOS 15 多項功能降級 | VM 級隔離與隱私、sub-second 開機、最小資料掛載、與 macOS 系統服務深度整合 |
| **Docker Desktop** | 單一共享 Linux VM（WSL2 / HyperKit / Apple Virtualization.framework），VM 內跑 containerd，OCI 相容 | x86_64 或 Apple Silicon Mac；商業用途需付費 | 共享 VM 隔離弱於 per-container VM；需把資料全掛進 VM；資源佔用固定底線高 | 生態最完整、GUI、Compose、K8s 整合、跨平台一致 |
| **Colima** | 以 Lima 為底層起共享 Linux VM，VM 內跑 Docker daemon，CLI 控制 | Apple Silicon 或 Intel Mac；開源免費 | 共享 VM 模型固有取捨；功能較 Docker Desktop 陽春 | 輕量、免費、資源佔用低於 Docker Desktop |
| **OrbStack** | 共享 Linux VM + 自家優化 runtime，OCI 相容，macOS 原生 | Apple Silicon Mac；商用需付費 | 共享 VM 隔離；閉源 | 啟動極快、CPU/記憶體佔用低、UX 接近 Docker Desktop |
| **Lima** | 起 Linux VM（QEMU 或 Apple Virtualization.framework），VM 內跑 containerd / Docker / K8s | 跨平台基底；開源 | 需手動設定；共享 VM 模型 | 最底層通用方案，Colima / Finch 等建構其上 |

### 各方案切入點差異

| 切入點 | Apple Container | Docker Desktop / Colima / OrbStack / Lima |
|---|---|---|
| **隔離邊界** | 容器邊界＝VM 邊界（每容器一 VM） | 容器邊界＝Linux namespace（VM 是共用的外殼） |
| **資料掛載哲學** | 只掛必要資料進各 VM | 預先把資料掛進共享 VM |
| **與 macOS 整合深度** | 原生 Swift + Virtualization/vmnet/XPC/Launchd/Keychain | 多為 Go 跨平台工具，與 macOS 系統服務整合較淺 |
| **目標平台** | 僅 Apple Silicon + macOS 26 | 跨 Apple Silicon / Intel、跨平台 |
| **映像檔格式** | OCI 標準 | OCI 標準 |
| **適用場景** | 重視隔離與隱私、願意綁定 macOS 26 的開發者 | 重視生態完整、跨平台一致性、或無法升級 macOS 26 的場景 |

### 補充思考方式

- **「container =輕量 VM」並非 Apple 首創**：Kata Containers 早在 Linux 雲端場景即採用「每容器一 VM」模型（QEMU/firecracker）。Apple Container 的差異在於把此模型搬到 macOS、用 Swift + Virtualization.framework 原生實作，並以 macOS 26 為前提。
- **「共享 VM vs per-container VM」是核心取捨軸**：共享 VM 換來的是低資源底線與生態成熟；per-container VM 換來的是隔離與隱私。Apple Container 的存在讓此取捨在 macOS 上首次成為可選項。