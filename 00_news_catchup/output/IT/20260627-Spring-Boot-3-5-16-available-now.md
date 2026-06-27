# 4. Spring Boot 3.5.16 available now

**Source**: https://spring.io/blog/2026/06/25/spring-boot-3-5-16-available-now
**Author**: Andy Wilkinson
**Date**: 2026-06-25
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Spring Boot 3.5.x 世代進入生命週期終點。本次 3.5.16 版本是該世代的**最後一個 OSS（開源免費）版本**，包含 3 個依賴升級。使用者若不升級至 4.0.x 或 4.1.x，將不再收到免費的安全性修補與功能更新。

## 2. 這個問題為什麼會發生?(背景)

| 根因 | 說明 |
|------|------|
| Spring Boot 版本生命週期政策 | Spring 專案採用固定生命週期：每個 major.minor 世代在特定時間後結束 OSS 支援，僅提供商業支援（VMware Tanzu Spring） |
| 3.5.x 世代歷史 | Spring Boot 3.5.0 於 2025 年 5 月發布，至今約 13 個月，符合 Spring 典型的 12-14 個月 OSS 支援週期 |
| 4.x 世代已成熟 | Spring Boot 4.0.x 和 4.1.x 已發布並穩定，作為升級目標 |

推測: Spring Boot 的版本策略是「目前最新 stable + 前一個 major 的維護線」。當 4.1.x 成為最新 stable 後，3.5.x 的 OSS 支援自然結束。這與 Spring Framework 6.x 的生命週期政策一致。

**Spring Boot 近期版本時間線**：

```
3.5.0 (2025-05) ──→ 3.5.16 (2026-06-25, EOL)
4.0.x (2025-11) ──→ 持續 OSS 支援
4.1.x (2026-05) ──→ 最新 stable
```

## 3. 這個技術/政策是如何解決該問題的?

**3.5.16 的具體內容**：
- 3 個依賴升級（官方未列出具體依賴名稱，推測為 Spring Framework 相關元件或第三方 library 的安全性修補）
- 無新功能、無 breaking changes
- 從 Maven Central 可取得

**升級路徑建議**：

| 目前版本 | 建議動作 | 理由 |
|---------|---------|------|
| 3.5.x | 升級至 4.0.x 或 4.1.x | 3.5.x OSS 支援已終止 |
| 4.0.x | 可停留或升級至 4.1.x | 4.0.x 仍在 OSS 支援期內 |
| 4.1.x | 維持最新 | 最佳選擇 |

**商業支援替代方案**：
- VMware Tanzu Spring 提供 3.5.x 的商業支援與 binary 發行
- 包含 OpenJDK、Spring、Apache Tomcat 的統一訂閱

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 框架 | 版本生命週期策略 | 與 Spring Boot 的差異 |
|------|-----------------|----------------------|
| Quarkus | 活躍支援線 + LTS 線並行，LTS 提供更長支援 | Quarkus 的 LTS 線（如 3.15.x）支援期更長，但升級路徑可能更複雜 |
| Micronaut | 每個 major 版本有明確 EOL 日期 | 類似 Spring Boot，但社群規模較小 |
| Helidon | Oracle 主導，SE 與 MP 兩條線 | 生命週期與 Oracle 的 Java EE/Jakarta EE 策略綁定 |
| Dropwizard | 較慢的發版節奏 | 適合穩定優先的團隊，但生態較小 |
| Ruby on Rails | 嚴格語意化版本，minor 版本有明確維護期 | Rails 的維護期通常更長（約 18-24 個月），且有 Rails LTS 商業支援 |

**對用戶的啟示**：
- 用戶技術棧為 Ruby on Rails + React + GCP，目前不直接使用 Spring Boot。但用戶正在學習 Spring+AI，若未來團隊引入 Java 微服務，需注意 Spring Boot 版本生命週期管理。
- 作為即將轉管理者的角色，版本生命週期管理是技術債控制的核心環節。Spring Boot 的 EOL 公告模式（提前通知 + 明確升級路徑 + 商業支援選項）可作為團隊內部技術棧版本管理的參考範本。
- 若團隊使用 GCP GKE 上的 Java 服務，建議建立自動化依賴升級 pipeline（Dependabot / Renovate），在 EOL 前完成遷移。
