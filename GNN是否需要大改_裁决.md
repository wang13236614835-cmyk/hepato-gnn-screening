# GNN 是否需要大改：裁决

**唯一裁决：小修即可。**

## 依据

1. 代码可导入，旧 numpy GCN 是真实消息传递/反向传播/Adam/MC-dropout 实现；
2. 数据、split、预测、日志、报告和成员工作台均可定位并保留；
3. 新 PyG GCN/GINE benchmark 已在 AIDD 主库真实完成，结果可读并且与 Ridge 同折断言一致；
4. 主要问题是研究定位和状态边界，而不是架构已经阻碍复现；
5. 现有 `docs/REPO_SCOPE.md`、`docs/PROJECT_STATUS.md` 已有较多审计边界，所需修改是增量同步而不是目录搬迁。

## 本轮允许的小修

- README 当前入口改为“方法学习/历史复核/组员工作区”，移除当前主任务中的候选排名承诺；
- 增加 `RESEARCH_STATE.md`、`STATUS.json`、`GNN_RESEARCH_PLAN_v2.md`、`GNN数据与模型状态表.csv`；
- 在文档中明确旧 split/标签/Top-10/docking 的状态；
- 增加指向 AIDD 主库 registry 和 qualification_v1 的交接入口；
- 保留原目录和公共 API，不搬迁 `src/`、`data/`、`results/`、个人工作台。

## 不做中等/大改的理由

- 没有证据表明目录混乱已经阻碍复现；
- 全量迁移会增加 path、Git 历史、成员工作台和旧报告链接的破坏面；
- 用户要求保留优先；
- GNN 是否启用由主库门控决定，而不是靠仓库重命名或技术栈重构解决。

## 未来触发中等重构的条件

仅当以下事实出现，才重新评估中等重构：旧/新模型无法由 manifest 区分；同一文件路径同时承载历史和当前训练输入；测试无法建立；或 Gate T1 通过后需要长期维护多个正式 benchmark。当前均未满足。
