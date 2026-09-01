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
| VERIFY_TASKS.md | 总纲 | 王启龙 | 人工校验任务分派表（AI文献/数据/筛选真人核验：宁代码·龙辅助·衣+代数据·曼文献）+附录A全仓库138文件→校验人映射 | 分派与 CONTRIBUTORS/PHASE_PLAN 分工无冲突；任务编号引用的 VERIFY_MANUAL 小节真实存在；第0节 Top-10 与 final_ranking.csv 前10行一致；附录A五线文件数 12+90+14+18+4=138 与 git ls-files 总数相符 |
| MEMBER_WORKBENCH.md | 总纲 | 王启龙 | 全员工作台·按全名导航：一级按人的结构说明+每人一节（是什么/做什么/怎么操作/名下文件/学习线）+全队速查表+五步通用上手 | 五节姓名与 CONTRIBUTORS 一致；每人任务编号/文件数与 VERIFY_TASKS §2 及附录A 对应小节一致；"我的文件夹"链接与根目录五个全名文件夹实际一致 |

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
| 推进程序_负责人_王启龙.md | 下学期 | 王启龙 | 全员 | 负责人学期16周逐周推进程序：AIDD学习线×WP推进线×重头校验线三线合一，每周学习验证卡锚定存档基线数字 |

每个工作包的核验方式：完成后在文件末尾"核验记录"表追加一行
（核验人、日期、各验收项✓/✗、备注）。

## 9. 个人工作档案 docs/personal/

| 文件 | 负责人 | 内容 | 核验方法 |
|---|---|---|---|
| 00_工作量与成果总表.md | 王启龙 | 五人工作量实测（提交/文件/行数）+成果归属+候补机制 | 行数/提交数与 `git log`、wc -l 复算一致 |
| P1_王启龙.md ~ P5_王散曼.md | 各自成员 | 个人实际工作、量化成果、第二阶段安排、待核验事项 | 与 MANIFEST 各节及 git 署名对照 |

## 10. 全量PDF版 reports/pdf_all/

仓库内全部36个源 md 文档的PDF镜像（目录结构与源一一对应；个人文件夹里的
md 与 待核文件/ 快照副本**不参与镜像**，它们是个人份而非源文档），由
`reports/pdf_build/md2pdf.py` 一键再生成。md 为源文件、PDF 为
阅读/打印版；修改 md 后重跑转换器即可同步。

## 11. 工具层 tools/ 与学习档案 learning/王启龙/

| 文件 | 负责人 | 内容 | 核验方法 |
|---|---|---|---|
| tools/semester_flow.py | 王启龙 | 学期学习推进流工具（负责人版）：内置16周三线程序（AIDD学习×WP推进×重头校验），按日期定位周次、任务勾选、自动核验引擎（真实执行 run_all.py/verify.py/git/CSV行数比对存档基线）、练习骨架生成（[FLOW]契约）、台账与周报 | 运行 `python tools/semester_flow.py check 1 --deep`：预期 C1-01~05 全部[通过]（12条关键行逐字一致）；预期值来源均标注于各检查项 source 字段 |
| tools/snapshot_member_files.py | 王启龙 | 个人待核文件快照生成器：按 VERIFY_TASKS 附录A 映射把每人名下文件复制到 `<姓名>/待核文件/`（按原目录结构），生成快照清单.md（来源/大小/md5/生成时 git 版本；大件豁免标注原因）；附录A 变更后重跑同步 | 重跑后各人待核文件数与附录A 一致（12/14/18/4/32）；清单 md5 与根目录原件一致；五人文件夹内无清单之外的多余文件 |
| learning/王启龙/flow_state.json | 王启龙 | 推进流工具状态（任务勾选/核验记录，含时间戳） | 由工具自管；ledger 命令可回放全部记录 |
| learning/王启龙/week01_exercise.py | 王启龙 | W1 环境自检练习（工具 scaffold 1 生成，开箱即用） | 运行输出 [FLOW] env=ok ... |
| learning/王启龙/weekNN_*.py/md | 王启龙 | 各周学习练习（scaffold N 生成骨架后按验证卡实现） | `check N` 机器判定 [FLOW] 契约行；每项预期值锚定存档文件 |

| 学期推进流_王启龙.exe | 王启龙 | 学期推进流工具的 Windows 独立运行版（PyInstaller 单文件，双击=本周看板） | 双击显示看板；命令行 check/plan/week 等用法见 tools/使用说明_学期推进流exe.md |
| 使用说明_学期推进流exe.md | 王启龙 | exe 用法/放置/核验口径/重打包命令 | 与 semester_flow.py 文档头一致 |
| 学期推进流_王启龙.html（打卡页，已迁至 王启龙/打卡.html） | 王启龙 | 学期推进流工具的网页打卡版（单文件HTML，双击浏览器打开；16周三线规划+任务打卡+核验清单+周报生成，进度存localStorage可导出/导入）；v3 起首屏为「🧭 我的工作台」 | 打开后头部显示当前周与总进度；勾选任务/核验项（核验项有"凭实测勾选"确认弹窗）；与 exe 版数据口径同源 |

