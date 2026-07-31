# 5. Amplify ホスティングで Route 53 管理外のカスタムドメインを設定する方法を教えてください

**Source**: https://dev.classmethod.jp/articles/tsnote-amplify-third-party-dns-custom-domain-setup/
**Author**: クラスメソッド AWS テクニカルサポートチーム
**Date**: 2026-07
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

本篇為 AWS 技術支援 TIPS，解決的問題：

> **「AWS Amplify Hosting 的自訂網域一定要用 Route 53 管理嗎？」**

具體痛點：
| 痛點 | 說明 |
|------|------|
| DNS 供應商非 Route 53 | 企業既有網域在 Cloudflare、Google Domains、Onamae 等第三方 DNS |
| 誤以為 Amplify 強綁 Route 53 | 文件未明示「手動設定」路徑，開發者誤判無法接 |
| 所有權驗證時效性 | ACM 檢驗頻率隨時間遞減，延遲設定 DNS 會卡在 pending |
| 網域刪除/子網域增改 | 設定後續維運流程不清 |

本篇給出從「新增 → 驗證 → 子網域/刪除」的完整手動設定流程。

## 2. 這個問題為什麼會發生?(背景)

1. **AWS 服務預設強烈引導同生態服務**：Amplify Console 預設流程暗示 Route 53，使非 Route 53 使用者誤以為需先遷移 DNS
2. **ACM 所有權驗證機制設計**：ACM 透過 CNAME 驗證網域所有權，但「驗證頻率隨時間遞減」的設計鮮少被強調——若新增網域後數小時才設 DNS，可能卡在 pending 直到逾時
3. **日本企業常見 DNS 配置**：Onamae（お名前.com）、Cloudflare 在日本普及，但 Route 53 並非主流，跨服務設定需求常見
4. **Amplify Hosting 取代 S3 靜態託管**：AWS 已推薦 Amplify Hosting 作為 S3 靜態網站託管的後繼方案，使本流程成為高頻問題

推測背景：クラスメソッド（Classmethod）作為日本最大 AWS 顧問公司，將過去 AWS 總合支援服務收到的常見詢問整理為 TIPS，本文屬於「DNS 跨供應商」這類高頻疑問的官方化回答。

## 3. 這個技術/政策是如何解決該問題的?

完整手動設定流程：

```
1. Amplify Console → 選應用程式
2. ホスティング → カスタムドメイン → ドメインの追加
3. 輸入網域 → ドメインの可用性を確認
4. ★ 選「手動設定」 ★（關鍵：非 Route 53 路徑）
5. 確認/修改預計子網域
6. ドメインを追加
7. 等待 DNS 記錄生成
8. 將顯示的 CNAME 記錄設到第三方 DNS（例：Cloudflare）
9. 等 AWS 驗證完成 → ステータス「使用可能」
```

**關鍵設計要點**：

| 要點 | 細節 |
|------|------|
| 手動設定選項 | 選此即跳過 Route 53 自動整合，改走 ACM CNAME 驗證 |
| CNAME 驗證記錄 | ACM 產生 `_xxx.example.com → yyy.acm-validations.aws` |
| 時效性警告 | 新增網域後**立刻**設 DNS；逾時後 ACM 檢查頻率降低，可能 pending 停滯 |
| 子網域增改 | 設定後仍可由「ドメイン設定」進入修改 |
| 網域刪除 | アクション → ドメイン削除 |

**第三方 DNS 設定範例（以 Cloudflare 為例）**：將 ACM 產生的 CNAME 直接加到 Cloudflare DNS 控制台，等待傳播即可。需注意若第三方 DNS 有「CNAME flatten」或「proxy」功能，可能影響驗證。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 對應場景 | 與 Amplify 手動設定對比 |
|------|---------|----------------------|
| **Route 53 自動設定** | 網域已在 Route 53 | 全自動、零手動，但需先把 DNS 遷移進 Route 53 |
| **Cloudflare Pages + Cloudflare DNS** | DNS 已在 Cloudflare | 同生態整合最順，但綁定 Cloudflare 託管 |
| **Vercel + 第三方 DNS** | Vercel 託管 | Vercel 對第三方 DNS 流程更簡化，驗證機制類似 |
| **Netlify + 第三方 DNS** | Netlify 託管 | 同上 |
| **GKE + Ingress + cert-manager**（使用者現職棧） | 自管 K8s | cert-manager + Let's Encrypt 自動簽發/續期，完全自控但需自行維運 |
| **Firebase Hosting** | Google 生態 | 類似 Amplify，第三方 DNS 需手動驗證 |

**思考方式啟發**：
- **「同生態便利 vs 跨生態可控」的權衡**：AWS 服務預設引導 Route 53 換取零設定，但代價是 DNS 遷移成本。此權衡在使用者現職 GCP 棧亦有對應（Cloud DNS vs 第三方 DNS），可對照思考
- **ACM 驗證「頻率遞減」設計**是常被忽略的時序陷阱——這類「服務端輪詢頻率隨時間衰減」的設計模式，在 K8s controller、MCP polling、Spring AI retry 等場景皆存在，值得建立「驗證類操作要儘早完成」的直覺
- **「手動設定」作為一等公民選項**：許多雲服務預設流程引導自動化，但保留手動路徑是成熟服務的標誌。使用者即將任管理者，在採購/選型時可評估「這服務是否提供完整手動路徑」作為風險指標

**行動建議**：
1. 對照使用者現職 GKE + Ingress + cert-manager 流程與 Amplify 手動設定，整理「DNS 驗證模式」跨雲對照表
2. 若團隊未來有 AWS 工作或客戶需求，本流程可作為 SRE runbook 範本
3. 雖然使用者主棧為 GCP，但「跨雲 DNS / 證書驗證時序陷阱」是通用知識，建議以 ACM 行為對照 GCP Certificate Manager 的驗證機制，建立跨雲直覺