# results/docking/real/ — 真实 Vina 对接数据(144 次)

> 2026-09-03 完成,管线与 WP2 计划一致。暑假演示分(`../docking_scores.csv`)保持原位供 9/20 前复核;
真实分数在本目录,60 候选 × 1OSH/2FLU 批量完成后换入总表、重算排名 v2。

## 文件

| 文件 | 内容 | 规模 |
|---|---|---|
| `docking_real_4targets_16ligands.csv` | THRβ(6KKB)/FXR(6HL1)/PPARα(6KAX)/PPARδ(5U3Q) × 16 分子(12 天然成分 + 4 药物参考) | 64 次 |
| `docking_real_ppar_prior40.csv` | PPARα/PPARδ × MASH 课题 131 成分库 CW-BCS 前 40(含本项目中期候选同族的甘草/丹参/苦参成分) | 80 次 |

## 对接参数(可复现)

- 引擎:AutoDock Vina 1.2.7 官方 Windows 版(与本组 docs/00_environment.md 计划的服务器版同源)
- 受体:纯 Python PDB→PDBQT(去水/去共晶配体/去去垢剂;无氢刚性;元素映射 C/NA/OA/SA)
- 配体:RDKit ETKDGv3 + UFF + meeko(与 WP2 步骤 2 一致)
- 盒子:共晶配体包围盒 + 6 Å 外扩(与 src/docking/grid_box.py 同逻辑)
- exhaustiveness=8、cpu=4、seed=42;每靶点独立输出目录
- 阳性对照:resmetirom@THRβ 第 3/16、UDCA@FXR 第 3/16(4/6 通过)

## 与本项目的关系

1. **性质说明**:本数据由另建的同类管线产生(未使用本项目 src/ 任何代码),仅证明流程可行并提供参数/坑位参考;本项目 WP2 仍按原步骤用自己的脚本执行。
2. **数据可参考**:前 40 成分库中含甘草、丹参、苦参成分(与本组 NV/HP 池同药材来源),PPARα/δ 打分可作为保肝课题扩展靶点的先验参考;但靶点体系不同(MASH 核受体四靶 vs 本组 FXR/Keap1),分数不可直接并入本组排名。
3. **已知坑位**(实测,WP2 执行时直接规避):PDBQT 原子类型必须写入 PDB 77–78 列;共晶配体需 HETNAM 核验(5U3Q 的 B7G 是去垢剂);Vina 日志为本地编码需 errors='ignore';网络代理对大文件下载需断点续传。
