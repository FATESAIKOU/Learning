# LingBot-Map — Geometric Context Transformer for Streaming 3D Reconstruction

> 分析日期：2026-05-31
> 論文：arXiv 2604.14141 (2026-04-15)
> 倉庫：https://github.com/robbyant/lingbot-map
> 授權：Apache 2.0

---

## 1. 這個技術解決什麼問題？

**從連續影片串流中，即時還原相機姿態（camera pose）與三維點雲（point cloud），且必須同時滿足幾何精度、時間一致性與計算效率三個條件。**

具體來說，LingBot-Map 解決的是「streaming 3D reconstruction」問題：
- 輸入：一個影片串流（連續 RGB 幀，無其他感測器輔助）
- 輸出：每幀的相機 6-DoF 姿態（外參） + 深度圖 + 世界坐標點雲
- 約束：需以 feed-forward 方式即時處理（非離線優化），支援超過 10,000 幀的長序列而不發生姿態漂移（drift）

---

## 2. 這個問題為什麼會發生？（背景）

### 2-1. 文章中明確提到的技術背景

- **傳統 visual SLAM / SfM 依賴 iterative optimization**（如 bundle adjustment、BA），每次新幀加入都需要重新最佳化，計算量大，無法達到 real-time streaming。
- **既有 feed-forward 方法（如 VGGT）雖然快，但是在 batch-mode 設計：** 一次性輸入所有畫面做全局 attention，無法處理 streaming 場景（新增幀時需要重跑整個模型）。
- **Streaming 場景的核心困難是「長程漂移（long-range drift）」：** 若模型只靠最近幾幀的局部資訊推估姿態，累積誤差會隨時間線性增長，軌跡會逐漸偏離真實路徑。

### 2-2. 通用技術背景（從外部補充）

| 因素 | 說明 |
|------|------|
| **Transformer 架構的序列限制** | 標準 Transformer 的 self-attention 計算量和記憶體是 O(N^2) 對序列長度，無法直接處理 10,000+ 幀的 streaming 場景 |
| **SLAM 的前端/後端分離** | 傳統 SLAM（如 ORB-SLAM、DROID-SLAM）將系統拆為「前端（局部追蹤）」和「後端（全局優化）」，後端的 BA 在大場景下成為瓶頸 |
| **KV cache 膨脹問題** | 若每次新幀都把其 token 追加進 KV cache，cache 大小隨幀數無限制增長，記憶體和延遲雙雙失控 |
| **RoPE 訓練範圍限制** | 使用 Rotary Position Embedding 的 Transformer 在訓練時只見過最多 320 views 的序列（如 LingBot-Map 的設計），超過此範圍後 positional encoding 失效導致效能下降 |

---

## 3. 這個技術是如何解決該問題的？

### 3-1. 核心架構：Geometric Context Transformer（GCT）

GCT 的 attention 機制拆分為三種互補的 attention context，各自處理不同尺度的幾何資訊：

```
                 ┌──────────────────────────┐
                 │   GCT 單幀處理循環         │
                 │                          │
 輸入影像 ──────►│ ① Anchor Context          │
  (第 t 幀)      │   (空間定位 grounding)     │
                 │   ├─ 跨幀學習到的 anchor   │
                 │   │   token 集合           │
                 │   └─ 當前幀 token 與        │
                 │       anchor token 做交叉   │
                 │       attention             │
                 │                          │
                 │ ② Pose-Reference Window   │
                 │   (稠密幾何線索)            │
                 │   ├─ 以當前幀為中心取       │
                 │   │   最近 N 個 keyframe    │
                 │   └─ 計算局部 cross-        │
                 │       attention             │
                 │                          │
                 │ ③ Trajectory Memory        │
                 │   (長程漂移修正)            │
                 │   ├─ 壓縮的軌跡表徵          │
                 │   └─ 與記憶 token 交互       │
                 │      修正累積誤差            │
                 └──────────────────────────┘
```

#### ① Anchor Context（坐標接地）

- **目的**：提供一個全局共用的坐標參考系。將 3D 空間中的固定參考點學習為一組可訓練的 anchor token。
- **機制**：每個新幀的 image token 與 anchor token 做 cross-attention，將該幀的局部表徵「接地」到同一個全局坐標框架中。這取代了傳統 SLAM 中每個幀自己估計自己坐標系的做法。
- **偽碼概念**：

```python
# 每幀處理時
frame_tokens = image_encoder(frame)            # [1, N_patches, D]
anchor_tokens = self.learnable_anchors         # [K, D]  可學習參數，不隨幀變化
grounded = cross_attention(frame_tokens, anchor_tokens)  # Q=frame, K,V=anchor
```

#### ② Pose-Reference Window（局部稠密幾何線索）

