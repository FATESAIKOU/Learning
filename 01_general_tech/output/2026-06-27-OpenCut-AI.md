# OpenCut-AI 技術分析報告

> 調研來源：`github.com/Ekaanth/OpenCut-AI`（fork of OpenCut-app/OpenCut）+ 官網 opencutai.video
> 調研日期：2026-06-27
> 原始碼：clone 至暫存區逐檔分析

---

## 1. 這個技術解決什麼問題？

> 把「AI 驅動的影片剪輯」從雲端 SaaS 搬到**完全自託管的本地環境**——轉錄、文字剪輯、語音克隆、AI 生成視覺/音樂、自然語言指令、互動分析評分，全部在使用者的機器上執行，原始素材不離開本機。

拆解為四個子問題：

| 子問題 | 具體痛點 |
|---|---|
| **P1 隱私外洩** | Descript / CapCut / Runway 等把素材上傳雲端處理，記者、企業、隱私敏感使用者的素材被迫離機 |
| **P2 訂閱與按人計費** | 主流 AI 剪輯器按座位或用量計費（$24–79/人/月），團隊成本線性增長 |
| **P3 AI 能力與剪輯器割裂** | DaVinci Resolve 本地但 AI 有限；AI 工具雲端但剪輯弱；兩者無法在同一介面內閉環 |
| **P4 本地 AI 部署門檻** | 自行組裝 Whisper + XTTS + Stable Diffusion + Ollama + FFmpeg 各自獨立服務，散裝難以整合與操作 |

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到

- README 開宗明義：「Every major video editor sends your footage to the cloud. OpenCut AI doesn't.」
- 定位為 OpenCut 的 fork：「This project is a fork of OpenCut. We gratefully acknowledge the OpenCut team and all upstream contributors for the core video editor that makes this possible.」——繼承了 OpenCut 的前端編輯器（Next.js + EditorCore 單例 + Manager 架構），在此之上疊加 AI 後端
- 對標表明確列出 Descript / CapCut / DaVinci Resolve 在「自託管 / 開源 / 資料本地 / AI 影片生成 / A/B 測試 / 互動分析」六維度的空白

### 通用技術背景（文章未明說，為技術脈絡補充）

| 背景因素 | 說明 |
|---|---|
| **Whisper / XTTS / SD 等開源模型成熟** | 2023–2025 年開源 AI 模型品質逼近商業方案，使「本地跑得動」成為可行前提 |
| **Ollama 降低本地 LLM 門檻** | 一行指令拉模型、統一 API，讓本地 LLM 推論不再需要手架 vLLM / text-generation-webui |
| **KV cache 量化技術（TurboQuant）** | LLM 推論的 VRAM 瓶頸在 KV cache；2-bit/3-bit 壓縮讓中小型 GPU 也能跑大模型，這是 OpenCut-AI 的差異化基礎 |
| **OPFS（Origin Private File System）** | 瀏覽器提供檔案系統級隔離儲存，Web app 可在本地持久化大型媒體而不碰伺服器 |
| **FFmpeg.wasm / mediabunny** | 瀏覽器端影片解封裝與處理成熟，前端不需伺服器即可做 Smart Cut、靜音偵測等 |
| **Docker Compose v2.3+ GPU 透傳** | `deploy.resources.reservations.devices` 語法讓 GPU 容器化標準化，自託管 AI 棧可一鍵起 |
| **印度多語言市場缺口** | Sarvam AI 提供 22 種印度語言 ASR/TTS，主流編輯器不覆蓋；OpenCut-AI 把它列為差異化賣點 |

---

## 3. 這個技術是如何解決該問題的？

### 3.1 整體架構（三層）

