# Runtime-Sandbox（運行時沙箱隔離）技術分析

> 本報告將 microVM 與 gVisor 視為同一問題域（容器運行時安全隔離）的兩種不同技術路線進行整合分析。

## 1. 這個技術解決什麼問題？

Runtime-Sandbox 技術（microVM 生態 + gVisor）共同解決的核心問題是：

**在多租戶環境中運行容器化工作負載時，既要獲得容器等級的啟動速度和資源密度，又要獲得 VM 等級的安全隔離保證，補足傳統 Linux namespace+cgroup 無法防止 kernel 漏洞導致容器逃逸的根本缺陷。**

具體而言：
- **容器共享 Host kernel 的安全風險**：所有容器透過 syscall 接觸同一個 Host kernel binary（C 語言撰寫、無記憶體安全保護）。任何 kernel 漏洞（DirtyCow、特權提升等）都可讓攻擊者從單一容器逃逸至 Host，存取同一主機上所有其他容器的資料。
- **傳統 VM 的資源成本**：完整 VM 的記憶體開銷達數百 MB、啟動時間秒級，無法實現每台 Host 上千實例的高密度部署。
- **seccomp 的結構性限制**：僅能過濾 syscall 種類，無法防禦 TOCTOU race、無法精細控制 ioctl/prctl、不修復 kernel 自身 bug。

## 2. 這個問題為什麼會發生？（背景）

### 2.1 技術根源：Linux kernel 的單體攻擊面

```
                      ┌───────────────────────────────────┐
                      │      Linux Kernel (Monolithic)     │
                      │                                    │
                      │  VFS │ Network │ Memory │ Device   │
                      │  層   │  Stack  │  Mgmt  │ Drivers │
                      │      │         │        │  ioctl   │
                      ├──────┴─────────┴────────┴─────────┤
                      │      全部以 C 語言撰寫                │
                      │   (手動記憶體管理 → buffer overflow,  │
                      │    use-after-free, race condition)  │
                      │      全部子系統共享特權空間            │
                      └───────────────────┬────────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              ▼                           ▼                           ▼
        Container A                  Container B                  Container C
        (被入侵，利用                   (正常)                       (正常)
         kernel 漏洞 → 逃逸)
```

### 2.2 文章中明確提到的背景因素

| 因素 | 出處 |
|------|------|
| AWS Lambda 2014 上線以 per-customer EC2 instance 隔離，隨業務成長資源浪費嚴重 | Firecracker FAQ |
| 容器共用 kernel 導致 CVE-2016-5195 DirtyCow 等可實現容器逃逸 | 通用技術背景 |
| gVisor 官方聲明「Containers are not a sandbox」 | gVisor 架構指南 |
| QEMU 作為通用 VMM 功能過於龐雜（PCI、ACPI、USB、VGA 等），攻擊面大 | Red Hat KVM userspace 文章 |
| Google 內部需在 Borg 上安全執行任意用戶程式碼（multi-tenant） | gVisor 設計文件 |
| seccomp-bpf 存 TOCTOU race、無法精細過濾寬泛 syscall | gVisor 安全模型 |

### 2.3 通用技術背景

- **Linux syscall 介面規模**：x86_64 約 350+ 個 syscall，每個 syscall 的 kernel 實作都是 C 手動記憶體管理，邊界條件錯誤即可觸發漏洞。
- **namespace 的本質限制**：隔離的是「資源視圖」而非「kernel 程式碼路徑」。user namespace 理論上可映射 root→non-root，但因歷史 bug 頻繁，實際安全性不足。
- **Serverless/FaaS 崛起**：AWS Lambda (2014)、Fargate (2017)、Google Cloud Run 等服務要求毫秒級冷啟動 + 高密度部署 + 多租戶安全。這三個條件在傳統 VM 與容器間存在空白地帶。
- **虛擬化硬體演進**：Intel VT-x (2005) / AMD-V (2006) 引入硬體輔助虛擬化，KVM (2007) 將 Linux kernel 變成 hypervisor，降低了 VM 技術的進入門檻卻未解決傳統 VM 的資源浪費問題。

## 3. 這個技術是如何解決該問題的？

Runtime-Sandbox 有 **兩條技術路線**，對應兩種不同的隔離哲學：

