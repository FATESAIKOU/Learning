# 02. GitHub CopilotでGPT-5.6 Sol, Terra, Lunaが利用可能に

**Source**: https://codezine.jp/news/detail/28923
**Author**: CodeZine編集部
**Date**: 2026-07-12
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

GitHub Copilot 整合 GPT-5.6 三模型解決的是 **開發者 AI 輔助工具的「一刀切」問題**：過去 Copilot 使用單一後端模型，所有程式碼補全、聊天、agent 任務共用同一推理能力。這導致：

| 場景 | 舊問題 | GPT-5.6 解法 |
|------|--------|-------------|
| 大規模重構 / 跨檔案修改 | 模型深度不足，需多次往返 | Sol：高度推理，適合長時間作業 |
| 日常 CRUD / 單行補全 | 模型過重，延遲高、成本高 | Luna：輕量快速，低延遲 |
| 一般開發任務 | 無中間選項 | Terra：平衡型，日常編碼最佳 |

開發者現在可以在 VS Code、JetBrains、Xcode 中依任務類型切換模型，實現 **成本-速度-品質的三角取捨**。

## 2. 這個問題為什麼會發生?(背景)

### 2.1 Copilot 的模型演進路徑

```
2021-2023: OpenAI Codex (單一模型)
    ↓
2024: GPT-4o / GPT-5 系列 (逐步升級，仍為單一選擇)
    ↓
2025-2026: 多模型支援 (Claude Fable 5 對應, GPT-5.6 三層)
```

GitHub Copilot 在 2026 年已支援多個外部模型（含 Anthropic Claude Fable 5），OpenAI 若只提供單一模型會在 Copilot 生態內失去競爭力。GPT-5.6 的三層結構是 OpenAI 在 Copilot 平台上的 **防禦性 + 進攻性布局**。

### 2.2 開發場景的異質性

現代軟體開發中，AI 輔助的任務類型極度分散：

- **程式碼生成**：從註解產生函數 → Luna 足夠
- **程式碼審查**：理解上下文、發現邏輯漏洞 → Terra 適合
- **架構重構**：跨 50+ 檔案的大型變更 → 需要 Sol
- **除錯**：從 stack trace 追溯到 root cause → 依複雜度選擇
- **測試生成**：理解業務邏輯後產生覆蓋率高的測試 → Terra/Sol

單一模型無法在所有場景同時做到最優。

## 3. 這個技術/政策是如何解決該問題的?

### 3.1 模型-方案對應矩陣

| Copilot 方案 | Sol | Terra | Luna |
|-------------|-----|-------|------|
| Pro | ✗ | ✓ | ✓ |
| Pro+ | ✓ | ✓ | ✓ |
| Max | ✓ | ✓ | ✓ |
| Business | ✓ (管理者開啟) | ✓ | ✓ |
| Enterprise | ✓ (管理者開啟) | ✓ | ✓ |

### 3.2 三模型技術定位

```
Sol ─── 高度な推論が必要な大規模コードベースや長時間の作業に適する
        適用: アーキテクチャ設計、大規模リファクタリング、複雑なバグ調査

Terra ─ 汎用性が高く、日常的なコーディングに最適なバランス型
        適用: コードレビュー、機能実装、テスト作成、ドキュメント生成

Luna ── 軽量・低コストで、小規模かつ高速なタスクに向く
        適用: コード補完、簡単な関数生成、ボイラープレート作成
```

### 3.3 多 IDE 支援

GPT-5.6 三模型在以下環境中均可選擇使用：
- **Visual Studio Code**（含 VS Code Insiders）
- **JetBrains** 全系列（IntelliJ IDEA, PyCharm, WebStorm 等）
- **Xcode**（Apple 開發生態）

這確保了無論團隊使用何種技術棧（Ruby on Rails / React / GCP），都能在熟悉的 IDE 中獲得對應的 AI 輔助。

### 3.4 企業管理控制

Business 與 Enterprise 方案中，管理者可從設定面板控制 GPT-5.6 各模型的啟用/禁用。這對 Softbank 這類大型組織的安全合規至關重要——可以逐步放開 Sol 給資深工程師，同時限制 Luna 給全員使用。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

### 4.1 Copilot 生態內競爭

| 模型 | 在 Copilot 中的定位 | 優勢 |
|------|-------------------|------|
| **GPT-5.6 Sol** | 深度推理、大型程式碼庫 | Coding Agent Index 80.0，多 agent 協調 |
| **Claude Fable 5** | 程式碼理解、大型修改 | SWE-Bench Pro 80.0%，長上下文 |
| **GPT-5.6 Terra** | 日常平衡型 | 成本為 Sol 一半，效能等同 GPT-5.5 |
| **GPT-5.6 Luna** | 快速補全 | 最低延遲，適合即時補全場景 |

### 4.2 其他 AI 編碼工具對照

| 工具 | 模型策略 | 與 Copilot+GPT-5.6 的差異 |
|------|---------|--------------------------|
| **Cursor** | 多模型選擇（GPT-5.6, Claude 等）+ agent 模式 | 更靈活的模型切換，但無企業管理控制層 |
| **Windsurf** | 自研模型 + 多模型 fallback | 整合度更高但模型選擇較少 |
| **Codeium** | 自研模型為主 | 成本低但尖端推理能力不如 Sol |
| **Amazon Q Developer** | 內部模型 + Bedrock 整合 | AWS 生態深度整合，但通用性較低 |

### 4.3 對用戶的實踐建議

對在 Softbank AxrossRecipe 的技術團隊（Ruby on Rails + React + GCP）而言：

1. **立即行動**：確認 Copilot Business/Enterprise 方案中 GPT-5.6 模型已由管理者開啟
2. **分級使用策略**：
   - 日常開發（Controller/Model/Component 編寫）→ **Terra**
   - 程式碼審查、測試編寫 → **Terra**
   - 架構決策、跨服務重構、GKE 配置優化 → **Sol**
   - 快速補全、boilerplate → **Luna**
3. **與 Cursor 互補**：Copilot 用於 IDE 內即時輔助，Cursor 用於 agent 模式的大型跨檔案修改
4. **成本追蹤**：作為即將轉管理職的技術主管，建立模型使用量的追蹤機制，量化 AI 輔助的 ROI

### 4.4 趨勢判斷

GPT-5.6 進入 Copilot 代表 AI 編碼工具從「模型之爭」進入「任務匹配之爭」。未來 6-12 個月，開發者不會問「哪個 AI 最強」，而是問「這個任務用哪個模型最適合」。這與用戶正在學習的 MCP（Model Context Protocol）方向一致——AI 工具的價值在於如何與開發工作流深度整合，而非單純的模型能力。

---

*字數: ~1,100*