```
┌──────────────────────────────────────────────────────────────┐
│  前端：Next.js 16 + React 19 (apps/web)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ EditorCore 單例 (apps/web/src/core/index.ts)            │  │
│  │  ├─ playback / timeline / scene / project / media       │  │
│  │  ├─ renderer / commands / save / audio                  │  │
│  │  ├─ selection / version                                 │  │
│  │  └─ (12 Manager, 透過 editor.xxx 互相調度)              │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ AIClient (lib/ai-client.ts) ── 唯一對後端出口            │  │
│  │  ├─ transcribe / analyze / generate / tts / llm        │  │
│  │  ├─ youtube / engagement / search / turboquant          │  │
│  │  └─ NDJSON 串流 + keepalive ping + 404 降級回退         │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Copilot Agent (lib/copilot + ai-action-executor)        │  │
│  │  └─ 自然語言 → LLM 產生 plan → 19 種 EditorAction 執行   │  │
│  └────────────────────────────────────────────────────────┘  │
│  儲存：OPFS（媒體）+ PostgreSQL（專案/帳號）+ Redis（佇列）     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP (同機 Docker network)
┌────────────────────────▼─────────────────────────────────────┐
│  AI Backend：FastAPI (services/ai-backend, port 8420)         │
│  ─ 聚合閘道，不自己跑模型，轉發給下游 7 個微服務                  │
│  ─ 20 個 route 模組：transcribe/tts/generate/llm/command/     │
│    analyze/engagement/youtube/video/turboquant/sarvam/...     │
│  ─ /health 聚合下游健康 + GPU/RAM 狀態, 一次呼叫回全部          │
└────────────────────────┬─────────────────────────────────────┘
                         │
   ┌─────────────┬───────┴───────┬────────────┬───────────┐
   ▼             ▼               ▼            ▼           ▼
┌────────┐ ┌──────────┐ ┌──────────────┐ ┌────────┐ ┌──────────────┐
│whisper │ │tts-svc   │ │image-service │ │speaker │ │face-service  │
│:8421   │ │:8422     │ │:8423 (SD)    │ │:8424   │ │:8425(Mediapipe│
│(Whisper)│ │(XTTS v2) │ │              │ │(pyannote│ │ pin amd64)  │
└────────┘ └──────────┘ └──────────────┘ └────────┘ └──────────────┘
   ┌─────────────┐              ┌──────────────┐
   │clip-service │              │turboquant-svc│
   │:8426 (open- │              │:8430         │
   │ CLIP ViT-B) │              │(KV 2/3/4-bit)│
   └─────────────┘              └──────────────┘
                    ┌──────────────┐
                    │   ollama     │
                    │  :11434      │
                    │(本地 LLM 執行)│
                    └──────────────┘
```

### 3.2 解 P1 隱私：全棧本地 + OPFS

| 層 | 機制 | 證據 |
|---|---|---|
| 媒體儲存 | **OPFS（Origin Private File System）**——瀏覽器檔案系統級隔離，素材不經伺服器 | README：「Files stored in OPFS. Nothing leaves the browser or your server.」 |
| AI 推論 | 7 個微服務全部 Docker 化、跑在同一台機器，Docker network `opencut-network` 內部通訊 | `docker-compose.yml` 全服務同一 bridge network |
| 外部 API 例外 | Sarvam / Smallest / Seedance / Replicate / Stability / Luma 為**可選**雲端 API，需使用者自行配置 key，且前端把 key 存 localStorage 透過 header 透傳 | `ai-client.ts` `getStoredApiKey()` + `X-Sarvam-Api-Key` 等 header |
| 影片生成 | 9 個模型跨 5 provider，但列為可選；核心剪輯/轉錄/TTS/影像生成本地即可完成 | `config.py` 外部 API key 預設空字串 |

### 3.3 解 P2 訂閱：自託管 + Docker 一鍵 + uv 加速

**部署模式**（`docker-compose.yml`）：

```
docker compose build --parallel   # BuildKit 並行建 + cache mount
docker compose up -d              # 起 12 個容器 (db/redis/ollama/ai-backend/7微服務/web)
```

**關鍵建置優化**（README 明列）：

| 技巧 | 效益 |
|---|---|
| CPU-only PyTorch | 4 個服務各省 ~8GB 下載（~200MB vs ~2GB CUDA） |
| BuildKit cache mount | uv/pip 下載快取跨重建保留，純程式碼變動跳過依賴安裝 |
| 平行建置 | `docker compose build --parallel` 所有服務並行 |
| uv 取代 pip | 10–100× 快，cold-cache Docker build 秒級 |
| 鎖檔 `--universal` | PEP 508 marker 保留，macOS 產鎖檔 Linux 可用 |

**成本對照**（README 明列）：Starter $20–40/mo（4vCPU/8GB CPU）→ Production $300–500/mo（8vCPU/64GB + A10G GPU），無按人計費。

### 3.4 解 P3 AI×剪輯閉環：EditorCore + AIClient + Copilot Agent 三層耦合

這是 OpenCut-AI 的核心設計——**AI 不是外掛，而是直接驅動編輯器內部 Manager**。

