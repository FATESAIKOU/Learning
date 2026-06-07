# AI Engineering from Scratch — 技術分析報告

> 分析對象：https://github.com/rohitg00/ai-engineering-from-scratch
> 分析日期：2026-06-06

---

## 1. 這個技術解決什麼問題？

**被解決的具體問題**：解決「AI 學習者只能在碎片化的文章、論文、教學影片中拼湊知識，無法獲得一條從數學基礎到多智能體自主系統的**完整、可追溯、有因果鏈**的 AI 工程學習路徑」的問題。

具體而言：
- 學習者能做出 chatbot，但無法解釋其 loss curve 的走勢
- 學習者能將 function 掛接到 agent，但不知道模型內部的 attention 機制如何運作
- 市面上缺乏一條從 `線性代數` → `Backprop` → `Tokenizer` → `Attention` → `Agent Loop` 的「脊椎式」學習路徑

此問題描述**明確**，repo 以具體數字（503 課、20 階段、~314 小時）和「Build It / Use It」方法論鎖定了問題邊界。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景

| 因素 | 描述 |
|------|------|
| 知識碎片化 | AI 教材分散在論文、部落格文章、微調教學、Agent demo 中，彼此缺乏關聯 |
| 缺乏因果鏈 | 學習者能操作 API 但無法理解底層原理；框架成為黑箱 |
| 工具與原理脫節 | 84% 學生已使用 AI 工具，但僅 18% 覺得準備好專業使用（引自 repo README） |
| 缺乏完整路徑 | 現有資源沒有從「原始數學推導」→「手寫實作」→「框架使用」→「產出可重用工具」的閉環 |

### 通用技術背景（從網路搜尋補充）

| 因素 | 描述 |
|------|------|
| AI 領域快速膨脹 | 2023-2026 期間，LLM、Agent、MCP 等領域爆炸式成長，傳統教材更新速度跟不上 |
| 框架抽象層級過高 | PyTorch、HuggingFace、LangChain 等框架隱藏了大量底層實作細節 |
| 動手實作教材稀缺 | 多數線上課程以影片/投影片為主，缺乏可執行的程式碼與測試 |
| 開源 AI 教育缺乏結構化 | 現有開源資源（fast.ai、d2l.ai、Andrej Karpathy 系列）各有所長但未形成 0→生產的完整閉環 |

---

## 3. 這個技術是如何解決該問題的？

### 核心機制：三層結構化學習系統

```
┌─────────────────────────────────────────────────────┐
│                   Curriculum                        │
│  20 Phases × 503 Lessons × ~314 小時                │
│  Python / TypeScript / Rust / Julia                 │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Build It│ │Use It  │ │Ship It │
│手寫實作 │ │框架使用 │ │產出工具 │
└────────┘ └────────┘ └────────┘
```

### 具體做法

#### 3.1 課程結構：20 階段線性依賴

```
Phase 0   Setup & Tooling
    │
Phase 1   數學基礎 (線代、微積分、機率、資訊論)
    │
Phase 2   ML 基礎 (回歸、分類、評估、集成)
    │
Phase 3   深度學習核心 (感知機、Backprop、Optimizer、Mini Framework)
    │
    ├──── Phase 4   電腦視覺 (CNN, YOLO, Diffusion, NeRF, VLM)
    ├──── Phase 5   NLP (Tokenization, Seq2Seq, Attention, LLM Eval)
    ├──── Phase 6   語音與音訊 (ASR, TTS, Whisper, Voice Clone)
    ├──── Phase 9   強化學習 (DQN, PPO, RLHF)
    │
Phase 7   Transformers 深入 (Self-Attention, BERT, GPT, MoE, Flash Attention)
    │
Phase 8   生成式 AI (GAN, Diffusion, ControlNet, Flow Matching)
    │
Phase 10  LLMs from Scratch (Tokenizer 實作, Pre-training 124M GPT, SFT, RLHF, DPO)
    │
Phase 11  LLM Engineering (RAG, Prompting, Evals, Guardrails, Agents intro)
    │
Phase 12  多模態 AI
    │
Phase 13  Tools & Protocols (MCP 建構)
    │
Phase 14  Agent Engineering (Agent Loop, Tool Use, Memory, Planning)
    │
Phase 15  自主系統
    │
Phase 16  多智能體與群體智慧
    │
Phase 17  基礎設施與生產部署
    │
Phase 18  倫理、安全與對齊
    │
Phase 19  畢業專案
```

#### 3.2 每堂課的六段結構（MOTTO → PROBLEM → CONCEPT → BUILD IT → USE IT → SHIP IT）

