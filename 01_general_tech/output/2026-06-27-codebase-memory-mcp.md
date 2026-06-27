# codebase-memory-mcp 技術分析報告

> 來源：[DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) README + arXiv:2603.27277 論文摘要
> 調研日期：2026-06-27

---

## 1. 這個技術解決什麼問題？

LLM coding agent（Claude Code、Codex CLI、Gemini CLI 等）探索程式庫時，只能反覆 `grep` + 逐檔 `read`，**缺乏結構性理解**：
- 每次查詢消耗數萬 token，卻仍不知道「誰呼叫誰」「跨檔呼叫鏈」「介面實作歸屬」。
- 5 個結構性問題 = ~412,000 token（file-by-file）vs ~3,400 token（本工具）→ **99.2% token 浪費**。

**被解決的具體問題**：在無須嵌入 LLM、無須 API key 的前提下，讓 coding agent 透過 MCP 取得一個**持久化、可跨 session 重用、sub-ms 查詢**的程式庫知識圖譜，把「結構性理解」從 agent 端外移到一個靜態二進位後端。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到
- LLM coding agent 預設只有 `read` / `grep` / `glob` 等工具，**沒有程式庫的全域結構索引**。
- 其他 code graph 工具選擇在內部嵌入一個 LLM 做「自然語言 → 圖查詢」轉譯，導致**額外 API key、額外成本、又一個模型要設定**。
- MCP 協議出現後，agent 本身就是查詢轉譯器，使得「後端只負責結構分析、不負責語意翻譯」成為可行分工。

### 通用技術背景（自行補充）
- **tree-sitter** 只給語法 AST，無法解析 `user.profile.display_name()` 跨三個模組的型別歸屬；要靠 LSP（tsserver / pyright / gopls / rust-analyzer）做型別解析，但 LSP 需 per-project 起一個 language server process。
- **Token 成本** 是 LLM agent 落地的硬限制：context window 越大越貴，重複讀檔會把 context 塞滿噪聲。
- **持久化** 是跨 session 的關鍵：每次都從零重算索引會拖慢 agent 響應。

```
背景成因階層
└─ LLM agent 只有檔案級工具
   └─ 無全域結構索引 → 重複 grep/read → token 爆炸
      └─ 傳統解法：工具內嵌 LLM 做 NL→graph 轉譯
         └─ 副作用：多一個 API key、多一份成本
            └─ MCP 出現 → agent 本身可當轉譯器
               └─ 後端只需「結構分析 + 持久化圖譜」即可
```

---

## 3. 這個技術是如何解決該問題的？

### 核心機制：Pure C 靜態二進位 + tree-sitter + Hybrid LSP + SQLite 知識圖譜

```
┌─────────────────────────────────────────────────────┐
│  codebase-memory-mcp（單一靜態二進位，零依賴）        │
│                                                      │
│  [索引階段]  RAM-first pipeline                       │
│   ├─ File discovery（.gitignore / .cbmignore / 硬編碼）│
│   ├─ tree-sitter pass（158 語言 → 語法 AST）          │
│   ├─ Hybrid LSP pass（11 語言 → 型別解析 refine 邊）  │
│   │   ├─ import graph + per-file/cross-file def registry│
│   │   └─ 參數綁定 / 回傳型別推論 / 泛型替換 / 繼承分派 │
│   ├─ 多 pass：structure→defs→calls→HTTP links→config→tests│
│   └─ LZ4 壓縮 + in-memory SQLite + 結尾單次 dump       │
│                                                      │
│  [儲存]  ~/.cache/codebase-memory-mcp/ (SQLite, WAL)  │
│   └─ 可匯出 .codebase-memory/graph.db.zst（團隊共享）  │
│                                                      │
│  [查詢階段]  14 MCP tools over JSON-RPC 2.0 (stdio)   │
│   ├─ search_graph / trace_path / detect_changes       │
│   ├─ query_graph（openCypher read subset）            │
│   ├─ semantic_query（內建 Nomic embedding，無 API key）│
│   ├─ get_architecture / manage_adr / dead code ...    │
│   └─ sub-ms ~ 150ms                                   │
│                                                      │
│  [分發]  install 自動偵測 11 個 agent 並寫入 MCP 設定  │
└─────────────────────────────────────────────────────┘
         │ MCP stdio
         ▼
┌─────────────────────────┐
│  LLM coding agent        │  ← 查詢轉譯器（不內嵌 LLM）
│  (Claude/Codex/Gemini…)  │
└─────────────────────────┘
```