**資料流**：

```
使用者自然語言 ("make this a 60s reel with captions and music")
   │
   ▼
CopilotPlan (LLM 產生, JSON 結構, lib/copilot/copilot-types.ts)
   ├─ goal / estimatedTime / requiresConfirmation
   └─ steps[]: { id, description, action: EditorAction }
      │
      ▼
ai-action-executor.ts executeAction(action)  ── 19 種 EditorActionType
   ├─ REMOVE_SEGMENTS → useTranscriptStore.deleteSegments(ids)
   ├─ REMOVE_FILLERS  → 逐 segment regex 清除 filler word
   ├─ REMOVE_SILENCE  → 以 silences[] 過濾 segments
   ├─ ADD_CHAPTER_MARKERS / ADD_SUBTITLE_TRACK / ADD_TRANSITION
   ├─ TRIM_CLIP / SPLIT_CLIP / ADJUST_SPEED / SET_CANVAS_SIZE
   ├─ GENERATE_IMAGE → AIClient.generateImage() → 插入 timeline
   ├─ ADD_VOICEOVER → AIClient.generateSpeech() → 插入 timeline
   ├─ ADD_MUSIC / NORMALIZE_AUDIO / AUTO_DUCK / DENOISE_AUDIO / COLOR_CORRECT
   └─ EXPORT_PROJECT
      │
      ▼
EditorCore.xxx()  ── 呼叫對應 Manager, 觸發 Command (undo/redo)
```

**關鍵設計點**：

- **19 種 EditorActionType** 是 AI 與編輯器之間的**契約層**——LLM 只能產生這 19 種動作，executor 對應到 EditorCore Manager，確保 AI 的輸出邊界可控
- **`requiresConfirmation`**：破壞性操作（REMOVE_*/TRIM/SPLIT）LLM 必須標 `true`，使用者審核後才執行
- **`previewAction()`**：每個動作有人類可讀摘要，供 UI 顯示 plan
- **Copilot 預設 6 種**：Make 60s reel / Remove silences / Add chapters / Social clips / Polish audio / Color grade——涵蓋最常見剪輯工作流
- **Actions vs Commands 分層**（`AGENTS.md`）：Actions 是「觸發層」（`@/lib/actions/definitions.ts` 單一來源），Commands 是「執行+undo/redo 層」（`@/lib/commands/` 按域分 timeline/media/scene）——Copilot 產生的 EditorAction 走 actions 系統，享有 toast/驗證/undo

### 3.5 解 P4 散裝 AI 整合：FastAPI 閘道 + 7 微服務 + 統一 health

**ai-backend 是純轉發閘道**，自己不載模型（`main.py` lifespan 只 log 微服務 URL），所有 AI 計算在下游：

| 微服務 | port | 職責 | 模型/技術 |
|---|---|---|---|
| whisper-service | 8421 | 語音轉文字（word-level timestamp） | faster-whisper, int8, CPU/GPU |
| tts-service | 8422 | 語音合成 + 聲音克隆（6 秒樣本） | XTTS v2, 6GB mem limit |
| image-service | 8423 | 文生圖 | Stable Diffusion |
| speaker-service | 8424 | 說話者分離（diarization） | pyannote（需 HF_TOKEN） |
| face-service | 8425 | 臉部偵測（reframe/scene） | MediaPipe，**pin linux/amd64**（無 aarch64 wheel） |
| clip-service | 8426 | 視覺語義搜尋 embedding | open_clip ViT-B-32 |
| turboquant-service | 8430 | LLM 推論 + KV cache 量化 | TurboQuant 2-bit(GPU)/3-bit(CPU) |

**統一健康檢查**（`main.py:101` `/health`）：一次呼叫聚合并行 ping 全部下游 + Ollama models + RAM(psutil) + GPU(torch.cuda)，前端只需一次輪詢。

### 3.6 TurboQuant：差異化的本地 LLM 加速

這是 OpenCut-AI 與「散裝 Ollama + Whisper」的最大技術差異點：

