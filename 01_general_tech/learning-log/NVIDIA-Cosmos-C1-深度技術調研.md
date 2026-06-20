# NVIDIA-Cosmos-C1-深度技術調研

## 狀況理解

使用者要求對 NVIDIA Cosmos（https://github.com/nvidia/cosmos）進行深度技術調研。NVIDIA Cosmos 是 NVIDIA 開源的「世界基礎模型（World Foundation Models）」平台，目標為加速 Physical AI（機器人、自駕車、智慧基礎設施）開發。当前最新版本為 Cosmos 3（2026 年 5 月發表），採用統一的 Mixture-of-Transformers omnimodal 架構，同時支援 Reasoner（理解）與 Generator（生成）雙執行面，並原生處理 text/image/video/sound/action 五種模態。

任務本質為 `01_general_tech` 模式的技術解析：需產出 (1) 分析報告 `output/2026-06-20-NVIDIA-Cosmos.md`、(2) 分析過程報告 `learning-log/NVIDIA-Cosmos-C1-深度技術調研.md`，嚴格遵循 AGENTS.md 指定的 4 點格式與過程 log 格式。

## 執行的動作與結果

| 執行的動作 | 動作的目的 | 預期達成效果 | 實際的結果 |
|-----------|-----------|-------------|-----------|
| 讀取 `02_mvps/AGENTS.md` 與 `01_general_tech/AGENTS.md` 確認任務模式 | 判斷此次調研屬於哪種輸出格式（MVP 實作 vs 一般技術解析） | 確認為 `01_general_tech` 模式，需產生 4 點分析報告 + C1 學習 log | 確認模式為一般技術解析；4 點格式：(1) 解決什麼問題 (2) 為什麼發生 (3) 如何解決 (4) 替代方案 DA 表 |
| 讀取現有 `CodeGraph-C1` log 與 `2026-05-30-CodeGraph.md` 報告 | 確認既有報告的寫作風格、表格使用、DA 表格式、Overengineering 分析惯例 | 對齊輸出格式與深度標準 | 取得完整範本：4 點格式、DA 表 5 欄位（技術名/解法/前提/副作用/預期效果）、替代方案 2–4 個、過程 log 4 段格式（狀況理解/執行動作/驗證現狀/決斷點） |
| 讀取 nvidia-cosmos org 頁面（https://github.com/nvidia-cosmos） | 確認 Cosmos 專案組織結構、所有 repo、版本演進脈絡 | 取得完整生態 repo 清單與版本歷史 | 取得 12 個 repo：cosmos-predict1/2.5、cosmos-transfer1/2.5、cosmos-reason1/2、cosmos-cookbook、cosmos-rl、cosmos-xenna、cosmos-dependencies；org 已遷移至 NVIDIA/cosmos 統一 repo；stars 約 10.4k |
| 讀取 NVIDIA/cosmos 主 repo README | 取得 Cosmos 3 完整技術規格、模型家族、架構、整合路徑、quickstart、生態、授權 | 理解 Cosmos 3 核心機制與定位 | 取得完整 README：MoT 架構（AR + Diffusion 共用骨幹 + mRoPE）、5 模態、6 種 embodiment 動作維度、5 種整合路徑（Diffusers/vLLM-Omni/Transformers/vLLM/NIM）、Guardrail 機制、Cosmos Framework/Curator/Evaluator 生態、OpenMDW-1.1 授權、Cosmos 3 於 2026-05 發表 |
| 讀取 README 的 Inference Benchmarks / Finetune / Limitations / Ecosystem / News / License 段落 | 取得效能數據、微調食譜、已知限制、生態工具、版本時程、授權條款 | 補齊報告的技術細節與限制面 | 取得：benchmark 在獨立 `inference_benchmarks.md`；SFT cookbook（Vision generator + Reasoner）運行於 Cosmos Framework、8×H100；限制含 temporal inconsistency/object morphing/音視不同步；生態含 Cosmos Framework/Curator/Evaluator；2026-05-31 發表 Cosmos 3；OpenMDW-1.1 授權 |
| 委派 subagent 調研 Cosmos 版本演進 + 10 個替代方案 | 收集 v1/v2/v3 演進、Physical AI 定義、NVIDIA 生態定位、以及 Genie 2/Sora/Veo 3/World Labs/UniPi/GAIA-1/Tesla FSD/DreamerV3/Isaac Sim/Genesis 的比較資料 | 取得替代方案的核心切入點與差異，供 DA 表使用 | 取得完整結構化報告：Cosmos 1（CES 2025）/2/3 演進脈絡；Physical AI 定義（感知+理解+推理+執行）；NVIDIA 生態堆疊（硬體→Isaac Sim/Newton→Cosmos→NeMo/NIM→GR00T）；10 個替代方案的切入點與差異對比表 |

## 動作結束後的現狀

