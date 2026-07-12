# 03. Apple Sues OpenAI, Accusing It of Stealing Company Secrets

(原 URL: https://www.nytimes.com/2026/07/10/technology/apple-openai-lawsuit.html, 替代來源: https://www.theguardian.com/technology/2026/jul/10/apple-sues-openai-trade-secrets)

**Source**: https://www.theguardian.com/technology/2026/jul/10/apple-sues-openai-trade-secrets
**Author**: Dara Kerr
**Date**: July 10, 2026
**Category**: 政治經濟

## 1. 這個技術/政策解決什麼問題?

Apple 於2026年7月10日在加州北區聯邦地方法院對 OpenAI 提起訴訟，指控 OpenAI 竊取商業機密以建立其硬體業務。訴訟的核心指控包括：

- OpenAI 要求來自 Apple 的求職者分享機密專案細節，並攜帶設備零件和原型機參加面試
- OpenAI 硬體長 Tang Yew Tan（前 Apple 副總裁）指示求職者帶「實際零件」來進行「展示與講解」會議
- 前 Apple 員工 Chang Liu 被指控利用認證漏洞入侵 Apple 內部網路，下載「數十份 Apple 機密硬體相關文件」
- OpenAI 利用機密資訊接觸 Apple 的製造合作夥伴，要求展示 Apple 的金屬表面處理技術

Apple 尋求損害賠償及法院禁令，阻止 OpenAI 持有或使用其商業機密。

## 2. 這個問題為什麼會發生?(背景)

| 時間線 | 事件 |
|--------|------|
| 2024年 | Apple 與 OpenAI 宣布重大合作，ChatGPT 整合進 iOS/macOS |
| 2025年 | OpenAI 以64億美元收購 Jony Ive 創立的硬體新創 io Products，進軍硬體 |
| 2026/2月 | Apple 致函 OpenAI 表達機密資訊可能「不當流入 OpenAI 業務」的擔憂，OpenAI 未回應 |
| 2026/6月 | Apple 展示新版 Siri，AI 組件基於 Google Gemini 而非 ChatGPT |
| 2026/7/10 | Apple 正式起訴 OpenAI |

根本原因：OpenAI 從純 AI 軟體公司轉型為硬體製造商，直接與 Apple 的核心業務競爭。Jony Ive 的 io Products 收購案是觸發點——Ive 曾是 Apple 的設計靈魂人物（設計 iPhone、MacBook 等），他的團隊對 Apple 的設計哲學和供應鏈瞭若指掌。

Apple 在訴狀中寫道：「OpenAI 的新生硬體業務建立在最不穩固的基礎上，因其非法依賴盜用的商業機密而從核心腐爛。」

## 3. 這個技術/政策是如何解決該問題的?

Apple 採取**法律訴訟 + 商業切割**雙軌策略：

- **法律面**：以《商業機密保護法》（Defend Trade Secrets Act）為基礎提起聯邦訴訟，要求損害賠償和禁制令。訴訟對象包括 OpenAI 公司、硬體長 Tang Yew Tan、前員工 Chang Liu，以及 Jony Ive 的 io Products。
- **商業面**：Apple 已將新版 Siri 的 AI 底層從 ChatGPT 切換至 Google Gemini，降低對 OpenAI 的技術依賴。這既是技術選擇，也是戰略信號——合作關係已實質降級。
- **證據面**：Apple 指控 Liu 利用「認證漏洞」入侵內部網路，暗示 Apple 已進行內部 forensic 調查，掌握了數位證據。

OpenAI 的回應：發言人 Drew Pusateri 表示「我們對其他公司的商業機密沒有興趣，我們專注於建立能賦能所有人的創新技術」。這是否認指控的標準公關回應，但未正面回應具體指控。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 案例 | 適用性 |
|------|------|--------|
| 競業禁止訴訟 | Waymo vs Uber (2017) | 類似模式：前員工帶走機密，Uber 最終和解賠償 |
| 供應鏈合約限制 | Apple 與富士康的獨家條款 | 可阻止製造夥伴與 OpenAI 合作，但法律強制力有限 |
| 技術隔離（Clean Room） | IBM-PC 相容機 BIOS 逆向工程 | OpenAI 若主張獨立開發，需證明 clean room 流程 |
| 事前預防：員工監控 | — | Apple 已發現 Liu 的下載行為，顯示內部監控有效 |
| 產業自律協議 | AI 安全承諾 | 不適用於商業機密爭端 |

對用戶（學習 Rust/MCP/Spring+AI、探索 Cursor+Claude）的啟示：此案反映 AI 產業從「軟體合作」轉向「硬體競爭」的轉折點。Apple 與 OpenAI 的決裂顯示：AI 時代的商業機密保護將成為科技公司的核心法務議題。對於使用 AI 工具的開發者，需注意：你輸入到 AI 工具的程式碼和設計文件，理論上可能被用於訓練競爭模型——Apple 的訴訟正是這種擔憂的極端案例。
