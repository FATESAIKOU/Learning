# 2. Python Morsels- Binary search in Python with bisect

**Source**: https://www.pythonmorsels.com/binary-search/
**Author**: Trey Hunner (Python Morsels)
**Date**: 2026-07
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Python `bisect` 模組解決的是「在已排序序列上進行查詢/插入」時的效能問題：

| 情境 | 朴素做法 | bisect 做法 |
|------|---------|------------|
| 檢查 10M 元素是否存在 | `in` 逼近 2M 次比較（O(n)） | 23 次比較（O(log n)） |
| 找最接近目標的值 | 全表 `min(key=...)` 掃描 | `closest()` 兩點夾擊 |
| 找區間內所有值 | 全表過濾 | `between()` 切片 |
| 插入並維持排序 | `append` + `sort()`（O(n log n)） | `insort`（搜尋 O(log n)，但插入仍 O(n)） |

關鍵洞見：bisect 不是取代 `set`/`dict` 的精確查詢，而是補足「模糊查詢」（最近值、前後鄰、區間）這塊 set/dict 無法勝任的場景。

## 2. 這個問題為什麼會發生?(背景)

1. **Python 預設資料結構的成本認知落差**：多數 Python 開發者熟知 `set`/`dict` 的 O(1) 查詢，但忽略「排序資料本身蘊含的結構資訊未被利用」
2. **教科書與實務的斷層**：CS 課堂教手刻 binary search，但 Python 已內建 `bisect`，開發者重複造輪子或退而用線性掃描
3. **大資料量場景**：時間序列、日誌、排程等本就按時間排序的資料，線性查詢在 10M+ 筆時成本明顯

推測背景：Python Morsels 作為進階 Python 教學平台，長期觀察到學員在「排序資料上做模糊查詢」時誤用 set 或全表 loop，故以此篇系統化補完 `bisect` 知識。

## 3. 這個技術/政策是如何解決該問題的?

`bisect` 模組提供 4 函式 + 2 alias，並支援 `key` 參數：

```
bisect 模組
├── bisect_left  / bisect_right   → 回傳可插入索引
├── insort_left  / insort_right   → 插入並維持排序
├── bisect (= bisect_right)       → alias
└── insort  (= insort_right)      → alias
```

**核心機制：插入點索引**
- `bisect_left`：回傳最左側可插入點（命中時指向第一個等於 target 的位置）
- `bisect_right`：回傳最右側可插入點之後（命中時指向最後一個等於 target 的位置 +1）
- 兩者差可用來切片出所有等於 target 的元素：`seq[bisect_left(seq,t):bisect_right(seq,t)]`

**食譜化包裝**：官方文件提供一系列高階 recipe，文章列出 7 類：

| Recipe | 用途 |
|--------|------|
| `has_match` | 精確存在檢查 |
| `count` | 計數等於 target 的筆數 |
| `index` / `rindex` | 首/末命中索引 |
| `find_lt/le/gt/ge` | 找前/後鄰 |
| `closest` | 最接近值 |
| `between*` | 區間切片 |

**`key` 參數**（Python 3.10+）：比照 `sorted`/`min`/`max`，可傳入正規化函式（如大小寫/標點忽略），讓 bisect 也能處理「排序規則非字面值」的資料。

**重要陷阱**：
- bisect **不檢查排序性**，未排序資料會回傳錯誤答案而非例外
- `insort` 搜尋 O(log n) 但 `list.insert` 仍 O(n)（需搬移後續元素），bisect「省搜尋不省插入」
- 只排序一次就要查詢時，先 sort 再 bisect 反而比線性 `min` 慢

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 與 bisect 對比 |
|------|---------|--------------|
| `set` / `dict` | 精確查詢、無序 | O(1) 但無模糊查詢能力 |
| `heapq` | 動態取極值 | 不維持全排序，僅保證頂端 |
| `sortedcontainers.SortedList` | 頻繁插入+查詢 | 插入 O(log n)（bisect+list 為 O(n)），第三方套件 |
| **Rust `std::collections::BTreeMap`**（使用者學習中） | 排序映射 | 內建平衡樹，插入查詢皆 O(log n)，與 bisect 的 list 限制形成對照 |
| **NumPy `searchsorted`** | 數值陣列大規模 | 向量化 binary search，適合資料科學場景 |
| **間隔樹/區間樹** | 區間重疊查詢 | 比 `between()` 更適合動態區間集合 |

**思考方式啟發**：
- 「利用資料已排序這個不變量」是演算法優化的常見切入點，與 K8s CRD 中「利用 controller 對資源狀態的單調性假設」概念同源
- 「Stdlib 先行」原則：Python 將 binary search 收進 stdlib 避免重造，對比 Rust 將 `BTreeMap` 收進 std，呈現不同語言對「排序資料查詢」的預設策略
- 對使用者即將轉管理者的意義：審 code review 時，可將「排序資料上的線性查詢」列為常見效能異味，並指向 `bisect` 作為標準替代

**行動建議**：在使用者既有 Rails + React 棧中，Ruby 有對應的 `Array#bsearch_index`；可對照 Python `bisect` 與 Ruby `bsearch` 兩者 API 設計差異，作為跨語言資料結構素養的練習。