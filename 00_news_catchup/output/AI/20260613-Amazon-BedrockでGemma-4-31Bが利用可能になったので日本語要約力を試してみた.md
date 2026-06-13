# 03. Amazon BedrockでGemma 4 31Bが利用可能になったので日本語要約力を試してみた

**Source**: https://dev.classmethod.jp/articles/gemma-4-31b-bedrock-mantle-japanese-summarization/
**Author**: DevelopersIO (Classmethod)
**Date**: 2026-06-13
**Category**: AI技術

## 1. この技術/政策は何を解決するのか?

本驗證解決的核心問題是：**在 AWS 託管環境中，是否存在一個兼具高日語能力、低成本的 LLM 選項，用於替代昂貴的 Claude/GPT 系列進行日語文本處理任務**。

Gemma 4 31B 在 Amazon Bedrock 上的可用性直接回應了以下需求：

| 需求 | 現狀 | Gemma 4 31B 的定位 |
|------|------|---------------------|
| **日語能力** | Claude/GPT 日語能力強但昂貴；開源模型日語能力參差不齊 | Google 官方支援 35+ 語言，日語為重點最佳化語言之一 |
| **成本控制** | Claude Opus 4.8 輸出單價 $25.00/1M tokens | Gemma 4 31B 輸出單價 $0.40/1M tokens，為 Opus 的 **1/62.5** |
| **託管便利性** | 自架開源模型需管理基礎設施 | Bedrock 全託管，無需管理 GPU 實例 |
| **API 相容性** | Bedrock 既有 InvokeModel/Converse API 與業界標準不同 | 透過 bedrock-mantle 端點提供 OpenAI 相容的 Chat Completions API |

## 2. この問題が発生する背景は?

### 2.1 Bedrock 上 LLM 選擇的價格斷層

截至 2026 年 6 月，Amazon Bedrock us-east-1 的 on-demand 價格呈現明顯的「高階昂貴、低階能力不足」的斷層：

```
價格分布（輸出單價, $/1M tokens）:

$0.40  ██ Gemma 4 31B ← 新選項
$0.60  ██ gpt-oss-120b
$4.00  ██████████ Claude Haiku 4.5
$15.00 ██████████████████████████████ Claude Sonnet 4.6
$16.50 ████████████████████████████████ GPT-5.4
$25.00 ██████████████████████████████████████████████ Claude Opus 4.8
$33.00 ██████████████████████████████████████████████████████████ GPT-5.5
```

Gemma 4 31B 的 $0.40/1M tokens 輸出單價填補了「低價但能力不足」與「高能力但昂貴」之間的空白地帶。

### 2.2 bedrock-mantle 新端點的架構背景

Gemma 4 31B 是首批透過 `bedrock-mantle` 端點提供的模型。這是一個重要的架構轉變：

```
傳統 Bedrock 架構:
  應用 → bedrock-runtime (InvokeModel/Converse API) → 模型

新 Bedrock Mantle 架構:
  應用 → bedrock-mantle (OpenAI 相容 Responses/Chat Completions API) → 模型
```

`bedrock-mantle` 的設計意圖是提供與 OpenAI API 相容的介面，降低從 OpenAI 遷移到 Bedrock 的程式碼修改成本。但這也帶來了限制：

- **InvokeModel / Converse API 非対応**：既有的 Bedrock 應用無法直接使用 Gemma 4 31B
- **Reasoning 輸出僅在 Responses API 中可見**：Chat Completions API 不返回 reasoning tokens
- **並列 tool call 非対応**：一次回應中無法返回多個 tool call
- **Payload 上限 3.5 MB**：雖然模型支援 256K context，但實際可投入的輸入量受 payload 大小限制

### 2.3 Gemma 3 → Gemma 4 的技術演進

| 項目 | Gemma 3 27B | Gemma 4 31B | 變化 |
|------|-------------|-------------|------|
| 參數數 | 27B | 30.7B | +13.7% |
| 架構 | Dense | Dense | 不變 |
| Context 長度 | 128K | 256K | **2x** |
| 輸入模態 | 文字、圖片 | 文字、圖片、**影片** | 新增影片 |
| Reasoning | 無 | **內建** | 新增 |
| Function calling | 無 | **原生支援** | 新增 |
| 對應語言 | 35+ | 35+ | 不變 |

## 3. この技術/政策はどのようにその問題を解決するのか?

### 3.1 驗證方法

作者使用以下環境對 Gemma 4 31B 的日語要約能力進行實證：

