# 图文一致性核验台账（2026-09-05）

这张表是 GNN 两周收尾的 W2 必核文件。图片只在“来源表、对象 ID、受体/配体、单位、软件/数据版本”五项齐全且逐项对应后，才允许进入 AIDD 交接或论文草稿。历史图不因为文件存在就被当作当前结论。

| 图片 | 对应数据/脚本 | 对象与单位 | 当前状态 | 处理口径 |
|---|---|---|---|---|
| `results/figures/top_candidates.png` | `results/rankings/final_ranking.csv`；`src/viz/plots.py` | compound_id/rank；分数单位按表头 | 历史待复核 | 只核对排序是否逐行对应；旧 Top-10 不放行 |
| `results/figures/reliability_diagram.png` | `results/metrics/reliability_curve.csv`；`results/validation/software_checks.json` | test compound；概率/频率为无量纲 | 历史待复核 | ECE 只能引用同一版本 CSV，不能把旧 0.210 写成校准后结论 |
| `results/figures/uncertainty_vs_error.png` | `results/predictions/test_predictions.csv` | compound_id；方差与绝对误差均无量纲 | 历史待复核 | 逐点抽查 compound_id；缺 ID 或轴转换异常记问题 |
| `results/figures/model_dock_scatter.png` | `results/predictions/fullpool_predictions.csv` + `results/docking/docking_scores.csv` | compound_id；模型分数无量纲、对接分数 kcal/mol | 历史待复核 | 模型/对接版本必须同批次；禁止混用 demo/mock 与 real |
| `docs/audit/20260905/scatter_numeric_audit.png` | `docs/audit/20260905/docking_score_check.csv` | 数值轴；单位按 CSV | 已修正核查图 | 已将字符串数值显式转数值；仍需在 W2 记录复核人 |

## 发现即登记

- 图中标签、点数、排序、轴单位、受体/配体或版本任一对不上：写入 `docs/audit/20260905/问题清单.csv`，保留“未解决”，不得用截图覆盖。
- 只有 `results/validation/software_checks.json` 通过的软件项可以写“软件核验通过”；科学有效性、MASH 标签和候选释放仍分别受 `docs/REPO_SCOPE.md` 与 AIDD 主库门控。
- 图表核验完成后，由代维斯丹初核、衣思淼复核、王启龙汇总；王散曼只核对文献/终点语义，宁显泷核对脚本和数值。