| 維度 | GPUTurboBackend | CPUTurboBackend |
|---|---|---|
| KV cache 壓縮 | **2-bit** 或 3-bit，cuTile fused kernel | **3-bit** only（2-bit decode 在 CPU 有 lossy 風險） |
| Decode 路徑 | `engine.generate()` 走壓縮 KV cache | HF `model.generate`（greedy fallback 太慢） |
| 加速策略 | TF32 matmul / cuDNN benchmark / `auto_tune()` warm-up | 實體核心 thread pinning / MKLDNN / 單次 warm-up probe |
| 觸發條件 | `DEVICE=cuda` + `turboquant-gpu` 已裝 | `DEVICE=cpu` 或 GPU 初始化失敗自動降級 |

**Compute Mode 三段切換**（UI Settings → AI Optimization）：

```
Auto  ── 偵測 CUDA → MPS → CPU（預設）
CPU   ── 強制 CPU，CPUTurboBackend
GPU   ── 強制 CUDA，無 GPU 時按鈕灰掉 + tooltip
```

選擇後寫 `OPENCUTAI_AI_COMPUTE_MODE` 到 `.env`，重載 backend config + 在新裝置重載模型。

**防崩潰設計**（`compute_backends.py` factory）：GPU backend `__init__` 丟例外（cuda-tile 未裝、driver 太舊）→ log warning + 降級 CPU backend，服務仍啟動，`/health` 回 `"backend": "cpu"`。

### 3.7 前端 AIClient 的長時操作處理

本地 LLM 在 CPU 上慢（README 明言「LLM generation can be slow on CPU」），AIClient 有三層逾時策略：

| 逾時 | 值 | 適用 |
|---|---|---|
| `HEALTH_TIMEOUT_MS` | 5s | health / status 輕量呼叫 |
| `REQUEST_TIMEOUT_MS` | 120s | 一般 API（轉錄、TTS、圖像） |
| `LLM_TIMEOUT_MS` | **600s（10 分鐘）** | LLM chat / command / engagement scoring |

**NDJSON keepalive 串流**（`requestWithKeepalive`）：後端逐行送 `{"ping": true}` 保活，前端忽略 ping 只取 `{"result": ...}`；若後端舊版回純 JSON 則自動降級。`chatStream` 另有 404 降級到非串流 `chat()`。

### 3.8 額外的差異化功能（非核心架構，但構成賣點）

| 功能 | 機制 | 值得注意的設計 |
|---|---|---|
| Virality Score | 7 信號加權（hook 0.25 / curiosity 0.20 / viral 0.15 / energy 0.15 / emotion 0.10 / audio_sync 0.10 / face 0.05） | `config.py` 啟動時驗證權重和 = 1.0，否則 `raise ValueError` |
| Smart Reframe | 臉部偵測 → 位置/縮放 keyframe，4 preset（9:16/1:1/4:5/16:9） | face-service MediaPipe |
| Scene Detection | color histogram 分析，client-side，無資料外傳 | README 強調 client-side |
| YouTube→Reels | yt-dlp 下載 → clip detection → face reframe → captions → export | Redis job queue（可降級 in-memory） |
| Chroma Key | WebGL shader，5 preset + tolerance/softness/spill suppression | `lib/effects/` |
| 20 transitions | WebGL dual-texture shaders | `lib/transitions/shaders/` |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 候選方案一覽

| # | 技術名 | 切入點差異 |
|---|---|---|
| 1 | **OpenCut（上游原版）** | 純剪輯器無 AI；OpenCut-AI 是其 fork，AI 層全部為新增 |
| 2 | **Descript** | 雲端 SaaS，文字剪輯+轉錄強，但素材上傳、按人計費 |
| 3 | **CapCut** | 雲端（字節跳動），免費但浮水印+資料出境，AI 強但不可自託管 |
| 4 | **散裝本地 AI 栈（Ollama + Whisper.cpp + SD WebUI + 手接 FFmpeg）** | 各工具獨立，無統一 UI，剪輯需另用 DaVinci/NLE |
| 5 | **DaVinci Resolve + 其內建 AI** | 本地+免費版可用，但 AI 有限（無文字剪輯、無語音克隆、無影片生成），閉源 |