### 關鍵設計點

| 設計 | 做法 | 效果 |
|---|---|---|
| **不內嵌 LLM** | 後端只回傳結構化圖查詢結果，由 agent 端 LLM 把自然語言轉成工具呼叫 | 省一個 API key、省一份成本 |
| **Hybrid LSP（非真 LSP）** | 用 C 重新實作 tsserver/pyright/gopls/Roslyn/JDT/rust-analyzer 的型別解析演算法，嵌入二進位 | 取得 IDE「Go to Definition」等級的邊精確度，但不啟動 language server process |
| **158 tree-sitter grammar 直接編譯進二進位** | vendored，無 runtime 依賴 | 裝好即用、不會因 grammar 缺漏而壞 |
| **RAM-first 索引** | LZ4 HC 壓縮讀取 + in-memory SQLite + 結尾單次 dump | Linux kernel 28M LOC / 75K 檔在 3 分鐘完成（M3 Pro） |
| **團隊共享 artifact** | `.codebase-memory/graph.db.zst`：SQLite VACUUM INTO + zstd 壓縮（8–13:1），`merge=ours` 避免衝突 | 隊友 clone 後跳過全量 reindex，只跑增量 |
| **Cypher read subset** | 支援 MATCH/WHERE/WITH/RETURN/UNWIND/UNION 等，超出子集回傳明確 `unsupported` 錯誤 | 不回傳空結果誤導 agent |

### 虛擬碼示例：agent 端使用流程

```
# agent 收到使用者問題：「誰呼叫 ProcessOrder？」
→ agent 呼叫 tool: trace_path(function_name="ProcessOrder", direction="inbound")
← codebase-memory-mcp 回傳結構化 call chain
→ agent 用自然語言呈現給使用者
```

### arXiv 評估數據（31 個 real-world repo）
- answer quality：83%（vs file-exploration agent 92%）
- token：**10× 更少**
- tool calls：**2.1× 更少**
- graph-native 查詢（hub detection、caller ranking）：**19/31 語言追平或超越** explorer

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### DA 表（同級 / 替代方案）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|---|---|---|---|---|
| **tree-sitter 原生（直接呼叫）** | agent 直接呼叫 tree-sitter 取 AST，自行解析 | 已內建 tree-sitter；agent 需懂 AST | 只有語法層、無跨檔型別、無持久化 | 取得函式/類別定義與 call site，但 call 鏈跨檔失效 |
| **Sourcegraph / Cody** | 雲端 code graph + LLM 助手，索引所有 repo | 需連線 Sourcegraph 實例（雲或自架）；程式碼需上傳/索引 | 程式碼離開本機（雲版）；需帳號 | 跨數千 repo 的 code search + 智慧問答，企業級規模 |
| **Aider repo-map（CTags-based）** | 用 tree-sitter/CTags 產出壓縮的 repo 摘要 map，塞進 LLM context | 在 Aider 內使用 | map 是文字摘要、非可查詢圖譜；隨 repo 變大 context 壓力上升 | 給 LLM 一份低 token 的全域結構概覽，改善大範圍修改 |
| **graphify（README 提及）** | 產出 `graphify-out/` 目錄的知識圖譜產物 | 需安裝 graphify | 目錄式產物、無 MCP 整合、無兩 tier 匯出、無 `merge=ours` | 類似精神的「commit 進 repo 的圖譜 artifact」，但整合度低 |

