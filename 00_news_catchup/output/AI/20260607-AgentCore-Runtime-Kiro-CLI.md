# 10. AgentCore Runtime のインタラクティブシェルで Kiro CLI を動かしてみた (原文)

**Source**: https://dev.classmethod.jp/articles/bedrock-agentcore-runtime-kiro-cli/
**Author**: suzuki.ryo (DevelopersIO / Classmethod)
**Date**: 2026/06/07
**Category**: AI技術

## 1. 這個技術解決什麼問題?

本文解決的問題:**Amazon Bedrock AgentCore Runtime(以下簡稱「Runtime」)的 microVM 互動式 shell 中,如何執行 Kiro CLI(AWS 推出的 AI CLI 工具)並完成 AWS 身份驗證**。

被解決的子問題:
1. **Lambda 環境無法執行 Kiro CLI 互動模式** — Lambda 沒有 PTY(虛擬終端機),`kiro-cli chat` 互動模式、device code flow 認證都失敗
2. **AgentCore Runtime 預設 image 不含 Kiro CLI** — 需要選擇「執行期臨時安裝」或「build 期燒進 image」
3. **`use_aws` 工具需要 AWS CLI 內部依賴** — Kiro CLI 的 `use_aws` MCP 工具會 spawn `aws` CLI,需另外安裝
4. **microVM 內的 IAM 身份** — 透過 MMDS(microVM Metadata Service)取得 `execution_role` 短期憑證,讓 Kiro CLI 呼叫 AWS API 時自動帶正確身份

## 2. 這個問題為什麼會發生?(背景)

| 因素 | 說明 |
|---|---|
| Kiro CLI 設計為互動式工具 | 內建 device code flow、chat REPL、tool use 循環等互動功能,需要 PTY 才能運作 |
| Lambda 是無伺服器函式執行環境 | 設計給「單一事件 → 短時間運算 → 回應」,沒有持久化 shell session |
| AgentCore Runtime 是 microVM 為基礎 | 保留完整 OS / shell / 套件安裝能力,但預設 image 是 minimal |
| AWS IAM Identity Center(I IdC)是 SSO 趨勢 | 組織登入需要 browser-based device flow,CLI 需對應支援 |
| MCP 工具鏈化 | Kiro CLI 透過 MCP 整合 `use_aws` 工具,任何使用 Kiro 的 Agent 都自動繼承此能力 |

> 通用背景:**「LLM Agent 在雲端執行個體中需要互動式 shell」** 是 2026 年的新興工作負載,各家 hyperscaler(AWS / Azure / GCP)都在建構對應服務。

## 3. 這個技術是如何解決該問題的?

### 3.1 兩種部署模式對比

```text
        模式 A:直接安裝                  模式 B:Dockerfile 預裝
        ┌─────────────────┐             ┌─────────────────┐
        │ 啟動 microVM     │             │  Dockerfile     │
        │   ↓             │             │   ↓             │
        │ curl install    │             │ COPY 安裝指令   │
        │  kiro-cli + aws │             │   ↓             │
        │   ↓             │             │ docker build    │
        │ kiro-cli chat   │             │   ↓             │
        │ (揮發)          │             │ ECR push        │
        └─────────────────┘             │   ↓             │
                                        │ Runtime 啟動時  │
                                        │ 預裝即用        │
                                        │ (持久)          │
                                        └─────────────────┘
```

| 面向 | 模式 A(直接安裝) | 模式 B(Dockerfile 預裝) |
|---|---|---|
| 適用場景 | 一次性驗證、debug | 持續 production |
| 部署時間 | 10 秒(curl 安裝) | 1 分 12 秒(CodeBuild 完整 build) |
| 重啟持久性 | ❌ Runtime 重 deploy 後丟失 | ✅ 永遠內建 |
| 操作複雜度 | 低 | 中(需寫 Dockerfile + .bedrock_agentcore.yaml) |
| 適合 | 探索性測試 | 團隊共用環境 |

### 3.2 身份驗證 3 種方式

| 方式 | 命令 | 適用場景 | 風險 |
|---|---|---|---|
| Device code flow | `kiro-cli login --use-device-flow` | 互動式環境(本篇場景) | 需瀏覽器確認 |
| 環境變數(API key) | `export KIRO_API_KEY="..."` | 自動化、headless | 需保護 shell 歷史 |
| SSM Parameter Store | `aws ssm get-parameter --name "/kiro/headless/api-key" --with-decryption` | 團隊 / 企業 | 需 KMS 解密 + `ssm:GetParameter` IAM |

