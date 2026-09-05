# 人工核验复现手册（VERIFY MANUAL）

> 目的：任何成员（或老师）在不了解代码的情况下，按本手册逐步操作，
> 即可核验暑假阶段全部结果的真实性与可复现性。
> 预计耗时：§0–§2 约10分钟（一键复现+数字核验）；§3–§5 约40分钟（逐模块人工核验）。
> 每完成一节，在文末"核验记录表"打勾签名。
> 谁核验哪几节、交付物与时限：见 `docs/VERIFY_TASKS.md`（任务分派表）。

## §0 前置条件（1分钟）

```bash
python --version        # 预期 3.9 及以上
python -c "import numpy; print(numpy.__version__)"   # 预期 1.24 及以上
```

无需 GPU、无需联网、无需安装 RDKit/PyTorch。

## §1 获取仓库并确认完整性

```bash
cd hepato-gnn-screening
git log --oneline        # 预期能看到12次提交
git shortlog -sn HEAD    # 预期5位作者：王启龙4 衣思淼3 宁显泷2 王散曼2 代维斯丹1
```

## §2 一键复现 + 数字核验（核心，约2分钟）

### 2.1 一键复现

```bash
python run_all.py
```

预期控制台输出（关键行，数字必须逐字一致）：

```
[clean] 带标签集: 88 条 (正样本 48 / 负样本 40)；筛选池: 12 条；剔除 0 条
[split] train: 58 条 (正 28)
[split] val: 13 条 (正 8)
[split] test: 17 条 (正 12)
[split] 骨架组总数 53；ACLYCIC(无环)组 1
[baseline] 高斯朴素贝叶斯(描述符): {'AUC': 0.85, 'ACC': 0.706, 'BACC': 0.733, 'F1': 0.762}
[baseline] 逻辑回归(2048bit指纹): {'AUC': 0.967, 'ACC': 0.706, 'BACC': 0.792, 'F1': 0.737}
[gnn] 选定正类损失权重 w_pos=1.25 (验证集F1=0.667)
[gnn] 测试集: {'AUC': 0.967, 'ACC': 0.824, 'BACC': 0.875, 'F1': 0.857, 'ECE': 0.21}；方差-|误差| Spearman rho=0.718
[docking] FXR演示评分均值: 保肝活性分子 -5.46 vs 负参照 -5.05 kcal/mol (差距 0.42)
[ad] h*=0.362；筛选池域外分子 7/12 (58%) 已标记预警
[fuse] 协同评分完成: 60 个候选入库
全流程完成，用时 ...s；结果见 results/
```

### 2.2 确定性核验（结果可重复）

连跑两次，第二次结束后比较：

```bash
python run_all.py > /dev/null 2>&1
find results data/processed data/splits -type f -name "*.csv" | sort | xargs md5sum > h1.txt
python run_all.py > /dev/null 2>&1
find results data/processed data/splits -type f -name "*.csv" | sort | xargs md5sum > h2.txt
diff h1.txt h2.txt && echo 一致   # 预期输出：一致
```

### 2.3 独立数字核验（45项）

```bash
python reports/pdf_build/verify.py
```

预期最后一行：`通过 45 项；不符 0 项`。
该脚本不导入项目任何代码，独立从CSV重算AUC/ρ/对接均值/Top-10等全部被引用数字。

## §3 逐模块人工核验（可选深度核验，每小节约5分钟）

### 3.1 SMILES解析器（宁显泷模块）

```bash
python -c "
import sys; sys.path.insert(0,'src')
from chem.smiles_graph import parse_smiles
for smi in ['CCO','c1ccccc1','O=C1C=C(c2ccc(O)cc2)Oc2cc(O)cc(O)c12','OC[C@H]1O[C@@H](O)[C@H](O)[C@H](O)[C@H]1O','[nH]1cccc1']:
    g = parse_smiles(smi)
    print(smi, '->', 'OK' if g else 'FAIL', g and len(g.atoms))
"
```

预期：5行全 OK，重原子数依次 3（乙醇）/ 6（苯）/ 20（芹菜素C15H10O5）/
12（葡萄糖）/ 5（吡咯）。

### 3.2 描述符（衣思淼模块）

