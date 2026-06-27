# 7. Visual Studio Code 1.126が公開、コスト管理やセキュリティ強化など追加

**Source**: https://codezine.jp/news/detail/24668
**Author**: CodeZine編集部
**Date**: 2026-06-27
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

VS Code 1.126 解決三個開發者日常痛點：(1) AI 聊天成本不透明，開發者無法追蹤哪個 session 消耗最多 token/credit；(2) 語言模型設定分散，context size 與推理思考量分開調整，操作繁瑣；(3) 開啟未知專案時的安全性風險，預設行為可能讓惡意程式碼自動執行。

## 2. 這個問題為什麼會發生?(背景)

| 痛點 | 根因 |
|------|------|
| AI 成本不透明 | Copilot/Chat 的 token 計費模式下，開發者僅看到單次對話成本，無法追蹤 session 累積消耗。對於即將轉管理者的用戶，團隊 AI 工具成本控管是實際管理課題 |
| 模型設定分散 | 舊版將 context size 與 thinking/reasoning 分為兩個獨立設定項，開發者需在兩處調整才能最佳化模型行為 |
| 未知專案安全風險 | VS Code 的 workspace trust 機制在舊版中，開啟新資料夾時可能自動繼承父資料夾的信任狀態，存在安全漏洞 |
| 多任務 AI 對話管理 | 舊版 Copilot Chat 僅支援單一對話，切換任務時需手動整理上下文 |

推測: Microsoft 在 2026 年加速 VS Code 的 AI 整合（Copilot Cowork 一般提供、Agents 視窗預覽），1.126 是此策略的延續，重點從「功能新增」轉向「成本可控 + 安全強化 + 多工體驗」。

## 3. 這個技術/政策是如何解決該問題的?

**1.126 的關鍵變更**：

| 功能 | 變更內容 | 解決的痛點 |
|------|---------|-----------|
| AI 聊天成本管理 | 新增 session 總成本顯示（原僅顯示單次對話成本） | AI 成本不透明 |
| 模型設定整合 | context size 與 thinking/reasoning 合併為單一 picker，模型性能說明簡潔化 | 設定分散、操作繁瑣 |
| Agents 視窗（預覽） | 單一 Copilot session 內多 tab 並行對話，各自獨立保留上下文 | 多任務 AI 對話管理 |
| 限制模式強化 | 新資料夾預設以 Restricted Mode 開啟，移除「信任父資料夾」按鈕 | 未知專案安全風險 |
| 文件與部落格 | 部落格頁面改善、文件結構重新整理 | 資訊可尋性 |

**安全性改進的設計意圖**：

```
舊行為: 開啟新資料夾 → 可能繼承父資料夾信任 → 惡意程式碼自動執行
新行為: 開啟新資料夾 → 強制 Restricted Mode → 使用者明確審查後信任
```

Restricted Mode 下，VS Code 停用：
- 工作區設定（settings.json）的自動載入
- 擴充套件的自動啟用
- 建置 task 與 debug configuration 的自動執行

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 領域 | VS Code 1.126 | 替代方案 | 差異 |
|------|-------------|---------|------|
| AI 成本管理 | Copilot Chat session 成本 | Cursor 的 usage dashboard, Claude Code 的 token 計數 | Cursor 提供更詳細的 model-by-model 成本；Claude Code 顯示每次對話的 token 消耗 |
| 多工 AI 對話 | Agents 視窗（多 tab） | Cursor 的 Composer, Zed 的 AI panel | Cursor Composer 支援多個獨立 session；Zed 的 AI 整合較輕量 |
| 安全性 | Restricted Mode 強化 | JetBrains IDEA 的 Trusted Projects, Cursor 的 workspace trust | JetBrains 的方案更早成熟，但 VS Code 的 Restricted Mode 更激進（預設拒絕） |
| 模型設定 | 整合 picker | Cursor 的 model selector, Continue.dev 的 config | Cursor 的 model selector 支援更多第三方模型；Continue.dev 為開源替代 |
| IDE 選擇 | VS Code | Cursor, Zed, JetBrains Fleet, Windsurf | Cursor 是 VS Code fork 專注 AI；Zed 是 Rust 實作的高效能編輯器；Fleet 是 JetBrains 的輕量 IDE |

**對用戶的啟示**：
- 用戶正在探索 Cursor+Claude AI 驅動開發。VS Code 1.126 的 Agents 視窗（多 tab 並行對話）與 Cursor 的 Composer 多 session 功能直接競爭。建議對比兩者在實際開發流程中的上下文管理效率。
- 成本管理功能對即將轉管理者的用戶尤為重要：團隊 AI 工具的成本可視化是控管 ROI 的基礎。VS Code 的 session 成本顯示可作為團隊 Copilot 使用量管理的參考指標。
- Restricted Mode 強化是安全性最佳實踐的案例：預設拒絕（deny-by-default）而非預設允許，可應用於團隊的 CI/CD pipeline 與依賴管理策略。
