# 09. 【AWS】AgentCore Managed Harness から自前の Skills を使えたけどさぁ… (原文)

**Source**: https://qiita.com/yakumo_09/items/63fde342ef76bad8abab
**Author**: yakumo_09 (Qiita)
**Date**: 2026/06/06
**Category**: AI技術

## 1. 這個技術解決什麼問題?

本文探討的問題是:**Amazon Bedrock AgentCore Managed Harness(以下簡稱「Harness」)能否在內建的 microVM 環境中載入使用者自定義的「Skills」**。

所謂 **Agent Skills**,指的是以 `SKILL.md` 格式撰寫的 markdown 文件,描述特定領域的工作流程 / 工具定義 / 行為約束。Harness 啟動時若能掛載這些 skills,Agent 在執行任務時就能遵循自定義規範(例如:commit message 格式、PR 範本、特定領域最佳實踐)。

被解決的子問題:
1. Harness 原本設計為「封閉式 managed 環境」,如何把外部自定義內容注入而不破壞隔離性
2. 多種部署場景(一次性 demo / 持續 production / 跨 VM 共享)對應的部署模式選擇
3. 自定義 skills 應在 Harness 啟動時載入,還是在 session 內動態注入

## 2. 這個問題為什麼會發生?(背景)

| 因素 | 說明 |
|---|---|
| Harness 是 managed microVM | 每次 invoke 啟動獨立 microVM,持久化層僅限 S3 / EFS / container image,VM 本地檔案不保留 |
| Skills 概念源自 Claude / Cursor 編輯器 | 開發者已熟悉「把領域知識編碼成 SKILL.md」的工作流,期待雲端 Agent 也能使用 |
| AWS 採用漸進式 API 開放 | Harness 剛發布時只支援 path 型,後續 boto3 1.43.17+ / aws-cli 2.34.56+ 開放 S3/Git 型 |
| 文章本身是踩坑筆記 | 作者明確指出:「Harness 発表直後は追加がうまくできなかった」,說明 AWS 文件不完整 |

> 通用背景:**Skills / Tools / Functions** 在 2024-2026 已成為 LLM Agent 的標準擴展點(MCP 即是統一此概念),各家雲端廠商都在追趕。

## 3. 這個技術是如何解決該問題的?

作者整理出 **4 種 Skills 載入模式**,並實作了 ①② 兩種。

### 3.1 模式總覽

```text
              ┌──────────────┐
              │ SKILL.md     │  (使用者的 markdown 技能定義)
              └──────┬───────┘
                     │
       ┌─────────────┼─────────────┬──────────────┐
       ↓             ↓             ↓              ↓
   ① 啟動注入     ② 燒進 image    ③ S3/Git path   ④ EFS mount
       │             │             │              │
       ↓             ↓             ↓              ↓
 InvokeAgent    Docker COPY   Harness 啟動時    microVM 啟動時
 RuntimeCommand →  ECR push   自動 fetch       自動 mount
  (exec 寫入)       │             │              │
       ↓             ↓             ↓              ↓
   揮發性,        持久,        集中管理,        跨 VM 共享,
   只在 session   每次啟動     需 IAM 授權      需 NAT Gateway
   VM 內          都有        s3:GetObject     費用較高
```

### 3.2 模式比較(作者整理)

| 模式 | 持久性 | 部署複雜度 | 適用場景 | 限制 |
|---|---|---|---|---|
| ① 啟動時注入(session) | 揮發 | 低(用 `npx invoke --exec`) | 一次性驗證、demo | 不會出現在 management console 的 skills 設定欄 |
| ② 燒進 container image | 持久(每次重啟都有) | 中(Dockerfile + ECR push) | 官方推薦 production | 自定義 image 無法在 console 設定,需 `aws bedrock-agentcore-control create-harness` |
| ③ Harness 啟動時 fetch S3/Git | 持久 | 低-中(只需 IAM 權限) | 集中管理 skills 庫 | 每次啟動都需 fetch,需 `s3:GetObject` / Git 認證 |
| ④ EFS mount | 持久 + 共享 | 高(需 NAT Gateway) | 多 agent 共享同一份 skills | 額外儲存 + 流量費用 |

### 3.3 實作範例(模式 ①)

