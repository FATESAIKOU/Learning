# 01. Is the Super Smash Bros. Brawl donut from Mister Donut? (原文)

**Source**: https://sethmlarson.dev/is-the-donut-from-super-smash-bros-brawl-a-mister-donut
**Author**: Seth Larson (Python 核心貢獻者, 安全工程師)
**Date**: 2026/06/05
**Category**: 傳統IT技術

## 1. 這個技術解決什麼問題?

本文看似遊戲/食物閒聊,實則演示一個**資訊溯源失敗 (provenance gap)** 的案例:Seth Larson 在 Mister Donut 博物館照片中,認出 Super Smash Bros. Brawl 的巧克力甜甜圈 sprite;但負責蒐集此類考據的 **Render96 wiki** 卻明確記載此 sprite 的出處「不明」。問題是:**當第一手素材不存在時,我們要如何推論、記錄、並誠實標示「不可知」?**

| 面向 | 問題 |
| --- | --- |
| 考據 | 為何 sprite 長得「很像」現實商品?是致敬、巧合、還是日本/美國合作? |
| 來源記錄 | Render96 wiki 已標「unknown」,而作者認為可能是 Mister Donut |
| 認知偏誤 | 「像我熟悉的東西」是否就等於「就是那個東西」? |
| 不確定性管理 | 為何專案選擇寫「unknown」而不是「probably Mister Donut」? |

## 2. 這個問題為什麼會發生?(背景)

### 觸發鏈

```text
1. Bluesky 看到 Mister Donut 博物館連結
2. 點進去 → 看到巧克力環狀甜甜圈
3. 與記憶中的 SSBB sprite 比對 → 視覺相似
4. 查 Render96 wiki → 記載 "origin is not known"
5. 結論: 永遠不會知道 (We'll probably never know!)
```

### 為什麼考據會卡住?

| 阻礙 | 說明 |
| --- | --- |
| sprite 素材原始檔案不對外公開 | Sakurai / HAL Laboratory 美術組內部參考圖不會釋出 |
| 設計師訪談未涵蓋小道具 | 訪談集中於角色/系統設計,食物類道具很少被提及 |
| 商業合作未必公告 | 若有 Mister Donut 合作,未必有正式 press release 留存 |
| 推測:文化翻譯損耗 | 日本在地商品 (Mister Donut = ミスタードーナツ) 在西方 wiki 容易脫離脈絡 |
| Render96 wiki 的「unknown」標記 | 是一種**結構化的不確定性**——把「我沒找到證據」明確寫入資料模型 |

### 與一般「網路迷因」的差異

普通迷因 (meme) 多為「二次創作引用」,出處可考;但遊戲內 sprite 屬**商業美術資產**,考據時常碰到 NDAs、保密協議、未公開檔案等牆。

## 3. 這個技術是如何解決該問題的?

本文展示的不是單一技術,而是一套**資訊溯源方法論**——給軟體開發者/技術寫作者處理「不確定知識」時的 SOP:

### 3.1 視覺比對法 (Pattern Recognition, 但須克制)

| 步驟 | Seth Larson 的操作 |
| --- | --- |
| 建立基準 | 多年閱讀 SSBB / Kirby Air Riders sprite sheet |
| 提出假設 | 「這 donut = SSBB donut」 |
| 假設檢驗 | 查 wiki + 公開訪談 |
| 接受反證 | wiki 標 unknown,接受「不可知」 |

### 3.2 引用次級來源 (Secondary Source Triangulation)

Render96 wiki 在此扮演**結構化不確定性紀錄者**角色——比 Reddit 討論串、Twitter 推文更可信,但仍非第一手來源。

### 3.3 明示不確定性 (Epistemic Honesty)

| 寫法 | 效果 |
| --- | --- |
| "We'll probably never know!" | 誠實標示知識邊界 |
| 不用 "definitely Mister Donut" | 避免過度推論 |
| 提供 wiki 連結 | 讓讀者自行驗證 |

### 3.4 套用於軟體工程

| 場景 | 對應方法 |
| --- | --- |
| 第三方 SDK 行為異常 | 視覺比對 = 復現步驟;次級來源 = 官方 issue tracker |
| 函式庫 bug 起源 | 寫 "regression introduced in vX.Y" 而非 "this is broken" |
| API 反直覺設計 | 標 "design intent unknown" + 引用 RFC/PR |
| LLM 產生莫名輸出 | 標 "hallucination suspected, source: none" |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 框架 | 應用領域 | 與本文的對應 |
| --- | --- | --- |
| **W3C PROV (Provenance Ontology)** | 資料/檔案來源語意網標準 | 推測:可套用於 wiki 條目,記錄「unknown」是經過哪些來源驗證後的狀態 |
| **Provenance Graph (Datalog/SPARQL)** | 資料血緣追蹤 | 把 sprite → 設計師訪談 → 商業記錄 → 結論連成可查詢圖 |
| **Software Bill of Materials (SBOM / SPDX / CycloneDX)** | 軟體供應鏈溯源 | 對應到程式碼:每個 API 呼叫都該能追溯到 commit/RFC/文件 |
| **Git Blame / git-bisect** | 程式碼歷史定位 | 對應 sprite 考據:從「現在的樣子」反推「最初提交者」 |
| **SLSA (Supply-chain Levels for Software Artifacts)** | 軟體工件完整性 | 推測:若遊戲美術有 SLSA 等級記錄,就能直接驗證 sprite 來源 |
| **Open Source Wiki 文化 (Wikipedia: Verifiability, ORES)** | 維基百科的可驗證性政策 | Render96 wiki 的 "unknown" 標記與此精神一致 |
| **推測:Wayback Machine 快照比對** | 過時網頁考古 | 可檢查 2008 年前後 SSBB 官方網站,看是否提過食物道具合作 |
| **推測:像素圖 hash 比對** (perceptual hash / pHash) | 影像去重 | 若 SSBB 與 Kirby Air Riders 都用同一個 donut sprite,可佐證共享來源 |

### 給開發者的反思

- **寫文件時**:遇到「我也不知道為什麼」就明確標 `TODO: investigate origin`,而非刪除或猜測
- **code review 時**:對 LLM 生成的 commit 多問一句「這行為是文檔還是不確定性?」
- **技術寫作時**:學 Seth Larson 把 "probably never know" 寫進去,比硬下結論更專業
- **開源維護時**:把 wiki 條目當資料庫,unknown 也是有效狀態,不要為了好讀而補上推測
