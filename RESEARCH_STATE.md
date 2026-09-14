# GNN 库当前研究状态

**更新：2026-09-14｜权威上游：`D:\zcode-workspace\aidd-repo-work\00-当前研究\qualification_v1\` 与 `asset_preservation_and_gnn_replan_v1/`。**

## 当前角色

本仓库继续保留原名 `hepato-gnn-screening`，本轮裁决为：**GNN 方法学习 + 历史模型复核 + 组员任务工作区**。不改远程仓库名，不拆仓库，不把本仓库升级为第二个科研主库。

## 当前运行状态

- `gnn_enable_gate`: **closed / gated**；
- `project_stage`: `pipeline_revalidation`；
- `candidate_release`: `false`（以 AIDD 主库为准）；
- `FASN`: canonical assay local model 已有资格，但 external generalization failed/limited，Gate T1 pending；
- `GNN`: 在冻结 96 分子 canonical assay 上首次同折 benchmark 未优于 Ridge/XGB；GCN R² 中位 0.078，GINE −0.040，Ridge 0.732；
- `Moracin N`: experimental_start_qualified，biological_validation not_executed；不在本仓库产生候选放行。

## 旧资产状态

| 资产 | 状态 | 允许用途 |
|---|---|---|
| `src/models/gnn.py` numpy GCN | VERIFIED code / HISTORICAL method | 方法学习、梯度/传播教学、旧结果复核 |
| `src/models/dataset.py` | REQUALIFY | 代码学习；元素未知值回退问题待修，不能自动升级数据资格 |
| `data/splits/` | HISTORICAL / INVALID_FOR_GENERALIZATION | 复现旧实验；禁止作为当前泛化证据 |
| `results/` 旧 Top-10/预测/日志 | HISTORICAL | 错误分析、教学、可复现历史；禁止当前候选榜 |
| `data/curation/` 结构修订 | NEEDS_HUMAN_CHECK | 组员逐条身份核验；未签名前不能进入正式训练 |
| `final-aidd-screening/` | HISTORICAL pipeline | 课程/软件流程复盘；不代表当前 MASH 候选发现 |

## 本库不负责

- 不负责维护新的正式 MASH 候选榜；
- 不把旧 Top-10、黄芩苷居首、旧 docking ranking 写成当前结论；
- 不在 Gate T1 之前把 GNN 作为 FASN 主模型；
- 不将软件测试通过、旧标签分类性能或 docking 分数等同于药效/机制证据。

## 下一步唯一主计算

AIDD 主库先完成 FASN Gate T1：多 assay 共享分子对、assay 间对齐、归一化训练集和分层验证。T1 通过后，才在本仓库或由主库调用的独立 benchmark 中比较 Ridge/XGB/GNN；T1 失败则 GNN 只保留学习/方法比较状态。
