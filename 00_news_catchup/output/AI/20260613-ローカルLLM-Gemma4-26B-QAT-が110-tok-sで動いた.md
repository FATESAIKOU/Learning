# 02. ローカルLLM（Gemma4 26B QAT）が110 tok/sで動いた

**Source**: https://qiita.com/rS_alonewolf/items/7859599ed282facb05d7
**Author**: rS_alonewolf
**Date**: 2026-06-13
**Category**: AI技術

## 1. この技術/政策は何を解決するのか?

本驗證解決的核心問題是：**如何在消費級 GPU（16GB VRAM）上，以實用速度執行 26B 參數級別的大型語言模型，同時維持可接受的輸出品質**。

具體的技術突破點：

| 問題 | 傳統方案 | QAT 方案 |
|------|----------|----------|
| 26B 模型無法載入 16GB VRAM | 使用 CPU offloading，速度降至 5-10 tok/s | QAT Q4_K_XL 量化使模型完全載入 GPU VRAM |
| 常規量化（Q4/Q5/Q6）品質損失大 | 33-35 tok/s，但輸出品質明顯下降 | QAT（Quantization-Aware Training）在訓練階段就考慮量化誤差，品質保留度更高 |
| 128K context 下記憶體不足 | 縮短 context 或使用較低精度 | QAT 版在 128K context 下仍可全載入 16GB VRAM |

最終成果：`gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf` 在 RTX 5070 Ti 16GB 上達到 **111.9 tok/s**，是常規量化版（33-35 tok/s）的 **3.2 倍**。

## 2. この問題が発生する背景は?

### 2.1 本地 LLM 部署的硬體現實

2026 年的消費級 GPU 市場結構如下：

```
GPU VRAM 分布（消費級）:
  8GB  ████████████████████████  主流（RTX 4060/5060）
 12GB  ████████████              （RTX 4070/5070）
 16GB  ██████████                （RTX 4070 Ti Super / 5070 Ti）
 24GB  ████                      （RTX 4090/5090，高階）
 32GB+ ██                        （專業卡/Apple Silicon）
```

26B 參數模型在 FP16 精度下需要約 52GB VRAM，即使使用 4-bit 常規量化仍需約 16-18GB，剛好超出 16GB 消費級 GPU 的邊界。這使得大多數開發者被迫在「使用較小模型（7B-13B）」和「忍受 CPU offloading 的低速」之間二選一。

### 2.2 QAT（Quantization-Aware Training）的技術背景

傳統的 Post-Training Quantization（PTQ）在模型訓練完成後直接對權重進行量化，不考慮量化誤差對模型行為的影響。這導致：

```
PTQ 流程:
  訓練完成 → 直接量化 → 精度損失不可逆

QAT 流程:
  訓練中模擬量化 → 模型學習補償量化誤差 → 量化後精度損失最小化
```

Gemma 4 的 QAT 版本是 Google 在訓練階段就針對 4-bit 量化進行最佳化的官方版本。其核心優勢在於：

- **A4B 架構**：Gemma 4 26B 採用 Mixture-of-Experts 的 A4B（Active 4 Billion）設計，每次推理僅啟動約 4B 活躍參數，其餘專家處於休眠狀態
- **QAT 訓練**：在預訓練/Fine-tuning 階段就模擬 4-bit 量化的數值行為，使模型權重分布天然適應低精度表示
- **UD（Unified Decoder）格式**：統一的解碼器格式減少了推理時的格式轉換開銷

### 2.3 實際使用場景的驅動力

作者的使用場景是 **OpenCode + llama-swap**，即用本地 LLM 驅動 AI 輔助程式設計工具。這類場景對模型的要求是：

- **低延遲**：程式碼補全/修改建議需在 1-2 秒內返回
- **長 context**：分析大型程式碼庫需要 128K token 以上的 context window
- **高品質**：程式碼生成的邏輯正確性不能因量化而顯著下降

## 3. この技術/政策はどのようにその問題を解決するのか?

### 3.1 技術棧架構

```
┌──────────────────────────────────────────┐
│             OpenCode (客戶端)              │
├──────────────────────────────────────────┤
│          llama-swap (路由層)              │
│  ┌─────────────┐  ┌──────────────────┐   │
│  │ 常用設定     │  │ 速度計測設定      │   │
│  │ b2048/ub256 │  │ b4096/ub512      │   │
│  │ 日常使用基準  │  │ 111.9 tok/s 峰值 │   │
│  └─────────────┘  └──────────────────┘   │
│  ┌─────────────┐                         │
│  │ fallback    │                         │
│  │ b1024/ub128 │                         │
│  │ CPU 退避模式 │                         │
│  └─────────────┘                         │
├──────────────────────────────────────────┤
│     llama.cpp / llama-server (推理引擎)    │
│  - Q4_0 cache type (ctk q4_0, ctv q4_0) │
│  - Flash Attention (fa on)               │
│  - 99 GPU layers (ngl 99)               │
│  - DeepSeek reasoning format             │
├──────────────────────────────────────────┤
│  RTX 5070 Ti 16GB VRAM (硬體層)           │
│  gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf │
└──────────────────────────────────────────┘
```