```
          隔離技術光譜（攻擊面遞增 →）

    Hardware VM ────── microVM ────── gVisor ────── seccomp ────── runc
    (獨立kernel)     (KVM最小VM)   (用戶態kernel)  (規則過濾)   (共享kernel)
    ├── 最重 ──────── 中等 ────────── 較輕 ───────── 最輕 ────────┤
    ├── 最安全 ────── 高度安全 ────── 中高安全 ──── 低安全 ──────┤
    └── 最慢 ──────── 快 (~125ms) ─── 快 (~100ms) ─ 即時 ────────┤
```

---

### 路線一：microVM（KVM 硬體隔離路線）

**核心思路**：只保留 KVM 提供的最小硬體抽象，砍掉所有非必要設備模擬（PCI、ACPI、USB、VGA、BIOS），以最小攻擊面換取硬體級安全隔離，同時實現接近容器的啟動速度。

#### A. Firecracker（AWS）

```
機制要點：
┌──────────────────────────────────────────┐
│ 1. 最小設備模型（僅 5 個 virtio 設備）    │
│    virtio-net / virtio-block /            │
│    virtio-vsock / serial console /        │
│    最小鍵盤控制器（僅用於關機）             │
│                                           │
│ 2. 明確禁用（不存在於 binary 中）：        │
│    ✗ PCI bus  ✗ ACPI  ✗ USB controller   │
│    ✗ VGA display  ✗ Legacy BIOS          │
│    ✗ SATA/IDE controller                  │
│                                           │
│ 3. Rust 實作                              │
│    - 記憶體安全（無 UAF/buffer overflow）  │
│    - 執行緒安全                            │
│                                           │
│ 4. Jailer（加固層）                        │
│    每個 microVM 運行於獨立：               │
│    PID ns / mount ns / seccomp filter /    │
│    cgroup v1/v2                           │
│                                           │
│ 5. 效能指標（SPECIFICATION.md, CI 強制）： │
│    啟動 < 125ms / 記憶體 < 5MiB /VM/       │
│    建立速率 150 VM/s per host             │
└──────────────────────────────────────────┘
```

#### B. Kata Containers

```
機制要點：
┌──────────────────────────────────────────┐
│ 1. OCI runtime 相容（可直接替換 runc）    │
│    實作 CRI / OCI runtime spec            │
│    K8s RuntimeClass → 每個 Pod 一個專用 VM │
│                                           │
│ 2. 架構                                   │
│    ┌─ K8s Pod ──────────────────────┐    │
│    │  專用 VM (QEMU/Firecracker/     │    │
│    │  Cloud-Hypervisor)              │    │
│    │  ├ 獨立 guest kernel           │    │
│    │  ├ kata-agent（virtio-vsock）   │    │
│    │  └ containers                  │    │
│    └────────────────────────────────┘    │
│                                           │
│ 3. 支援多 hypervisor 後端                 │
│    QEMU（預設）/ Firecracker /            │
│    Cloud Hypervisor / Dragonball          │
│                                           │
│ 4. 企業支援：Red Hat OpenShift 整合       │
└──────────────────────────────────────────┘
```

#### C. 底層技術：KVM + virtio

```
Host 端                              Guest 端
┌──────────────────┐       ┌──────────────────────┐
│ virtio backend   │       │ virtio frontend        │
│ (vhost-user /    │◄─────►│ (virtio-net, blk,      │
│  vhost-net /     │       │  vsock, fs...)         │
│  vhost-vsock)    │       │                        │
│                  │       │ 傳輸: virtio-mmio       │
└──────┬───────────┘       └────────────────────────┘
       │
       ▼ KVM ioctl(/dev/kvm)
┌──────────────────┐
│ Linux KVM        │
├──────────────────┤
│ VT-x / AMD-V     │  ← EPT 二層位址轉換（GVA→GPA→HPA）
└──────────────────┘
```

關鍵差異：microVM 偏好 **virtio-mmio**（memory-mapped I/O）而非 virtio-pci，因為不需要 PCI bus 基礎設施。

---

### 路線二：gVisor（用戶態 kernel 攔截路線）

**核心思路**：在應用程式與 Host kernel 之間插入一個以記憶體安全語言（Go）重寫的「應用層 kernel」（Sentry），攔截全部 syscall 並在 userspace 處理，**不將任何 syscall 直接傳遞給 Host kernel**。

#### A. 架構總覽

