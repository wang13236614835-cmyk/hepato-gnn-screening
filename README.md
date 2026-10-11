# hepato-gnn-screening：GNN 方法学习与历史复核工作区

**当前角色（2026-09-14）**：GNN 方法学习 + 历史模型复核 + 组员任务工作区。AIDD 正式科研结论唯一入口是 `D:/zcode-workspace/aidd-repo-work`，Workbench 只读镜像主库状态。本仓库不产生第二套候选发布链。

> **重要状态**：GNN 当前为 `gated/closed`，不是当前正式主模型。它在 AIDD 主库冻结的 96 分子 FASN canonical assay 上首次同折 benchmark 未优于经典 baseline：Ridge R² 中位 0.732、XGB 0.594、RF 0.217、GCN 0.078、GINE −0.040。不要把旧 Top-10、黄芩苷居首、旧 docking 排名或旧 AUC 当作当前 MASH 候选结论。

## 当前入口

- [RESEARCH_STATE.md](RESEARCH_STATE.md)：本仓库状态；权威科研状态仍在 AIDD 主库 `00-当前研究/qualification_v1/RESEARCH_STATE.md`；
- [STATUS.json](STATUS.json)：机器可读状态；
- [GNN_RESEARCH_PLAN_v2.md](GNN_RESEARCH_PLAN_v2.md)：当前计划；
- [GNN仓库审计.md](GNN仓库审计.md)：本轮定位裁决；
- [GNN是否需要大改_裁决.md](GNN是否需要大改_裁决.md)：小修即可，不改仓库名；
- [GNN数据与模型状态表.csv](GNN数据与模型状态表.csv)：旧代码/标签/split/结果的保留与资格状态；
- [docs/00_environment.md](docs/00_environment.md)：统一环境策略与跨平台安装说明；
- AIDD 主库资产登记：`D:/zcode-workspace/aidd-repo-work/00-当前研究/asset_preservation_and_gnn_replan_v1/MASTER_ASSET_REGISTRY.csv`。

## 环境快速开始

**推荐 Python 3.11，完整栈兼容目标为 Python 3.10–3.12。** 环境按三层拆分，避免 Windows/Linux、CPU/GPU 或 CUDA 差异互相影响：

```bash
# 所有人：基础层
python -m pip install -r requirements.txt
python tools/check_env.py

# 需要 RDKit / pandas / sklearn 等
python -m pip install -r requirements-science.txt

# 需要 PyG：先按本机 CPU/CUDA 安装 PyTorch，再执行
python -m pip install -r requirements-ml.txt
```

`requirements-validated.txt` 是历史精确复现快照，不是默认安装入口；CUDA 不写死在通用 requirements 中。

## 现在做什么

1. 维护可运行的 GNN/基线代码和学习材料；
2. 复核历史数据、结构、split、日志和模型输出；
3. 等待主库 FASN Gate T1（多 assay 对齐）后再决定是否开展下一轮严格 benchmark；
4. 记录 GNN 的正负结果、UQ、split 和数据限制，不强行让 GNN 赢过 Ridge。

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
