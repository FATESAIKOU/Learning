# OpenCut-AI-C1-完整技術調研與自託管AI剪輯架構拆解

## 狀況理解

使用者初次給的 URL（`opencut-app/opencut`）是錯誤目標，已完成一輪調研後使用者澄清真正要分析的是 `Ekaanth/OpenCut-AI`。這是 OpenCut 的 fork，但疊加了完整的自託管 AI 後端（7 微服務 + FastAPI 閘道 + Ollama/TurboQuant），定位與原版完全不同：原版是純剪輯器，此 fork 是「隱私優先、全本地 AI 剪輯閉環」。需從頭調研，先前的輸出物已刪除。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|---|---|---|---|
| 刪除先前錯誤目標的輸出物 | 清除錯誤調研痕跡 | 避免兩份報告並存混淆 | ✅ output/2026-06-27-OpenCut.md + learning-log/OpenCut-C1 已刪 |
| webfetch repo 首頁 | 初步理解定位與功能 | 取得 README 全文（34.6K，極詳盡） | ✅ 確認為 OpenCut fork、自託管 AI 剪輯、7 微服務、對標 Descript/CapCut/DaVinci |
| `git clone --depth 1` | 取得完整原始碼 | 逐檔驗證 README 宣稱的架構 | ✅ 取得 apps/web + services/*（7 微服務）+ packages/ui + scripts |
| 讀 `AGENTS.md`（此 repo 自己的） | 理解前端架構原則 | 確認 EditorCore/Actions/Commands 分層 | ✅ EditorCore 單例 + 12 Manager；Actions=觸發層；Commands=undo/redo 層 |
| 讀根 `package.json` + `turbo.json` | 理解 monorepo 結構 | 確認工具鏈與 workspace | ✅ bun 1.2.18 workspace + turbo 任務編排 |
| 讀 `apps/web/package.json` | 確認前端技術棧 | 取得所有依賴 | ✅ Next 16 + React 19 + Zustand + Drizzle + mediabunny + wavesurfer + @ffmpeg/* + @huggingface/transformers |
| 讀 `services/ai-backend/app/main.py` | 理解 AI 閘道 | 確認 route 模組清單與 health 聚合邏輯 | ✅ 20 route + 聚合 health（並行 ping 7 下游 + Ollama + GPU/RAM） |
| 讀 `services/ai-backend/app/config.py` | 理解設定模型 | 確認 env_prefix、外部 API key、engagement 權重 | ✅ Pydantic BaseSettings、OPENCUTAI_ prefix、7 信號權重和=1.0 驗證 |
| 讀 `apps/web/src/lib/ai-client.ts`（1774 行） | 理解前端↔後端唯一出口 | 確認所有 API 方法與逾時/串流策略 | ✅ 三層逾時（5s/120s/600s）+ NDJSON keepalive + 404 降級 + 6 種外部 API key 透傳 |
| 讀 `lib/copilot/copilot-types.ts` | 理解 AI Agent 結構 | 確認 CopilotPlan/Step/EditorAction 契約 | ✅ 19 種 EditorActionType + system prompt 內嵌 action 清單 + 6 preset |
| 讀 `lib/ai-action-executor.ts`（256 行） | 理解 AI 動作如何落地 | 確認 AI 動作→EditorCore Manager 的對接 | ✅ executeAction switch 19 case，呼叫 useTranscriptStore + EditorCore |
| 讀 `docker-compose.yml`（324 行） | 理解完整部署拓撲 | 確認 12 容器 + network + volume + healthcheck | ✅ db/redis/redis-http/ollama/ai-backend/7 微服務/web，同一 bridge |
| 列舉 ai-backend routes 與 services | 確認 route 與 service 對應 | 取得 20 route + 30 service 檔案清單 | ✅ route: transcribe/tts/generate/llm/command/analyze/engagement/youtube/video/turboquant/sarvam/smallest/search/export/audio/podcast/factcheck/setup/template |
| 列舉前端 lib 目錄 | 理解功能切片 | 確認 36 個 lib 子目錄 | ✅ actions/animation/audio/auth/blog/chapters/color/commands/copilot/db/effects/fonts/gradients/infographic-templates/media/motion-tracking/multicam/music/podcast/preview/reframe/scene-detection/script-to-video/search/sharing/stickers/templates/text/thumbnail/timeline/transcription/transitions/video-gen |
| 列舉前端 services 目錄 | 理解前端基礎服務 | 確認 renderer/storage/proxy/video-cache/sync/version/merge/diff/search | ✅ 含 renderer/nodes（場景節點）+ storage/migrations（專案 schema 版本） |
| 讀 `docker-compose.gpu.yml` | 確認 GPU 透傳 | 取得 nvidia device + TURBOQUANT_EXTRAS 機制 | ✅（由 README 引用，已從 README 取得完整說明） |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|---|---|---|
| 報告格式合規 | 對照 AGENTS.md 4+1 點格式 | ✅ §1 問題 4 子問題 / §2 背景「文章提到」與「通用背景」分節 / §3 流程圖+程式碼+表格 / §4 DA 表 5 欄 6 列 / §5 Q&A 章節存在但本輪無提問 |
| 技術本質掌握 | 能否一句話說清 OpenCut-AI 解的核心問題 | ✅ 「全棧本地的 AI×剪輯閉環，19 種 EditorAction 讓 LLM 直接驅動編輯器 Manager」 |
| Fork 關係交代 | 報告是否說明與上游 OpenCut 的關係 | ✅ §2 明列「fork of OpenCut，繼承前端編輯器，AI 層全為新增」 |
| 隱私機制有據 | OPFS / 本地微服務 / 外部 API 可選 是否有原始碼佐證 | ✅ README OPFS + docker-compose 同 network + config.py 外部 key 預設空 |
| 19 種 EditorAction 完整 | 是否列出全部 action type | ✅ §3.4 列舉 + copilot-types.ts 系統提示內嵌清單佐證 |
| TurboQuant 雙後端 | GPU/CPU 路徑差異是否說清 | ✅ §3.6 表格列壓縮位元/decode/加速策略/觸發條件 + 防崩潰降級 |
| 逾時策略 | 三層逾時值是否列明 | ✅ §3.7 表格 5s/120s/600s + NDJSON keepalive + 404 降級 |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|---|---|---|---|
| 錯誤調研處理 | (A) 保留舊報告，新報告另開<br>(B) 刪舊報告，從頭寫 | **B** | 使用者明確說「從頭開始寫」，且目標完全不同（OpenCut vs OpenCut-AI 是不同 repo、不同定位）；保留舊報告會造成兩份並存混淆 |
| 資料取得方式 | (A) webfetch GitHub 逐頁<br>(B) CDP 繞反爬<br>(C) git clone 本地探索 | **C** | README 極詳盡（34.6K）可直接 webfetch 取得，但原始碼（ai-client.ts 1774 行、main.py 263 行、config.py 148 行、docker-compose 324 行、ai-action-executor 256 行、copilot-types 120 行）需逐檔精讀，webfetch GitHub 頁面夾雜大量導覽 HTML，clone 後用 read/grep 精準且可驗證檔案互引 |
| §3 敘事主軸 | (A) 逐微服務描述<br>(B) 以「AI×剪輯閉環」為主軸貫穿 | **B** | 使用者要分析的是「這個技術解什麼問題、怎麼解」；逐微服務是清單不是洞見；以 EditorCore+AIClient+Copilot 三層貫穿才能呈現「AI 不是外掛而是直接驅動 Manager」的核心設計 |
| DA 表替代方案 | (A) 只列同類自託管<br>(B) 涵蓋雲端 SaaS + 散裝 + 原版 fork | **B** | 需呈現完整設計空間：原版 OpenCut（無 AI）、Descript（雲端）、CapCut（雲端免費）、散裝本地栈（無整合）、DaVinci（本地專業但 AI 有限），才能凸顯 OpenCut-AI 的差異化定位 |
| 是否啟用 CDP | (A) 嘗試 CDP<br>(B) 跳過 | **B** | git clone 已取得全部原始碼，webfetch README 即取得完整功能清單，無 CAPTCHA/反爬，無需 CDP |
| 功能清單取捨 | (A) 把 README 全部功能列進報告<br>(B) 只列架構性關鍵，其餘歸入附錄式表格 | **B** | README 列數十項功能（20 transitions/22 filters/8 templates/7 engagement signals/9 video models），全列會讓 §3 失焦；只取架構性關鍵（EditorAction/TurboQuant/health 聚合/逾時/OPFS）深述，其餘用表格點到 |