```bash
python -c "
import sys; sys.path.insert(0,'src')
from chem.smiles_graph import parse_smiles
from chem.descriptors import compute_descriptors
g = parse_smiles('O=C1C(O)=C(c2cc(O)c(O)cc2)Oc2cc(O)cc(O)c12')  # 槲皮素
print(compute_descriptors(g))
"
```

预期：MW=302.24（与槲皮素真实分子量302.24一致）、nHBD=5、nHBA=7、
nHeavy=22、nAromSystems=2。核对 docs/01_data_dictionary.md 的口径表。

### 3.3 指纹确定性（代维斯丹模块）

```bash
python -c "
import sys; sys.path.insert(0,'src')
from chem.smiles_graph import parse_smiles
from chem.fingerprints import morgan_fp
a = morgan_fp(parse_smiles('CC(=O)Nc1ccc(O)cc1'))  # 对乙酰氨基酚
b = morgan_fp(parse_smiles('CC(=O)Nc1ccc(O)cc1'))
print('一致' if a==b else '不一致', '置位数', sum(a))
"
```

预期：一致（MD5哈希保证跨平台确定性）。

### 3.4 数据抽查（王散曼+衣思淼模块）

用Excel打开 `data/raw/tcm_seed_compounds.csv`：
1. 行数89（含表头）；HP-xxx 48行、DC-xxx 40行；
2. 抽 HP-015（水飞蓟宾）行：label=1，evidence_level=A；
3. 到 `literature/01_classic_evidence.md` A级表找到水飞蓟宾条目，两边描述对应；
4. 打开 `data/splits/` 三个文件：在 train 里找到"黄芩苷"的 scaffold 值，
   确认 test/val 中无相同 scaffold（骨架不跨集合）。

### 3.5 排名总表（衣思淼+王启龙模块）

打开 `results/rankings/final_ranking.csv`：
1. 61行（含表头），rank 列 1–60 连续无重复；
2. 第1–3行：黄芩苷 / 二氢杨梅素 / 葛根素；
3. 第7行：水飞蓟宾（临床金标准落在前列=体系合理性）；
4. 找 NV-011（奥贝胆酸）：ad_warning=域外、pred_mean≈0.26；
5. 任选一行手工验算融合公式：
   final = 0.45×pred_mean×(0.5+0.5×confidence) + 0.35×(1-dock名次比例) + 0.20×(1-0.25×违规数)，
   与 final_score 列在±0.002内一致（第1行黄芩苷应≈0.9291）。

### 3.6 结果图（王启龙+代维斯丹模块）

打开 `results/figures/`：
- top_candidates.png：条形顺序与 final_ranking.csv 前15行一致；
- reliability_diagram.png：折线整体在虚线上方/下方波动（过自信即低于对角线），
  与 ECE=0.210 的结论方向一致；
- uncertainty_vs_error.png：散点呈右上趋势（方差大误差大）；
- model_dock_scatter.png：叉号（域外）多位于右侧模型分高但排名低区域。

## §4 抽样溯源核验（王散曼主导，下学期WP5完成）

从 `data/raw/tcm_seed_compounds.csv` 随机抽10条正样本，逐条到
PubMed/CNKI 检索证据（化合物名 + hepatoprotective / liver injury），
回填 literature/01 对应条目的"已核对"标记。当前 literature/01 头部
已声明"引用为整理稿"——正式结题前必须完成本节。

## §5 常见问题

| 现象 | 原因与处理 |
|---|---|
| CSV中文乱码 | 读取统一 utf-8-sig；Excel打开用"数据→自文本→UTF-8" |
| run_all 某阶段报错 ModuleNotFoundError | 确认在仓库根目录执行（脚本依赖相对路径 src/） |
| 图中中文方框 | 正常：图内标签设计为英文，中文在报告正文 |
| 指标小数位与文档差千分之一 | 不应出现；若出现说明结果文件被改动，重跑 §2 |

## 核验记录表

| 日期 | 核验人 | §0 | §1 | §2.1 | §2.2 | §2.3 | §3 | §4 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| （示例）2026-09-02 | 王启龙 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 下学期 | 全过 |
| | | | | | | | | | |
