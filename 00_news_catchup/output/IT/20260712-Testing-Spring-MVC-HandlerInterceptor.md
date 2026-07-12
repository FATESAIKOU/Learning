# 06. Testing Spring MVC HandlerInterceptor

**Source**: https://feeds.feedblitz.com/~/960129299/0/baeldung~Testing-Spring-MVC-HandlerInterceptor
**Author**: Baeldung
**Date**: 2026-07
**Category**: 傳統IT技術

## 1. 這個技術/政策解決什麼問題?

Spring MVC 的 `HandlerInterceptor` 是處理 cross-cutting concerns（logging、認證、feature flag）的標準機制，但測試 interceptor 有兩個痛點：(1) interceptor 嵌入 request lifecycle，難以隔離測試；(2) 啟動完整 Spring context 的整合測試太慢。本文展示如何使用 `@WebMvcTest` + `MockMvc` 以最小成本測試 interceptor 的完整 request flow。

## 2. 這個問題為什麼會發生?(背景)

### HandlerInterceptor 的生命週期

```
Request → preHandle() → Controller → postHandle() → View → afterCompletion()
              ↑                                    ↑              ↑
         路由決策、認證                         Model 修改      資源清理、log
```

三個 lifecycle method 在不同階段執行，且 interceptor 透過 `WebMvcConfigurer.addInterceptors()` 註冊，與 Spring context 耦合。

### 測試選項的取捨

| 測試方式 | 優點 | 缺點 |
|---------|------|------|
| 純 unit test (MockHttpServletRequest) | 極快 | 不測試 interceptor 註冊、path pattern matching、與 controller 的整合 |
| `@WebMvcTest` | 載入 web layer only，自動載入 interceptor | 需 mock 所有 service dependency |
| `@SpringBootTest` | 完整 context，最真實 | 慢，不適合頻繁執行 |

### 本文的案例場景

以「配送費計算的漸進式 rollout」為例：透過 feature flag 控制新舊演算法（v1/v2）的流量分配。Interceptor 在 `preHandle()` 中根據 rollout percentage + 隨機值決定 routing，將結果寫入 `request.setAttribute()`，controller 讀取 attribute 後呼叫對應版本的 service。

## 3. 這個技術/政策是如何解決該問題的?

### 架構設計

```
DeliveryChargeInterceptor (HandlerInterceptor)
├── preHandle(): 讀取 rollout%，隨機決定 v1/v2，寫入 request attribute
└── 不執行業務邏輯，只做 routing decision

DeliveryChargesController (@RestController)
├── POST /delivery-charges/calculate
├── 讀取 request attribute "useV2"
└── 呼叫 calculateV1() 或 calculateV2()

WebMvcConfig (implements WebMvcConfigurer)
└── addInterceptors(): 註冊 interceptor，scope 到 /delivery-charges/**
```

### 測試策略

```java
@WebMvcTest(controllers = DeliveryChargesController.class)
class DeliveryChargeInterceptorIntegrationTest {

    @Autowired private MockMvc mockMvc;

    @MockBean private DeliveryChargeService deliveryChargeService;
    @MockBean private FeatureFlagService featureFlagService;
}
```

關鍵點：`@WebMvcTest` 自動載入所有 `WebMvcConfigurer` beans → interceptor 自動啟用，不需額外配置。

### 三層測試覆蓋

**測試 1：rollout 0% → 全部 v1**
```java
when(featureFlagService.rolloutPercentage()).thenReturn(0);
when(deliveryChargeService.calculateV1("SW1A")).thenReturn(5.0);

mockMvc.perform(post("/delivery-charges/calculate").param("postcode", "SW1A"))
  .andExpect(status().isOk())
  .andExpect(content().string("5.0"));
```

**測試 2：rollout 100% → 全部 v2**
```java
when(featureFlagService.rolloutPercentage()).thenReturn(100);
when(deliveryChargeService.calculateV2("SW1A")).thenReturn(3.5);
// 驗證 response 為 3.5
```

**測試 3：rollout 50% → 兩版本皆有流量**
```java
// 發送 20 次請求，統計 v1/v2 次數
// assertThat(v1Count).isGreaterThan(0)
// assertThat(v2Count).isGreaterThan(0)
```

### 測試金字塔對應

```
        ┌──────────┐
        │ @SpringBootTest │  ← 完整整合（少）
        ├─────────────────┤
        │  @WebMvcTest    │  ← 本文重點（中）
        ├─────────────────┤
        │  Unit Test      │  ← MockHttpServletRequest（多）
        └─────────────────┘
```

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 方案 | 適用場景 | 取捨 |
|------|---------|------|
| **Spring Filter (OncePerRequestFilter)** | 需要更早介入 request lifecycle | Filter 在 Servlet 層，無法取得 handler metadata |
| **Spring AOP (Aspect)** | method-level cross-cutting | 更靈活（可切入任何 bean），但無法取得 HttpServletRequest |
| **Spring WebFlux WebFilter** | Reactive stack | 對應的 reactive 測試方式不同（WebTestClient） |
| **API Gateway 層 (Kong/Traefik)** | 跨服務的 cross-cutting | 集中管理，但無法存取應用層 context |
| **OpenRewrite 自動重構** | 大規模 interceptor 遷移 | 非測試方案，但可輔助 interceptor 註冊方式的重構 |

**思考方式**：本文展示的測試模式核心是「分層隔離」——`@WebMvcTest` 在 unit test 和 full integration test 之間提供一個 sweet spot：載入 web layer 的完整 request processing pipeline（含 interceptor），但排除 service/repository 層。這對 Spring Boot 專案的測試策略設計有普遍參考價值。

**對用戶的意義**：用戶有深厚的 Spring Boot 經驗（卡片會員系統、BayCurrent 顧問時期），且正在制定微服務 Code Review 標準。本文的 interceptor 測試模式可直接納入團隊的測試規範——特別是 feature flag 的漸進式 rollout 測試，與用戶在 AxrossRecipe 的運營改造工作直接相關。
