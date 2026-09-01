# 环境配置说明

负责人：王启龙（工程支撑）
更新：暑期第 2 周末（本地）；第 4 周更新服务器部分

## 1. 本地环境（小样本跑通用）

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.12 | 3.9+ 均可 |
| numpy | 1.26 | 唯一必需依赖 |
| matplotlib | 3.8 | 可选，出图用 |
| git | 2.54 | 版本管理 |

安装：

```bash
pip install -r requirements.txt
python run_all.py     # 全流程约 6 秒
```

零 RDKit / 零 PyTorch 设计说明：SMILES 解析、描述符、指纹、GNN 全部为
纯 numpy 实现（见 `src/chem/`、`src/models/gnn.py`），保证任何成员的
笔记本都能跑通。代价是精度与速度，见各模块头部的"服务器版迁移说明"。

## 2. 服务器环境（第 3 周起，上量用）

```bash
conda create -n hepato python=3.11 -y
conda activate hepato
conda install -c conda-forge rdkit pytorch torchvision -y
pip install torch-geometric vina pandas scikit-learn
```

GPU：CUDA 12.x；CPU 也能跑（数据量 <10k 时差异不大）。

## 3. 常见问题

- **Windows 下中文乱码**：所有 CSV 以 UTF-8(无BOM) 存储，读取统一用
  `encoding="utf-8-sig"`。
- **matplotlib 图内中文变方框**：图内标签统一用英文；中文标题放报告里。
- **复现性**：全部随机过程固定种子（训练 seed=7/42、划分 seed=42、
  对接噪声按分子ID哈希），重跑 `run_all.py` 结果一致。
