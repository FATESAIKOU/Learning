# NVIDIA Cosmos 技術分析報告

## 1. 這個技術解決什麼問題？

Physical AI（機器人、自駕車、智慧基礎設施）的開發需要**大量且多樣化的實體世界訓練資料**（影片、動作軌跡、感測器流），但在真實世界收集這些資料面臨成本極高、危險場景無法重現、邊緣案例稀缺、動作標註困難等限制；同時，傳統物理模擬器（Isaac Sim、Genesis）雖然物理精確，但生成的畫面不夠擬真，導致 sim-to-real gap。

NVIDIA Cosmos 解決的具體問題是：**如何以一個大規模預訓練的「世界基礎模型（World Foundation Model）」，統一提供（a）從文字/影像/動作生成擬真未來世界影片與合成資料、（b）從影片/影像進行物理常識理解、空間定位與動作預測、（c）讓機器人 policy 直接以 world model 為模擬器進行 forward / inverse dynamics 學習，以取代或補足真實資料收集與傳統規則式模擬。**

問題描述的模糊之處：Cosmos 同時被定位為「世界模擬器」「合成資料生成器」「VLM 推理器」「機器人 policy 骨幹」四種角色，文檔並未嚴格區分哪些能力來自統一架構的哪個子路徑，也未說明作為「模擬器」時其物理精確度相對規則式模擬器的量化邊界。

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

- **Physical AI 資料瓶頸**：開發機器人、自駕車需要大量在真實世界難以收集的訓練資料（危險場景、邊緣案例、多樣環境）。
- **傳統模擬器的限制**：規則式模擬器（如 Isaac Sim）物理精確但渲染擬真度受限，且建立新場景資產成本高，無法無限多樣化。
- **生成式 AI 已具備世界模擬潛力**：diffusion model 與 transformer 在影片生成、多模態推理上已展現能力，但缺少統一框架同時支援「理解」與「生成」。
- **模態割裂的歷史問題**：v1/v2 時代感知（Reason1/Reason2）與生成（Predict1/Predict1、Transfer1）為分離模型，text/image/video 模態並未與 sound、action 統一，導致跨任務遷移與 sim-to-real 整合困難。
- **實體 embodiment 差異極大**：相機運動 (9D)、自駕車 (9D)、ego-motion (57D)、單臂 (10D)、雙臂 (20D)、人形 (29D)，各自的動作空間與資料分布差異巨大，缺乏統一架構同時處理。

### 通用技術背景

- **World Model 概念演進**：從 Dreamer 系列（model-based RL 學習環境模型用於 policy 學習）到 UniPi（policy-as-video）、Genie 2（image→playable 3D world），學界已驗證「學習式世界模型」可行，但缺乏工業規模化、多 embodiment、多模態的開源基礎模型。
- **Sim-to-real gap**：機器人在模擬中訓練後部署真實世界時，因渲染差異、感測器雜訊、物理近似而效能下降，業界長期以 domain randomization、domain adaptation 緩解，Cosmos 透過「生成擬真合成資料」與「world-model-as-simulator」提供新路徑。
- **Diffusion + Autoregressive 架構分歧**：影像/影片生成主流使用 diffusion transformer（DiT），語言/推理主流使用 AR transformer；兩者如何統一為單一架構是技術界開放問題，Cosmos 3 採 Mixture-of-Transformers（MoT）回應。
- **Omniverse / OpenUSD 生態**：NVIDIA 既有 Omniverse 提供規則式物理模擬（PhysX）與 OpenUSD 場景描述，Cosmos 與之分工為「學習式補充」。

## 3. 這個技術是如何解決該問題的？

Cosmos 3 採用**單一架構 + 雙執行面**設計，將過去分離的 VLM、影片生成器、世界模擬器、world-action model 統一為單一 omnimodal world model。

### 3.1 系統架構