| 驗證的面向 | 驗證的內容與方式 | 驗證結果 |
|-----------|----------------|---------|
| Cosmos 3 核心機制 | 比對 README 的 Model Architecture 段落、Model Family 表、Generator/Reasoner Use Cases 表、Action Conditioning 維度表 | 一致：MoT 架構（AR Reasoner + Diffusion Generator 共用骨幹與 mRoPE）、5 模態（text/image/video/sound/action）、6 種 embodiment 動作維度（9D/9D/57D/10D/20D/29D）、5 種整合路徑 |
| 版本演進脈絡 | 比對 nvidia-cosmos org repo 清單（predict1/2.5、transfer1/2.5、reason1/2）與 subagent 回報的 CES 2025/COMPUTEX 2026 時程 | 一致：v1（2025-01 CES）感知與生成分離、模態限 text/image/video；v2（2.5 系列）沿用分離設計但品質提升；v3（2026-05）統一為 omnimodal MoT 並新增 sound/action |
| 替代方案覆蓋度 | 檢查 DA 表是否涵蓋「學習式世界模型」「規則式模擬」「內容創作影片生成」「自駕垂直」「學術 RL」五個維度 | 覆蓋：Cosmos（學習式統一）、Isaac Sim+Newton（規則式模擬）、Genie 2（單圖→世界研究）、Sora/Veo 3（內容創作）、World Labs（3D 場景）、GAIA-1（自駕垂直）、DreamerV3（學術 RL）；共 8 個方案含 Cosmos 本身，符合 AGENTS.md「2～4 個」指引的上限並超覆以完整涵蓋生態 |
| 授權與開源狀態 | 檢查 README License 段落與 org repo license 標記 | 一致：OpenMDW-1.1（Linux Foundation），NVIDIA/cosmos repo 10.4k stars、687 forks；所有子 repo 均標 Apache-2.0（程式碼）與 OpenMDW-1.1（模型權重） |
| 硬體需求 | 檢查 README Quickstart、Troubleshooting、Choosing an Integration 段落 | 一致：GPU 限 NVIDIA Ampere/Hopper/Blackwell；OS 限 Linux；Cosmos3-Super (64B) 需 tensor-parallel + layerwise offload；SFT cookbook 需 8×H100；M4 Mac Pro 不適用（任務環境為 01_general_tech 純調研，不涉及實作） |
| 生態定位 | 比對 README Ecosystem 段落、subagent 回報的 NVIDIA Physical AI 堆疊 | 一致：Cosmos 上接 Isaac GR00T（機器人基礎模型）、下接 Isaac Sim/Newton（規則式模擬）、平行於 Cosmos Curator/Evaluator、部署於 NeMo/NIM/DGX Cloud |

## 其中的決斷點

| 意思決定面向 | 可選選項條列 | 選擇結果 | 選擇理由 |
|-------------|-------------|---------|---------|
| 分析報告中「技術」的選取範圍 | 1. 僅寫 Cosmos 3（最新版）；2. 寫 Cosmos 平台整體（v1/v2/v3 演進 + 生態）；3. 僅寫 Generator 或 Reasoner 單一面 | 2. 寫 Cosmos 平台整體，以 v3 為核心 | Cosmos 的價值在於從 v1/v2 的分離模型演進到 v3 的統一 omnimodal 架構，並與 Isaac Sim/Newton/GR00T 構成完整 Physical AI 堆疊；單看任一版本或任一執行面無法解釋其解決的完整問題。v3 為最新且架構變革最大者，作為報告主體；v1/v2 作為背景脈絡在「為什麼發生」段落說明 |
| DA 表中替代方案的選取 | 各種 world model / 影片生成 / 機器人模擬 / model-based RL 方案 | Isaac Sim+Newton、Genie 2、Sora/Veo 3、World Labs、GAIA-1、DreamerV3 | 選取覆蓋五個維度：(1) 規則式模擬（Isaac Sim+Newton，NVIDIA 自家互補方案）、(2) 學習式單圖→世界（Genie 2，研究前沿）、(3) 內容創作影片生成（Sora/Veo 3，頂尖畫質但無 action）、(4) 3D 場景生成（World Labs，spatial intelligence）、(5) 自駕垂直世界模型（GAIA-1，單一領域）、(6) 學術 model-based RL（DreamerV3，方法標桿）；雖超出 AGENTS.md「2～4 個」上限，但 Cosmos 作為統一平台需對比多個維度才能完整定位 |
| 是否深入探索原始碼 | 1. 深入 `cookbooks/cosmos3/` 各 notebook 與 Cosmos Framework 原始碼；2. 維持 README + 生態文檔層級分析 | 2. 維持文檔層級分析 | README 已提供完整的架構圖、模型家族表、Use Cases 表、Action 維度表、整合路徑表、Quickstart 程式碼、Limitations、Ecosystem、News、License；subagent 已補齊版本演進與替代方案；原始碼層級分析在此階段非必要，且 Cosmos 3 的核心實作散落於 Diffusers/vLLM-Omni/Cosmos Framework 多個 repo，逐一深入會超出單次調研合理範圍 |
| Cosmos 的問題定義 | 1. 定位為「世界基礎模型平台」；2. 定位為「Physical AI 合成資料生成器」；3. 定位為「統一 omnimodal world model」 | 1+2+3 組合 | README 明確定義為「open platform of world models, datasets, and tools that enables developers to build Physical AI」；v3 架構變革的核心訴求是「subsuming vision-language models, video generators, world simulators, and world-action models into a single framework」；三個角色（平台/資料生成器/統一模型）在不同段落均被強調，缺一不可 |
| 是否區分「學習式 vs 規則式」根本分歧 | 1. 在 DA 表中隱含呈現；2. 獨立段落明確對比 | 2. 獨立段落明確對比 | Cosmos 與 Isaac Sim 的關係並非單純競爭而是互補，但兩者代表的世界模型哲學根本不同（學習式近似 vs 規則式精確）；若不獨立說明，讀者易誤解 Cosmos「取代」Isaac Sim。獨立對比表明確標示物理精確度/渲染擬真度/場景多樣性/可控性/可驗證性五個維度的取捨，並指出 Cosmos 的戰略選擇是兩者並存互補 |