- **目的**：透過鄰近幀之間的 attention 捕捉稠密幾何對應（如特徵點的 2D-2D 匹配），推估當前幀的相對位移。
- **機制**：以 sliding window 選取最近 N 個 keyframe（keyframe 指被存入 KV cache 的幀），在 window 內做 cross-attention。這類似 stereo matching 或 optical flow 的效果，但在 attention 空間中完成。

```python
# 窗口 attention
window_keyframes = kv_cache[-window_size:]    # 最近 N 個 keyframe 的 KV
frame_output = cross_attention(frame_tokens, window_keyframes)
```

#### ③ Trajectory Memory（長程漂移修正）

- **目的**：儲存壓縮的歷史軌跡表徵，在必要時回溯修正因為只依靠局部窗口而產生的累積誤差。
- **機制**：維護一個固定大小的 trajectory memory token 集合，每過一段間隔將當前幀的資訊壓縮編碼寫入。當模型偵測到 loop closure 或 drift 時，透過與 memory 的 attention 進行全局一致性校正。

```python
# 週期性寫入軌跡記憶
if frame_idx % memory_interval == 0:
    trajectory_memory.append(compress(frame_tokens))
# 每幀都可與軌跡記憶做 attention
corrected = cross_attention(frame_tokens, trajectory_memory)
```

### 3-2. Paged KV Cache Attention（記憶體管理）

透過 FlashInfer 的 paged KV cache 技術管理 streaming attention 的記憶體：
- **分頁管理**：將 KV cache 分割為固定大小的 pages（類似作業系統的虛擬記憶體分頁），不需要的 page 可以釋放。
- **Keyframe Interval**：只將每 N 幀中的 keyframe 存入 KV cache。非 keyframe 的幀仍然產生預測輸出，但不佔據 cache 空間。
- **Windowed Mode**：當序列長度超過 RoPE 訓練範圍（~320 幀）時，自動重置 cache 並以 sliding window 方式處理，window 之間用 overlap 幀維持連續性。

### 3-3. 架構層級結構