```
┌───────────────────────────────────────────────────────────────┐
│ 使用者 / 開發者                                                │
│   想要：(a) 生成擬真合成資料  (b) 理解影片物理常識             │
│         (c) 預測機器人動作     (d) 閉環模擬評估                │
└────────────────────────────┬──────────────────────────────────┘
                             │ OpenAI-compatible API / Diffusers / vLLM-Omni / NIM
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ Cosmos 3 Model（omnimodal world model）                       │
│                                                               │
│   ┌────────────────────┐      ┌──────────────────────────┐    │
│   │  Reasoner Surface  │      │  Generator Surface       │    │
│   │  (AR transformer)  │      │  (Diffusion transformer) │    │
│   │                    │      │                          │    │
│   │  text/vision →     │      │  text/vision/sound/      │    │
│   │  text（理解、定位、│      │  action → vision/sound/   │    │
│   │  動作預測、物理常識）│      │  action（生成、模擬、    │    │
│   │                    │      │  policy、forward dyn.）  │    │
│   └─────────┬──────────┘      └──────────┬───────────────┘    │
│             │                              │                   │
│             └──────────┬───────────────────┘                   │
│                        ▼                                       │
│   ┌──────────────────────────────────────────────────────┐    │
│   │  共用骨幹：Mixture-of-Transformers (MoT)             │    │
│   │  + 多模態注意力層                                     │    │
│   │  + 統一 3D mRoPE 位置編碼（空間 + 時間跨模態一致）    │    │
│   └──────────────────────────────────────────────────────┘    │
└────────────────────────────┬──────────────────────────────────┘
                             │ 訓練資料
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ 資料層：2000 萬小時真實世界影片 + 文字 + Isaac Sim 合成場景    │
│ 工具：Cosmos Curator（整理）/ Cosmos Evaluator（評測）         │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 Mixture-of-Transformers（MoT）核心機制

兩個 transformer 在同一架構內分工：

| 子路徑 | 類型 | 注意力機制 | 用途 |
|--------|------|-----------|------|
| **Reasoner** | Autoregressive (AR) | 因果自注意力（causal self-attention） | next-token prediction——感知、規劃、世界推理、動作預測 |
| **Generator** | Diffusion (DM) | 全注意力（full attention） | 對 noisy image/video/audio/action tokens 去噪——聯合生成多模態輸出 |

兩者共用：
- 同一 transformer 骨幹權重
- 多模態注意力層
- **統一 3D mRoPE（multi-dimensional Rotary Position Embedding）**：編碼影像、影片、音訊串流、動作軌跡的空間與時間結構，使跨模態推理一致

### 3.3 模型家族

| 模型 | 規模 | 主要能力 |
|------|------|---------|
| Cosmos3-Nano | 16B | 緊湊型 omnimodal，支援理解/模擬/動作推理 |
| Cosmos3-Super | 64B | 前沿規模，進階多模態理解/模擬 |
| Cosmos3-Super-Text2Image | 64B | 高保真文字轉圖像 |
| Cosmos3-Super-Image2Video | 64B | 時序一致圖像轉影片 |
| Cosmos3-Nano-Policy-DROID | 16B | DROID 機器人操作 vision-language policy |

### 3.4 Generator 與 Reasoner 的任務對應

```
Generator（生成面）
├── Text → Image / Video / Video+Sound
├── Image → Video / Video+Sound
├── Video → Video（prompt-guided transformation）
├── Forward Dynamics（vision + action → 未來 vision）
└── Action Policy（vision → action chunk + rollout video）

Reasoner（推理面）
├── Caption（影片描述）
├── Temporal Localization（事件時間戳）
├── Embodied Reasoning（下一步動作預測）
├── Common-sense Reasoning（物理常識判斷）
├── 2D Grounding（bounding box 定位）
├── Action Chain-of-Thought（軌跡預測推理）
├── Physical Plausibility（物理合理性分類）
└── Situation Understanding（情境理解與下一步預測）
```

### 3.5 Action Conditioning 與 Embodiment 支援

Cosmos 3 將動作序列視為一等模態，支援多種 embodiment 的動作空間：

| Embodiment | 動作維度 | 應用 |
|------------|---------|------|
| Camera motion | 9D | 攝影機運動模擬 |
| Autonomous vehicle | 9D | 自駕場景 |
| Egocentric motion | 57D | 第一人稱運動 |
| Single-arm robot | 10D | DROID/UR/Fractal/Bridge/UMI |
| Dual-arm robot | 20D | 雙 DROID 臂 |
| Humanoid robot | 29D | AgiBot |

這使 Cosmos 3 可作為 **world-action model**：給定當前影像 + 動作 → 預測未來影像（forward dynamics），或從影片推導出動作（inverse dynamics），或直接作為 policy（vision → action）。

### 3.6 整合路徑

| 使用目標 | 整合方式 | 說明 |
|---------|---------|------|
| Generator 研究/開發 | **Diffusers** (`Cosmos3OmniPipeline`) | Python-first，載入完整 checkpoint |
| Generator 生產推理 | **vLLM-Omni** | OpenAI-compatible API，image/video/sound/action |
| Reasoner 研究/開發 | **Transformers**（coming soon） | Python-first |
| Reasoner 生產推理 | **vLLM** | OpenAI-compatible chat API |
| Reasoner 開箱部署 | **NIM** | 預建最佳化容器 |
| 訓練/評測工作流 | **Cosmos Framework** | 完整 setup/inference/training/eval |

Diffusers 範例（text-to-video）：

```python
from diffusers import Cosmos3OmniPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler

