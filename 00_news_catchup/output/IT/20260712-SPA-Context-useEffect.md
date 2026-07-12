# 05. SPAのContextとuseEffectについて理解を深める

**Source**: https://qiita.com/har1101/items/01d1a3816852a135d6d9
**Author**: har1101 (ふくち)
**Date**: 2026-07-11
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

SPA (Single Page Application) 中，開發者容易將 Context（瀏覽器記憶體中的 state）誤認為可靠的資料來源。本文以一個實際 bug 為切入點：**「一覽頁面 → 詳細頁面」正常，但「直接 URL / 新分頁 / 重新整理」顯示「找不到」**。根本原因是詳細頁面依賴 Context 中由一覽頁面預先載入的資料，而非自行從 API 取得。

核心命題：**Context 是暫時的快取，不是資料來源。每個頁面必須能獨立從 API 獲取所需資料。**

## 2. 這個問題為什麼會發生?(背景)

### SPA 的架構特性

```
MPA (Multi-Page Application):
  URL 變更 → 伺服器回傳完整 HTML → 頁面獨立、自包含

SPA (Single Page Application):
  初次載入 JS bundle → URL 變更 → JS 切換元件 → 不重新載入頁面
  Context 在記憶體中跨路由共享 → 但僅存在於當前 tab 的生命週期
```

### 問題的技術根因

```
正常流程（從一覽進入）：
  一覧ページ → API取得 → Contextに保存 → 詳細ページ → Contextから検索 → 表示 ○

異常流程（直接 URL）：
  詳細ページ直リンク → Context空 → 検索失敗 → 「見つかりません」 ×
```

Context 中的資料在以下場景不存在：
- 新分頁開啟（獨立 JS context）
- 瀏覽器重新整理（JS context 重置）
- 直接輸入 URL / 書籤 / 外部連結
- 前一頁面未完成資料載入就導航

### React 的 state 管理模型

```
React 元件樹
├── Context Provider（頂層）
│   ├── 一覧データ: [A, B, C]  ← 記憶體中，非持久化
│   ├── ログイン情報
│   └── 表示設定
├── 一覧ページ（寫入 Context）
└── 詳細ページ（讀取 Context）← 依賴上游寫入
```

## 3. 這個技術/政策是如何解決該問題的?

### 解決方案：兩層修正

**修正 1：新增單筆 API 呼叫**

```
修正前：
  詳細ページ → Context.find(id) → 找不到 → 即時顯示 Not Found

修正後：
  詳細ページ → Context.find(id) → 找不到 → fetchItem(id) → API 回應 → 顯示
```

- 不重新取得全量一覽（效能考量）
- 取得後 upsert 回 Context（後續頁面間導航可共享）

**修正 2：畫面狀態從 2 種擴展為 5 種**

| 狀態 | 含義 | 畫面顯示 |
|------|------|---------|
| loading | API 查詢中 | ローディング表示 |
| loaded | 成功取得資料 | 詳細畫面 |
| not-found | API 回傳無此資料 | 「見つかりません」 |
| forbidden | 資料存在但無權限 | 權限錯誤 |
| error | 網路/伺服器錯誤 | 取得失敗錯誤 |

### useEffect 的正確使用模式

```typescript
useEffect(() => {
  // 1. Guard: 已有資料或無 ID → 不發請求
  if (!itemId || item) return;

  // 2. Race condition 防護
  let canceled = false;

  // 3. 設定 loading 狀態
  setLoadState('loading');

  // 4. 非同步 API 呼叫
  fetchItem(itemId)
    .then((fetchedItem) => {
      if (canceled) return;  // 元件已 unmount，丟棄結果
      setLoadState(fetchedItem ? 'loaded' : 'not-found');
    })
    .catch((error) => {
      if (canceled) return;
      setLoadState('error');
    });

  // 5. Cleanup: 元件 unmount 或依賴變更時取消
  return () => { canceled = true; };
}, [fetchItem, item, itemId]);  // 依賴陣列
```

### useEffect 使用判斷表

| 處理 | useEffect | 正確放置位置 |
|------|-----------|-------------|
| props/state 計算顯示值 | **不要** | render 中直接計算 |
| 按鈕點擊儲存 | **不要** | event handler |
| API/ブラウザ API 同步 | **使用候補** | Effect 或 data fetching library |
| 跨畫面 server data 快取 | **生 Effect 不足** | Router / React Query / SWR |

### 關鍵設計原則

1. **Context 是暫時快取，不是 single source of truth**（真正的 truth 在後端資料庫）
2. **每個 route 必須能獨立啟動**（直接 URL / 新分頁 / reload 都是合法進入點）
3. **cleanup 函數防止 race condition**（舊 API 回應不覆蓋新頁面狀態）
4. **依賴陣列是宣告式契約**，不是「執行次數調整 knob」

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 取捨 |
|------|---------|------|
| **React Router loader (v6.4+)** | React SPA | 路由層級 data fetching，自動處理 loading/error state，不需手寫 useEffect |
| **Next.js App Router + Server Components** | Next.js | 資料在 server 端 fetch，props 直傳 client component，完全消除 client-side fetching |
| **TanStack Query (React Query)** | 任何 React 應用 | 自動 cache/invalidation/refetch/race condition 處理，取代手寫 useEffect |
| **SWR (stale-while-revalidate)** | Next.js 生態 | 輕量級，自動 revalidation，與 Next.js 深度整合 |
| **MPA + htmx** | 不需要 SPA 的場景 | 每個頁面自包含，無 Context 問題，但失去 SPA 的流暢導航 |
| **SSR (Next.js pages router getServerSideProps)** | 需要 SEO 的 SPA | 每次請求 server 端 fetch，props 注入，無 client-side loading state |

**思考方式**：本文反映一個常見的 SPA 學習曲線——初學者先學會 Context 做 state 共享，然後遇到「Context 不是 persistent storage」的教訓。React 官方文件將 useEffect 定位為「脫出手段」（escape hatch），暗示大部分 data fetching 應交由框架或專用 library 處理。用戶若在 AxrossRecipe 的 React 前端遇到類似問題，優先考慮 React Query 或路由層級 loader，而非手寫 useEffect。

**對用戶的意義**：用戶的技術棧包含 React，且正在轉向管理角色。本文的 5 種狀態分類（loading/loaded/not-found/forbidden/error）可作為團隊 code review 的 checklist。cleanup 函數的 race condition 防護模式在用戶 review 前端程式碼時是常見的潛在 bug 來源。
