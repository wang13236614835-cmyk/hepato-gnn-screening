# WP2 真实分子对接（第3–6周）

> **进度(2026-09-03)**:对接管线已验证——Vina 1.2.7 真实对接 144 次(四步骤全跑通,
> 阳性对照 4/6),参数与坑位见 `results/docking/real/README.md`,任务拆分见
> `reports/真实对接与统一筛选报告.md`。剩余:60 候选 × 1OSH/2FLU ≈ 30 分钟机时;
> 服务器加氢受体与本机无氢简化版各跑一份做对照。

主责：代维斯丹（验证） | 核验人：宁显泷
前置条件：WP1 完成；服务器账号；Vina/ADFR 已按 docs/00_environment.md §2 安装

## 目标

用 AutoDock Vina 真实对接替换演示分（`results/docking/docking_scores.csv`
的 mode 列从 mock_local 变为 vina），重算排名 v2。

## 步骤

1. 受体准备（一次性）：

```bash
# 从 RCSB 下载 1OSH / 2FLU，去水加氢
prepare_receptor4.py -r 1OSH_fxr.pdb   -o fxr.pdbqt   -A hydrogens
prepare_receptor4.py -r 2FLU_keap1.pdb -o keap1.pdbqt -A hydrogens
```

2. 配体准备：60候选（HP活性+NV池）从 fullpool SMILES 批量转 pdbqt
   （RDKit 生成3D构象 → obabel 加氢 → prepare_ligand4）；
3. 批量对接（盒子参数以 src/docking/grid_box.py 为准，勿手改）：

```bash
bash src/docking/run_vina.sh <ligand_pdbqt目录> results/docking/vina_out/
```

4. 汇总：新写 `src/docking/collect_vina_logs.py` 解析 log 的打分列，
   覆盖 docking_scores.csv（保留原演示分列作对照）；
5. 阳性对照有效性检查：水飞蓟宾(FXR)与已知 Keap1 配体回打分；
6. 重跑 `python run_all.py`（fuse 自动读新对接分，产出排名 v2）；
7. 对比 v1/v2 排名变化，写入本文件末尾。

## 期望输出

- docking_scores.csv 更新（mode=vina，两靶点×60候选）；
- 排名 v2 与变化分析；阳性对照回打分记录。

## 验收标准

- [ ] 阳性对照回打分 RMSD<2Å 或打分进前20%（否则检查盒子/质子化）
- [ ] 演示分与真实分的相关性报告（Spearman，预期中低相关——
      这正是替换的意义，如实记录）
- [ ] 排名 v2 中 Top-10 变化逐条有解释
- [ ] 宁显泷复核代码路径与盒子参数未偏离 grid_box.py

## 核验记录

| 日期 | 核验人 | 结果 | 备注 |
|---|---|---|---|
| | | | |
