# CloakBrowser 技術分析報告

> 分析日期：2026-05-31
> 技術全名：CloakBrowser（Stealth Chromium with C++ source-level fingerprint patches）
> 版本：v0.3.31（基於 Chromium 146.0.7680.177.5）

---

## 1. 這個技術解決什麼問題？

**被解決的具體問題：**

基於 Playwright / Puppeteer / Selenium 的自動化瀏覽器工具，在訪問具有反機器人（anti-bot）防護的網站時，會被偵測並阻擋。偵測依據是瀏覽器暴露的「指紋資訊」（fingerprint）中包含自動化工具的標記——例如 `navigator.webdriver === true`、Canvas/WebGL 渲染結果與真實瀏覽器不一致、WebRTC IP 洩漏、CDP（Chrome DevTools Protocol）偵測等。˚

CloakBrowser 透過在 Chromium 的 **C++ 原始碼層級**修改指紋相關程式碼並重新編譯為二進位檔，使得自動化瀏覽器在 30+ 種反機器人檢測服務（Cloudflare Turnstile、reCAPTCHA v3、FingerprintJS、BrowserScan 等）面前表現為「正常瀏覽器」，不會觸發驗證碼或遭到封鎖。

**文章中未明確說明的部分（推測注記）：**

- 作者未詳細說明 58 個 C++ patch 分別修改了 Chromium 原始碼中的哪些具體檔案與函數。
- 未提供 patch 的原始碼或 diff 內容（二進位檔授權禁止逆向工程）。
- 未說明與 ungoogled-chromium 基底之間的具體差異範圍。

---

## 2. 這個問題為什麼會發生？（背景）

### 文章中明確提到的背景因素

| 因素 | 說明 |
|------|------|
| **JS injection 方案容易被偵測** | 現有方案（playwright-stealth、puppeteer-extra）透過 JavaScript 注入來覆蓋瀏覽器屬性，但反機器人系統可以偵測到這些注入行為本身。 |
| **Config-level patches 隨 Chrome 更新而失效** | undetected-chromedriver 等工具透過修改 Chrome 啟動參數或修補 chromedriver 二進位檔來隱藏自動化標記，但每次 Chrome 版本更新都需要重新適配，且容易出現相容性問題。 |
| **CDP 協定本身留下自動化訊號** | Puppeteer 透過 CDP 與瀏覽器通訊，reCAPTCHA Enterprise 可偵測 CDP 協定特有的行為模式，導致間歇性 403 錯誤。 |
| **Headless 模式有獨特的指紋** | 標準 Playwright/Puppeteer 在 headless 模式下，User-Agent 包含 `HeadlessChrome`、`navigator.plugins.length === 0`、`window.chrome === undefined` 等特徵，很容易被辨識。 |

### 通用技術背景（從外部資料補充）

```
┌─────────────────────────────────────────────────────────────────┐
│                    瀏覽器指紋（Browser Fingerprint）              │
│                                                                 │
│  網站可透過 JavaScript API 收集以下資訊來唯一識別瀏覽器：          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Canvas 指紋   │  │ WebGL 指紋   │  │ AudioContext 指紋     │  │
│  │ (5.7 bits    │  │ (GPU vendor, │  │ (AudioBuffer 雜訊    │  │
│  │  entropy)    │  │  renderer)   │  │  差異)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 字體列表      │  │ 硬體資訊      │  │ 自動化標記            │  │
│  │ (系統安裝     │  │ (CPU核心數,   │  │ (navigator.         │  │
│  │  字體差異)    │  │  裝置記憶體)  │  │  webdriver, CDP)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 螢幕屬性      │  │ TLS 指紋      │  │ WebRTC IP 洩漏       │  │
│  │ (解析度,     │  │ (JA3/JA4     │  │ (真實 IP 可透過      │  │
│  │  colorDepth) │  │  handshake)  │  │  ICE candidate 取得) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  據 EFF Panopticlick 研究：83.6% 的瀏覽器指紋是唯一的             │
│  加入 Canvas 指紋後可增加 5.7 bits 熵                            │
└─────────────────────────────────────────────────────────────────┘
```

**核心矛盾：** 自動化工具需要控制瀏覽器，而控制行為會留下可偵測的痕跡。傳統方案試圖在「應用層」抹除這些痕跡，但反機器人系統也在應用層執行偵測腳本，形成軍備競賽。應用層的修補（JS injection / config flags）始終可以被偵測腳本觀察到。

---

## 3. 這個技術是如何解決該問題的？

### 核心機制：C++ 原始碼層級修補 + 重新編譯

CloakBrowser 不注入 JavaScript、不修改啟動參數，而是**直接修改 Chromium 的 C++ 原始碼**，然後重新編譯為自訂的 Chromium 二進位檔。由於修補發生在瀏覽器引擎內部，執行在網頁中的反機器人偵測腳本無法區分修補後的輸出與真實瀏覽器的輸出。

### 修補架構（58 個 source-level patches 的分類）

