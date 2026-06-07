# 05. Cloudflare supports Vite's mission (原文)

**Source**: https://vite.dev/blog/cloudflare-supports-vite
**Author**: Vite 官方公告(Evan You 創辦人於 VoidZero 公告,Cloudflare 部落格同步)
**Date**: 2026/06/04
**Category**: AI技術

## 1. 這個技術解決什麼問題?

本公告本身**不是技術釋出**,而是一個**組織/治理事件**:
- VoidZero(由 Evan You 創立,負責 Vite / Vitest / Rolldown / Oxc / Vite+ 等前端工具鏈的公司)於 2026/06/04 正式**加入 Cloudflare**
- Cloudflare 同時宣布設立 **$1M Vite Ecosystem Open Source Fund**

被解決的問題有三層:
1. **Vite 生態的資金與商業永續性** — 開源前端工具鏈僅靠 GitHub Sponsors / Open Collective 難以維持核心維護者全職投入
2. **避免「企業收購導致 OSS 走向封閉」的疑慮** — 開發者社群對 Vite 被收編後是否仍中立(vendor-agnostic)有疑慮
3. **Cloudflare 對前端 build tooling 的策略卡位** — 取得 Vite/Rolldown/Oxc 對其 Workers / Pages 生態有直接效益

## 2. 這個問題為什麼會發生?(背景)

| 因素 | 說明 |
|---|---|
| Vite 已是 web 基礎建設 | Vite 是 Vue / React / Svelte / Solid 等主流框架的預設 dev server / build tool,2024-2026 進入「critical OSS」階段 |
| VoidZero 商業模式未公開細節 | 從 Vite+ 等付費產品的市場反饋推測,單靠 enterprise 版難以同時養 5 條產品線 |
| Cloudflare Workers 需要更好 build | Workers 的 bundling 過去依賴 esbuild / webpack,Vite + Rolldown 直接整合可省一層 |
| Web platform 演進加速 | 提案如 Import Maps / Wasm Component Model / TC39 持續推進,需要有人「在標準機構有耳朵」的工具團隊 |

> 通用背景:近年來出現「OSS 工具被 hyperscaler 收購但仍保持中立」的成功案例(如 GitHub 收購 npm、Microsoft 持有 VS Code),為本次收購提供治理範本。

## 3. 這個技術是如何解決該問題的?

### 3.1 治理保證(明文條款)

```text
VoidZero 治理 →  Cloudflare 員工(原 VoidZero 員工帶過去)
                 ↓
       Vite Team(由多家公司員工 + 獨立成員組成)
                 ↓
   Open Collective 資金(由 Vite Team 管理,非 Cloudflare 直接控)
                 ↓
   $1M Ecosystem Fund(由 Cloudflare 出資,但用於支援 plugin / 框架)
```

關鍵條款:

| 條款 | 內容 |
|---|---|
| License | 維持 **MIT**(不變) |
| Vendor-agnostic | Vite-built apps 仍可部署到任何平台 |
| 治理結構 | Vite Team 包含 Cloudflare 員工 + 其他組織員工 + 獨立成員,集體決策 |
| Open Collective | 仍由 Vite Team 獨立管理,用於發放核心成員 stipend |
| 適用範圍 | Vite / Vitest / Rolldown / Oxc / Vite+ **全部**適用同樣條款 |

### 3.2 $1M Fund 的具體用途

- 補助熱門 plugin / tooling 的維護者
- 提供獨立 Vite Team 成員的 stipend
- 與 Rolldown / Oxc / Vite+ 團隊協作
- 與框架 / 部署平台 / plugin maintainers 協作
- 與標準機構接軌(如 W3C / TC39)
- **加速安全漏洞 audit 與發布**(這一項對企業用戶尤其重要)

### 3.3 技術路線圖(治理不變前提下的承諾)

- **Full Bundle Mode**(讓 Vite 在 production 也完全用 Rolldown 取代 Rollup)
- **Ecosystem Sync Calls**(Vite 與框架 / 部署平台 / plugin 的定期會議)
- **Environment API** 在 Vite 9 穩定
- **更快採用 web platform 新特性**

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 技術 / 模式 | 治理解法 | 使用前提 | 副作用 | 預期效果 |
|---|---|---|---|---|
| **OpenJS Foundation / CNCF 託管** | 把專案捐給中立基金會,由董事會管理 | 願意放棄商標 / 決策權 | 決策變慢,需跨公司協調 | 長期中立性最高,例如 Node.js / Kubernetes |
| **GitHub Sponsors + 個人 maintainer** | 維持個人 / 小團隊主導 | 核心 maintainer 仍在 | Bus factor 高,一旦離開風險大 | 早期 OSS 典型模式 |
| **Tidelift / 商業訂閱制** | 由商業公司代理 funding | 願意付費的企業用戶足夠 | 中小型開源者被排除 | 企業導向 OSS(如 Ionic) |
| **Bun 模式:商業公司 + 開源旗艦** | 母公司主導開發,閉源 runtime + 開源 build tool 混合 | 母公司有強商業模式 | 開發者對「是否被收購」敏感 | 整合度高,中立性較低 |

> **切入點差異**:
> - Cloudflare × VoidZero 採「**收購但保留治理多樣性**」:Cloudflare 取得人才與 IP,但 Vite Team 仍由跨公司成員組成
> - OpenJS / CNCF 採「**完全中立基金會**」:最適合基礎協議級 OSS,但協作成本高
> - Bun 採「**單一公司主導**」:決策快,但開發者社群信任度較低
> - Tidelift 採「**訂閱資助**」:適合企業依賴的關鍵函式庫,小型開源者未必受惠

---

**對用戶的意義**:
- 使用者層面:Vite / Rolldown / Oxc 仍是 MIT,且 vendor-agnostic,現有 React / Vue 專案無需變動
- 即將轉管理者:這是「OSS 治理 + 企業投資」的良好範本,可作為公司內部開源資產治理的參考(如制定 OSS contribution policy)
- 學習 K8s CRD 脈絡:Vite Team 的「跨組織成員 + 獨立 maintainer」治理結構與 CNCF 類似,概念可互通