| 学期推进流_王启龙.html（v2 学习资源版） | 王启龙 | 在打卡版基础上新增：27条视频课程清单（改编自《AIDD 28天保姆级突进系统》，映射16周，B站搜索直达链接，勾选记进度）、研究发展与工具库（9数据库+7关键论文arxiv/Nature链接+前沿检索式）、28天速查表（v1口径，标注与现行流水线的对应关系） | 打开「学习资源」标签页：视频/外链可点、勾选后头部「视频学习 n/27」更新并持久化 |
| 学期推进流_宁显泷/_衣思淼/_代维斯丹/_王散曼.html（打卡页，已迁至各自全名文件夹/打卡.html） | 王启龙 | 四位成员的学期推进流打卡页（gen_member_pages.py 从负责人版模板生成：各自16周程序——学习线前置到各自主责工作包、专属验证卡/核验清单/里程碑/视频清单、独立localStorage） | 打开各页标题与姓名一致、勾选任务进度更新且互不影响；周卡片含"本周视频"块 |
| gen_member_pages.py | 王启龙 | 成员页生成器（负责人版为模板，换 WEEKS/MANUALS/MILESTONES/RES 四块数据） | 修改负责人版后重跑 `python tools/gen_member_pages.py`，四页同步更新 |
| 学期推进流五页 v2（大白话版） | 王启龙 | 全部页面小白化改写：字段改为"学什么做什么/怎么动手/过关标准/出处/没过怎么办/谁来检查"；核验人按 PHASE_PLAN 真实分工（WP2宁显泷查/WP3王散曼查/WP4衣思淼查/WP5代维斯丹查）；新增新手三步引导卡与20条名词小词典；视频条目改为"真实频道名+完整搜索词"；修复主题重复前缀 | 打开各页：字段为大白话、"谁来检查"与 PHASE_PLAN 分工一致、「学习资源」页底部有名词小词典；revise_plain_leader.py+gen_member_pages.py 可再生 |
| 学期推进流五页 v3（我的工作台版） | 王启龙 | 每页新增首屏默认标签「🧭 我的工作台」：身份卡（全名/角色/校验线/名下文件数/时限）、我的校验任务表（N/Y/D/M/L 编号，与 VERIFY_TASKS 同源）、我的文件清单（附录A 映射分组）、五步上手操作、GitHub 仓库直链（含各自文件夹工作台.md）、全队五人入口（各自文件夹打卡.html）；数据由 gen_member_pages.py 的 MYWORKS 字典注入（负责人版为模板）；页面文件位于各成员一级文件夹 | 打开任一页默认即"我的工作台"且姓名正确；任务数=VERIFY_TASKS 对应小节条数（6/6/5/4/5）；文件数组数合计=附录A 该线文件数（12/14/18/4/90）；改 VERIFY_TASKS 后须同步 MYWORKS 再生页面 |
| 学期推进流五页 v4（两篇学习指南融入版） | 王启龙 | 融入微信文章《AIDD大模型时代的学习规划指南》+《AIDD学习-第001天》：①学习资源页顶部新增「AIDD 证据链」卡（生物学问题→靶点/分子/数据/模型/决策→实验验证，五对象对应本项目实例）②新增「100 天地图」10 阶段表（含与本学期 16 周对应列）③资源组新增 TeachOpenCADD/复旦课程/AIDD入门书/B站药学生系列 ④名词小词典新增 6 词条（AIDD/CADD、证据链、基础模型、富集率、Pareto 前沿、微调/提示工程）⑤打卡台账新增「我的 AIDD 学习日志」（起点自评 4 项+学期目标+担心问题，存独立 localStorage，随进度可导出）⑥页脚新增铁律"模型给出的是值得验证的假设，不是被证明的药物结论" | 打开「学习资源」页可见证据链卡与 100 天地图（10 行）；「打卡台账」页可自评并刷新后保持；词典含"Pareto 前沿"词条；页脚含"值得验证的假设"；五页一致（负责人版改后重跑生成器同步） |

## 12. 成员工作区（一级按人，仓库根目录五个全名文件夹）

结构约定：**一级目录即分派到人**；数据、文献、代码、结果**全队公用一份**
（data/ literature/ src/ results/ docs/，不复制、以仓库为唯一真相）；
每人的任务与记录**在各自文件夹里再有一份**。

| 文件夹/文件 | 负责人 | 内容 | 核验方法 |
|---|---|---|---|
| 王启龙/ 宁显泷/ 衣思淼/ 代维斯丹/ 王散曼/ | 各自成员 | 每人三件：**工作台.md**（我是谁/任务勾选表/名下文件/公用资源指引/操作五步/完成记录）＋**打卡.html**（学习·打卡·周报，浏览器打开）＋**待核文件/**（名下要核验的具体文件快照副本，按原目录结构摆放；快照清单.md 记录来源/大小/md5 与生成时的 git 版本） | 任务行数=VERIFY_TASKS 对应小节（6/6/5/4/5）；待核文件数=附录A 该线（12/14/18/4/王启龙32+大件清单）；打卡页首屏姓名与文件夹名一致；与 docs/ 公用总表不矛盾（改公用表须同步个人份并重跑快照脚本） |
| 待核文件快照大件豁免 | 王启龙 | exe（8MB 二进制）、reports/pdf_all 27 份 PDF 镜像、pdf_build 中间产物、2 份大 PDF 报告**不入快照**：属可再生产物，复制即纯冗余数据；以根目录为准 | 快照清单.md 尾部逐条标注豁免原因；需要时在根目录核验（exe 双击、PDF 直接打开） |
| semester_flow.py v1.1 | 王启龙 | 修复 cmd 窗口中文乱码：仅输出被管道时才强制 UTF-8，直接在 cmd 运行走系统 Unicode 接口 | cmd 中运行 学期推进流_王启龙.exe check 1 中文正常显示 |
