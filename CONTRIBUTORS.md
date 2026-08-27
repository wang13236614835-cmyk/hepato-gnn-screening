# 贡献与分工映射

| 成员 | 角色 | 负责模块（本仓库内） |
|---|---|---|
| 王启龙 | 工程支撑 | README、requirements、docs/00_environment.md、docs/minutes/*、src/data/ad.py(预警集成)、run_all.py、src/viz/plots.py(工程) |
| 宁显泷 | 算法 | src/chem/smiles_graph.py、src/models/gnn.py、src/models/dataset.py、docs/02_model_notes.md |
| 衣思淼 | 数据 | src/data/clean.py、src/data/split.py、src/data/ad.py(边界定义)、src/chem/descriptors.py、src/scoring/fuse.py(融合规则)、docs/01_data_dictionary.md |
| 代维斯丹 | 验证 | src/docking/*、src/models/baseline.py、src/chem/fingerprints.py、docs/03_docking_protocol.md |
| 王散曼 | 化学信息与文献 | data/raw/*.csv(数据整理)、literature/* |

提交约定：模块归属者以本人身份提交；联合任务（适用域、评分融合、
出图）按"主责+协作"双作者记录。
