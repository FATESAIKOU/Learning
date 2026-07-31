# 3. This Week in Spring - July 28th 2026

**Source**: https://spring.io/blog/2026/07/28/this-week-in-spring-july-28-2026
**Author**: Josh Long
**Date**: 2026-07-28
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

本篇為 Spring 生態週報，匯整當週多個主題，各自解決不同問題：

| 主題 | 解決的問題 |
|------|-----------|
| **Spring Tools MCP server** | IDE 對 Spring 專案缺乏結構化、可程式化的查詢介面，LLM/agent 難以取得 Spring 專案語意 |
| **JetBrains IntelliJ 對 Spring 的新支援** | IntelliJ 對 Spring 設定的智慧提示仍有限，需官方深化整合 |
| **Tanzu SLSA Level 3 合規依賴** | 供應鏈資安：依賴來源缺乏可驗證的構建 provenance |
| **動態多租戶 Spring Boot** | 多租戶 SaaS 的資料/配置隔離需手刻，缺官方範式 |
| **Spring AI Alibaba workflow graph 視覺化**（Craig Walls） | Spring AI Alibaba workflow 難以直觀理解與除錯 |
| **Spring AI ChatMemory + JDBC 持久化** | 對話記憶預設 in-memory，跨重啟/橫向擴展失效 |
| **ChatMemory 三種新持久化方式** | 單一 JDBC 不足以涵蓋不同持久化需求 |
| **Java 27 預覽**（Billy Korando） | 開發者需提前掌握 Java 27 對 Spring 生態的影響 |
| **Spring Batch + MongoDB（Spring Boot 4.1）** | 批次處理過去綁 RDB，NoSQL 場景需自行整合 |
| **Hibernate 基礎教學** | JPA/Hibernate 入門痛點 |
| **in-memory vector search engine + Spring AI 整合**（Brian Sam-Boden） | 自建向量搜尋缺乏輕量、易接 Spring AI 的選項 |

對使用者最相關的三大主軸：**MCP server（學習中）、Spring AI 持久化（學習 Spring+AI）、供應鏈資安 SLSA**。

## 2. 這個問題為什麼會發生?(背景)

1. **MCP 協議 2024 末由 Anthropic 推出後快速成為 agent-tool 標準**，Spring Tools 需對應提供 MCP server 才能讓 Cursor/Claude 等 agent 理解 Spring 專案結構
2. **Spring AI 2024 起 GA 後快速演化**，ChatMemory 早期僅 in-memory，生產場景（k8s 橫向擴展、長對話）需求浮現，持久化成為必要
3. **供應鏈攻擊（SolarWinds、xz utils 後門）**使 SLSA 框架成為主流，Tanzu 作為 Spring 商業發行方需達 Level 3 以滿足企業採購要求
4. **Java 27（2026 下半年預覽）**持續補強 pattern matching、value type（Project Valhalla），Spring 需預先對接
5. **向量搜尋從「必接 Pinecone」走向「輕量 in-memory 可起步」**，降低 POC 門檻

推測背景：Josh Long 作為 Spring Developer Advocate，週報刻意把「MCP + AI + 供應鏈 + Java 27」編排在一起，呈現 Spring 團隊 2026 中期的策略主軸——把 Spring 從「Web 框架」推進為「AI 應用 + agent 友善 + 供應鏈可信」的綜合平台。

## 3. 這個技術/政策是如何解決該問題的?

針對最相關的項目展開：

### Spring Tools MCP server
```
IDE (VS Code / Eclipse)
   ↓ MCP protocol
Spring Tools MCP server
   ↓
Spring 專案語意模型（beans / configurations / dependencies / routes）
```
- 將原本 IDE 內的 Spring 智慧功能以 MCP server 形式對外暴露
- 任何 MCP 相容 client（Cursor、Claude Desktop、自建 agent）都能以結構化方式查詢「這個專案有哪些 bean、自動設定來源、依賴圖」
- 對使用者「Cursor+Claude 探索」學習線直接相關：Spring 專案接入 MCP 後，Claude 能更精準生成/重構 Spring 程式碼

### Spring AI ChatMemory 持久化
| 方式 | 適用場景 |
|------|---------|
| JDBC | 傳統 RDB、易部署 |
| 三種新方式（Craig Walls 文） | 推測涵蓋 Redis / Neo4j / Cassandra 等不同特性後端 |

### SLSA Level 3
- Tanzu 發行的 Spring 相依二進位具備可驗證的 build provenance
- 達 Level 3 表示：建置平台受託管、有隔離、產出簽章、可追溯

### Spring Batch + MongoDB（Boot 4.1）
- `MongoItemReader` / `MongoItemWriter` 強化，使批次處理可直接讀寫 MongoDB，不需自製 adapter

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 對應領域 | 替代方案 | 與 Spring 作法對比 |
|---------|---------|------------------|
| MCP server | LangChain tools、自建 MCP server | Spring Tools MCP 提供「框架內建語意模型」優勢，免自寫描述 |
| AI 對話記憶持久化 | LangGraph checkpointer、Mem0、自建 Redis | Spring AI 的 JDBC/Redis adapter 較薄，但與 Boot DI 一致 |
| 供應鏈 SLSA | Sigstore + SLSA GitHub generator | Tanzu 走商業發行簽章，GitHub generator 走 OSS 簽章 |
| Vector search in-memory | LanceDB、Chroma（in-memory mode）、hnswlib | Brian Sam-Boden 專案主打 Spring AI 開箱即用 |
| 多租戶 | Hibernate Filter、schema-per-tenant | 動態多租戶在 Spring 仍需組裝，未有一等公民 |

**思考方式啟發**：
- **MCP 化既有工具**是當前 LLM 時代「老工具新介面」的典型策略——把 IDE 內部 API 以 MCP 對外暴露，等於把工具能力借給所有 agent。使用者學習 MCP 時可參考此案例：MCP 不只包新工具，更能「解放」既有工具
- **ChatMemory 持久化多後端**對照 K8s CRD 的「storage driver 抽象」設計，是同一種「介面分離後端」模式
- **SLSA Level 3** 是企業導入 Spring 的採購門檻，對使用者即將任管理者、負責採購與時程的情境，需理解供應鏈合規與時程的權衡

**行動建議**：
1. 實際啟用 Spring Tools MCP server 並接上 Cursor + Claude，對照未接 MCP 前的生成品質差異
2. 以 Spring AI ChatMemory JDBC 為起點，練習切換為 Redis 後端，驗證抽象設計
3. 追蹤 Brian Sam-Boden 的 in-memory vector engine，作為 Spring+AI 學習線的 side project 標的