pipe = Cosmos3OmniPipeline.from_pretrained("nvidia/Cosmos3-Nano", torch_dtype=torch.bfloat16, device_map="cuda")
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=10.0)

result = pipe(
    prompt="A mobile robot navigates a warehouse aisle and stops at a shelf.",
    num_frames=189, height=720, width=1280, fps=24,
    num_inference_steps=35, guidance_scale=6.0,
    enable_sound=False,
    generator=torch.Generator(device="cuda").manual_seed(1234),
)
```

vLLM-Omni 啟動（生產 API）：

```bash
docker run --runtime nvidia --gpus all -p 8000:8000 --ipc=host \
  vllm/vllm-omni:cosmos3 \
  vllm serve nvidia/Cosmos3-Nano --omni \
  --model-class-name Cosmos3OmniDiffusersPipeline \
  --allowed-local-media-path / --port 8000 --init-timeout 1800
```

### 3.7 Guardrail 機制

Cosmos 3 內建 safety guardrail（篩檢 prompt、模糊生成輸出中的人臉），可 per-request 或 server-wide 關閉。需申請 gated `nvidia/Cosmos-1.0-Guardrail` HF repo 存取。

### 3.8 生態系定位

```
NVIDIA Physical AI Stack
├── 硬體層：Blackwell GB200 / RTX PRO 6000 / Jetson / DRIVE AGX
├── 物理模擬層（規則式）
│   ├── Isaac Sim（Omniverse/OpenUSD 機器人模擬）
│   ├── Newton（NVIDIA + DeepMind + Disney，可微物理引擎，Linux Foundation）
│   └── Isaac Lab（強化學習框架）
├── 世界基礎模型層（學習式）—— Cosmos
│   ├── 生成擬真合成資料（補 Isaac Sim 場景多樣性不足）
│   ├── 作為 world simulator 做閉環評估
│   └── 作為 VLM 進行感知/定位/動作預測
├── 訓練/部署層：NeMo / NIM / DGX Cloud / TAO
└── 機器人基礎模型：Isaac GR00T（人形機器人基礎模型，以 Cosmos 為骨幹）
```

### 3.9 技術規格

| 面向 | 細節 |
|------|------|
| 解析度 | 256p / 480p / 720p（預設 480p） |
| 長寬比 | 16:9 / 4:3 / 1:1 / 3:4 / 9:16 |
| 幀率 | 10 / 16 / 24 / 30 FPS |
| 幀數 | 5–300 frames（預設 189 ≈ 7.9s @ 24fps） |
| 精度 | BF16 |
| 作業系統 | Linux |
| GPU 架構 | NVIDIA Ampere / Hopper / Blackwell |
| 音訊輸出 | Stereo AAC 48kHz（與影片同步） |
| 授權 | OpenMDW-1.1（Linux Foundation） |
| 版本 | Cosmos 3（2026-05 發表） |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（決策輔助表）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **NVIDIA Cosmos 3** | 統一 Mixture-of-Transformers（AR + Diffusion）omnimodal 架構，共用 mRoPE；Reasoner 處理理解、Generator 處理生成；action 為一等模態支援 6 種 embodiment；與 Isaac Sim/Newton/GR00T 整合 | NVIDIA GPU（Ampere+）；Linux；HF token；guardrail repo 申請；Cosmos3-Super 需多 GPU（tensor parallel / layerwise offload） | 模型龐大（16B/64B）；長高解析度輸出有 temporal inconsistency、object morphing、音視不同步；學習式世界模型物理精確度不如規則式模擬；guardrail 限制敏感內容生成 | 統一 VLM+影片生成+世界模擬+policy 於單一架構；生成無限多樣擬真合成資料；forward/inverse dynamics 直接用於機器人訓練；與 NVIDIA 硬體/模擬/機器人生態深度整合 |
| **NVIDIA Isaac Sim + Newton（規則式模擬）** | 基於 Omniverse/OpenUSD 的物理引擎（PhysX、MuJoCo-Warp 可微），提供物理精確的虛擬環境、感測器模擬、合成資料生成 | NVIDIA RTX GPU；Omniverse runtime；場景資產建立 | 渲染擬真度受限（CG 感）；場景多樣性受限於資產；建立新場景成本高；sim-to-real gap 仍在 | 物理精確可驗證；感測器模擬逼真；可完全控制場景參數；支援 domain randomization |
| **DeepMind Genie 2** | 從單張圖片生成可互動 3D 環境；自迴歸 latent diffusion；接受鍵盤/滑鼠動作輸入 | 研究預覽（未開源、無 API） | 僅維持一分鐘世界一致性；無法用於工業規模訓練；無 action policy 輸出 | 快速從單圖建立 agent 訓訓練環境；湧現物理/光照/NPC 行為；概念驗證 image→playable world |
| **OpenAI Sora** | Diffusion transformer 文字/影像→影片；影片表達為 patches 統一表示 | OpenAI API；商用授權 | 無原生 action 輸出；無 policy 學習；不與機器人模擬整合；物理一致性有限 | 頂尖創意內容影片生成；模擬物理世界作為 AGI 里程碑 |
| **Google Veo 3** | 頂尖影片生成 + 原生同步音訊/對白；相機控制、首尾影格、outpainting | Google Cloud / Gemini API | 純內容創作定位；無動作/policy；無實體 AI 整合 | 電影/敘事級美學與創意控制；原生音訊 |
| **World Labs（Fei-Fei Li）** | 「空間智慧」生成空間一致、可持久化、可漫遊編輯的 3D 世界 | 商業 API（早期） | 輸出為可消費 3D 資產；非 world model；無動作預測 | 可導航 3D 場景重建與編輯；spatial intelligence |
| **Wayve GAIA-1** | 自駕專用生成式世界模型；video+text+action → next-token 預測擬真駕駛場景 | Wayve 授權（非開源） | 僅自駕自駕領域；單一 embodiment；模態有限 | 自駕場景生成與閉環評估；細粒度 ego-vehicle 控制 |
| **DreamerV3** | model-based RL：學習環境模型 → 在模型中「想像未來」改進策略；單一配置跨 150+ 任務 | 學術開源；RL 環境 | 規模與模態遠小於工業基礎模型；無影片/音訊生成 | model-based RL 標桿；展現世界模型 scaling 特性 |

### 各方案切入點差異

- **Cosmos 3**：以 **統一 omnimodal world foundation model** 為切入點，將 VLM、影片生成、世界模擬、world-action model 合一，原生支援多 embodiment 動作，並與 NVIDIA 硬體/模擬/機器人生態深度整合。
- **Isaac Sim + Newton**：以 **規則式物理精確模擬** 為切入點，物理可驗證、感測器模擬逼真、場景完全可控，但渲染擬真度與多樣性受限。與 Cosmos 為**互補關係**（Cosmos 生成擬真資料補 Isaac Sim 場景不足）。
- **Genie 2**：以 **單圖→可互動世界** 為切入點，概念前沿但僅為研究預覽，無工業規模化與 action policy 輸出。
- **Sora / Veo 3**：以 **創意內容影片生成** 為切入點，頂尖畫質但無動作/policy 模態，定位為內容創作而非 Physical AI 訓練。
- **World Labs**：以 **可導航 3D 場景重建與編輯（spatial intelligence）** 為切入點，輸出為可消費 3D 資產而非世界模型。
- **GAIA-1**：以 **自駕垂直領域世界模型** 為切入點，單一 embodiment、非開源。
- **DreamerV3**：以 **model-based RL 通用方法** 為切入點，學術標桿但規模與模態遠小於工業基礎模型。

### 學習式 vs 規則式世界模型——根本分歧

```
                學習式世界模型                    規則式物理模擬
                (Cosmos, Genie, Sora)            (Isaac Sim, Newton, Genesis)
─────────────────────────────────────────────────────────────────────────
物理精確度      近似（資料驅動）                  精確（物理方程）
渲染擬真度      高（生成式）                      受限（CG 資產）
場景多樣性      無限（生成）                      受資產限制
可控性          有限（prompt 引導）               完全（參數控制）
可驗證性        弱                                強（可重現）
計算成本        推理時高（diffusion）             模擬時中（物理引擎）
sim-to-real    直接擬真輸出                      需 domain randomization
適用場景        資料擴充、policy 學習、閉環評估  精確物理驗證、感測器模擬
```

Cosmos 的戰略選擇是**兩者並存互補**：Isaac Sim/Newton 提供物理精確骨架，Cosmos 在其上生成無限多樣擬真資料與可學習的 world-action model。