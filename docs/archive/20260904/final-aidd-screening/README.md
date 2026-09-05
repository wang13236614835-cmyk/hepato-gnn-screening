# 保肝中药成分虚拟筛选 · 完整研究管线（AIDD 课程 8 步 SOP）

**是什么**：从靶点档案到多样性 Top-10 的**全链路真实计算**研究管线——每个数字都由
AutoDock Vina 1.2.7 / RDKit 实际运行产出，固定种子一键复现。

**怎么跑**：

```bash
# 依赖: numpy pandas scikit-learn rdkit meeko matplotlib + AutoDock Vina(放入 docking/vina.exe)
#       mk_prepare_receptor(meeko 自带脚本)
python run_all.py            # 全流程: 受体制备+redock门控+建模+120次真实对接(约40-60分钟)
python run_all.py --model    # 快速模式: 复用对接缓存, 只重跑建模/评分/报告(约1分钟)
```

**结果**: `results/tables/`(排名表) · `results/figures/`(图) · `results/summary.json`(汇总)
**解读**: 见 `REPORT.md` · **全线流程与进度**: 打卡页「🔬 全线流程」标签页

## 管线结构（复旦 MOOC《人工智能药物设计》8 步 SOP + 五级漏斗）

| 步骤 | 实现 | 代码 |
|---|---|---|
| 1 选题与靶点档案（证据四栏） | FXR(1OSH·FEX) + Keap1(4IQK·IQK) 双靶档案 | `s1_target_profile.py` |
| 2 拿结构、查口袋、redock 自检 | 共晶配体盒子+6Å；RMSD<2Å 门控不过不放行 | `s2_prep_redock.py` |
| 3 活性数据清洗建模（基线先行） | scaffold 划分 + ECFP+RF / Desc+LR 双基线 + GNN(MC Dropout) + 适用域 | `s3_model.py` |
| 4 虚拟筛选漏斗 | Lipinski/PAINS 预过滤 → Vina 1.2.7 真实对接 | `s4_dock.py` |
| 5 多目标打分排序 | 三源共识 0.45/0.35/0.20 + 域外降权 | `s5_fuse_select.py` |
| 6 多样性挑选 | ECFP4 Butina 骨架聚类，每簇最优 → 多样性 Top-10 | `s5_fuse_select.py` |
| 7 可得性 | 天然产物以药材来源列标注 | 数据列 |
| 8 报告留档 | `REPORT.md` + `summary.json` 全指标 | `s6_report.py` |

## 数据

- `data/cleaned_compounds.csv`：88 条带标签（HP 正 48 / DC 负 40）；
- `data/screening_pool.csv`：12 条 NV 新分子（萜类/木脂素）；
- `data/smiles_fix.json`：5 条结构按 PubChem 权威记录校准（留档可溯源）；
- 候选池 = HP 活性 48 + NV 12 = 60；DC 负样本用于训练。
