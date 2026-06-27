# OpenCut-AI-C2-Ollama雲端可行性查證與操作指令整理

## 狀況理解

使用者在初版調研完成後提出兩個追問：
1. 能否用 Ollama cloud 訂閱接上 OpenCut-AI（屬 Q&A 觸發——「可以用...嗎」為可行性質問）
2. 要求一步一步的操作指令來嘗試（屬實務指引，非質問，但與 Q1 相關，一併處理）

需先查證 Ollama 雲端是否真有訂閱制、API 介面是否與本地相容、OpenCut-AI 的 OllamaService 是否能直接接，再據實回答並補 patch 點。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| webfetch `ollama.com` | 確認雲端訂閱是否存在 | 取得定價與方案 | ✅ Free（隨帳號）/ Pro $20/mo / Max $100/mo，且有「Scale with cloud」明確段落 |
| webfetch `docs.ollama.com/cloud` | 確認雲端 API 介面 | 取得 host、認證、路徑 | ✅ host=`https://ollama.com`，路徑 `/api/tags`/`/api/chat` 與本地完全相同，認證=`Authorization: Bearer $OLLAMA_API_KEY` |
| grep `OLLAMA_URL` 於 services/ | 確認 OpenCut-AI 的 Ollama 整合點 | 找到所有引用處 | ✅ 13 處：config.py / ollama_service.py / main.py / model_backend.py / setup.py / .env.example |
| 讀 `ollama_service.py` 開頭 | 確認是否注入 auth header | 判斷能否直接指向雲端 | ❌ 不會：`httpx.AsyncClient(base_url=self.base_url)` 無 header 注入邏輯 |
| 讀 `config.py` OLLAMA_URL 設定 | 確認可否用 env 覆寫 | 判斷改動量 | ✅ `OLLAMA_URL: str = "http://localhost:11434"` + `env_prefix="OPENCUTAI_"`，可用 `OPENCUTAI_OLLAMA_URL` 覆寫 |
| 讀 `routes/llm.py` | 確認 LLM 路徑與 status 回傳 | 理解前端如何感知 LLM 狀態 | ✅ `/api/llm/status` 回 active_backend + turboquant_available + models |
| 對照 Ollama 雲端文件與 OpenCut-AI 程式碼 | 推導三種接法 | 給出改動量對照 | ✅ 三種：改程式碼補 header / 本地 daemon+signin+雲端模型名 / 反向代理加 header |
| 判斷雲端覆蓋範圍 | 確認哪些微服務能用雲端取代 | 避免誤導使用者以為雲端全包 | ✅ 只覆蓋 LLM 路徑；whisper/tts/image/speaker/face/clip/turboquant 不受 Ollama 雲端影響 |
| 整理五階段操作指令 | 回答 Q2 | 給出可複製貼上的 bash 序列 | ✅ 階段 0 前置→1 取碼→2 Docker 後端→3 前端→4 拉模型→5 試功能，每階段附驗證 curl |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| Q1 事實核對 | Ollama 雲端訂閱存在性 + API 相容性 + 認證方式，三項都有官方文件佐證 | ✅ ollama.com/pricing + docs.ollama.com/cloud 確認 |
| Q1 程式碼核對 | OpenCut-AI 是否能直接指向雲端，grep + read 原始碼 | ✅ OLLAMA_URL 可覆寫，但 ollama_service.py 不帶 Bearer header |
| Q1 三種接法對照 | 改動量 + 副作用 + 推薦 | ✅ 推薦「本地 daemon + signin + -cloud 模型名」零改動路徑 |
| Q1 覆蓋範圍 | 雲端能/不能取代的微服務清單 | ✅ 明確列出 LLM 路徑可取代、其餘 6 微服務不可 |
| Q2 操作指令 | 五階段每步可複製貼上 + 預期產出 + 驗證點 | ✅ 含 CPU/GPU 分支 + 停止清理 + Ollama 雲端接法示範 |
| 報告 Q&A 格式 | 遵守 AGENTS.md 的 Q<N> + A + 表格 + 結論結構 | ✅ Q1/Q2 各有表格佐證、結論一行收斂、不使用比喻與情緒語言 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| Q1 回答策略 | (A) 只說「可以」並給改法<br>(B) 查證雲端存在性+API 相容性+程式碼整合點再答 | **B** | 使用者問「可以用嗎」隱含「我以為 Ollama 只有本地」，需先核對雲端訂閱真實存在，否則可能回答一個不存在的產品；再核對 API 介面是否相容，否則改動量評估會錯 |
| 推薦哪種接法 | (A) 改程式碼補 header<br>(B) 本地 daemon + signin + 雲端模型名<br>(C) 反向代理 | **B** | Ollama 官方雲端設計就是「local daemon 透明代理」，`<model>-cloud` 後綴自動路由雲端，API 介面完全不變，OpenCut-AI 零改動，upgrade upstream 不衝突；A 需 fork 維護、C 多一層代理 |
| 是否說明雲端覆蓋範圍 | (A) 只答 LLM 部分<br>(B) 明確列出雲端不能取代的 6 個微服務 | **B** | 使用者若以為「接 Ollama 雲端 = 全部 AI 都走雲端」，會在試用時困惑為何 TTS/圖像生成仍需本地 GPU；明確切分能避免誤期望 |
| Q2 指令粒度 | (A) 只給啟動指令<br>(B) 五階段每步 + 驗證 curl + 預期產出 + 清理指令 + Ollama 雲端接法 | **B** | 使用者說「讓我可以嘗試」，需讓他照做就能跑通並自我驗證；缺驗證點會在卡住時不知是哪一步錯 |
| Q2 是否含 GPU 分支 | (A) 只給 CPU 路徑<br>(B) CPU + GPU 兩條 | **B** | 使用者機器未知；README 明列兩種啟動方式，且 GPU 路徑有 `docker-compose.gpu.yml` 覆寫檔需額外說明 |
| 是否把 Q1 的 Ollama 雲端接法也放進 Q2 指令 | (A) Q1 只答原理，Q2 只給預設啟動<br>(B) Q2 末段加「若要接 Ollama 雲端」示範 | **B** | 兩題相關，使用者可能想「一邊試用一邊接雲端」；把接法放進操作流程可讓使用者直接照做，無需再對照 Q1 |