### DA 表（導入目的導向評估）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|---|---|---|---|---|
| **OpenCut-AI** | Next.js 前端 + FastAPI 閘道 + 7 微服務 + Ollama/TurboQuant，Docker Compose 一鍵自託管 | 需 4vCPU/8GB+ 機器；GPU 為可選加速；Docker + BuildKit | 12 容器佔資源（全棽 ~8GB RAM）；face-service 在 Apple Silicon 走 Rosetta；LLM 在 CPU 慢（10 分鐘級逾時） | 全棧本地 AI 剪輯閉環、無訂閱、無資料外傳、19 種 EditorAction 可被 LLM 驅動 |
| **OpenCut（上游）** | 純前端編輯器（Rust/WASM + Next.js），無 AI 後端 | 只需瀏覽器或輕量伺服器 | 無轉錄/TTS/生成/分析；需自行外接 AI 工具 | 隱私本地剪輯，但 AI 能力為零 |
| **Descript** | 雲端 SaaS，文字剪輯+轉錄+Overdub 語音克隆 | 付費訂閱；素材上傳雲端 | 按人計費；資料在雲端；無法離線 | 即裝即用、協作強、AI 品質穩定 |
| **CapCut** | 雲端（字節跳動），免費+付費，AI 自動字幕/模板/生成 | 帳號綁定；資料出境 | 浮水印（免費版）；隱私風險（多國限制）；無自託管 | 零門檻、行動版強、模板生態豐富 |
| **散裝本地 AI 栈** | Ollama + Whisper.cpp + SD WebUI + DaVinci 各自獨立 | 需自行整合；各工具 UI 不統一 | 維護成本高；剪輯與 AI 跨工具手動搬素材；無統一 undo | 各環節可選最強開源模型，但無整合閉環 |
| **DaVinci Resolve** | 桌面 NLE + 有限 AI（魔法遮罩/語音隔離/調色） | 桌面 OS；免費版功能受限 | AI 能力有限（無文字剪輯、無語音克隆、無影片生成）；閉源 | 專業調色+剪輯強，AI 為輔助 |

### 切入點差異總結

```
隱私/自託管需求強 ─┬─ OpenCut-AI (全棧本地, AI×剪輯閉環, 需自架)
                  ├─ OpenCut (純剪輯, 無 AI)
                  ├─ 散裝本地栈 (各環節最強但無整合)
                  └─ DaVinci (本地專業剪輯, AI 有限)

雲端即用需求強    ─┬─ Descript (文字剪輯強, 按人計費, 雲端)
                  └─ CapCut (免費+浮水印, 資料出境, 行動強)
```

---

## 5. User Q&A

### Q1：我可以用 Ollama cloud 訂閱接上嗎？

**A**：可以，但需要補一個 `Authorization` header，現有 `OllamaService` 不會自己帶。三種接法如下表，推薦第 2 種。

#### 事實核對

| 項目 | 狀態 |
|---|---|
| Ollama 雲端是否存在訂閱 | 存在。Free（隨帳號附贈）/ Pro $20/mo / Max $100/mo（`ollama.com/pricing`） |
| Ollama 雲端 API 路徑 | 與本地完全相同：`/api/tags`、`/api/chat`、`/api/generate`，host 改為 `https://ollama.com` |
| Ollama 雲端認證方式 | `Authorization: Bearer $OLLAMA_API_KEY`（在 `ollama.com/settings/keys` 建立 API key） |
| OpenCut-AI 的 `OLLAMA_URL` 是否可改 host | 可以。`config.py:25` `OLLAMA_URL: str = "http://localhost:11434"` 為預設值，可由 `OPENCUTAI_OLLAMA_URL` 環境變數覆寫 |
| OpenCut-AI 的 `OllamaService` 是否會帶 Bearer header | **不會**。`ollama_service.py:19` 直接 `httpx.AsyncClient(base_url=self.base_url)`，未注入任何 auth header |

#### 三種接法對照

| # | 做法 | 改動量 | 副作用 |
|---|---|---|---|
| 1 | 改 `OPENCUTAI_OLLAMA_URL=https://ollama.com`，並在 `ollama_service.py` 的 `_client()` 補 `headers={"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}"}` | 2 處程式碼 + 1 個 env | 需 fork 維護；升級 upstream 會衝突 |
| 2 | 本地裝 Ollama CLI 並 `ollama signin`，雲端模型用 `gpt-oss:120b-cloud` 這類 `-cloud` 後綴名稱；`OLLAMA_URL` 維持 `http://localhost:11434` | **0 程式碼改動**，只改 `OPENCUTAI_OLLAMA_DEFAULT_MODEL` | 需本機跑 Ollama daemon 當代理；雲端模型選擇受限於 Ollama 雲端模型庫 |
| 3 | 在本機用 nginx/反向代理把 `https://ollama.com` 加上 Bearer header 後暴露在 `localhost:11434` | 0 程式碼改動，只加代理設定 | 多一層代理要維護；但可完全用雲端模型庫 |