```
┌─────────────────────────────────────────┐
│           Python (openai ライブラリ)       │
│  Chat Completions API                    │
├─────────────────────────────────────────┤
│  aws-bedrock-token-generator            │
│  (IAM 認証 → OpenAI SDK 互換トークン生成)  │
├─────────────────────────────────────────┤
│  bedrock-mantle.us-east-1.api.aws       │
│  /openai/v1 (OpenAI 互換エンドポイント)    │
├─────────────────────────────────────────┤
│  google.gemma-4-31b (モデルID)           │
└─────────────────────────────────────────┘
```

### 3.2 成本效益的量化分析

以日語要約任務為例，假設每次要約輸入 5,000 tokens、輸出 500 tokens：

| 模型 | 每次成本 | 相對 Gemma 4 31B |
|------|----------|-------------------|
| **Gemma 4 31B** | $0.0009 | 1x（基準） |
| Claude Haiku 4.5 | $0.0060 | 6.7x |
| Claude Sonnet 4.6 | $0.0225 | 25x |
| GPT-5.5 | $0.0440 | 49x |

對於每日處理 1,000 件日語文件要約的企業場景，選擇 Gemma 4 31B 而非 Claude Sonnet 4.6 可節省約 **$7,884/月**。

### 3.3 技術限制與取捨

Gemma 4 31B 的低價並非沒有代價：

```
優勢:
  ✓ 極低價格（輸出 $0.40/1M tokens）
  ✓ 256K context window
  ✓ 原生 Reasoning + Function calling
  ✓ 多模態（文字/圖片/影片）
  ✓ OpenAI 相容 API

劣勢:
  ✗ 31B 參數，絕對能力上限低於 120B+ 模型
  ✗ bedrock-mantle 專用，無法使用既有 Converse API
  ✗ Reasoning 輸出僅在 Responses API 可見
  ✗ 並列 tool call 非対応
  ✗ Payload 3.5 MB 上限限制實際輸入量
```

### 3.4 適用場景判斷

基於以上分析，Gemma 4 31B 的適用場景矩陣：

| 場景 | 適用性 | 理由 |
|------|--------|------|
| 日語文件要約/分類 | **最適** | 日語能力強、成本極低、不需複雜 tool call |
| 多模態內容分析 | **適合** | 支援圖片+影片輸入，256K context |
| 複雜 Agent 工作流 | **部分適合** | Function calling 可用但並列 tool call 受限 |
| 高精度程式碼生成 | **不適合** | 31B 參數上限，複雜邏輯建議使用 Claude/GPT |
| 即時串流對話 | **適合** | Chat Completions API 支援 streaming |

## 4. 類似の問題を解決する他の技術/フレームワーク/考え方は存在するか?

### 4.1 Bedrock 上低價 LLM 的替代選項

| 模型 | 輸出單價 | 參數 | 日語能力 | 特點 |
|------|----------|------|----------|------|
| **Gemma 4 31B** | $0.40 | 30.7B | 高（Google 官方日語最佳化） | 256K context, 多模態 |
| **gpt-oss-120b** | $0.60 | 120B | 中高 | 參數大但價格僅略高 |
| **Llama 4 (預期)** | 未定 | 多種 | 中 | Meta 開源，預期也將登陸 Bedrock |
| **自架 Gemma 4** | 基礎設施成本 | 30.7B | 高 | 無託管便利性但完全可控 |

### 4.2 多雲端低價日語 LLM 選項

| 平台 | 模型 | 特點 |
|------|------|------|
| **GCP Vertex AI** | Gemini 2.5 Flash | Google 原生平台，日語能力最強，但價格高於 Gemma 4 |
| **Azure AI** | Phi-4 系列 | 微軟小型模型，日語能力中等，價格低 |
| **本地部署** | Gemma 4 QAT + llama.cpp | 完全免費但需自備 GPU（參考 idx 7 的驗證） |

### 4.3 策略建議：混合模型架構

對於需要處理大量日語內容的企業應用，最佳策略是採用混合模型架構：

```
┌─────────────────────────────────────────┐
│              路由層 (Router)              │
│  依任務複雜度/成本預算分配請求              │
├────────────┬────────────┬───────────────┤
│ 簡單任務    │ 中等任務    │ 複雜任務       │
│ (要約/分類) │ (分析/提取) │ (生成/推理)    │
│            │            │               │
│ Gemma 4    │ gpt-oss    │ Claude Sonnet │
│ 31B        │ 120b       │ 4.6 / GPT-5.4 │
│ $0.40/M    │ $0.60/M    │ $15-16/M      │
└────────────┴────────────┴───────────────┘
```

這種架構在維持高品質輸出的同時，可將整體 LLM 成本降低 60-80%。Gemma 4 31B 的出現使這種混合策略在 Bedrock 單一平台上即可實現，無需跨多個雲端平台管理。