```
CloakBrowser 二進位檔（基於 Chromium 146 + ungoogled-chromium）
│
├── 圖形渲染層修補
│   ├── Canvas 2D 渲染 → 輸出與真實 GPU 一致的雜訊
│   ├── WebGL 渲染 → 偽造 UNMASKED_VENDOR_WEBGL / UNMASKED_RENDERER_WEBGL
│   ├── WebGPU adapter → 偽造 adapter features、limits、device ID
│   └── AudioContext → 偽造 AudioBuffer 浮點數雜訊
│
├── 硬體資訊層修補
│   ├── navigator.hardwareConcurrency → 偽造 CPU 核心數
│   ├── navigator.deviceMemory → 偽造裝置記憶體
│   ├── GPU vendor/renderer → 從 GPU 模型資料庫隨機選取
│   └── screen.width/height/colorDepth → 偽造螢幕參數
│
├── 自動化標記層修補
│   ├── navigator.webdriver → 強制回傳 false（patch 009）
│   ├── CDP 偵測防護 → 移除 Runtime.runIfWaitingForDebugger 等特徵
│   ├── CDP input 事件 → 移除自動化輸入事件中的合成標記
│   └── window.chrome → 確保存在（真實 Chrome 有此物件）
│
├── 網路層修補
│   ├── WebRTC ICE candidate → 偽造 IP 位址（--fingerprint-webrtc-ip）
│   ├── Proxy 訊號移除 → DNS/connect/SSL timing 歸零，Proxy-Connection header 移除
│   ├── TLS fingerprint → JA3/JA4/Akamai fingerprint 與真實 Chrome 一致
│   └── SOCKS5 proxy → 原生支援，QUIC/HTTP3 透過 UDP ASSOCIATE 隧道
│
├── 儲存層修補
│   ├── Storage quota normalization → 修復 storage.estimate() 回傳值
│   ├── StorageBuckets API → 關閉 incognito 偵測向量
│   └── outerHeight calculation → 修復非 incognito context 計算
│
└── 平台層修補
    ├── navigator.platform → 偽造作業系統
    ├── User-Agent → 移除 HeadlessChrome 字串
    ├── fonts → 支援外部字體目錄（--fingerprint-fonts-dir）
    └── timezone/locale → 使用原生 C++ patch 而非 CDP emulation
```

### 使用流程（虛擬碼層級）

```python
# Step 1: 安裝 wrapper
# pip install cloakbrowser

# Step 2: 首次啟動時自動下載修補後的 Chromium 二進位檔（~200MB）
# 二進位檔快取於 ~/.cloakbrowser/

# Step 3: 每次啟動時，wrapper 載入自訂二進位檔 + stealth args
from cloakbrowser import launch

# Step 4: 使用標準 Playwright API
browser = launch(
    proxy="http://user:pass@residential-proxy:port",  # 住宅 IP（關鍵）
    headless=False,      # 部分網站偵測 headless
    humanize=True,       # 人類化輸入行為
    geoip=True,          # 根據 proxy IP 自動設定時區/語系
)
page = browser.new_page()
page.goto("https://protected-site.com")
# → 反機器人系統看到的指紋與真實 Chrome 一致
# → navigator.webdriver === false
# → reCAPTCHA v3 score = 0.9（人類等級）
```

### 指紋種子（fingerprint seed）機制

```
啟動時決策樹：

launch() 呼叫
│
├── 無 --fingerprint 參數
│   └── 二進位檔自動產生隨機 seed (10000–99999)
│       └── 從 seed 派生所有偽造值（GPU、canvas 雜訊、WebGL 雜訊、
│           audio 雜訊、字體雜訊、硬體資訊）
│       └── 每次啟動 = 全新身分
│
├── --fingerprint=42069
│   └── 從 seed 42069 確定性派生所有偽造值
│       └── 相同 seed = 相同指紋（跨啟動一致）
│       └── 用於需要「回頭客」身分的場景（reCAPTCHA v3 Enterprise）
│
└── --fingerprint=42069 + 顯式 flags
    └── 顯式 flags 覆蓋自動派生值，其餘由 seed 派生
```

### humanize=True 的行為變化

| 互動類型 | 預設行為 | humanize=True |
|----------|---------|---------------|
| 滑鼠移動 | 瞬間傳送 | Bézier 曲線 + easing + 輕微 overshoot |
| 點擊 | 瞬間 | 真實瞄準點 + 按住持續時間 |
| 鍵盤輸入 | 瞬間填入 | 逐字輸入 + 思考停頓 + 偶爾錯字並自我修正 |
| 滾動 | 跳躍 | 加速 → 巡航 → 減速微步 |
| `fill()` | 瞬間設值 | 清除現有內容，逐字輸入 |

---

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式？

### 各方案切入點差異總覽

