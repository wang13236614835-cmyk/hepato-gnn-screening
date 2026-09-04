# 保肝中药成分虚拟筛选 · 最终融合版（AIDD 课程标准流程对齐）

**是什么**：把三条研究线（GNN 主线 / 真实 Vina 对接线 / 课程 8 步 SOP）融合后的
**最终、完整、最简**研究包——从靶点档案到多样性 Top-10，全链路真实计算、零演示分、一键复现。

**怎么跑**：

```bash
# 依赖: numpy pandas scikit-learn rdkit meeko matplotlib + AutoDock Vina(包内自带 vina.exe)
#       mk_prepare_receptor(meeko 自带脚本)
python run_all.py            # 全流程: 受体制备+redock门控+建模+120次真实对接(10-20分钟)
python run_all.py --model    # 快速模式: 复用缓存对接结果, 只重跑建模/评分/报告(约1分钟)
```

**结果**: `results/tables/`(排名表) · `results/figures/`(图) · `results/summary.json`(汇总)
**解读**: 见 `REPORT.md`

## 与 AIDD 课程标准流程的对照（复旦 MOOC《人工智能药物设计》第 11 章 8 步 SOP）

| 课程步骤 | 本包实现 | 代码 |
|---|---|---|
| 1 选题与靶点档案（证据四栏） | FXR(1OSH)+Keap1(4IQK) 双靶档案 | `s1_target_profile.py` |
| 2 拿结构、查口袋、redock 自检 | 共晶配体盒子+6Å；redock RMSD<2Å 门控（不过不放行） | `s2_prep_redock.py` |
| 3 活性数据清洗建模（QSAR 基线） | scaffold 划分 + ECFP+RF / Desc+LR 双基线 + GNN(MC Dropout) + 适用域 | `s3_model.py` |
| 4 虚拟筛选（漏斗） | Lipinski/PAINS 预过滤 → 真实 Vina 1.2.7 精对接 | `s4_dock.py` |
| 5 多目标打分排序 | 三源共识 0.45/0.35/0.20 + 域外降权 | `s5_fuse_select.py` |
| 6 目检+多样性挑选 | ECFP4 Butina 骨架聚类，每簇最优 → 多样性 Top-10 | `s5_fuse_select.py` |
| 7 逆合成/可购性 | 天然产物以药材来源列替代（逆合成不适用，报告说明） | 数据列 |
| 8 报告（数据-方法-指标-局限） | `REPORT.md` + `results/summary.json` 全指标留档 | `s6_report.py` |

## 相比原三线的取舍

- **取**：scaffold 级划分、GNN+MC Dropout 不确定性、杠杆值适用域、三源融合评分公式（主线精华）；
  真实 Vina 对接与 redock 门控方法（对接线验证过的工程实践）。
- **舍**：`mock_docking` 演示分（不符合课程标准，全部替换为真实 Vina 分）；
  Keap1 结构 2FLU（肽复合物无小分子配体、无法 redock，换 4IQK）；管理性文档不随包。
- **补**：redock RMSD 门控、PAINS 预警、ECFP+RF 课程基线、温度校准评估、骨架聚类多样性挑选、
  5 条无效 SMILES 的 PubChem 权威结构修复（`data/smiles_fix.json`）。

## 数据

- `data/cleaned_compounds.csv`：88 条带标签（HP 正 48 / DC 负 40），来自主线已清洗数据；
- `data/screening_pool.csv`：12 条 NV 新分子（萜类/木脂素）；
- 候选池 = HP 活性 48 + NV 12 = 60；DC 负样本仅用于训练。