```
┌──────────────────────────────────────────────────────────┐
│                     LingBot-Map                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Input (RGB image stream)                                │
│      │                                                   │
│      ▼                                                   │
│  ┌────────────┐  DINOv2 backbone (ViT patch embedding)  │
│  │ Image Enc  │  + trainable adapter                     │
│  └────────────┘                                          │
│      │                                                   │
│      ▼                                                   │
│  ┌──────────────────────────────────────┐               │
│  │       Aggregator (StreamAggregator)   │               │
│  │  ┌────────────────────────────────┐  │               │
│  │  │ GCT Attention Block × N layers │  │               │
│  │  │  ├─ Anchor Context Attention   │  │               │
│  │  │  ├─ Pose-Reference Attention   │  │               │
│  │  │  └─ Trajectory Memory Attn     │  │               │
│  │  └────────────────────────────────┘  │               │
│  └──────────────────────────────────────┘               │
│      │                                                   │
│      ▼                                                   │
│  ┌───────────────┬───────────────┬──────────────────┐   │
│  │  Camera Head   │  Depth Head   │  Point Cloud     │   │
│  │  (pose iter)   │  (DPT-like)   │  (unprojection)  │   │
│  └───────────────┴───────────────┴──────────────────┘   │
│      │               │               │                   │
│      ▼               ▼               ▼                   │
│   6-DoF pose     depth map      world point cloud        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3-4. 推理模式

| 模式 | 檔案 | 適用場景 |
|------|------|----------|
| **Streaming** | `gct_stream.py` | <= 320 幀的短序列，single-pass 完整推理 |
| **Windowed** | `gct_stream_window.py` / `gct_stream_window_v2.py` | > 3000 幀的長序列，sliding window 分割處理 |

### 3-5. 程式碼架構對照

| 模組 | 檔案 | 職責 |
|------|------|------|
| `aggregator/stream.py` | StreamAggregator | 管理 streaming 狀態（KV cache、anchor token），每幀調用 GCT attention |
| `heads/camera_head.py` | CameraHead | 從 aggregated token 推估相機 6-DoF 姿態（含 iterative refinement） |
| `heads/dpt_head.py` | DPTHead | DPT-like 架構，從 token+image 特徵預測 depth map |
| `layers/attention.py` | Multi-head attention with FlashInfer | 核心 attention 實現，支援三種 context pattern |
| `layers/flashinfer_cache.py` | Paged KV Cache | 基於 FlashInfer 的 paged KV cache wrapper |
| `layers/rope.py` | 3D Rotary Position Embedding | 在 patch + frame id 維度上編碼空間-時間位置 |
| `models/gct_base.py` | GCTBase | 基礎模型定義，載入 checkpoint 權重 |
| `models/gct_stream.py` | GCTStream | Streaming 推理包裝 |
| `models/gct_stream_window.py` | GCTStreamWindow | Windowed 推理包裝 |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 4-1. Decision-Alternatives 對照表（DA 表）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|----------------|
| **DROID-SLAM** (NeurIPS 2021) | 基於 RAFT 的 recurrent iterative update + Dense Bundle Adjustment (DBA) layer，以 GRU 循環更新相機姿態與深度，每步透過 DBA layer 以 Gauss-Newton 做全局 BA 校正 | 需 GPU 具備 11GB+ VRAM；序列不可太長否則 DBA 層計算量隨幀數增加；需提供相機內參 calib 檔 | 計算量為 O(N^2)（DBA 層）；推理速度約 3 FPS，遠低於 real-time；在長序列上 BA 層的線性系統求解時間會成為瓶頸 | 在小於數百幀的序列上精確度極高，支援 Mono/Stereo/RGB-D |
| **VGGT** (CVPR 2025 Best Paper) | Feed-forward Transformer 一次性處理所有輸入視圖，使用 Alternating-Attention 機制在幀間與幀內做雙向 attention，直接輸出相機參數、深度圖、點圖、3D 點軌跡 | 需在推理前取得全部視圖（batch mode），無法處理 streaming 的新增幀；輸入幀數受限於 GPU 記憶體 | 新增幀需要重新處理全部視圖；長序列受 GPU VRAM 限制；無 trajectory memory 機制，批次推理無長程漂移修正能力 | 在靜態場景的多視圖重建（如 CO3D）上達 SOTA，AUC@30 = 90.37，推理 < 1 秒；支援 1 到數百張視圖 |
| **ORB-SLAM3** (TRO 2021) | 特徵點提取（ORB）+ 局部 BA + 全局 BA + loop closure detection + pose graph optimization，經典優化路線 | 需要紋理豐富的場景（依賴 ORB 特徵點）；對低紋理/動態場景容易追丟；需 CPU 即可執行 | 特徵點數量與 BA 規模影響速度；loop closure 依賴 bag-of-words 匹配，誤匹配可能導致軌跡斷裂；無深度/點雲輸出（僅稀疏地圖） | 在特徵豐富場景下精度極高（公分級），CPU real-time（~30 FPS，依賴特徵點密度） |
| **DUSt3R / MASt3R** (CVPR 2024) | 雙幀 stereo reconstruction 基礎模型，以 ViT 做 dense matching，輸出 pixel-aligned 3D pointmap；多幀時透過 pairwise 對齊拼接 | 需將多幀分解為 pair-wise 關係，再以 global alignment 拼接；pairwise 組合數為 O(N^2)，大場景下極慢 | 全局對齊步驟複雜（需 RANSAC + 非線性優化）；無 streaming 設計，每個新 pair 需獨立推理；點雲拼接過程可能產生不一致 | 在雙幀/少量幀的 dense reconstruction 上精度優異，點雲稠密程度遠高於特徵點 SLAM |

### 4-2. 各方案的核心設計哲學差異

| 面向 | LingBot-Map | DROID-SLAM | VGGT | ORB-SLAM3 |
|------|------------|------------|------|-----------|
| **推理方式** | Feed-forward（單次 forward） | Recurrent iterative（多次循環優化） | Feed-forward（單次 forward） | Optimization（BA） |
| **處理模式** | Streaming（逐幀處理） | Streaming（滑動窗口） | Batch（全部同時） | Streaming（逐幀 + 後端優化） |
| **長程修正** | Trajectory Memory attention | DBA layer（每步 Gauss-Newton） | 全局 Alternating Attention | Pose graph + loop closure |
| **輸出稠密度** | Dense（depth map + point cloud） | Sparse（只輸出 pose + sparse depth） | Dense（depth + point + track） | Sparse（特徵點地圖） |
| **外部依賴** | 無（純 RGB） | 需 camera intrinsics | 無（純 RGB） | 無（純 RGB，可選 IMU） |
| **推論速度** | ~20 FPS (518×378) | ~3 FPS | < 1 sec（batch） | ~30 FPS（CPU） |

### 4-3. 圖解：各技術的長序列處理策略

```
序列長度增長 →

LingBot-Map (Windowed Mode):
  [Window 1  │ overlap │][Window 2  │ overlap │][Window 3  ...]
   KV cache reset        KV cache reset        KV cache reset
   + Trajectory Memory 維持跨 window 一致性

DROID-SLAM:
  [Window 1     ][Window 2     ][Window 3     ...]  ← sliding window
   BA on keyframes within each window
   無跨 window 的軌跡記憶機制

VGGT:
  ❌ 無法處理超過 GPU VRAM 上限的幀數，無 streaming/windowed 模式

ORB-SLAM3:
  逐幀處理 + 關鍵幀插入 + 後端定期全局 BA + loop closure
  在極長序列下 BA 計算量線性增長
```