### 3.2 關鍵參數配置與其作用

| 參數 | 值 | 作用 |
|------|-----|------|
| `-ngl 99` | 99 層載入 GPU | 將幾乎所有模型層載入 GPU VRAM，避免 CPU/GPU 間的 PCIe 傳輸瓶頸 |
| `-fa on` | Flash Attention 啟用 | 將 attention 計算的記憶體複雜度從 O(n²) 降至 O(n)，使 128K context 可行 |
| `-ctk q4_0 -ctv q4_0` | KV cache 4-bit 量化 | 大幅減少 128K context 下的 KV cache 記憶體佔用 |
| `-b 4096 -ub 512` | batch size / micro-batch | 大 batch 提高 GPU 利用率，但需平衡 VRAM 壓力 |
| `--reasoning auto --reasoning-format deepseek` | DeepSeek 式推理格式 | 支援 chain-of-thought 推理輸出 |

### 3.3 三層配置策略的設計邏輯

作者設計了三層配置而非單一設定，這反映了生產環境中本地 LLM 部署的現實需求：

```
常用設定 (b2048/ub256):
  → 穩定性優先，適合日常開發使用
  → GPU 全載入，速度已遠超常規量化版

速度計測設定 (b4096/ub512):
  → 極限性能測試，展示 QAT 的理論上限
  → 16GB VRAM 邊界上的激進配置

Fallback 設定 (b1024/ub128):
  → 當 GPU 全載入不穩定時的逃生路徑
  → 部分 expert 層退避至 CPU，確保可用性
```

### 3.4 與常規量化的性能對比

| 指標 | 常規 Gemma4 26B Q4/Q5/Q6 | QAT Q4_K_XL | 倍率 |
|------|--------------------------|-------------|------|
| 推理速度 | 33-35 tok/s | 111.9 tok/s | **3.2x** |
| VRAM 佔用 | 超出 16GB（需 CPU offload） | 16GB 內全載入 | — |
| 128K context | 需大幅縮減或 CPU offload | 完全支援 | — |
| 輸出品質 | 常規 PTQ 品質損失 | QAT 訓練補償，品質保留度更高 | — |

## 4. 類似の問題を解決する他の技術/フレームワーク/考え方は存在するか?

### 4.1 本地 LLM 部署的替代方案矩陣

| 方案 | 代表技術 | 優點 | 缺點 |
|------|----------|------|------|
| **QAT 量化** | Gemma4 QAT, Llama QAT | 品質保留度最高，速度最快 | 需原廠在訓練階段就進行 QAT，模型選擇有限 |
| **MoE 架構** | Mixtral 8x7B, DeepSeek-V2 | 活躍參數少，推理效率高 | 總參數量大，VRAM 需求仍高 |
| **CPU/GPU 混合推理** | llama.cpp CPU offloading | 任何模型都能跑 | 速度降至 5-10 tok/s，實用性受限 |
| **模型蒸餾** | DistilBERT, Phi 系列 | 小模型速度快 | 能力上限受限，複雜任務表現不足 |
| **API 服務** | OpenAI, Anthropic, Google | 無本地硬體需求 | 延遲、成本、資料隱私問題 |
| **Apple Silicon 統一記憶體** | M4 Max 128GB + MLX | 超大模型可全載入 | 硬體成本高，生態系較封閉 |

### 4.2 QAT 技術的發展脈絡

QAT 並非新概念，但在 LLM 領域的規模化應用是 2025-2026 年的重要趨勢：

```
2018: QAT 首次在電腦視覺領域證明有效性 (Google)
2020: TensorFlow Lite / PyTorch QAT 工具鏈成熟
2023: LLM 時代，PTQ (GPTQ, AWQ) 成為主流
2024: Llama 3 開始提供官方 QAT 版本
2025: Gemma 3 QAT, DeepSeek QAT 出現
2026: Gemma 4 QAT 達到消費級 GPU 全載入的實用水準
```

### 4.3 對實際開發者的意義

對於使用 macOS 環境的開發者（如 ABOUTUSER.md 所述），本地 LLM 部署的選擇更為多元：

- **Apple Silicon + MLX**：M4 Pro/Max 的統一記憶體架構可支援更大模型，但 MLX 生態系的工具鏈（llama-swap 等效方案）成熟度仍低於 llama.cpp
- **WSL2 + Docker + llama-swap**（本文作者方案）：在 Windows 環境中利用 WSL2 的 GPU passthrough，是目前消費級 GPU 本地 LLM 部署的最佳實踐
- **雲端 GPU 租用**：Lambda Labs / RunPod 提供 A100/H100 租用，適合偶發性的大量推理需求

本驗證的核心價值在於證明了 **2026 年的消費級 GPU（RTX 5070 Ti 16GB）配合 QAT 量化技術，已能達到本地部署 26B 級模型且速度超越人類閱讀速度（~10 tok/s）一個數量級的實用水準**。這意味著「本地 AI 程式設計助手」從「勉強可用」進入了「流暢使用」的階段。