> 推薦第 2 種：Ollama 官方設計就是「local daemon 透明代理雲端模型」，`ollama run <model>-cloud` 會自動路由到雲端，API 介面完全不變，OpenCut-AI 無需感知「這次是雲端還是本地」。

#### 注意：雲端只覆蓋 LLM，不覆蓋其他 AI 微服務

```
Ollama 雲端能取代的          ── ai-backend 的 /api/llm/* + /api/llm/command（Copilot Agent 計畫生成）
                              ── ai-backend 的 /api/analyze/structure + suggestions + keywords + question-cards（LLM 文本分析）
Ollama 雲端不能取代的         ── whisper-service（語音轉文字，用 faster-whisper，非 Ollama）
                              ── tts-service（XTTS v2 語音合成）
                              ── image-service（Stable Diffusion）
                              ── speaker-service（pyannote 說話者分離）
                              ── face-service（MediaPipe 臉部偵測）
                              ── clip-service（open_clip 語義搜尋）
                              ── turboquant-service（這是另一條 LLM 路徑，與 Ollama 平行，可設 AI_LLM_BACKEND=ollama 關掉它）
```

若只想用 Ollama 雲端、不跑其他重微服務，可在 `docker-compose.yml` 把 whisper/tts/image/speaker/face/clip/turboquant 七個服務註解掉，`ai-backend` 仍會啟動（health 會顯示這些服務 stopped，但 LLM 路徑正常）。

**結論**：可以接，推薦「本地 Ollama daemon + signin + 雲端模型名稱」的零改動路徑；雲端只省 LLM 運算，其餘 AI 能力仍需本地或對應雲端 API。

---

### Q2：這東西怎麼用，給我一步一步的指令讓我可以嘗試？

**A**：以下為 macOS 上的最小可執行路徑，分四階段。每階段標注預期產出與驗證點。

#### 階段 0：前置確認

```bash
# 1. 確認 Docker + BuildKit
docker --version          # 需 Docker 24+
docker compose version    # 需 v2.3+
docker buildx version     # BuildKit 支援

# 2. 確認 bun（前端開發用，非 Docker 部署所需）
bun --version             # 需 1.2+，沒有則 curl -fsSL https://bun.sh/install | bash

# 3. 確認磁碟空間（模型 + 容器映像約 15-20GB）
df -h .                   # 建議預留 30GB
```

#### 階段 1：取得程式碼 + 設定環境

```bash
git clone https://github.com/Ekaanth/OpenCut-AI.git
cd OpenCut-AI

# 複製環境範本
cp apps/web/.env.example apps/web/.env.local
```

#### 階段 2：啟動 AI 後端 + 資料庫（Docker）

**選項 A — CPU（任何機器都跑得動，但 LLM/圖像生成慢）**：

```bash
export DOCKER_BUILDKIT=1
docker compose build --parallel     # 首次約 10-30 分鐘（下載 PyTorch 等）
docker compose up -d                # 起 12 個容器
```

**選項 B — NVIDIA GPU（需先裝 NVIDIA Container Toolkit）**：

```bash
nvidia-smi                          # 先確認 host 看得到 GPU
export DOCKER_BUILDKIT=1
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

**驗證後端健康**（這一步是關鍵檢查點）：

```bash
curl -s http://localhost:8420/health | jq
# 預期回傳：
# {
#   "available": true,
#   "services": ["ollama", "whisper", "tts", "image", "speaker", "face", "turboquant", "clip"],
#   "gpuAvailable": false,
#   "memoryUsage": { "ram": {...}, "gpu": null }
# }
```

> 若 `services` 陣列缺幾個是正常的（首次啟動模型下載中），等 1-2 分鐘再 curl 一次。

#### 階段 3：啟動前端編輯器

```bash
bun install
bun dev:web
```

**驗證前端**：

```
開瀏覽器 → http://localhost:3000
預期：看到 OpenCut AI 編輯器介面（時間軸 + 預覽 + 側邊欄）
```

#### 階段 4：拉 LLM 模型（讓 Copilot / 自然語言指令可用）

```bash
# 在編輯器內操作：Settings → AI Models → Pull Model
# 或用 curl 經 ai-backend：
curl -X POST http://localhost:8420/api/llm/pull-model \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:1b"}'      # 最小模型，~1.3GB，CPU 也能跑
```

#### 階段 5：試用核心 AI 功能（最小體驗路徑）

| 功能 | 操作方式 | 預期結果 |
|---|---|---|
| **語音轉文字** | 匯入一段影片/音訊 → 點「Transcribe」 | 時間軸出現文字段，可像文件一樣刪句剪片 |
| **Smart Cut** | 點「Smart Cut」按鈕 | 自動偵測 um/uh/silence 並標示，確認後剪掉 |
| **Copilot Agent** | 側邊欄輸入「Remove all silence and filler words」 | LLM 產生 plan（多步驟），確認後自動執行 |
| **TTS 配音** | 文字框輸入文字 → 選語音 → Generate | 產生音訊插入時間軸 |
| **影片生成** | Video Gen Hub → 選 provider（需先設 API key）→ 輸入 prompt | 生成影片插入時間軸 |

#### 若要接 Ollama 雲端（Q1 的第 2 種做法）

```bash
# 1. 本機裝 Ollama CLI
curl -fsSL https://ollama.com/install.sh | sh