### 切入點差異
- **codebase-memory-mcp**：把「結構分析後端」從 LLM 解耦，透過 MCP 成為 agent 的可查詢圖譜服務，主打 sub-ms 查詢 + 持久化 + 團隊共享。
- **tree-sitter 原生**：只給語法 AST，把結構理解責任完全留給 agent，無持久化。
- **Sourcegraph/Cody**：企業雲端規模 + 自帶 LLM 助手，反向選擇「工具內嵌 LLM」路線，犧牲隱私/成本換規模。
- **Aider repo-map**：不建可查詢圖譜，而是把圖譜「壓扁成文字摘要」餵進 context，省 token 但仍是 LLM 端理解。
- **graphify**：同為「commit 進 repo 的圖譜產物」精神，但缺 MCP 整合與兩 tier 匯出機制。

```
切入點光譜
結構分析外移 ◄──────────────────────────────► 結構分析內嵌
codebase-memory-mcp ─ tree-sitter原生 ─ Aider repo-map ─ Sourcegraph/Cody
(可查詢圖譜服務)      (純AST)            (文字摘要入context) (雲端圖譜+內嵌LLM)
```

---

## 5. User Q&A

### Q1：跟 codegraph / gitnexus 相比呢？是不是又是重造輪子？

**A**：

從「問題域」看，三者解的是**同一個問題**——讓 LLM coding agent 跳過 grep/read 循環，改查持久化知識圖譜，且都採 MCP server 形態。從這一層看，「重造輪子」的質疑成立。

從「實作手段」看，三者存在實質差異化。下表逐維度對照：

| 維度 | CodeGraph | GitNexus | codebase-memory-mcp |
|---|---|---|---|
| 實作語言 | TypeScript / Node（自捆綁 runtime） | Node + C++ 原生模組 | **Pure C，單一靜態二進位** |
| 安裝 | `npx` 一行 | 需編譯原生模組（或 skip grammar） | 下載 + `install`，零 runtime 依賴 |
| 解析引擎 | tree-sitter wasm | tree-sitter + 自研 | tree-sitter vendored 進二進位 |
| 語言覆蓋 | 20+ | 16（各有 parsing gap） | **158** |
| 型別解析 | 動態 dispatch synthesizer（heuristic 邊） | 自幹 scope-resolution | **Hybrid LSP**（C 重實作 tsserver/pyright/gopls/Roslyn/JDT/rust-analyzer 演算法） |
| 儲存 | SQLite WAL | **自研 LadybugDB** | SQLite WAL |
| 查詢語言 | FTS5 + 10 個專屬工具 | BM25+vector RRF + Cypher | **openCypher read subset** + 14 tools |
| 語意搜尋 | 無 | 內建 embedding + vector | 內建 Nomic embedding（11-signal 評分） |
| 框架路由 | 14 框架 | 16 tools | REST/gRPC/GraphQL/tRPC route 節點 |
| 跨邊界 | **iOS/ObjC/RN/Expo 深度橋接** | cross-repo contract bridge | cross-service HTTP linking + channel 偵測 |
| auto-sync | watcher + debounce + **staleness banner** | 無（需 hooks 或 `--force`） | background watcher + git polling |
| 授權 | MIT | **PolyForm Noncommercial** | MIT |
| 圖視覺化 | 無 | 無 | **3D UI（localhost:9749）** |
| 團隊共享索引 | 無 | 無 | **`.codebase-memory/graph.db.zst`（兩 tier 匯出 + `merge=ours`）** |
| 效能基準 | 7 repo：62% fewer tool calls | 無公開 benchmark | Linux kernel 28M LOC 3 min；arXiv 31 repo 評測 |

### 差異化增量 vs 重複造輪的逐項判定

