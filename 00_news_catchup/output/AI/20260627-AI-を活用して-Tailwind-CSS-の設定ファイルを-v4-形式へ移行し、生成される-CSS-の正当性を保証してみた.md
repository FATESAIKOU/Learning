# 2. AI を活用して Tailwind CSS の設定ファイルを v4 形式へ移行し、生成される CSS の正当性を保証してみた

**Source**: https://dev.classmethod.jp/articles/tailwind-v4-config-to-theme-migration/
**Author**: るおん (クラスメソッド リテールアプリ共創部)
**Date**: 2026-06
**Category**: AI技術

## 1. 這個技術/政策解決什麼問題?

解決的是 **AI 輔助程式碼遷移的「正確性驗證」問題**。

具體場景：將 Tailwind CSS v3 的 `tailwind.config.js`（JS 設定）遷移到 v4 的 `@theme`（CSS-first 設定）。遷移工作本身交由 Claude Code（AI）執行，大幅降低工數，但引入一個新問題：

> AI 輸出的遷移結果，如何證明與遷移前完全等價？

核心痛點：

| 痛點 | 說明 |
|------|------|
| 大量 token 遷移 | 39 個 fontSize + 13 個顏色 + 陰影 + 字體，人工逐個比對不現實 |
| 複合值拆分 | v3 的 `fontSize: ["14px", { lineHeight, fontWeight }]` 在 v4 拆成 3 個 CSS 變數，映射錯誤不易發現 |
| 表面驗證不可靠 | 建置通過 ≠ 值正確；class 名稱生成 ≠ px/顏色/字重一致 |
| camelCase 相容性 | `bg-extremelyPale` 等 camelCase 色名在 v4 是否會遺漏或別名化 |

## 2. 這個問題為什麼會發生?(背景)

**Tailwind CSS v4 的架構變革**：

v3 到 v4 是一次根本性的設計哲學轉變：

```
v3: JS-first（tailwind.config.js 為設定中心）
    ├── theme.extend.fontSize / colors / boxShadow / fontFamily
    └── Tailwind 啟動時自動讀取 JS 設定檔

v4: CSS-first（@theme 為設定中心）
    ├── @theme { --text-* / --color-* / --shadow-* / --font-* }
    └── tailwind.config.js 不再自動讀取（需 @config 顯式指定）
```

v4 提供兩種遷移路徑：

| 方法 | 機制 | 優點 | 缺點 |
|------|------|------|------|
| `@config` 互換模式 | CSS 中 `@config "../tailwind.config.js"` 引用舊設定 | 零遷移成本，現有設定不動 | 非 v4 原生寫法，無法享受 CSS-first 優勢 |
| `@theme` CSS-first | 將 JS 設定改寫為 CSS `@theme { ... }` | 設定一元化、CSS 變數可直接引用、建置更輕 | 需手動遷移，複合值映射複雜 |

**AI 輔助遷移的矛盾**：

AI（Claude Code）能快速完成大量 token 的語法轉換，但：
- AI 對「fontSize 的 3 點 set 映射為 3 個 companion 變數」可能出錯
- 39 個 fontSize 中任一筆的 line-height 或 font-weight 映射錯誤，人工 code review 幾乎不可能發現
- 「建置通過」只證明語法正確，不證明語意等價

因此核心命題變成：**AI 加速了遷移，但驗證必須機械化**。

## 3. 這個技術/政策是如何解決該問題的?

**整體策略：遷移前後生成 CSS 的實值 diff**

```
移行前 (@config + tailwind.config.js)  ──build──▶  before.css
                                                    │
                                         實值比較（變数解決後）
                                                    │
移行後 (@theme)                        ──build──▶  after.css
```

**關鍵步驟**：

### Step 1: 全 token 探測檔案
建立一個包含所有自訂 class 的 dummy file（`text-9ptW3` ~ `text-34ptW6` 共 39 個、全色 `bg-*`、`shadow-medium`、`font-sans`/`font-body`），放在 `src/` 下讓 Tailwind 掃描生成對應 CSS。

