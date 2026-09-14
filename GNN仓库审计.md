# GNN 仓库审计

**日期：2026-09-14｜结论：小修即可；不改仓库名；当前状态 gated。**

## 一、定位问题

旧 README 的当前入口仍写成“从中药成分筛选保肝候选并产出候选排名总表”，并把“黄芩苷居首/双靶共识排名/Top-10”写在当前流程中。这与当前主库状态冲突：FASN canonical 外部泛化失败、NP54 全部 OOD、GNN enable gate closed、docking 不得承担活性排序、`candidate_release=false`。

`docs/REPO_SCOPE.md` 和 `docs/PROJECT_STATUS.md` 已经较谨慎，明确旧 Top-10 不能直接作为药效结论、旧标签待核验、AIDD 主线在主库；所以不是架构性失效，而是根 README 和若干入口文案需要同步。

## 二、代码审计

- `src/models/gnn.py`：真实 2 层 numpy GCN，使用归一化邻接、均值池化、dropout、手写 Adam 和反向传播；不是形式上的“GNN”。保留为 VERIFIED code / HISTORICAL method。
- `src/models/dataset.py`：真实 SMILES→graph 加载；节点特征 13 维，但未知元素回退到元素槽位 0（碳槽位），需后续修正；因此代码可学、数据资格不能直接升格。
- 旧 `data/splits/`：可加载、无相同 SMILES，但本轮实测 train/test 共享 2 个 Murcko scaffold，不能支持 scaffold/generalization 主张。
- 旧 loss/label：weighted BCE 分类，旧标签存在“未知当阴性/混合终点”问题；标签层 REJECTED，不进入当前正式训练。
- `results/`、`final-aidd-screening/`：文件和日志可保留，角色降为历史流程/教学/错误分析；不作为当前候选榜。

## 三、数据/结构审计

`docs/PROJECT_STATUS.md` 已记录：100 条结构中 52 条连接关系不符、43 条分子式不符、4 条立体化学不符；所有结构修订仍需逐条人工审核。不能让 Agent 或批处理自动签名为 VERIFIED。

## 四、与主库关系

- AIDD 主库：唯一正式状态、证据矩阵、候选发布策略和 Gate T1；
- GNN 库：方法学习、历史复核、成员工作区；
- Workbench：主库只读镜像；
- 本库不复制主库的 candidate ranking 或新的科研事实。

## 五、最终裁决

仓库**不需要大改**。做小修：README/状态/计划/状态表/交接入口同步；保持旧目录、Git 历史、API、个人工作台、数据和结果。未来若 Gate T1 通过且出现多个正式 benchmark，再评估中等重构。
