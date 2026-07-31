# 1. Building Intelligent Document Processing with Apache Camel, Docling and LangChain4j

**Source**: https://feeds.feedblitz.com/~/964749371/0/baeldung
**Author**: Baeldung
**Date**: 2026-07-31
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

解決「LLM 無法直接且高品質地處理真實世界文件(尤其是 PDF)」的問題。具體痛點有三:

| 痛點 | 說明 |
|------|------|
| 結構資訊流失 | PDF 中的標題、表格、圖片在純文字抽取後被打散,LLM 失去語意脈絡 |
| 重複轉換成本 | 每次問答都重新解析同一份文件,浪費運算資源 |
| 缺乏統一編排 | 文件解析、向量檢索、LLM 推理散落各處,難以串成可靠管線 |

本方案目標:把非結構文件**一次性**轉成結構化 Markdown,再以同一份 Markdown 重複餵給 LLM 進行摘要分析與 Q&A,兼顧品質與成本。

## 2. 這個問題為什麼會發生?(背景)

LLM 的知識來源是其 context window 內的文字。當企業文件(合約、政策手冊、技術規格)以 PDF、DOCX、PPTX 儲存時,直接抽取純文字會產生以下失真:

- **表格崩塌**:多欄位表格被壓成單行雜湊文字,欄位對應關係消失
- **標題階層扁平化**:H1/H2/H3 的層級被抹平,LLM 無法分辨主從段落
- **圖片/圖表流失**:視覺化資訊無法轉成文字,關鍵數據遺漏
- **跨頁斷裂**:段落被分頁截斷,句子不完整

這些失真直接降低 RAG(Retrieval-Augmented Generation)的檢索品質與生成準確度。傳統解法(如 Apache Tika、PyMuPDF)只做「字面抽取」,不還原文件語意結構。IBM Docling 的出現,正是為了補上「結構還原」這一層,而 Apache Camel 提供企業級的整合編排,LangChain4j 則銜接 JVM 生態的 LLM 抽象層。

## 3. 這個技術/政策是如何解決該問題的?

整體管線分三層,各司其職:

```
[PDF/DOCX] → (Camel Route) → [Docling Server] → Markdown (.md)
                                                          ↓
                          [LangChain4j Chat] ← 組裝 Prompt → LLM → 分析/Q&A
                                                          ↓
                                              [Undertow HTTP API]
```

### 3.1 Docling:結構還原引擎

- 透過 `docling-serve` Docker 容器(REST API,port 5001)部署
- Camel 的 `docling:CONVERT_TO_MARKDOWN` endpoint 將文件送入 Docling,回傳 Markdown
- 保留標題階層、表格結構、圖片描述,輸出語意完整的 Markdown

### 3.2 Apache Camel:管線編排

- **File Component** 監控 `documents/` 目錄(`include=.*\.(pdf|docx|pptx|html|md)`)
- `noop=true` 保留原始檔案不刪除;`idempotent=true` 防止重複處理同一檔案
- **pollEnrich EIP**:Q&A API 不每次重新轉換 PDF,而是讀取已生成的 Markdown 檔,實現「轉換一次、重複使用」
- **Undertow Component**:嵌入式 HTTP server,暴露 `POST /api/ask` 端點

### 3.3 LangChain4j:LLM 抽象層

- `OpenAiChatModel` 透過 `baseUrl` 指向 OpenAI 相容端點(示範用 LangChain4j demo endpoint,亦可接 Ollama 本地模型)
- `langchain4j-chat` Camel component 在 route 中送 prompt 給 chat model
- Prompt 模板將 Markdown 文件 + 使用者問題組裝成 grounded context,要求 LLM「僅依文件內容回答」

### 3.4 成本與效率設計

| 設計 | 效益 |
|------|------|
| 轉換一次、存 Markdown | 避免每次請求都呼叫 Docling,降低 CPU/延遲 |
| pollEnrich 讀取快取 | HTTP 請求輕量化,LLM 只處理問答 |
| idempotent 檔案消費 | 防止批次重跑時重複轉換 |
| Camel Route DSL | 宣告式整合,易於擴充(加向量庫、加分流) |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 定位 | 與本方案差異 |
|------|------|-------------|
| **Unstructured.io** | Python 生態的文件解析 | 結構還原能力強,但非 JVM 原生,需跨語言整合 |
| **Apache Tika** | 通用文件抽取 | 只做字面抽取,不還原語意結構 |
| **Spring AI DocumentReader/Eater** | Spring 生態的文件讀取 | 與 Spring AI 整合更深(用戶正在學 Spring+AI,值得對比) |
| **LlamaIndex / Haystack** | Python RAG 框架 | 提供完整 RAG 管線(分塊、向量庫、检索),但 JVM 環境需額外橋接 |
| **OpenAI Assistants API / File API** | 雲端一站式 | 免自架管線,但文件解析能力受限、廠商綁定 |
| **PyMuPDF + 自訂 Markdown 轉換** | 手工打造 | 彈性最高,但維護成本高、表格還原仍需大量工 |

### 思考方式:轉換 vs. 檢索的分層

本方案體現一個重要架構思維:**把「文件理解」與「問答推理」解耦**。Docling 負責把文件變成 LLM 友善格式(一次性成本),LangChain4j 負責在友善格式上做推理(每次請求成本)。這與 RAG 的「索引層 vs. 查詢層」分離原則一致。

### 對用戶情境的對照

用戶技術棧為 Ruby on Rails + React + GCP,學習中 Spring+AI。本方案雖以 Java/Camel 為主,但其「轉換一次、重複使用」的快取思維可直接移植到 Rails 側:用 Sidekiq 預處理文件為 Markdown,再以 ActiveJob 佇列 Q&A 請求。而若要正式引入 Spring+AI,本方案的 Camel Route DSL 是觀察「企業整合模式(EIP)如何套用到 AI 管線」的良好範本。