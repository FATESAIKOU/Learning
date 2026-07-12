# 04. 攻撃者はブラウザを開いて最初の5分で何を見るのか〜バグバウンティで認可不備（P1/P2）を報告してきた視点で書く、フロントエンドの実装防御ガイド〜

**Source**: https://qiita.com/sei_official/items/3ce11ea5faed795d47fc
**Author**: SEI (@sei_official)
**Date**: 2026-07-10
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

前端開發者常將「隱藏 UI 元素」誤認為安全防禦，但攻擊者透過 Chrome DevTools 的 Network/Application/Sources 面板，可在 5 分鐘內繞過所有前端層級的「隱藏式防禦」。本文以 bug bounty 實戰視角，系統化整理 React/Next.js (App Router) 前端應用中 9 個必須修補的安全漏洞類別，核心命題是：**「瀏覽器收到的所有資訊，攻擊者也 100% 收到」→ 防禦必須在伺服器端。**

## 2. 這個問題為什麼會發生?(背景)

### 前端安全認知落差

```
開發者心態：  「按鈕藏起來就安全了」「API URL 沒人知道」「minify 過的 JS 看不懂」
攻擊者現實：  DevTools → Network tab → 所有 API 呼叫一覽無遺
              Sources tab → Ctrl+Shift+F 搜尋 "admin/debug/internal"
              Application tab → Local Storage / Cookie 中的 token
              .map 檔案 → 原始碼結構完全還原
```

### 最常見的漏洞類型

| 漏洞 | OWASP 分類 | 嚴重性 | 發生頻率 |
|------|-----------|--------|---------|
| BOLA (Broken Object Level Authorization) | API Security Top 10 #1 | P1/P2 | 極高 |
| 前端 role 判定作為唯一授權 | 授權繞過 | P1 | 高 |
| Source Map 在 production 暴露 | 資訊洩漏 | P2 | 中 |
| JWT 放在 Local Storage | XSS 後 token 竊取 | P1 | 高 |
| middleware-only 授權 | 授權繞過 | P1 | 中（CVE-2025-29927 為例） |

### 根本原因

前端框架（React/Next.js）的開發體驗讓開發者容易混淆「UX 控制」與「安全控制」。`{user.role === "admin" && <AdminPanel />}` 是 UX 邏輯，不是安全邏輯——攻擊者可以直接呼叫 API。

## 3. 這個技術/政策是如何解決該問題的?

### 9 步驟防禦體系

```
Step 1: 原則確立
  「瀏覽器收到的 = 全世界公開」→ 秘匿不是防禦

Step 2: API 授權（伺服器端）
  每個 endpoint 必須驗證：認證(401) + 授權(403)
  前端是否呼叫與安全無關（攻擊者直接 curl）

Step 3: Bundle 資訊洩漏
  minify 不是安全措施
  next.config.js: removeConsole (production), 移除 debug code

Step 4: Source Map 防護
  productionBrowserSourceMaps: false
  實際到 production URL 確認 .map 回 404

Step 5: BOLA 防禦（核心）
  ❌ if (user) return data  // 只檢查「存在」
  ✅ if (!data || data.ownerId !== session.userId) return 404
  GraphQL: resolver 層級逐個檢查
  UUID 不是防禦，只是 enumeration 緩和

Step 6: 前端 role 判定 = UX only
  {user.role === "admin" && <Button />}  // UX，非安全
  API 端必須重複相同授權檢查
  middleware/proxy 不能作為唯一授權點（CVE-2025-29927）

Step 7: Token 儲存
  JWT → HttpOnly Cookie (HttpOnly; Secure; SameSite=Lax)
  Cookie 認證後需追加 CSRF token（多層防禦）

Step 8: XSS 最終防線 — CSP nonce
  Next.js 需 nonce 方式（script-src 'self' 會破壞 hydration）
  middleware 生成 nonce → CSP header + x-nonce header
  dangerouslySetInnerHTML → DOMPurify sanitize

Step 9: robots.txt 不是防禦
  Disallow: /admin → 反而告訴攻擊者去哪裡找
  真正的防禦在 Step 2/5 的伺服器端授權
```

### 關鍵程式碼模式

**BOLA 防禦（REST）**：
```typescript
// ✅ 正確：檢查所有權
const user = await db.user.findUnique({ where: { id: params.id } });
if (!user || user.id !== session.userId) {
  return NextResponse.json({ error: "Not found" }, { status: 404 });
}
```

**BOLA 防禦（GraphQL）**：
```typescript
const resolvers = {
  Query: {
    order: async (_, { id }, { user }) => {
      const order = await db.order.findUnique({ where: { id } });
      if (!order || order.userId !== user.id) {
        throw new GraphQLError("Not found", { extensions: { code: "NOT_FOUND" } });
      }
      return order;
    },
  },
};
```

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 取捨 |
|------|---------|------|
| **Server Components (Next.js 13+)** | 資料直接在 server 端 fetch，不暴露 API endpoint | 減少攻擊面，但不能完全取代 API（client-side mutation 仍需 API） |
| **tRPC** | TypeScript full-stack | 型別安全，但 endpoint 仍可被直接呼叫，授權仍需手寫 |
| **GraphQL Shield / Hasura permissions** | GraphQL API | 宣告式授權規則，減少手寫檢查，但學習曲線高 |
| **API Gateway 層授權（Kong/Traefik）** | 微服務架構 | 集中管理，但無法處理 object-level 授權（BOLA 仍需應用層） |
| **ZAP/Burp Suite 自動掃描** | CI/CD 整合 | 可自動發現部分漏洞，但 BOLA 等邏輯漏洞需人工判斷 |

**思考方式**：本文的核心方法論是「攻擊者視角驅動的防禦設計」——不是從「我該加什麼防護」出發，而是從「攻擊者 5 分鐘內會看什麼」反推。這與傳統的 checklist-based security（XSS 打勾、CSP 打勾）形成互補：checklist 告訴你「做什麼」，攻擊者視角告訴你「為什麼做」和「做到什麼程度才算夠」。

**對用戶的意義**：用戶的技術棧包含 React（前端），且正在轉向管理角色。本文的 BOLA 防禦模式、middleware 不應作為唯一授權點、CSP nonce 實作等，對用戶 review 團隊的 frontend code 或制定安全編碼規範有直接參考價值。CVE-2025-29927（x-middleware-subrequest bypass）的案例也提醒：框架內建的安全機制不能盲目信任。
