# 01. Announcing Rust 1.97.0

**Source**: https://blog.rust-lang.org/2026/07/09/Rust-1.97.0/
**Author**: The Rust Release Team
**Date**: 2026-07-09
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Rust 1.97.0 解決三個長期存在的開發體驗與建置可靠性問題：

| 問題 | 舊狀況 | 新解法 |
|------|--------|--------|
| Symbol mangling 不一致 | Itanium ABI 為基礎的 mangling 無法保留 generic parameter 的具體值，部分場景需自訂 demangling | v0 mangling 預設啟用，完整保留 generic 資訊 |
| CI 中 warning 處理繁瑣 | 需透過 `RUSTFLAGS=-Dwarnings` 設定，會 invalidate build cache | Cargo 原生支援 `CARGO_BUILD_WARNINGS=allow/warn/deny`，不影響 cache |
| Linker 輸出被隱藏 | rustc 預設沉默 linker 的 stderr，掩蓋真實問題 | 預設顯示 linker 訊息為 warning lint |

## 2. 這個問題為什麼會發生?(背景)

**Symbol mangling v0**：Rust 自 1.59 起支援 v0 mangling scheme，但一直作為 opt-in。舊的 Itanium ABI 方案有兩個缺陷：(1) generic parameter 的具體值被 hash 取代，除錯時無法還原；(2) 部分編譯器內部使用不同 mangling，導致工具鏈需要同時支援兩套 demangling。自 2025 年 11 月起 nightly 已預設啟用 v0，1.97 正式推到 stable。

**Cargo warning 控制**：`RUSTFLAGS` 是編譯器層級的環境變數，改變它會使整個 build cache 失效。開發者在 refactor 後想暫時 silence warning 來專注 error 時，`RUSTFLAGS=-Awarnings` 會觸發全量重編譯。Cargo 層級的控制讓 warning level 與編譯 cache 解耦。

**Linker 輸出**：rustc 呼叫系統 linker（如 ld、lld），過去 linker 成功時 rustc 會隱藏其 stderr。這導致 linker 的 deprecation warning、最佳化設定忽略等訊息被吞掉，開發者無法察覺潛在問題。nightly 上已有多個 bug 因為不再隱藏 linker 輸出而被修復。

## 3. 這個技術/政策是如何解決該問題的?

### Symbol mangling v0

```
舊 (Itanium):  _RNvC...hash... → generic 資訊丟失
新 (v0):      _R...保留完整 module path + generic 值
```

- 預設啟用 `-Csymbol-mangling-version=v0`
- 舊方案僅在 nightly 可啟用，計劃完全移除
- 影響：更好的 debug 體驗、更精確的 profiling 符號解析

### Cargo warning 控制

```toml
# Cargo.toml
[lints.rust]
# 可設 allow / warn / deny
```

```bash
# 臨時 silence（不 invalidate cache）
CARGO_BUILD_WARNINGS=allow cargo check

# CI 中 deny + 收集全部錯誤
CARGO_BUILD_WARNINGS=deny cargo build --keep-going
```

關鍵設計：warning level 是 Cargo 的配置，不影響 rustc 的編譯 cache key。

### Linker 輸出

- 預設 emit `linker_messages` warning lint
- 已知的 false positive 由 rustc 過濾
- 可透過 `Cargo.toml` 的 `[lints.rust]` 設為 `allow` 來 silence
- 注意：`linker_messages` 不受 `warnings` lint group 控制（刻意設計，因為 linker 輸出具平台差異）

### 其他 stabilized API

- `Default for RepeatN`、`Copy for ffi::FromBytesUntilNulError`
- `Send for std::fs::File` on UEFI
- 整數 bit 操作系列：`isolate_highest_one`、`isolate_lowest_one`、`highest_one`、`lowest_one`、`bit_width`（含 `NonZero` 版本）
- `char::is_control` 進入 const context

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 語言/工具 | Symbol/名稱處理 | Warning 控制 | Linker 輸出 |
|-----------|----------------|-------------|-------------|
| C++ (Itanium ABI) | 同樣使用 Itanium ABI，但 template 展開後名稱極長，無 v0 等效方案 | `-Werror` / `#pragma GCC diagnostic` | 直接顯示 linker 輸出 |
| Go | 無 name mangling（無 generic 時），go 1.18+ generic 使用內部 scheme | `-gcflags` | 直接顯示 |
| Zig | 自訂 mangling，編譯器完全控制 | `-Werror` style flags | 直接顯示 |
| Swift | 自訂 mangling scheme，保留 generic 資訊 | `-warn-` flags | 直接顯示 |

**思考方式**：Rust 的做法反映「開發者體驗優先於向後相容」的哲學。v0 mangling 從 opt-in → nightly default → stable default 的漸進式遷移路徑是 Rust 版本管理的典型模式。Cargo warning 控制則展示「工具層與編譯器層分離關注點」的設計——Cargo 管 policy，rustc 管機制。

**對用戶的意義**：用戶正在學習 Rust，1.97 的 v0 mangling 對 debug Rust 程式（尤其是 generic-heavy 的程式碼）有直接幫助。`CARGO_BUILD_WARNINGS` 在 CI pipeline 設定中可簡化 warning-as-error 的配置。