> 安全注意(原文):最小 IAM 權限、KIRO_API_KEY 別留 shell 歷史、SSM 用 SecureString、microVM session 結束後會銷毀。

### 3.3 use_aws 工具的 IAM 驗證鏈

```text
Kiro CLI(use_aws MCP 工具)
   ↓ 呼叫
AWS CLI(子進程)
   ↓ 使用
MMDS 提供的 execution_role 短期憑證
   ↓ 授權
AWS APIs(例如 sts:GetCallerIdentity)
   ↓ 結果回傳
Kiro CLI 顯示
```

驗證測試:
- ✅ `sts:GetCallerIdentity` 成功 — 確認 execution_role 正確帶入
- ❌ `ec2:DescribeRegions` 拒絕 — 確認 IAM 權限邊界有效

### 3.4 Dockerfile 關鍵片段(模式 B)

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1

RUN apt-get update -qq && \
    apt-get install -y -qq curl unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Kiro CLI 預裝
RUN curl -fsSL https://cli.kiro.dev/install | KIRO_CLI_SKIP_SETUP=1 bash && \
    cp /root/.local/bin/kiro-cli* /usr/local/bin/

# AWS CLI v2(ARM64)
RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o /tmp/awscliv2.zip && \
    unzip -q /tmp/awscliv2.zip -d /tmp && \
    /tmp/aws/install && \
    rm -rf /tmp/aws /tmp/awscliv2.zip

ENV AWS_REGION=us-west-2
EXPOSE 8080
EXPOSE 8000
CMD ["opentelemetry-instrument", "python", "-m", "agent"]
```

關鍵技巧:`KIRO_CLI_SKIP_SETUP=1` 跳過 Kiro CLI 互動式首次設定,改由 `/usr/local/bin/` 統一管理路徑。

### 3.5 AgentCore Runtime vs Lambda 選擇

| 場景 | Lambda | AgentCore Runtime |
|---|---|---|
| 短暫事件(15 分內) | ✅ | ✅ |
| 互動式 shell | ❌ 無 PTY | ✅ 完整 shell |
| 15 分以上任務 | ❌ | ✅ |
| I/O 等待多(LLM 推論) | 持續計費 | ✅ I/O 期間無 CPU 計費 |
| 團隊共用環境 | 較不適合 | ✅ 適合 |

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 技術 | 技術解法 | 使用前提 | 副作用 | 預期效果 |
|---|---|---|---|---|
| **AWS Lambda + Layer** | 預先 build 包含 Kiro CLI 的 Lambda layer,搭配 Headless 模式 | 接受非互動式 + API key 認證 | 無 PTY,device flow 不可用 | 最低成本的事件驅動 |
| **ECS / Fargate Task** | 在 container 中跑 Kiro CLI,搭配 Session Manager 進入 | 自管 IAM role / VPC / NAT | 需自管 scaling / 監控 | 完全控制環境 |
| **Kiro CLI 直接裝在開發機** | 本機 Linux/macOS 直接 `curl \| bash` 安裝 | 個人開發 | 無法團隊共用、audit 困難 | 開發者日常使用最佳 |
| **Codespaces / Dev Container** | 雲端 IDE 內建 Kiro CLI,VS Code Remote 連線 | 已有 GitHub Enterprise | 需長期保留 VM | 適合 onboarding / code review |

> **切入點差異**:
> - **AgentCore Runtime** 採「**managed microVM + 短暫 + IAM 整合**」:互動性最強,適合 Agent 工作負載
> - **Lambda** 採「**event-driven + 完全無伺服器**」:成本最低,但放棄互動性
> - **Fargate** 採「**自管 container**」:控制權最大,運維最重
> - **Codespaces** 採「**開發者體驗優先**」:適合個人工作,非 production

---

**對用戶的意義**:
- 若在 AxrossRecipe 部署 Kiro CLI 給團隊:模式 B(Dockerfile 預裝)是最貼近 production 思維的做法
- 即將轉管理者:本文「模式 A vs B 的持久性取捨」可作為「快速 POC vs 長期 production」決策框架的範本
- GCP 背景:此模式在 GCP Cloud Run Jobs / GKE Ephemeral Containers 上有相似概念,邏輯互通
- K8s CRD 學習:AgentCore Runtime 的 `execution_role` 概念對應 K8s 的 `ServiceAccount` + IRSA(IAM Roles for Service Accounts)
