# 02. 6× faster binary search: from compiled code to mechanical sympathy

**Source**: https://pythonspeed.com/articles/branchless-binary-search/
**Author**: Itamar Turner-Trauring
**Date**: 2026-07-11
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Python 數值計算中，即使已使用編譯語言（Cython/Rust）撰寫擴展，binary search 仍可能因 CPU 層級的 branch misprediction 而顯著變慢。本文以 scikit-learn 的 gradient histogram boosting 中的 bucketize 操作為例，展示如何透過「mechanical sympathy」（理解 CPU 運作方式）將 binary search 加速 6 倍。

核心問題：**標準 binary search 的 branch 對 CPU branch predictor 而言完全不可預測**（輸入值均勻分佈時，每次 if/else 都是 50% 機率），導致 16.6% 的 branch misprediction rate。

## 2. 這個問題為什麼會發生?(背景)

現代 CPU 在單核心內透過 **instruction-level parallelism (ILP)** 同時執行多條獨立指令。但遇到 branch（if/while/for）時，CPU 必須猜測走哪條路來繼續 parallel execution。猜錯（branch misprediction）時，CPU 需丟棄已執行的錯誤路徑結果，重新執行正確路徑——這造成顯著的效能損失。

binary search 的結構性問題：
- 每次迭代的 `if value < boundaries[mid]` 結果完全取決於輸入資料
- 輸入值均勻分佈時，left/right 選擇是隨機的 → branch predictor 無法學習模式
- while loop 的迭代次數也因值而異 → 額外的不可預測 branch

硬體計數器測量結果（100 萬筆資料，255 個 bucket）：
- 原始版本：27 branches/value，16.6% misprediction，IPC 僅 1.1
- 耗時 45,870 µs

## 3. 這個技術/政策是如何解決該問題的?

作者透過四階段漸進式最佳化，每階段解決一類效能瓶頸：

### 階段 1：Branchless binary search（3.5× 加速）

```
核心技巧：
1. 固定迭代次數 = ceil(log2(boundaries.len()))，消除 while loop branch
2. 使用 std::hint::select_unpredictable() 取代 if/else
   → 編譯器生成 cmov 等無 branch 的條件選擇指令
```

結果：branch 從 27/value 降至 19/value，misprediction 0%，IPC 從 1.1 升至 4.0，耗時 13,198 µs。

### 階段 2：消除 bounds check + 預計算 halves（1.3× 再加速）

```
1. 使用 unsafe get_unchecked() 跳過 Rust 的陣列邊界檢查
   → 消除每次陣列存取的 bounds check branch
2. 預計算 halves 陣列（每次 binary search 的 half 值相同）
   → 減少重複計算
```

結果：branch 降至 8/value，指令數從 188M 降至 121M，耗時 10,043 µs。

### 階段 3：SIMD auto-vectorization（1.4× 再加速）

```
1. RUSTFLAGS="-C target-cpu=x86-64-v3" 啟用現代 CPU 指令集
2. 重構迴圈結構：halves 迭代在外層，values 在內層
   → 編譯器可將內層迴圈 auto-vectorize 為 SIMD 指令
3. 以 chunk size=16 分批處理，改善 memory cache locality
```

結果：指令數降至 99.9M，IPC 回升至 3.9，耗時 7,106 µs（總加速 6.5×）。

### 效能演進總表

| 版本 | 耗時 (µs) | 指令數 | Branches | Misprediction | IPC |
|------|----------|--------|----------|---------------|-----|
| classic | 45,981 | 184.9M | 27.0M | 16.6% | 1.1 |
| branchless | 13,269 | 188.1M | 19.0M | 0.0% | 4.0 |
| branchless2 | 10,037 | 121.1M | 8.0M | 0.0% | 3.4 |
| branchless3 (SIMD) | 7,106 | 99.9M | 6.8M | 0.0% | 3.9 |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 取捨 |
|------|---------|------|
| **Parallelism（多核）** | 資料量大、可分割 | 作者明確指出可疊加使用，非替代方案 |
| **Eytzinger layout（cache-friendly 資料排布）** | binary search on sorted array | 改變記憶體排布以改善 cache locality，與 branchless 互補 |
| **SIMD intrinsics 手寫** | 需要極致效能 | 比 auto-vectorization 更可控，但可攜性差、維護成本高 |
| **Lookup table / perfect hashing** | bucket 數量固定且小 | 直接 O(1) 查表，但記憶體開銷大 |
| **JIT compilation (Numba/PyPy)** | Python 生態系內 | Numba 的 `@jit(nopython=True)` 也可做 branchless 最佳化，但控制力不如 Rust |

**思考方式**：本文的核心方法論是「mechanical sympathy」——理解 CPU 的 branch predictor、instruction-level parallelism、SIMD、memory cache 等硬體特性，並讓程式碼配合而非對抗這些特性。這與傳統的「選好演算法 + 用編譯語言」的效能優化思路形成互補層次：

```
第 1 層：演算法選擇（複雜度）
第 2 層：編譯語言（消除直譯器 overhead）
第 3 層：Mechanical sympathy（本文重點）
第 4 層：Parallelism（多核）
```

**對用戶的意義**：用戶正在學習 Rust，本文以 Rust 實作展示效能最佳化，且使用 PyO3 與 Python/NumPy 整合——與用戶的 Python + Rust 學習路徑直接相關。文中使用的 `select_unpredictable`、`get_unchecked`、SIMD auto-vectorization 等技巧，在用戶未來用 Rust 加速 Ruby/Rails 後端或資料處理 pipeline 時可直接應用。