```bash
# 同一個 session_id 內,先 exec 寫入 SKILL.md,再 invoke 引用
ARN="<harness-arn>"
SID=$(uuidgen)  # 至少 33 字元
B64=$(base64 < skills/commit-message/SKILL.md | tr -d '\n')

# 1) 啟動 session,把 skill 寫入 microVM
npx -y @aws/agentcore@preview invoke \
  --harness-arn "$ARN" --region us-west-2 \
  --session-id "$SID" --exec \
  "mkdir -p /app/s/commit-message && printf %s '$B64' | base64 -d > /app/s/commit-message/SKILL.md"

# 2) 同 session 內,引用該 skill
npx -y @aws/agentcore@preview invoke \
  --harness-arn "$ARN" --region us-west-2 \
  --session-id "$SID" --skills "/app/s/commit-message" \
  "コミットメッセージ書いて: ..."
```

### 3.4 實作範例(模式 ②)

```dockerfile
FROM public.ecr/aws/docker/library/python:3.12-slim
# 目錄名 = skill 名,需與 SKILL.md 的 name 欄位一致
COPY skills/commit-message/SKILL.md /app/.agents/skills/commit-message/SKILL.md
```

```bash
aws bedrock-agentcore-control create-harness \
  --harness-name skilldemo_image \
  --execution-role-arn "$ROLE_ARN" \
  --model '{"bedrockModelConfig":{"modelId":"global.anthropic.claude-sonnet-4-6","apiFormat":"converse_stream"}}' \
  --environment-artifact '{"containerConfiguration":{"containerUri":"'"${REPO_URI}:latest"'"}}' \
  --skills '[{"path":"/app/.agents/skills/commit-message"}]'
```

### 3.5 必要環境版本(踩坑重點)

| 工具 | 最低版本 | 用途 |
|---|---|---|
| boto3 / botocore | **1.43.17+** | 包含 S3 / Git source 的 Harness API |
| aws CLI | **2.34.56+** | control plane 操作 |

> 文章中作者明確指出:「ここでつまづきました」,版本不足是最大坑。

## 4. 是否存在解決類似問題的其他技術 / 框架 / 思考方式?

| 技術 | 技術解法 | 使用前提 | 副作用 | 預期效果 |
|---|---|---|---|---|
| **Anthropic MCP(Model Context Protocol)** | 用統一 protocol 把 tools/skills/resources 抽象為 server,client 端動態讀取 | MCP server 已實作(社群有大量) | 需理解 protocol + transport | 跨平台 / 跨模型通用 |
| **OpenAI Assistants API / GPTs** | 上傳 file + 定義 function calling,模型內建 retrieval | 接受 OpenAI 生態綁定 | vendor lock-in,資料外流風險 | 開發速度快,適合內部工具 |
| **Google Vertex AI Agent Engine + Reasoning Engine** | 透過 GCS 把 prompt / 工具定義打包,部署到 managed runtime | 使用 Google Cloud + Gemini | 跨雲受限 | 與 BigQuery / Vertex AI 整合佳 |
| **自建 LangGraph / LangChain Agent** | 程式碼內顯式註冊 tools,自己部署到 ECS / k8s / Lambda | 願意自管基礎設施 | 維運成本最高,版本升級靠自己 | 最大彈性,完全可控 |

> **切入點差異**:
> - **AWS AgentCore Harness** 採「**managed microVM + 多種 skill 載入策略**」:兼顧隔離性與彈性,但 console 體驗不完整(2026/6 仍須 cli)
> - **MCP** 採「**protocol-first**」:把 skills/tools 變成可被任何 client 呼叫的服務
> - **OpenAI Assistants** 採「**平台綁定**」:最快上手,但資料與模型都依賴 OpenAI
> - **自建 LangGraph** 採「**完全程式碼控制**」:最自由但運維負擔最大

---

**對用戶的意義**:
- 作者定位為「想輕鬆使用 Harness 的人」,實測後結論是:**「Harness = 工具與 skills 內建 + 可客製的執行基盤」**,不是「什麼都能輕鬆做」的低代碼平台
- 即將轉管理者:這類「managed 服務的極限」文章對團隊選型極有參考價值 — 它會明確告訴你什麼做不到,省下後續決策成本
- MCP 學習脈絡:AgentCore Skills 與 MCP Resources 在概念上對齊,理解一個有助於理解另一個
