# hepato-gnn-screening v2 → v3 人工工作区迁移报告

**日期：2026-09-27｜角色：真人核验工作区 + 方法学习/历史复核**

## 当前默认任务源

从 2026-09-27 起，本库 CURRENT 任务源为：

`human_review/adora2a_mcule_20260927/HUMAN_REVIEW_QUEUE.csv`

共 7 条当前核验/执行任务，真人完成数仍为 0。

## v2 降级

以下内容继续保留，但不再作为默认当前进度：
- research_chain_v2_20260921
- Phase 2B 49/132 条任务
- W3-W16 旧周计划
- FASN T1 / GNN benchmark
- Moracin N 旧实验前任务

状态统一为 HISTORICAL_BACKLOG_NOT_DEFAULT / HISTORICAL_BASELINE。

## 五人当前分工

- 王启龙：湿实验合作方/执行方、采购/W0、人工结果总审。
- 宁显泷：binding/cAMP 与 W3/W4 统计设计。
- 衣思淼：五 MCULE 身份/来源、天然来源、到货后 lot/CoA。
- 代维斯丹：候选 3 立体化学、候选 2/4/5 药化系列/prior-art。
- 王散曼：Nobiletin/Tangeretin 直接 A2A 原始论文与肝病证据分离核验。

5 份工作台 Markdown 与 5 个 HTML 打卡页均加入 research_chain_v3 CURRENT 层；旧周卡仅保留历史。

## 防回退

`tools/sync_v2_to_pages.py` 默认拒绝运行。只有显式添加 `--legacy-v2` 才允许历史重放，避免将成员页面重新覆盖成 v2。

## 科学边界

- GNN 库不产生第二套正式候选结论。
- candidate_release=false。
- W0 ready_count=0。
- wetlab=NOT_EXECUTED。
- direct candidate ADORA2A activity=UNVERIFIED。
- 人工核验只能由真人产生 VERIFIED / CORRECTED / REJECTED。

## 验收

- 状态.json current=v3：PASS。
- v2/Phase2B 降级：PASS。
- 5/5 成员 Markdown v3 CURRENT：PASS。
- 5/5 HTML v3 banner：PASS。
- v3 导航与旧导航归档：PASS。
- legacy v2 生成器默认保护：PASS。