# 2. 登入雲端
ollama signin    # 瀏覽器跳轉輸入帳密

# 3. 拉一個雲端模型（會自動路由到雲端）
ollama pull gpt-oss:120b-cloud

# 4. 改 OpenCut-AI 的環境變數指向本地 Ollama + 雲端模型
#    編輯 .env 或 docker-compose.yml 的 ai-backend 區：
#    OPENCUTAI_OLLAMA_URL=http://ollama:11434   # 維持指向容器內 ollama
#    OPENCUTAI_OLLAMA_DEFAULT_MODEL=gpt-oss:120b-cloud

# 5. 重啟 ai-backend
docker compose restart ai-backend

# 6. 驗證
curl -s http://localhost:8420/api/llm/status | jq
# 預期 default_model 為 gpt-oss:120b-cloud
```

> 注意：Docker 內的 `ollama` 容器是獨立 daemon，不等於你本機的 Ollama。若要讓 Docker 內的 ollama 也走雲端，需在 ollama 容器內執行 `ollama signin`，或改 `OLLAMA_URL` 指向 host 本機的 Ollama（`http://host.docker.internal:11434`）。

#### 停止與清理

```bash
docker compose down                  # 停所有容器（保留資料 volume）
docker compose down -v               # 停 + 刪所有 volume（模型重下）
```

**結論**：四階段（前置→Docker 後端→bun 前端→拉模型）可跑到可用狀態；CPU 模式足以體驗轉錄/Smart Cut/Copilot，圖像生成與快速 LLM 建議加 GPU 或接 Ollama 雲端。

---

## 附錄：關鍵檔案索引

| 主題 | 路徑 |
|---|---|
| 前端 EditorCore 單例 | `apps/web/src/core/index.ts` |
| 前端↔後端唯一出口 | `apps/web/src/lib/ai-client.ts`（1700+ 行，涵蓋全部 API） |
| Copilot Agent 型別與系統提示 | `apps/web/src/lib/copilot/copilot-types.ts` |
| 19 種 EditorAction 執行器 | `apps/web/src/lib/ai-action-executor.ts` |
| Actions 定義（單一來源） | `apps/web/src/lib/actions/definitions.ts` |
| Commands（undo/redo） | `apps/web/src/lib/commands/`（timeline/media/scene/project） |
| AI Backend 入口 | `services/ai-backend/app/main.py`（20 route + 聚合 health） |
| AI Backend 設定 | `services/ai-backend/app/config.py`（Pydantic BaseSettings, env_prefix=OPENCUTAI_） |
| Engagement scoring | `services/ai-backend/app/services/engagement/`（7 信號 scorer） |
| TurboQuant service | `services/turboquant-service/`（compute_backends.py 雙後端） |
| Docker 拓撲 | `docker-compose.yml`（12 容器 + opencut-network bridge） |
| GPU 覆寫 | `docker-compose.gpu.yml`（nvidia device + TURBOQUANT_EXTRAS=gpu + DEVICE=cuda） |
| 架構原則 | `AGENTS.md`（EditorCore/Actions/Commands 分層） |
| 前端 package | `apps/web/package.json`（Next 16 / React 19 / Zustand / Drizzle / mediabunny / wavesurfer） |
| 根 package + turbo | `package.json` + `turbo.json`（bun workspace, turbo 任務編排） |