```
┌──────────────────────────────────────────────┐
│          Application (OCI container image)    │  ← 未修改的 Linux binary
├──────────────────────────────────────────────┤
│            SENTRY（應用層 kernel，Go 實作）    │
│  Syscall(~200+ 個) │ VFS │ Netstack │ mm     │
│  獨立 Go 實作      │     │(TCP/IP)  │ 記憶體  │
├──────────────────────────────────────────────┤
│       PLATFORM: systrap（預設）/ KVM          │  ← syscall 攔截層
├──────────────────────────────────────────────┤
│              Host Linux Kernel                │
└──────────────────────────────────────────────┘
                     │
     ┌───────────────┴──────────────┐
     │           GOFER               │  ← 每個容器一個，代理檔案操作
     │  (9P 協定，透過 Unix socket    │
     │   傳遞 file descriptor)        │
     └──────────────────────────────┘
```

#### B. Sentry 的設計約束

| 約束 | 說明 |
|------|------|
| Go 語言 | 記憶體安全（GC、bounds checking），無 buffer overflow / use-after-free |
| 禁止 CGo | Sentry 核心不含任何 C 程式碼 |
| unsafe 隔離 | 所有 unsafe Go 封裝在 `*_unsafe.go` 檔案中 |
| 最小相依 | 核心套件外部依賴最小化 |
| 不傳遞 syscall | 每個 syscall 有獨立 Go 實作，不轉送 Host |

#### C. Systrap（syscall 攔截，2023 年起的預設 Platform）

```
Application thread
    │  syscall 指令
    ▼
[seccomp filter: SECCOMP_RET_TRAP]
    │
    ▼
SIGSYS → signal handler → 共享記憶體 → Sentry goroutine
    │                                        │
    │                           在 Go 環境處理 syscall
    │                                        │
    ◄──────── 結果透過共享記憶體回傳 ──────────┘
    │
    ▼
Application 繼續執行
```

x86_64 快速路徑：Systrap 將 binary 中的 `syscall` 指令修補為 `jmp *%gs:offset`，直接跳轉 Sentry，繞過 seccomp+signal 開銷。

#### D. runsc：OCI Runtime 替換

```bash
docker run --runtime=runsc -it ubuntu bash   # gVisor
docker run -it ubuntu bash                    # 標準 runc
```

Kubernetes 整合：
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
---
spec:
  runtimeClassName: gvisor
```

---

### 兩路線對比：微觀機制差異

```
microVM 路線（Firecracker/Kata） ──── vs ──── gVisor 路線