```
                     修補層級
                         ▲
                  更深層 │
                         │     CloakBrowser
                         │     (C++ source-level)
                         │     ┌─────────────────┐
                         │     │ 修改 Chromium    │
                         │     │ 原始碼後重新編譯  │
                         │     └─────────────────┘
                         │
                         │     Camoufox
                         │     (C++ source-level)
                         │     ┌─────────────────┐
                         │     │ 修改 Firefox     │
                         │     │ 原始碼後重新編譯  │
                         │     └─────────────────┘
                         │
                         │     undetected-chromedriver
                         │     (binary patching)
                         │     ┌─────────────────┐
                         │     │ 修補 chromedriver │
                         │     │ 二進位檔 + JS     │
                         │     └─────────────────┘
                         │
                  較淺層 │     playwright-stealth / puppeteer-extra
                         │     (JS injection + config flags)
                         │     ┌─────────────────┐
                         │     │ 在頁面中注入      │
                         │     │ JavaScript 覆蓋   │
                         │     │ 瀏覽器屬性        │
                         └─────┴─────────────────┘
                                  修補層級 → 更淺層
```

### DA 表（Decision Analysis Table）

| 技術名 | 技術解法 | 技術使用前提 | 技術使用副作用 | 技術使用預期效果 |
|--------|---------|-------------|---------------|-----------------|
| **CloakBrowser** | 修改 Chromium C++ 原始碼（58 patches），重新編譯為自訂二進位檔。Wrapper 封裝 Playwright/Puppeteer API。 | 需下載自訂 Chromium 二進位檔（~200MB）；需 Python ≥3.9 或 Node.js；wrapper 為 MIT 授權，二進位檔為專有授權（禁止再散布/逆向）。 | 二進位檔非開源（不可審計 patch 內容）；無法使用標準 Chrome 發行版；macOS 需手動繞過 Gatekeeper；部分修補依賴 `--fingerprint` flag 啟動。 | reCAPTCHA v3 score 0.9；Cloudflare Turnstile PASS；FingerprintJS PASS；BrowserScan NORMAL（4/4）；navigator.webdriver = false；TLS fingerprint 與真實 Chrome 一致。 |
| **Camoufox** | 修改 Firefox C++ 原始碼後重新編譯，搭配 BrowserForge 產生符合統計分布的指紋。Wrapper 封裝 Playwright API。 | 需下載自訂 Firefox 二進位檔；僅支援 Python；需 Python ≥3.8。 | 基於 Firefox 引擎，部分僅支援 Chromium 的網站可能不相容；Firefox 市占率較低，指紋本身即具有區分性；（推測：最後更新 2025-01，維護狀態不穩定）。 | reCAPTCHA v3 score 0.7–0.9；可自動產生符合真實裝置統計分布的指紋；支援 geolocation/timezone/locale 自動匹配 proxy。 |
| **undetected-chromedriver** | 修補 chromedriver 二進位檔 + JavaScript injection，移除自動化偵測標記。基於 Selenium WebDriver API。 | 需使用 Selenium（非 Playwright）；需 Python ≥3.6；需系統安裝 Chrome 瀏覽器。 | 僅支援 Selenium API（無法使用 Playwright 生態）；每次 Chrome 更新需等待修補適配；（推測：最後更新約 2024 年，維護狀態停滯）；JS injection 本身可能被偵測。 | 可通過 Distil/Imperva/DataDome 等反機器人系統；headless 模式部分支援（非官方）；無需下載自訂瀏覽器。 |
| **puppeteer-extra + stealth plugin** | 在 Puppeteer 啟動時注入 JavaScript，覆蓋 navigator.webdriver、navigator.plugins、window.chrome 等屬性。 | 需使用 Puppeteer（非 Playwright）；需 Node.js 環境；需系統安裝 Chrome/Chromium。 | JS injection 可被反機器人腳本偵測（執行時序、變數特徵）；無法偽造 Canvas/WebGL/Audio 指紋；每次 Chrome 更新可能失效；僅修補 JavaScript 可讀屬性，無法影響 C++ 層行為。 | 可通過簡單的自動化偵測（navigator.webdriver 檢查）；對高階反機器人系統（reCAPTCHA v3、Cloudflare Turnstile）效果有限。 |

### 各方案切入點差異

1. **CloakBrowser vs Camoufox**：兩者皆為原始碼層級修補後重新編譯，但基底瀏覽器不同（Chromium vs Firefox）。Chromium 市占率較高，指紋本身較不突出；Firefox 修補後仍需面對 Firefox 使用者基數小的區分性問題。

2. **CloakBrowser vs undetected-chromedriver**：後者操作在 chromedriver 層（WebDriver 協定中間層），屬於「攔截並修改 WebDriver 指令」的思維，無法處理 WebGL/Canvas/Audio 等需要在渲染引擎層面處理的指紋。

3. **CloakBrowser vs puppeteer-extra**：後者僅在 JavaScript 執行環境中覆蓋屬性值，反機器人系統可以透過檢查屬性描述符（property descriptor）、原型鏈（prototype chain）或直接呼叫 C++ 層 API 來繞過 JS 層的偽造。