| 階段 | 內容 | 產出 |
|------|------|------|
| MOTTO | 一句核心概念 | 心智模型入口 |
| PROBLEM | 具體痛點描述 | 學習動機 |
| CONCEPT | 圖解與直覺（無程式碼） | 心智模型建立 |
| BUILD IT | 從原始數學手寫實作（無框架） | `code/main.py`（可執行、有測試） |
| USE IT | 使用 PyTorch / sklearn 等框架重做一次 | 框架理解、非黑箱 |
| SHIP IT | 產出可重用工具 | `outputs/` 中的 prompt / skill / agent / MCP server |

#### 3.3 輸出物：每堂課產出一個可重用工具

```
outputs/
├── prompts/      提示詞模板（可貼入任何 AI 助手）
├── skills/       SKILL.md（可載入 Claude/Cursor/Codex/Hermes）
├── agents/       自主 Agent（基於 Phase 14 手寫的 Agent Loop）
├── mcp-servers/  MCP 伺服器（基於 Phase 13）
└── index.json    索引
```

#### 3.4 依賴管理策略

```
語言      允許的依賴
─────────────────────────────────────
Python    numpy, h5py, zstandard, safetensors, stdlib
TypeScript hono, zod, ws, @hono/node-server, Node 20+ stdlib
Rust      stdlib only (rustc --edition 2021)
Julia     Random, Statistics, LinearAlgebra, Printf (stdlib)
```

強制 stdlib-first，確保學習者理解原理後才引入外部庫。

#### 3.5 Agent Skills（內建學習輔助）

| Skill | 功能 |
|-------|------|
| `/find-your-level` | 10 題定位測驗，輸出個人化學習路徑與時間估算 |
| `/check-understanding <phase>` | 各階段 8 題測驗，附回饋與建議複習課程 |

#### 3.6 CI/CD 自動化

| Job | 說明 |
|-----|------|
| `audit` | 對所有 PR/push 執行 `audit_lessons.py`，檢查課程結構完整性（blocking） |
| `readme-counts-sync` | 合併 main 後自動更新 README 課程數 |
| `site-rebuild` | 合併 main 後自動重建 `site/data.js` |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|----------|-------------|---------------|-----------------|
| **fast.ai** | 以 PyTorch 為基礎的 top-down 教學法（先訓練模型再理解原理） | 學習者具備 Python 基礎程式能力 | 學習者對底層運算理解較淺；課程範圍偏重 CV/NLP，不含 Agent/MCP/多智能體 | 能夠快速上手訓練實用模型，適合想先看到成果的學習者 |
| **d2l.ai (Dive into Deep Learning)** | 互動式 Jupyter Notebook 教科書，從數學推導到框架實作，支援 PyTorch/TensorFlow/JAX | 學習者具備基本微積分與線性代數知識 | 範圍以深度學習為主，缺少 LLM Engineering、Agent、MCP 等後期主題；無法產出可重用工具 | 提供扎實的深度學習理論與互動練習 |
| **Andrej Karpathy 系列 (nanoGPT, makemore, Zero-to-Hero)** | 從零開始建立 GPT/Transformer 的影片教學，逐步手寫實作 | 學習者具備 Python 與基礎 ML 知識 | 內容聚焦 LLM/Transformer 領域，缺少 CV/語音/強化學習/多智能體；無結構化測驗與定位系統 | 對 LLM 內部機制有深入理解，適合對 Transformer 有興趣的學習者 |
| **HuggingFace Course** | 圍繞 HuggingFace 生態系的實作教學（Transformers, Datasets, Tokenizers, Diffusers） | 學習者具備 Python 基礎 | 強依賴 HuggingFace 生態系，較少從零開始的底層數學推導；範圍以 NLP/CV 為主，不含 Agent/MCP | 能熟練使用 HuggingFace 工具鏈進行微調與部署 |

### 各方案切入點差異

```
fast.ai          ──→ Top-down: 先做再理解
d2l.ai           ──→ Bottom-up: 從數學理論出發
Karpathy series  ──→ 聚焦 LLM/Transformer 領域的深度實作
HuggingFace      ──→ 聚焦特定生態系的工具教學
───────────────────────────────────────────
ai-engineering-from-scratch
                  ──→ Bottom-up 全覆蓋: 數學 → 框架 → 生產 → 工具輸出
                      唯一一個從線性代數走到多智能體群體智慧的線性路徑
                      唯一一個強調每堂課「Ship It」產出可重用工具
```