┌────────────────────┐          ┌────────────────────┐
│ Application        │          │ Application        │
│       ↓ syscall    │          │       ↓ syscall    │
│ Guest Kernel (C)   │          │ Sentry (Go)        │ ← 關鍵差異
│       ↓ vmexit     │          │       ↓ seccomp    │
│ KVM (kernel)       │          │ Host Kernel        │
│       ↓            │          │                    │
│ Hardware (VT-x)    │          │                    │
├────────────────────┤          ├────────────────────┤
│ 隔離來源：硬體 EPT  │          │ 隔離來源：Go 記憶體安全│
│ kernel 語言：C     │          │ kernel 語言：Go     │
│ syscall 相容性：完整│          │ syscall 相容性：~200+│
│ 啟動時間：~125ms   │          │ 啟動時間：~100ms    │
│ 記憶體開銷：~5MB   │          │ 記憶體開銷：~20-50MB│
│ 需要 KVM：是       │          │ 需要 KVM：否(systrap)│
│ 需維護 guest kernel│          │ 無 guest kernel     │
└────────────────────┘          └────────────────────┘
```

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 4.1 替代方案 DA 表

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|---------|-------------|---------------|----------------|
| **傳統 Container** (runc/crun) | 使用 Linux namespace + cgroup 隔離 process，應用直接呼叫 Host kernel syscall。 | 信任 Host kernel 安全；工作負載之間無需強隔離。 | 攻擊面 = Host kernel 全部 syscall 介面（350+）；kernel 漏洞導致所有容器一起淪陷。 | 啟動 ~100ms，記憶體 ~1MB/容器，效能接近原生。 |
| **seccomp-bpf** | 在 kernel 層透過 BPF 過濾器限制 process 可呼叫的 syscall 集合。 | 能準確列舉最小 syscall 需求；應用行為可預測。 | TOCTOU race（多線程可修改參數）；無法過濾 ioctl 子操作；不防禦 kernel 自身漏洞。 | 幾乎零效能損失；不提供 kernel 0-day 保護。 |
| **Unikernel** (MirageOS, OSv, Nanos) | 應用與 kernel 合併編譯為單一 binary，直接在 hypervisor 上執行，無 guest OS 層。 | 應用必須用支援的語言重寫（OCaml、C 等）；無法執行任意 Linux binary。 | 無法執行未修改的應用；缺多工/多用戶能力；除錯困難。 | 啟動 < 10ms，記憶體 < 2MB，攻擊面極小（無 shell、無多餘 syscall）。 |
| **傳統 VM** (QEMU full) | 全設備模擬（PCI、ACPI、USB、VGA、BIOS），每個 VM 有完整 guest kernel，透過 KVM 硬體隔離。 | 可接受百 MB 級記憶體開銷與秒級啟動；Host 需支援 KVM；現有 libvirt/OpenStack 管理基礎設施。 | 啟動 1-5s，記憶體 100-500MB+/VM，攻擊面包含完整 QEMU 裝置模擬程式碼。 | 完整 OS 相容性（Linux/Windows）；支援 live migration、snapshot、GPU passthrough。 |

### 4.2 各方案在隔離光譜中的定位

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Runtime 隔離技術選擇矩陣                          │
│                                                                          │
│              runc    seccomp   gVisor   microVM   Kata     傳統VM       │
│  ────────────┬────────┬─────────┬─────────┬────────┬─────────┬──────    │
│  隔離基礎     │ kernel │ kernel  │ Go應用層│ KVM    │ KVM     │ KVM      │
│              │ 軟體   │ 過濾器   │ kernel  │ 硬體   │ 硬體    │ 硬體     │
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  kernel共享  │ 是     │ 是      │ 否      │ 否     │ 否      │ 否       │
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  記憶體安全   │ 否     │ 否      │ 是(Go)  │ 是(Rust)│ 部分    │ 否       │
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  啟動時間     │ ~100ms │ ~0      │ ~100ms  │ ~125ms │ ~1s     │ ~1-5s    │
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  記憶體/實例  │ ~1MB   │ 0       │ ~20-50MB│ ~5MB   │ ~100MB  │ ~100-500MB│
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  syscall相容 │ 完整   │ 受限    │ ~200+個 │ 完整   │ 完整    │ 完整      │
│  ────────────┼────────┼─────────┼─────────┼────────┼─────────┼──────    │
│  OCI相容     │ 原生   │ 附加    │ runsc   │ 需轉接 │ 原生    │ 否        │
│  ────────────┴────────┴─────────┴─────────┴────────┴─────────┴──────    │
│                             需求方向 →                                   │
│              密度優先 ◄─────────────────────────► 安全優先               │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 切入點差異總覽

| 方案 | 解決同一問題的切入點 |
|------|-------------------|
| **microVM** | 從「硬體虛擬化」角度切入：利用 KVM + EPT 硬體隔離，但砍掉傳統 VM 的所有非必要設備模擬。信任硬體邊界勝於軟體正確性。 |
| **gVisor** | 從「syscall 介面」角度切入：不虛擬化硬體，而是在 userspace 用記憶體安全語言重寫 kernel 的 syscall 處理邏輯。信任語言層的記憶體安全勝於硬體隔離。 |
| **runc** | 不做任何額外隔離，完全依賴 Host kernel 的安全性。適合同一信任域內的 workload。 |
| **seccomp** | 在 kernel 入口處設柵欄，限制可呼叫的 syscall 種類。不改變 kernel 自身的安全性。 |
| **Unikernel** | 從「消除 OS 層」角度切入：將應用與 kernel 合併為單一 binary，連 guest kernel 的攻擊面都消除。代價是相容性極低。 |
| **傳統 VM** | 從「完整硬體模擬」角度切入：每個 tenant 有完整獨立的硬體視圖和 OS。安全最強但資源最浪費。 |

---

## 5. 實際生產環境與導入決策點

### 5.1 各技術的實際生產使用者

#### microVM 路線

| 技術 | 主要使用者 | 規模 | 場景 |
|------|-----------|------|------|
| **Firecracker** | AWS Lambda | 每月數兆次執行、數十萬活躍客戶 | Serverless function |
| **Firecracker** | AWS Fargate | 每週數千萬容器執行 | Serverless container |
| **Firecracker** | Fly.io | ~300ms 端到端 VM 啟動 | Edge 運算、FaaS |
| **Kata Containers** | Red Hat OpenShift | 企業級 K8s 整合 | 合規行業（金融/醫療）容器隔離 |
| **Kata Containers** | Baidu / Huawei / ZTE / 中國移動 | 電信級雲原生基礎設施 | NFV、邊緣運算、多租戶容器 |
| **Cloud Hypervisor** | Microsoft Azure (OpenHCL) | Azure Boost paravisor 架構 | 雲端通用 workload |
| **QEMU microvm** | Red Hat 生態 | 實驗性，~100ms 啟動 | 結合 libvirt 安全框架的輕量 VM |

#### gVisor 路線

| 使用者 | 規模 | 場景 |
|--------|------|------|
| **Google Cloud Run** | 每月數百萬請求（未公開精確數字） | 所有 serverless 容器實例預設執行於 gVisor |
| **GKE Sandbox** | GKE 內建 RuntimeClass | 多租戶 Pod 隔離、GPU/TPU 支援 |
| **Google 內部 Borg** | 「每日數百萬 gVisor sandbox 實例」 | 內部 multi-tenant 工作負載隔離 |
| **Ant Group** | 10 萬+ 生產實例、70% app <1% overhead | 金融級交易系統（含雙十一） |
| **Cloudflare Pages** | 構建基礎設施 | CI/CD build sandbox（啟動從 2+ 分鐘降至 2-3 秒） |
| **OpenAI** | 內部研究基礎設施 | 高風險任務代碼執行 sandbox（PCI-DSS/SOC2/ISO27001 認證） |
| **Anthropic** | 內部系統 | 開源貢獻者 |
| **Modal** | 雲端資料/AI 平台 | 主要 runtime 隔離機制（HIPAA 合規） |
| **DigitalOcean App Platform** | PaaS 平台 | 用戶容器沙箱 |

### 5.2 導入決策框架

#### 決策維度與各方案對比

| 決策維度 | runc | gVisor | Firecracker | Kata | 傳統 VM |
|---------|------|--------|-------------|------|---------|
| **安全隔離強度** | ★☆☆☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **啟動速度** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| **資源密度** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| **syscall 相容性** | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★★★ |
| **營運複雜度** | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| **無需 KVM** | ✓ | ✓ (systrap)| ✗ | ✗ | ✗ |
| **GPU 支援** | ✓ | 實驗性 | ✗ | 有限 | ✓ |
| **Live Migration** | ✗ | ✗ | ✗（設計上不做）| ✓ (QEMU) | ✓ |
| **Windows Guest** | ✗ | ✗ | ✗ | ✗ | ✓ |

#### 場景 → 推薦方案

```
                        你的使用場景是什麼？
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    自建平台運行            企業 K8s 合規         公有雲 Serverless
    第三方代碼              需求（PCI/HIPAA）      選型
          │                   │                   │
          ├─ 密度優先          ├─ GCP → GKE        ├─ GCP → Cloud Run
          │  → gVisor         │  Sandbox           │  (gVisor 內建)
          │                   │  (gVisor 內建)     │
          ├─ 安全優先          │                   ├─ AWS → Lambda/
          │  → Firecracker    ├─ AWS → Kata        │  Fargate
          │  (自建 VMM 層)    │  on EKS            │  (Firecracker 內建)
          │                   │                   │
          └─ K8s 原生整合      ├─ 需 full kernel   ├─ 自建 →
              → Kata          │  ABI + live        │  gVisor 或
              Containers      │  migration         │  Firecracker
                              │  → Kata (QEMU)    │
