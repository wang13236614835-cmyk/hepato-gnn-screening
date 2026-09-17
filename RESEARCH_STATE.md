# GNN 库当前研究状态

**更新：2026-09-17｜权威上游：`D:\zcode-workspace\aidd-repo-work\00-当前研究\qualification_v1\` 与 `GLOBAL_RESEARCH_TASK_MAP.json`。**

## v0.6 人工核验闭环角色（2026-09-17 新增）

三库分工冻结为：

- **AIDD** = 正式科研事实唯一源（Single Source of Scientific Truth）；
- **Workbench**（`D:\aidd destoop`）= AI 探索 + 人工核验任务生成 + 人工结果严格导入 + 正式重算 + STALE 传播 + G0-G7 Gate 展示；
- **GNN（本库）** = **真人核验工作区** + 方法学习 / 历史模型复核 + 组员任务工作区。

本库在 v0.6 闭环中的位置：

```
Workbench 生成 human_review_task.json（compound identity 等对象）
→ 组员在本库 human_review/ 工作区核对原始来源
→ 填写 human_review_result（VERIFIED / CORRECTED / REJECTED）
→ 回传 Workbench 严格导入（校验 task_id + upstream_hash + reviewer）
→ Workbench 保留 AI 原值、替换正式值并自动 STALE 下游
→ 更新 G0-G7 Gate 状态
```

本库**不**生成正式科研结论，**不**单独发布候选榜，**不**把软件测试通过当作科研验证通过。

## 当前角色

本仓库继续保留原名 `hepato-gnn-screening`，本轮裁决为：**真人核验工作区 + GNN 方法学习 + 历史模型复核 + 组员任务工作区**。不改远程仓库名，不拆仓库，不把本仓库升级为第二个科研主库。

## 当前运行状态

- `gnn_enable_gate`: **closed / gated**；
- `project_stage`: `fifth_round_direction_exploration`；
- `current_stage`: 第五轮方向探索（FASN Gate T1 已裁决）；
- `candidate_release`: `false`（以 AIDD 主库为准）；
- `FASN`: Gate T1 **FAIL**；canonical assay local 方法学线保留，external generalization failed/limited；
- `GNN`: 在冻结 96 分子 canonical assay 上首次同折 benchmark 未优于 Ridge/XGB；GCN R² 中位 0.078，GINE −0.040，Ridge 0.732；
- `Moracin N`: experimental_start_qualified，biological_validation not_executed；不在本仓库产生候选放行。

## 旧资产状态

| 资产 | 状态 | 允许用途 |
|---|---|---|
| `src/models/gnn.py` numpy GCN | VERIFIED code / HISTORICAL method | 方法学习、梯度/传播教学、旧结果复核 |
| `src/models/dataset.py` | REQUALIFY（2026-09-17 未知元素修复：默认显式拒绝，可选独立 UNK 14 维；历史 13 维逐位不变；见 `tests/test_dataset_unknown_element.py`） | 代码学习；历史数据复现不受影响 |
| `data/splits/` | HISTORICAL / INVALID_FOR_GENERALIZATION | 复现旧实验；禁止作为当前泛化证据 |
| `results/` 旧 Top-10/预测/日志 | HISTORICAL | 错误分析、教学、可复现历史；禁止当前候选榜 |
| `data/curation/` 结构修订 | NEEDS_HUMAN_CHECK | 组员逐条身份核验；未签名前不能进入正式训练 |
| `final-aidd-screening/` | HISTORICAL pipeline | 课程/软件流程复盘；不代表当前 MASH 候选发现 |

## 本库不负责

- 不负责维护新的正式 MASH 候选榜；
- 不把旧 Top-10、黄芩苷居首、旧 docking ranking 写成当前结论；
- 不在 Gate T1 之前把 GNN 作为 FASN 主模型；
- 不将软件测试通过、旧标签分类性能或 docking 分数等同于药效/机制证据。

## 第五轮方向探索状态

- **Primary**：Moracin N–NRF2/ferroptosis 肝细胞机制验证（实验启动资格，尚未执行，不是候选放行）；
- **Secondary**：FXR/Formononetin 依赖性桥接 + Biochanin A QC；
- **Reserve**：THRβ reporter、Isorhamnetin、FASN 直接酶实验、SCD1/DGAT2 重资格化；
- **Rejected（当前用途）**：NP54 FASN 定量榜、docking ranking、旧 GNN/CW-BCS/TOPSIS 正向结论、ACC1/ACC2 合并模型、3′-methoxydaidzein 当前创新候选。

## 下一步唯一主计算

FASN 只有在获得第二个满足核心元数据约束的共享 assay pair 后才重开 T1；否则维持方法学/数据审计线。GNN 不因 T1 FAIL 开放，继续保留为学习和未来严格 benchmark 资产。
