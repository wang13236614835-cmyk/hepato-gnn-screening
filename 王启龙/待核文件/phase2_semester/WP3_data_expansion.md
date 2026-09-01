# WP3 数据扩充与正式库导出（第3–8周）

主责：衣思淼（数据） | 核验人：王散曼
前置条件：WP1 完成；TCMSP/PubChem 可访问

## 目标

用数据库正式导出替换教学版 SMILES 与标签，带标签数据从 88 条扩到
≥1000 条，重算全部指标并给出置信区间。

## 步骤

1. 正式导出（替换 raw/）：
   - TCMSP 检索保肝相关中药（肝炎/黄疸/肝纤维化等适应症字段）→
     导出成分表；PubChem 按名称/InChIKey 批量取标准 SMILES；
   - 新表增加列：source_db、std_smiles（PubChem标准）、inchikey；
   - 保留旧列 compound_id 编号规则（HP/DC/NV 前缀）；
2. 标签复核：王散曼按 evidence_level 口径复核每条正样本
   （文献检索至少到B级证据才保留 label=1，C级降为"待定池"）；
3. 去重升级：inchikey 完全去重（替换演示版规范化串去重）；
4. 重跑清洗/划分/训练，测试集预期≥150条，指标加95% bootstrap置信区间
   （新脚本 `src/models/bootstrap_ci.py`）；
5. 描述符升级：服务器端 RDKit Crippen/TPSA 替换演示估算
   （descriptors.py 加 rdkit 分支，列名不变）；
6. 三萜简化骨架修正：正式 SMILES 替换后，MW 系统偏差应消失，
   在 01_data_dictionary.md "已知偏差"节回填实测值。

## 期望输出

- data/raw 正式版（≥1000条带标签）；新旧数据规模与指标对照表；
- bootstrap 置信区间报告。

## 验收标准

- [ ] 每条正样本有 source_db 与可溯源证据标记
- [ ] inchikey 零重复（`python -c` 抽查脚本通过）
- [ ] 指标带置信区间，AUC 区间宽度较 v1 收窄
- [ ] 王散曼抽检30条标签与文献一致

## 核验记录

| 日期 | 核验人 | 结果 | 备注 |
|---|---|---|---|
| | | | |
