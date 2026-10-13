# 2026-10-13 来源与计算入口复核

| 问题 | 结论 | 依据 | 修正 |
|---|---|---|---|
| mock对接可被旧融合当成科研结果 | 演示用途需独立边界 | src/docking/mock_docking.py、src/scoring/fuse.py | 显式HEPATO_DATA_MODE=demo，写results/demo/docking；旧融合入口停用 |
| NaN/Inf/负方差进入排名 | 成立 | final-aidd-screening/src/s5_fuse_select.py | 总分/模型值有限数检查；非有限对接按缺测；tie按ID稳定序列化 |
| 融合总分能否证明筛选有效 | 不能 | 人为0.45/0.35/0.20权重，既有稳定性为描述性 | 输出HEURISTIC_REFERENCE_ONLY、scientific_release=false |
| Vina本机路径fallback | 需显式部署 | common.VINA原捆绑exe候选 | VINA_BIN或PATH，不把运行存在等同方法资格 |
| GEO/药物/assay来源规范 | 需统一事实与终点 | GEO、FDA及原论文 | data/curation/public_source_catalog.json，未知直接结合数值不补造 |

修改只针对计算入口与来源事实；未重做真实模型、对接或湿实验，未授候选发布资格。

公开依据：

- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE89632
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135251
- https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/217785s000lbl.pdf
- https://pubmed.ncbi.nlm.nih.gov/32292349/
- https://pubmed.ncbi.nlm.nih.gov/24166454/
- https://vina.scripps.edu/license/