```

#### gVisor vs Firecracker 的核心取捨

| 考量 | gVisor | Firecracker |
|------|--------|-------------|
| **隔離哲學** | 「攔截所有 syscall，不讓應用碰到 Host kernel」 | 「給每個 tenant 一個最小的 VM，用硬體隔離」 |
| **信任基礎** | 信任 Go 語言記憶體安全 + Sentry syscall 實作正確性 | 信任硬體虛擬化 (VT-x/AMD-V) + KVM + Rust VMM 正確性 |
| **攻擊突破條件** | 需同時攻破 Sentry（Go）和 Host kernel（C）——兩者不共享程式碼 | 需攻破 Firecracker VMM（Rust）或 guest kernel（C）並突破 KVM 邊界 |
| **何時最適合** | CPU-bound workload、需要無 KVM 環境（巢狀虛擬化）、追求營運簡單（無 guest kernel 維護） | 需要最強安全保證（hostile multi-tenancy）、已有 KVM 基礎設施、合規審計偏愛硬體 VM 語義 |
| **何時不適合** | I/O 密集（VFS overhead）、網路密集（netstack overhead）、需要 `io_uring`/`bpf`/`perf_event_open` | 無 KVM 環境、Windows guest、GPU compute（部分）、需要 live migration |

#### 合規考量

| 合規框架 | Firecracker 認證路徑 | gVisor 認證路徑 |
|---------|---------------------|----------------|
| **PCI-DSS** | AWS Lambda/Fargate 為 PCI-DSS 合格服務 | OpenAI 以 gVisor 達成 PCI-DSS v4.0.1 認證 |
| **HIPAA** | AWS 簽署 BAA（Lambda/Fargate） | GCP 簽署 BAA（Cloud Run/GKE Sandbox） |
| **FedRAMP** | AWS GovCloud FedRAMP High 覆蓋 Lambda/Fargate | GCP FedRAMP High 覆蓋 serverless 產品 |
| **SOC 2** | AWS + Fly.io + Modal 皆為 SOC 2 | Google + OpenAI + Modal 皆為 SOC 2 |
| **審計友善度** | 硬體 VM 邊界 = 審計員易理解 | 需額外說明 user-space kernel 如何提供等效隔離 |

#### 已知生產環境限制

**gVisor 常見問題：**
- 74 個 syscall 未實作或部分實作：`io_uring`（預設禁用）、`bpf`、`perf_event_open`、`setfsuid/setfsgid`
- syscall 密集 workload：KVM 平台 ~830ns/syscall（原生 ~62ns）——約 13 倍落差
- I/O-heavy 效能明顯下降（Redis 2-10x、Apache static file 5-10x）
- GKE Sandbox 無 port-forward、無 container-level 記憶體指標、無 Traffic Director
- Go runtime 需調優（timer buckets、GOMAXPROCS、GC 觸發閾值）

**microVM 常見問題：**
- Cold start：即使 Firecracker < 125ms 啟動，加上 image pull + app init 仍可能秒級；需 pre-warm 或 snapshot
- Guest kernel 維護：需自行做 CVE 修補、kernel config 必須匹配 VMM 預期
- Firecracker 無 live migration 設計、無 PCI、無 GPU、無 Windows
- Kata 記憶體開銷較大（~50-100MB/pod），但 KSM dedup + ballooning 可緩解
- 網路：所有流量經 host TAP device，無硬體卸載（TSO/LRO），高 PPS 負載受影響

---

## 參考來源

- Firecracker 官方: https://firecracker-microvm.github.io/
- Firecracker SPECIFICATION.md (GitHub)
- Kata Containers: https://katacontainers.io/
- QEMU microvm 文件: https://www.qemu.org/docs/master/system/i386/microvm.html
- Cloud Hypervisor: https://github.com/cloud-hypervisor/cloud-hypervisor
- Red Hat KVM userspace (Paolo Bonzini, 2019)
- gVisor 官方文件: https://gvisor.dev/docs/
- gVisor 架構指南: https://gvisor.dev/docs/architecture_guide/
- gVisor 安全模型: https://gvisor.dev/docs/architecture_guide/security/
- gVisor 效能指南: https://gvisor.dev/docs/architecture_guide/performance/
- Systrap 發布: https://gvisor.dev/blog/2023/04/28/systrap-release/
- Ant Group gVisor 生產經驗: https://gvisor.dev/blog/2021/12/02/running-gvisor-in-production-at-scale-in-ant/
- Cloudflare Pages 構建改進: https://blog.cloudflare.com/cloudflare-pages-build-improvements/
- AWS Firecracker 公告 (Jeff Barr, Nov 2018)
- GKE Sandbox 文件: https://cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods
- Cloud Run: https://cloud.google.com/run/docs/overview/what-is-cloud-run
- Modal 安全: https://modal.com/docs/guide/security
- gVisor 使用者頁面: https://gvisor.dev/users/
- gVisor Linux/amd64 Syscall Support: https://gvisor.dev/docs/user_guide/compatibility/linux/amd64/
- Google/gvisor GitHub: https://github.com/google/gvisor
- OCI Runtime Specification: https://github.com/opencontainers/runtime-spec
