# 全仓库文件清单（MANIFEST）

> 每个文件标注：所属阶段、负责人、用途、人工核验方法。
> 核验方法列给出"打开后看什么、预期是什么"；通用命令类核验的完整步骤见
> `docs/VERIFY_MANUAL.md`。下学期新增文件必须在此登记。

## 1. 仓库根目录

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| README.md | 暑假 | 王启龙 | 项目总览、速览指标、复核清单 | 打开核对：Top-3 与 results/rankings/final_ranking.csv 前三行一致；指标表与 results/metrics/baseline.csv 及 5.2 节数字一致 |
| CONTRIBUTORS.md | 暑假 | 王启龙 | 成员-模块映射 | 与 `git shortlog -sn HEAD`、各文件头"负责人"三方对照，无错配 |
| requirements.txt | 暑假 | 王启龙 | 依赖声明（仅 numpy 必需） | 核对列出的版本与 docs/00_environment.md 一致 |
| .gitignore | 暑假 | 王启龙 | 忽略缓存/venv/npy | 确认 results/*.csv 未被忽略（结果需入库） |
| run_all.py | 暑假 | 王启龙 | 一键复现八阶段流水线 | 运行 `python run_all.py`，控制台逐段输出与 VERIFY_MANUAL §2 的预期输出一致；总耗时约6秒 |

## 2. 数据层 data/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| raw/tcm_seed_compounds.csv | 暑假 | 王散曼 | 种子集：48活性+40负参照 | Excel打开数行数=89（含表头）；HP前缀48行、DC前缀40行；抽3条（如HP-015水飞蓟宾）到 literature/01 找对应证据条目 |
| raw/novel_terpenes_lignans.csv | 暑假 | 王散曼 | 新分子池12条 | 数行数=13（含表头）；核对NV-011为奥贝胆酸（阳性参照，不占名额） |
| processed/cleaned_compounds.csv | 暑假 | 衣思淼 | 清洗产物（88条+骨架/描述符列） | 行数=89；label列只有0/1；scaffold列非空 |
| processed/screening_pool.csv | 暑假 | 衣思淼 | 新分子池清洗产物（12条） | 行数=13；label列为空 |
| processed/rejected.csv | 暑假 | 衣思淼 | 剔除留痕（当前0条，仅表头） | 只有表头一行；若未来有内容，每条须有reject_reason |
| splits/train,val,test.csv | 暑假 | 衣思淼 | 骨架级划分 | 行数分别=59/14/18（含表头）；同一scaffold不得跨文件出现（可用Excel筛选抽查黄芩苷所在骨架） |

## 3. 代码层 src/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| chem/smiles_graph.py | 暑假 | 宁显泷 | SMILES→分子图解析器 | 见 VERIFY_MANUAL §3.1（含5条最小用例） |
| chem/descriptors.py | 暑假 | 衣思淼 | 7维二维描述符 | 见 VERIFY_MANUAL §3.2（槲皮素MW≈302口径核对） |
| chem/fingerprints.py | 暑假 | 代维斯丹 | Morgan型哈希指纹 | 同上 §3.3（确定性：两次调用比特位一致） |
| data/clean.py | 暑假 | 衣思淼 | 清洗管线 | 重跑后 processed 下三个文件内容不变（确定性） |
| data/split.py | 暑假 | 衣思淼 | 骨架划分 | seed=42 固定，重跑行数不变 |
| data/ad.py | 暑假 | 衣思淼+王启龙 | 适用域杠杆值 | h*=3×7/58≈0.362，与 results/ad/ad_report.csv 首行一致 |
| models/dataset.py | 暑假 | 宁显泷 | 图记录装载与节点特征 | 节点特征13维（10元素onehot+芳香+度+氢） |
| models/gnn.py | 暑假 | 宁显泷 | GNN+MC Dropout | 预测CSV为全精度小数（无固定位数截断） |
| models/baseline.py | 暑假 | 代维斯丹 | NB与LR双基准线 | 输出与 metrics/baseline.csv 一致 |
| docking/grid_box.py | 暑假 | 代维斯丹 | 双靶点盒子参数 | FXR=1OSH、Keap1=2FLU，中心/尺寸与 docs/03 表格一致 |
| docking/mock_docking.py | 暑假 | 代维斯丹 | 演示模式打分 | 噪声按(分子,靶点)哈希定种子，重跑分数逐字节一致 |
| docking/run_vina.sh | 暑假(供下学期WP2) | 代维斯丹 | 服务器真实对接脚本 | 下学期执行，见 WP2 验收标准 |
| scoring/fuse.py | 暑假 | 衣思淼+王启龙 | 协同评分融合 | 权重0.45/0.35/0.20与文档4.7一致；域外×0.9 |
| viz/plots.py | 暑假 | 王启龙+代维斯丹 | 4张结果图 | 图中数据与CSV一致（如Top-15条形图顺序=final_ranking前15行） |
| 各级__init__.py（7个） | 暑假 | 王启龙 | 包初始化 | 存在即可 |

## 4. 文档层 docs/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| 00_environment.md | 暑假 | 王启龙 | 环境说明 | 按文档装环境后能跑 run_all.py |
| 01_data_dictionary.md | 暑假 | 衣思淼 | 数据字典 | 字段描述与 CSV 表头逐列对照 |
| 02_model_notes.md | 暑假 | 宁显泷 | 模型说明 | 超参与 gnn.py 代码一致（p_drop=0.3, T=30, epoch=300） |
| 03_docking_protocol.md | 暑假 | 代维斯丹 | 对接流程 | 盒子参数与 grid_box.py 一致；"演示模式"局限性已写明 |
| minutes/week1-2,3-4,5-6.md | 暑假 | 王启龙 | 三次组会纪要 | 时间线与 PHASE_PLAN 里程碑一致 |
| PHASE_PLAN.md | 总纲 | 王启龙 | 两阶段划分 | 分工表与 CONTRIBUTORS.md 一致 |
| MANIFEST.md | 总纲 | 王启龙 | 本文件 | 覆盖仓库全部内容文件（pycache 除外） |
| VERIFY_MANUAL.md | 总纲 | 王启龙 | 人工核验手册 | 按 §0–§5 走一遍能全过 |

## 5. 文献层 literature/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| 01_classic_evidence.md | 暑假 | 王散曼 | 种子集证据库 | **逐条**与 raw CSV 的 evidence 字段对照；引用条目下学期WP5人工查原文 |
| 02_novel_terpenes_lignans.md | 暑假 | 王散曼 | 新分子调研 | 表格12行与 raw/novel CSV 的 NV 编号一一对应 |
| 03_top_candidate_mechanisms.md | 暑假 | 王散曼 | Top-10机制溯源与药效团 | 表中模型分/对接分与 final_ranking.csv 前十行一致 |

## 6. 结果层 results/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| metrics/baseline.csv | 暑假 | 代维斯丹 | 基准线指标 | 两行两模型，AUC 0.850/0.967 |
| metrics/reliability_curve.csv | 暑假 | 王启龙 | 可靠性曲线数据 | 与 reliability_diagram.png 折线一致 |
| predictions/test_predictions.csv | 暑假 | 宁显泷 | 测试集预测（17行） | 行数=18（含表头）；pred_var≥0 |
| predictions/fullpool_predictions.csv | 暑假 | 宁显泷 | 全候选池预测（60行） | 行数=61；全精度小数 |
| predictions/test_mean.npy, test_var.npy | 暑假 | 宁显泷 | 测试集数组缓存 | 可删（.gitignore忽略），重跑自动生成 |
| docking/docking_scores.csv | 暑假 | 代维斯丹 | 演示对接分 | 行数=201（100分子×2靶点+表头）；mode列全为mock_local |
| ad/ad_report.csv | 暑假 | 衣思淼 | 适用域报告（100行） | NV段7行in_domain=0 |
| rankings/final_ranking.csv | 暑假 | 衣思淼+王启龙 | 最终排名（60行） | Top-3=黄芩苷/二氢杨梅素/葛根素；rank列1–60连续 |
| figures/*.png（4张） | 暑假 | 王启龙+代维斯丹 | 结果图 | 打开与对应CSV目视对照 |

## 7. 报告层 reports/

| 文件 | 阶段 | 负责人 | 用途 | 人工核验方法 |
|---|---|---|---|---|
| midterm_report.md | 暑假 | 全员（王启龙汇编） | 中期考核报告 | 数字与 results/ 一致（verify.py 已覆盖） |
| 课题详解与阶段结果说明.pdf | 暑假 | 王启龙 | 详解版PDF（13页） | 打开抽查表5-1/5-2与CSV一致 |
| 暑假阶段报告汇总.pdf | 暑假 | 王启龙 | **本阶段汇总报告（交付姜老师）** | 目录可点击；第6章数字与 verify.py 输出一致 |
| pdf_build/build_body.py, build_phase1.py | 暑假 | 王启龙 | 详解PDF与阶段报告PDF的正文生成脚本 | 改内容后重跑+merge+QA |
| pdf_build/md2pdf.py | 暑假 | 王启龙 | Markdown批量转PDF转换器（27份镜像的生成器） | `python reports/pdf_build/md2pdf.py` 重新生成 pdf_all |
| pdf_build/cover*.html, cover*.pdf | 暑假 | 王启龙 | 两份报告的HTML封面源码与渲染产物 | 封面校验无重叠 |
| pdf_build/merge_final.py, patch*.py | 暑假 | 王启龙 | 封面正文合并脚本与内容修正补丁 | 合并后页数13/10 |
| pdf_build/verify.py | 暑假 | 王启龙 | 45项独立数字校验脚本 | 重跑输出"通过45项；不符0项" |
| pdf_build/push_via_api.py, upload_aidd.py, finalize_aidd.py | 暑假 | 王启龙 | GitHub API上传工具链（绕过直连封锁：blob断点续传+分块链式建树） | 附aidd_blobs.json缓存（瞬态，不入库） |
| pdf_build/body*.pdf | 暑假 | 王启龙 | 正文PDF中间产物 | 可由脚本再生 |

## 8. 下学期工作包 phase2_semester/

| 文件 | 阶段 | 主责 | 核验人 | 用途 |
|---|---|---|---|---|
| WP1_verify_baseline.md | 下学期 | 王启龙 | 全员 | 复现核验与基线固化（第1–2周） |
| WP2_real_docking.md | 下学期 | 代维斯丹 | 宁显泷 | 真实分子对接（第3–6周） |
| WP3_data_expansion.md | 下学期 | 衣思淼 | 王散曼 | 数据扩充与正式库导出（第3–8周） |
| WP4_model_upgrade.md | 下学期 | 宁显泷 | 衣思淼 | 模型升级与校准（第7–10周） |
| WP5_experiment_bridge.md | 下学期 | 王散曼 | 代维斯丹 | 文献深化与实验衔接（第9–16周） |

每个工作包的核验方式：完成后在文件末尾"核验记录"表追加一行
（核验人、日期、各验收项✓/✗、备注）。

## 9. 个人工作档案 docs/personal/

| 文件 | 负责人 | 内容 | 核验方法 |
|---|---|---|---|
| 00_工作量与成果总表.md | 王启龙 | 五人工作量实测（提交/文件/行数）+成果归属+候补机制 | 行数/提交数与 `git log`、wc -l 复算一致 |
| P1_王启龙.md ~ P5_王散曼.md | 各自成员 | 个人实际工作、量化成果、第二阶段安排、待核验事项 | 与 MANIFEST 各节及 git 署名对照 |

## 10. 全量PDF版 reports/pdf_all/

仓库内全部27个 md 文档的PDF镜像（目录结构与源一致），由
`reports/pdf_build/md2pdf.py` 一键再生成。md 为源文件、PDF 为
阅读/打印版；修改 md 后重跑转换器即可同步。
