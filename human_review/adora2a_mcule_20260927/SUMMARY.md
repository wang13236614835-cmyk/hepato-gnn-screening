# 2026-09-27 ADORA2A / Mcule 实际结果冻结包

## 定位

本包是 MASH-AIDD 三库闭环中的 **ADORA2A/Mcule exploratory branch** 实际结果冻结。它不会覆盖 AIDD 主库既有 Moracin N / FASN 主线，也不把软件验证、计算筛选或供应商目录当作湿实验阳性结果。

## 已冻结的五个 Mcule 计算候选

1. MCULE-5126266491 — WMVAAXSVXVZFGZ-UHFFFAOYSA-N
2. MCULE-1345325285 — IKHXIEZYNRKZEG-UHFFFAOYSA-N
3. MCULE-2952154734 — ALZDBLPPXBTCDL-UHFFFAOYSA-N
4. MCULE-1403143859 — SSLZNLJDMTXTMG-UHFFFAOYSA-N
5. MCULE-5892165876 — RBZMLMOEKVATPN-UHFFFAOYSA-N

身份 gate = PASS；当前供应/批次 gate = BLOCKED；W0 ready_count = 0。
五个候选都仍是 **synthetic-library computational priorities**，没有一个被证明为已上市药、中药成分或实验确认的 ADORA2A ligand。

## 反向药理

- 候选2：STRONG_RELATED_A2A_MEDCHEM_SERIES；与 3,5-dimethylpyrazolyl-pyrimidine A2A antagonist 药化系列高度相关，但不是已知系列化合物的精确同一物。
- 候选4/5：落在 pyrimidine-5-carbonitrile adenosine receptor ligand / A2A medicinal-chemistry space。
- 候选1：UNRESOLVED。
- 候选3：弱相关 pyrazine adenosine-antagonist prior-art space，具名系列未闭环。
- 临床药理锚点：Istradefylline = 已上市 A2A antagonist，但无 MASH 适应证。
- 未发现需要或能够合理映射到“生物药”的路径。

## MASH / ADORA2A 方向

ADORA2A 对 MASH/NASH 是 **PRECLINICAL_SUPPORTED，但治疗方向 UNRESOLVED_CONTEXT_DEPENDENT**。不同细胞、阶段和模型中 agonism / antagonism 证据并不统一，因此任何单一方向都不得被提前写成全局正确机制。

## 天然产物 / 中药 / 老药池

- 冻结 botanical pool：37 个。
- 保留：37 / 37；因“研究饱和”淘汰 = 0。
- 高成熟成分继续保留为 REPURPOSING_NEW_USE / NEW_MECHANISM_HYPOTHESIS。
- 欠开发 follow-up：physcion、dihydrotanshinone、tangeretin、chrysophanol、dihydromyricetin。
- 具名候选池并不证明这些成分通过 ADORA2A 治疗 MASH；成熟度检索只作 triage，不作活性证据。

## 当前最有价值的可购入科研面板

推荐 8 项：
1. ZM241385 — A2A antagonist 对照
2. CGS21680 — A2A agonist 对照
3. Nobiletin — 天然产物，已有直接 A2A binding + 肝/NASH 证据
4. Tangeretin — 天然产物，已有直接 A2A binding + NAFLD/NASH 证据
5. Salidroside — 成熟成分新机制支线
6. Dihydrotanshinone I — 欠开发中药单体
7. Physcion — 欠开发蒽醌单体
8. Istradefylline — 已上市 A2A antagonist，老药新用参照

目录/现货页 != W0 放行；正式实验仍要求 exact ordered structure、lot、lot-specific CoA、purity、identity evidence。

## G7 / 湿实验实际状态

- G7 只认冻结历史五候选；后验 sensitivity candidate MCULE-7744694197 不得替换正式五候选。
- W0 material release = BLOCKED，ready_count = 0。
- 实际湿实验数据 = 0。
- 尚未执行：直接 ADORA2A binding、cAMP agonist/antagonist、A1/A2B/A3 selectivity、细胞毒性、HSC、hepatocyte、macrophage/Kupffer、rescue/knockdown。
- 当前真实下一步是：落实湿实验执行方/合作课题组 → 采购科研级化合物 → W0 物料放行 → W1/W2/W3/W4。

## 计算/软件验证状态

Workbench 当前完整回归：**133 / 133 passed**。
软件回归通过不构成科学放行；candidate_release 仍为 false。

## 三库同步角色

- AIDD 主库：正式科研事实与分支状态冻结。
- MASH-AIDD Workbench：保留完整执行工件、evidence index、G7/W0、采购与审计链。
- hepato-gnn-screening：只接收 HUMAN_REVIEW_REQUIRED / 人工复核任务，不产生第二套正式候选结论。
