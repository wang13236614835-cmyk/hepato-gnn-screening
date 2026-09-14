# GNN_RESEARCH_PLAN_v2

**更新：2026-09-14｜本计划服从 AIDD 主库 qualification_v1 和 asset_preservation_and_gnn_replan_v1。**

## 研究定位

本仓库的 GNN 代码继续保留，但当前身份是**方法学习、历史复核和未来 benchmark 工作区**，不是独立候选发布链。仓库名暂不修改，以保留 GitHub 链接、组员任务和历史引用。

## 当前不做什么

- 不做 NP54 FASN 排名；NP54 对 canonical 域外，`candidate_release=false`；
- 不把未经 Gate T1 的 GNN 作为 FASN 主模型；
- 不用旧 train/val/test split 证明 scaffold/generalization；
- 不把未知标签当阴性重新训练并发布；
- 不把旧 Top-10、黄芩苷居首、docking ranking 或软件 AUC 写成当前候选结论；
- 不为了让 GNN 赢过 Ridge 而调参、改 split 或隐藏阴性结果。

## 当前做什么

### Phase 1：维护并验证传统 baseline（当前）

- 保留 Ridge/RF/XGBoost/均值 baseline 的代码和输出；
- 复现主库 qualification_v1 的同折 benchmark；
- 记录 seed、输入 hash、指标、失败和拒判；
- 对旧 numpy GCN 做教学级梯度、传播和 MC-dropout 复核。

### Phase 2：等待 FASN Gate T1

- 由 AIDD 主库组装多 assay 共享分子对；
- 本仓库不自行复制一份科学状态；
- 只有主库将 T1 数据冻结并发布 manifest 后，才接受新 benchmark 输入。

### Phase 3：T1 通过后比较模型

固定数据、scaffold split、external split、metric、seed、preprocessing；比较 Ridge/XGB/GNN。GNN 只有在严格 external/scaffold 下稳定增益，才进入 enable gate 复审。

### Phase 4：若无增益

GNN 保留为学习/方法比较和负结果资产，不强行进入论文主结论，不删除代码或历史 artifact。

## 资格门

| 门 | 条件 | 当前 |
|---|---|---|
| 数据身份 | assay-level provenance、统一 endpoint、人工结构核验 | 未完全满足 |
| split | scaffold-disjoint + 无结构重复/系列泄漏 | 新 FASN benchmark 满足；旧 split 不满足 |
| baseline | Ridge/XGB/RF/均值均报告 | 满足 |
| GNN 增益 | 多 seed、外部、AD/UQ 均不低于 baseline | 当前不满足 |
| release | 主库 G0–G4 必要门通过 | 关闭 |

## 产出纪律

每次实验必须生成 run manifest、输入 hash、模型参数、seed、训练/测试边界、预测文件和 QC。历史文件只追加状态，不覆盖。