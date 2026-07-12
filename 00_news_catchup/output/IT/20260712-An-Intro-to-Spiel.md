# 08. An Intro to Spiel – Creating Presentations in Your Terminal with Python

**Source**: https://blog.pythonlibrary.org/2026/07/10/an-intro-to-spiel-creating-presentations-in-your-terminal-with-python/
**Author**: Mike Driscoll (Mouse Vs Python)
**Date**: 2026-07-10
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Spiel 是一個 Python library，讓開發者直接在終端機中建立並播放簡報（presentation）。它解決的問題是：**開發者需要快速展示技術內容時，不必開啟 PowerPoint/Keynote/Google Slides 等 GUI 工具，直接在 terminal 中用 Python 程式碼定義 slide 內容並播放。**

## 2. 這個問題為什麼會發生?(背景)

### 開發者的簡報需求場景

```
傳統流程：
  想法 → 開 PowerPoint → 選模板 → 排版 → 匯出 → 播放
  耗時、context switch 大、版本控制困難

Spiel 流程：
  想法 → 寫 Python script → terminal 播放
  快速、純文字環境、可 version control (git)
```

### 技術基礎

Spiel 建立在 **Rich** library 之上——Rich 是 Python 終端機 UI 的事實標準，提供 color、table、markdown、panel 等豐富的 terminal rendering。Spiel 本質上是將 Rich 的 rendering 能力包裝成 slide-based presentation 框架。

### 當前狀態

Spiel 已被作者 **archive**（歸檔），原因是依賴的 Textual 版本過舊無法升級。Textual 是 Rich 作者開發的 TUI framework，API 在早期版本變動劇烈。這意味著 Spiel 目前處於「可用但不再維護」的狀態。

## 3. 這個技術/政策是如何解決該問題的?

### 基本架構

```python
from spiel import Deck, Slide, present
from rich.text import Text
from rich.align import Align
from rich.style import Style

# 方式 1：decorator 定義 slide
deck = Deck(name="My Presentation")

@deck.slide(title="Slide 1")
def slide_1():
    return "Your content here!"

# 方式 2：Slide 物件
def make_slide(title_prefix, text):
    def content():
        return Align(text, align="center", vertical="middle")
    return Slide(title=f"{title_prefix} Slide", content=content)

deck.add_slides(
    make_slide("First", Text("Python 101", style=Style(color="blue"))),
    make_slide("Second", Text("A Python list is...", style=Style(color="red"))),
)

if __name__ == "__main__":
    present(__file__)
```

### 操作方式

| 操作 | 按鍵 |
|------|------|
| 下一張 | → (右箭頭) |
| 上一張 | ← (左箭頭) |
| 結束 | Ctrl+C |

### 安裝與試用

```bash
pip install spiel
spiel demo present          # 播放內建 demo
docker run -it --rm ghcr.io/joshkarpel/spiel  # 不需安裝，Docker 直接試用
```

### 功能限制

- 僅支援 terminal 內 rendering（無匯出 PDF/HTML 功能）
- 依賴舊版 Textual，無法升級
- 專案已 archive，無新功能開發
- Rich 的 rendering 能力即為 slide 的表現力上限

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 語言/環境 | 特點 | 狀態 |
|------|----------|------|------|
| **Spiel** | Python + Rich | Terminal 原生，Python 程式碼定義 | Archived |
| **slides (Go)** | Go | Terminal-based markdown presentation | 活躍維護 |
| **lookatme** | Python | Terminal markdown presentation，支援 syntax highlighting | 活躍 |
| **presenterm** | Rust | Terminal markdown presentation，主題豐富 | 活躍 |
| **Marp** | Node.js | Markdown → HTML/PDF slide deck，VS Code 整合 | 活躍 |
| **Slidev** | Node.js/Vue | Markdown → 網頁簡報，支援程式碼互動執行 | 活躍 |
| **reveal.js** | JavaScript | HTML presentation framework，生態最大 | 活躍 |
| **Quarto** | Python/R/JS | 學術/技術寫作 → 多格式輸出（含 reveal.js 簡報） | 活躍 |

**思考方式**：Terminal-based presentation 是一個 niche 但有忠實用戶的領域。核心價值主張是「開發者留在 terminal 的 flow 中」——不切換到 GUI 工具、內容以純文字/Markdown 管理、可版本控制。Spiel 的 Python-native 設計（用 decorator 定義 slide）比 Markdown-based 方案更靈活（可動態生成內容），但 archive 狀態使其不適合新生產使用。

**對用戶的意義**：用戶偏好 CLI 工具（Taskwarrior、tmux、tig），terminal-based presentation 與其工作流契合。但 Spiel 已 archive，若有用 terminal 做簡報的需求，建議考慮 **presenterm (Rust)** 或 **Slidev (Markdown + 程式碼互動)** 作為替代。用戶正在學習 Rust，presenterm 本身也是 Rust 寫的，可作為學習參考。
