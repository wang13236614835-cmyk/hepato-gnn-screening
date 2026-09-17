# hepato-gnn-screening：真人核验工作区 + GNN 方法学习与历史复核

**当前角色（2026-09-17，v0.6）**：**真人核验工作区** + GNN 方法学习 + 历史模型复核 + 组员任务工作区。AIDD 正式科研结论唯一入口是 `D:/zcode-workspace/aidd-repo-work`；Workbench（`D:/aidd destoop`）负责 AI 探索、人工核验任务生成、人工结果严格导入、正式重算与 STALE 传播；本仓库是组员做真人核验、学习和历史复核的地方，不产生第二套候选发布链。当前 FASN Gate T1=FAIL；Phase 2B 真人核验（P0 8 个压缩单元 / 49 条原始任务）尚未开始，G0-G7 Gate 状态以 AIDD 主库与 Workbench 只读投影为准。

> **重要状态**：GNN 当前为 `gated/closed`，不是当前正式主模型。它在 AIDD 主库冻结的 96 分子 FASN canonical assay 上首次同折 benchmark 未优于经典 baseline：Ridge R² 中位 0.732、XGB 0.594、RF 0.217、GCN 0.078、GINE −0.040。不要把旧 Top-10、黄芩苷居首、旧 docking 排名或旧 AUC 当作当前 MASH 候选结论。

## 当前入口

- [RESEARCH_STATE.md](RESEARCH_STATE.md)：本仓库状态；权威科研状态仍在 AIDD 主库 `00-当前研究/qualification_v1/RESEARCH_STATE.md`；
- [STATUS.json](STATUS.json)：机器可读状态；
- [GNN_RESEARCH_PLAN_v2.md](GNN_RESEARCH_PLAN_v2.md)：当前计划；
- [GNN仓库审计.md](GNN仓库审计.md)：本轮定位裁决；
- [GNN是否需要大改_裁决.md](GNN是否需要大改_裁决.md)：小修即可，不改仓库名；
- [GNN数据与模型状态表.csv](GNN数据与模型状态表.csv)：旧代码/标签/split/结果的保留与资格状态；
- AIDD 主库资产登记：`D:/zcode-workspace/aidd-repo-work/00-当前研究/asset_preservation_and_gnn_replan_v1/MASTER_ASSET_REGISTRY.csv`；
- [GLOBAL_RESEARCH_TASK_MAP.json](D:/zcode-workspace/aidd-repo-work/00-当前研究/GLOBAL_RESEARCH_TASK_MAP.json)：按 Gate 连接 Workbench 动作、真人核验、patch、manifest 和验收条件；AIDD 是权威源，本库只提交学习/核验产物，不生成第二套正式科研状态或候选发布链。

## 现在做什么

1. **真人核验（v0.6 主线）**：在 `human_review/` 工作区完成 Phase 2B P0/P1 人工核验任务（8 个 P0 压缩单元 / 49 条原始任务；16 个 P1 / 132 条），按 `VERIFIED / CORRECTED / REJECTED` 回填，交 Workbench 严格导入；
2. 维护可运行的 GNN/基线代码和学习材料；
3. 复核历史数据、结构、split、日志和模型输出；
4. T1 已裁决 FAIL；只有获得第二个满足核心元数据约束的共享 assay pair 后才重开 FASN T1；
5. 记录 GNN 的正负结果、UQ、split 和数据限制，不强行让 GNN 赢过 Ridge。

> 2026-09-17 修复：`src/models/dataset.py` 未知元素不再静默按碳处理（默认显式报错，可选独立 UNK 14 维；历史 13 维数据逐位不变，永久测试见 `tests/test_dataset_unknown_element.py`）。

## 现在不做什么

- 不做 NP54 FASN 排名（天然产物对 canonical 域外）；
- 不用旧 split 证明泛化；
- 不把未知标签当阴性后发布模型；
- 不把 docking score 用于候选或 selectivity 排序；
- 不产生“正式 Top-10”或“已验证候选”。

## 保留哪些历史内容

`data/`、`src/`、`results/`、`final-aidd-screening/`、`reports/`、旧 split、旧标签、日志、预测和成员工作台全部保留。它们分别用于历史复现、错误分析、方法学习、软件核验和课程任务；具体状态见 `GNN数据与模型状态表.csv` 和 `docs/PROJECT_STATUS.md`。

## 旧一键流程边界

```bash
python run_all.py                 # 默认：只显示当前未放行状态，不改写历史结果
python run_all.py --legacy-demo   # 可选：旧教学流程复现，会写入旧 results/，仅作历史复盘
```

旧流程复现不代表当前科研验证通过，也不代表可生成候选发布榜。运行前应确认工作树和旧 results 已有备份；正式 FASN 资格结果以 AIDD 主库 qualification_v1 为准。

## 目录说明

- `data/`：历史原始/处理数据、旧 split、结构修订输入；
- `src/`：图解析、旧 numpy GCN、基线、对接和工程代码；
- `results/`：历史预测、排名、对接和日志；
- `final-aidd-screening/`：历史课程 SOP/完整管线复盘；
- `docs/`：任务、核验、历史状态和人工审核规则；
- `王启龙/` 等：组员工作台，不代替科研资格签核。