### Step 2: 雙向建置
分別在 `@config` 模式和 `@theme` 模式下執行建置，產出 `before.css` 和 `after.css`。

### Step 3: 變數解析 + 實值比較
這是核心。`@theme` 模式生成的 CSS 使用 CSS 變數（如 `var(--text-14ptW3)`），而 `@config` 模式直接寫入實值（如 `14px`）。直接 diff 會因語法差異而誤判。

解決方案：**僅解析 theme 變數（`--text-*`/`--color-*`/`--shadow-*`/`--font-*`），保留 runtime 變數（`--tw-leading`/`--tw-font-weight`）**。

```
before(@config):  font-size: 14px; font-weight: var(--tw-font-weight,300); line-height: var(--tw-leading,19px)
after (@theme):   font-size: 14px; font-weight: var(--tw-font-weight,300); line-height: var(--tw-leading,19px)
                  ↑ 變数解決後完全一致
```

### Step 4: 自動化比較腳本
`compare.mjs` 腳本自動執行：
1. 從 CSS 提取所有 theme 變數定義（`:root` 區塊）
2. 對每個 class 的宣告，遞迴解析 `var()` 中的 theme 變數
3. 正規化後逐 class 比較

**結果**：全 56 class，實值差分 **0**。

### 遷移的具體映射規則

| v3 JS 設定 | v4 @theme |
|-----------|-----------|
| `fontSize["14ptW3"] = ["14px", { lineHeight: "19px", fontWeight: "300" }]` | `--text-14ptW3: 14px; --text-14ptW3--line-height: 19px; --text-14ptW3--font-weight: 300;` |
| `colors.primary.DEFAULT` | `--color-primary` |
| `colors.primary.touch` | `--color-primary-touch` |
| `colors.extremelyPale` (camelCase) | `--color-extremelyPale` (camelCase 保持) |
| `boxShadow.medium` | `--shadow-medium` |
| `fontFamily.sans` | `--font-sans` |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 機制 | 適用場景 | 與本方法的差異 |
|------|------|---------|-------------|
| **Visual Regression Testing** (Chromatic / Percy) | 截圖 pixel 比較 | UI 元件層級的回歸 | 需渲染環境，受 anti-aliasing / 字體渲染差異影響；本方法直接比較 CSS 實值，更精確 |
| **Snapshot Testing** (Jest) | 序列化 DOM/CSS 比對 | 元件單元測試 | 需維護 snapshot，且 snapshot 更新時無法區分「預期變更」vs「意外破壞」 |
| **Playwright visual comparison** | headless browser 截圖比對 | E2E 層級 | 設定成本高，執行慢；本方法僅比較 CSS 字串，秒級完成 |
| **手動 code review** | 人眼逐行比對 | 小規模變更 | 39+ token 不現實，且人眼對 `19px` vs `18px` 的差異不敏感 |
| **Storybook + Chromatic** | 元件隔離 + 自動截圖 | 設計系統維護 | 需完整 Storybook 環境；本方法只需 Tailwind CLI 建置 |

**對用戶（學習中: Rust/MCP/Spring+AI/K8s CRD、探索中: Cursor+Claude）的啟示**：

- **AI 驅動開發的核心紀律**：AI 加速產出，但驗證必須機械化。這與用戶正在探索的 Cursor+Claude 開發模式直接相關——AI 寫 code 越快，越需要自動化測試作為安全網
- **diff-based 驗證模式**可推廣到其他遷移場景：設定檔遷移、API 版本升級、資料庫 schema 遷移，核心思路都是「遷移前後輸出 diff = 0」
- **CSS 變數解析策略**（只解析 theme 變數、保留 runtime 變數）展示了分層比較的思維，可應用於 K8s CRD 版本遷移時的 spec diff
- 作為即將轉管理者的角色，這類 **「AI 輔助 + 機械驗證」** 的工作流設計，是提升團隊開發品質與速度的關鍵槓桿