| 項目 | codebase-memory-mcp 做了什麼 | CodeGraph / GitNexus 是否已有 | 判定 |
|---|---|---|---|
| Pure C 靜態二進位 | 零 runtime 依賴、Linux kernel 3 min | CodeGraph 用 Node 自捆綁也能零依賴；GitNexus 需編譯 | **增量**（效能 + 安裝體驗） |
| 158 語言覆蓋 | vendored 158 grammar | CodeGraph 20+、GitNexus 16 | **增量**（長尾語言團隊受惠） |
| Hybrid LSP 型別解析 | C 重實作 11 語言 LSP 演算法 | CodeGraph 無型別解析；GitNexus 自幹 scope-resolution（C5 判定效率不佳） | **增量**（精確度提升），但**風險**：重複 LSP 工作、維護 11 套解析器 |
| openCypher 查詢 | read subset + 明確 unsupported 錯誤 | GitNexus 也有 Cypher；CodeGraph 無 | **部分重複**（vs GitNexus） |
| 內建語意 embedding | Nomic 40K token 768d int8 | GitNexus 已有 vector search | **重複**（vs GitNexus） |
| 3D 圖視覺化 UI | localhost:9749 | 兩者皆無 | **增量**（非核心功能） |
| 團隊共享 artifact | `graph.db.zst` + 兩 tier + `merge=ours` | 兩者皆無 | **增量**（解前兩者未解的團隊協作問題） |
| iOS/RN/Expo 跨語言橋接 | 無 | **CodeGraph 獨有** | CodeGraph 仍領先此維度 |
| staleness banner | 無 | **CodeGraph 獨有** | CodeGraph 仍領先此維度 |
| 14 框架路由識別 | REST/gRPC/GraphQL route 節點 | CodeGraph 14 框架 | **部分重複** |

### Overengineering 2×2 判定（沿用 CodeGraph-C5 方法論）

| 判定面向 | codebase-memory-mcp |
|---|---|
| **對其自身問題** | **否**。Pure C + vendored grammar 的工程投入換來 158 語言 + Linux kernel 3 min + 零依賴安裝，與「讓 agent 跨任意語言查圖譜」的目標成比例。風險點：Hybrid LSP 維護 11 套 C 型別解析器，長期跟隨各 LSP 演進的負擔等同重做 LSP，屬於**潛在效率不佳**但非當前 overengineering |
| **導入 SaaS 團隊** | **否**。MIT 授權 + 單一靜態二進位 + `install` 自動設定 11 agent，導入成本趨近零。對已用 CodeGraph 的團隊，增量收益主要在 158 語言 / Hybrid LSP 精確度 / team artifact / 3D UI；對未用任何圖譜工具的團隊，直接採用無負擔 |

### 結論

| 層次 | 判定 | 依據 |
|---|---|---|
| 問題域 | **是重造輪子** | 同一問題、同一 MCP code intelligence server 形態、同一 tree-sitter + SQLite 技術骨架 |
| 實作域 | **非單純重造** | Pure C + 158 語言 + Hybrid LSP + team artifact + 3D UI 的組合，前兩者皆無 |
| 增量價值是否必要 | **視團隊而定** | 主流語言 SaaS 團隊：CodeGraph 已夠用，增量非必要；長尾語言 / 需型別精確度 / 需團隊共享索引的團隊：codebase-memory-mcp 的增量才變必要 |

**結論**：問題域是重造輪子，實作域有實質差異化；是否「又是」取決於看哪一層。對已部署 CodeGraph 的主流語言團隊，遷移的增量收益不足以構成必要；對未部署任何工具或需 158 語言 / Hybrid LSP / team artifact 的團隊，codebase-memory-mcp 不是重造輪子而是不同取舍點的選項。

---

## 附錄：關鍵效能數據（Apple M3 Pro）

| 操作 | 耗時 | 備註 |
|---|---|---|
| Linux kernel 全量索引 | 3 min | 28M LOC, 75K 檔 → 4.81M nodes, 7.72M edges |
| Linux kernel 快速索引 | 1m 12s | 1.88M nodes |
| Django 全量索引 | ~6s | 49K nodes, 196K edges |
| Cypher 查詢 | <1ms | 關係遍歷 |
| 名稱 regex 搜尋 | <10ms | SQL LIKE 預過濾 |
| 死碼偵測 | ~150ms | 全圖掃描 + degree 過濾 |
| call path trace (depth=5) | <10ms | BFS |

Token 效率：5 個結構查詢 ~3,400 token vs file-by-file ~412,000 token = **99.2% 降低**。