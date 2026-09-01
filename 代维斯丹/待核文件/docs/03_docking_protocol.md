# 分子对接流程说明

负责人：代维斯丹（验证组）

## 1. 靶点与盒子

| 靶点 | PDB | 口袋类型 | 中心/尺寸(Å) | 参考配体 |
|---|---|---|---|---|
| FXR-LBD（胆汁酸核受体） | 1OSH | 疏水型 | 15.2,3.8,24.5 / 22×22×24 | fexaramine |
| Keap1-Kelch（Nrf2通路） | 2FLU | 极性/碱性 | -11.5,20.4,-6.2 / 20×20×20 | Nrf2 ETGE 肽 |

靶点选择逻辑：FXR 覆盖"利胆/胆汁淤积型"肝保护机制，Keap1 覆盖
"氧化应激型"机制，两个口袋类型互补，避免单靶点偏差。

## 2. 本地演示模式（当前）

本地未部署 Vina，`src/docking/mock_docking.py` 以物理启发打分替代：
口袋类型加权的描述符线性项 + MW>550 渗透罚 + (分子ID,靶点) 哈希种子
噪声(σ=0.35)，标定到 kcal/mol 量级仅供**排序流程验证**。

演示模式区分度自检：FXR 上保肝活性分子均分 -5.46 vs 负参照 -5.05
（差 0.42 kcal/mol），排序方向正确但区分度弱——这也是必须上真实
对接的原因之一。

## 3. 服务器真实对接（下一阶段）

```bash
# 受体预处理(一次性)
prepare_receptor4.py -r 1OSH_fxr.pdb  -o fxr.pdbqt   -A hydrogens
prepare_receptor4.py -r 2FLU_keap1.pdb -o keap1.pdbqt -A hydrogens

# 批量对接(exhaustiveness=16, 每配体取3构象)
bash src/docking/run_vina.sh <ligand_dir> <out_dir>
```

验收标准：水飞蓟宾(FXR)与已知 Keap1 配体的回打分 RMSD<2Å 或
打分位于前列（阳性对照有效性检查）。

## 4. 与模型分的并表

对接分经名次百分位归一后进入协同评分（`src/scoring/fuse.py`），
权重 0.35；两靶点取均值。真实对接完成后直接覆盖
`results/docking/docking_scores.csv`，下游无需改动。
