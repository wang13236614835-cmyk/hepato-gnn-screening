# 人工校验任务分派表（AI 产出的文献·数据·筛选 真人核验）

> 背景：暑假阶段全部结果（文献整理稿、数据集、模型打分、Top-60 排名）由
> AI 辅助流水线产出。在作为结题依据之前，
> 必须由真人分模块完成校验。执行手册为 `docs/VERIFY_MANUAL.md`，
> 本文件只做**任务到人**的分派、交付物定义与时间节点。
> 方法论沿用三原则：分模块独立复算、逆推法溯源、引擎级重跑；
> 预期值只引用存档基线（来源以括号标注），不得凭记忆填写。

## 0. 待校验的核心结论（最直接版）

`results/rankings/final_ranking.csv` 当前 Top-10（final_score 降序）：

| 排名 | 编号 | 化合物 | 类别 | 来源草药 | 模型分 | 对接 kcal | 终评 |
|---|---|---|---|---|---|---|---|
| 1 | HP-007 | 黄芩苷 | 黄酮苷类 | 黄芩 | 0.9612 | -6.86 | 0.9291 |
| 2 | HP-014 | 二氢杨梅素 | 黄酮醇类 | 显齿蛇葡萄(藤茶) | 0.9653 | -7.14 | 0.8990 |
| 3 | HP-013 | 葛根素 | 异黄酮苷类 | 葛根 | 0.9614 | -7.03 | 0.8903 |
| 4 | HP-016 | 姜黄素 | 多酚类 | 姜黄 | 0.8898 | -6.94 | 0.8821 |
| 5 | HP-009 | 柚皮素 | 黄烷酮类 | 枳实/骨碎补 | 0.9413 | -6.54 | 0.8811 |
| 6 | HP-005 | 木犀草素 | 黄酮类 | 金银花 | 0.9783 | -6.43 | 0.8704 |
| 7 | HP-015 | 水飞蓟宾 | 黄酮木脂素类 | 水飞蓟 | 0.9666 | -6.39 | 0.8497 |
| 8 | NV-009 | 松脂素 | 木脂素类 | 连翘/杜仲 | 0.8814 | -6.64 | 0.8397 |
| 9 | HP-001 | 槲皮素 | 黄酮类 | 槐米/银杏叶 | 0.9718 | -6.37 | 0.8198 |
| 10 | NV-010 | 落叶松脂素 | 木脂素类 | 连翘/亚麻籽 | 0.7912 | -6.89 | 0.8181 |

合理性旁证：临床金标准水飞蓟宾落第 7（§3.5）；阳性参照药奥贝胆酸
（NV-011）被适用域标记"域外"且 pred_mean≈0.26，未被顶替进榜单。
**上述数字全部未经真人核验，核验通过前仅称"AI 初筛结果"。**
全队纪律（老师着重强调）：**数据与证据只从公开权威数据库取**
（PubChem/ChEMBL/PDB/TCMSP/SwissADME/PubMed/CNKI 白名单），入库记
"库名＋唯一编号＋访问日期"；白名单与四条硬规则见 WP3"来源纪律"节
及各打卡页「🏛 权威来源纪律」卡。**

## 1. 分派总表（用户指定口径）

| 成员 | 校验线 | 一句话职责 | 完成时限 |
|---|---|---|---|
| 宁显泷 | 代码验证（主核） | 证明"代码跑得对、结果可复现" | W1 周五 9/13 |
| 王启龙 | 辅助 | 环境/汇总/固化标签，全流程托底 | W2 周五 9/20 |
| 衣思淼 | 数据线 A：数据集与排名表 | 证明"数字没被编造" | W1 周五 9/13 |
| 代维斯丹 | 数据线 B：对接·指纹·图 | 证明"打分与图忠实于代码输出" | W1 周五 9/13 |
| 王散曼 | 文献 | 证明"每条证据可溯源" | W2 周五 9/20（§4 为 WP5 任务，可顺延至 W14 全量） |

## 2. 任务明细

### 2.1 宁显泷 — 代码验证

| # | 任务 | 预期（来源） | 交付物 |
|---|---|---|---|
| N1 | §2.1 一键复现 `python run_all.py` | 12 条关键行逐字一致，含 60 候选入库（VERIFY_MANUAL §2.1） | 控制台输出粘贴本文件末尾记录表 |
| N2 | §2.2 确定性连跑两次 md5 比对 | 输出"一致"（§2.2） | 同上 |
| N3 | §2.3 独立数字核验 `python reports/pdf_build/verify.py` | 最后一行"通过 45 项；不符 0 项"（§2.3；旧工作库口径·审计F11，最终包另以 `tools/verify_fixes.py` 20 项验收） | 输出存 `results/logs/`（新建） |
| N4 | §3.1 解析器 5 用例 | 全 OK，重原子数 3/6/20/12/5（§3.1） | 记录表打勾 |
| N5 | 超参一致性抽查：`src/models/gnn.py` vs `docs/02_model_notes.md` | p_drop=0.3, T=30, epoch=300（MANIFEST §3） | 不一致项登记问题表 |
| N6 | 融合公式代码核对：`src/scoring/fuse.py` | 权重 0.45/0.35/0.20、域外×0.9，与文档 4.7 一致（MANIFEST §3） | 同上 |

### 2.2 王启龙 — 辅助

| # | 任务 | 预期（来源） | 交付物 |
|---|---|---|---|
| L1 | §0/§1 环境与仓库完整性预检；为任何成员排障 | 全员本地能跑 run_all.py（§0–§1） | 排障记录 |
| L2 | 汇总 5 人核验记录表；收齐 verify.py 截图 | 记录表 5 行签名（WP1 验收标准） | 汇总表 + `results/logs/` 截图 |
| L3 | 基线固化：`git tag -a v1.0-summer` 并推送 | 任何人 §2 失败则先修复再打标（WP1 步骤3） | 标签可见 |
| L4 | 每周日 `git push` 备份；周一组会按本表分派 | 推进程序 SOP（推进程序_负责人_王启龙.md §2.2） | 组会纪要 |
| L5 | A/B 级问题的工程修复与全量复跑 | 修复后旧库 verify.py 仍 45 项全过；最终包以 verify_fixes.py 20 项为准 | 修复说明 + 复跑输出 |

### 2.3 衣思淼 — 数据线 A（数据集与排名表）

| # | 任务 | 预期（来源） | 交付物 |
|---|---|---|---|
| Y1 | §3.4 原始表抽查 `data/raw/tcm_seed_compounds.csv` | 89 行；HP 48 / DC 40；HP-015 label=1、evidence=A（§3.4） | 验算留痕（Excel 筛选截图或手算页拍照入 `results/logs/`） |
| Y2 | 划分隔离抽查 `data/splits/` | 黄芩苷所在 scaffold 不出现在 test/val（§3.4）；train/val/test = 59/14/18 行含表头（MANIFEST §2） | 同上 |
| Y3 | §3.5 排名总表核验 | 61 行、rank 1–60 连续；Top-3 = 黄芩苷/二氢杨梅素/葛根素；第 7 行水飞蓟宾；NV-011 域外且 ≈0.26（§3.5） | 同上 |
| Y4 | 融合公式手工验算 ≥3 行（含第 1、7、10 名） | 与 final_score 差 ≤±0.002；黄芩苷 ≈0.9291（§3.5） | 计算过程留痕 |
| Y5 | §3.2 描述符独立复算（槲皮素） | MW=302.24、nHBD=5、nHBA=7、nHeavy=22（§3.2） | 同上 |
| Y6 | 适用域报告核对 `results/ad/ad_report.csv` | h*=0.362；域外 7/12 已标记（VERIFY_MANUAL §2.1 [ad] 行） | 同上 |

### 2.4 代维斯丹 — 数据线 B（对接·指纹·图）

| # | 任务 | 预期（来源） | 交付物 |
|---|---|---|---|
| D1 | §3.3 指纹确定性 | 两次调用一致、置位数相同（§3.3） | 记录表打勾 |
| D2 | 演示对接分核对：重跑 mock_docking | 保肝 -5.46 vs 负参照 -5.05（差距 0.42）逐字节复现（§2.1 [docking] 行；MANIFEST §3 哈希定种子） | 输出留痕 |
| D3 | §3.6 四张图与 CSV 对照 | top_candidates.png 顺序 = 前 15 行；可靠性图与 ECE=0.210 方向一致；叉号位置（§3.6） | 逐图结论一行 |
| D4 | 盒子参数核对 `src/docking/grid_box.py` vs `docs/03_docking_protocol.md` | FXR=1OSH、Keap1=2FLU，中心/尺寸一致（MANIFEST §3） | 不一致项登记 |
| D5 | 确认"演示模式"局限性已写明，并给 WP2 真实对接排期建议 | 03 文档含局限性声明（MANIFEST §4） | 一段排期建议入 WP2 |

### 2.5 王散曼 — 文献

| # | 任务 | 预期（来源） | 交付物 |
|---|---|---|---|
| M1 | §4 抽样溯源：随机抽 10 条正样本 → PubMed/CNKI 检索（化合物名 + hepatoprotective / liver injury） | 每条在 literature/01 回填"已核对"（§4） | 回填标记 + 核对台账 |
| M2 | Top-10 证据专查：第 0 节 10 个化合物逐条对照 literature/01 | 证据等级、来源草药描述两边一致；**重点 NV-009 松脂素、NV-010 落叶松脂素**（新分子池条目文献密度低） | 逐条结论一行 |
| M3 | literature/01 头部"引用为整理稿"声明处理 | M1/M2 完成后更新声明口径（§4：正式结题前必须完成） | 修改后的声明 |
| M4 | evidence_level 分布统计：CSV 与文献稿交叉计数 | A 级条目数两边一致（如实记录，不预设数字） | 计数表 |

## 3. 问题分级与处置（沿用 WP1 口径）

- **A 级（致命）**：复现失败、数字对不上、排名不可复算 → 立即停线，
  报王启龙修复后全员重跑 §2；
- **B 级（偏差）**：个别数字/描述不一致但不影响排名结论 → 登记本文件
  问题表，修复后由发现者复核；
- **C 级（建议）**：表述、排版、便利性 → 登记后择机处理。
暑假产物本体不改；改动一律在第二阶段进行（WP1"不可再改动"原则）。

## 4. 完成记录

| 日期 | 成员 | 完成任务编号 | 结果 | 签名 |
|---|---|---|---|---|
| | | | | |

> **编号补充**:D6/D7/N7/Y7/M5/L6 为复核后开展的**真实版任务**(定义见
> `reports/真实对接与统一筛选报告.md` 第三节,数据在 `results/docking/real/`),
> 不属于 9/20 前的复核任务;完成后同样记入第 4 节完成记录表。

## 5. 问题登记表

| 编号 | 级别 | 发现人 | 问题描述 | 涉及文件 | 处置 | 状态 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 附录A 全仓库文件 → 校验人映射（GitHub 内容按校验分工细化）

> 覆盖 `git ls-files` 全部 138 个文件，一个不漏。打开 GitHub 仓库后按
> 本表对号入座：每人先核验自己名下的文件，再由王启龙汇总。
> "任务号"指第 2 节任务明细中的编号；预期值来源见对应任务行。
> 与模块归属（CONTRIBUTORS.md）不一致处以本表校验线为准，模块主
> 作为第二核对人（复核栏）。
> 本表为**公用一份**的总表；每人自己的任务勾选表、文件清单、完成记录
> 在**各自全名文件夹**里另有一份（`<姓名>/工作台.md`＋`<姓名>/打卡_<姓名>.html`），
> 改本表须同步个人份。

### A1 宁显泷 · 代码验证（22 文件＝原12＋学习练习9＋状态1）

| 路径 | 任务号 | 看什么 |
|---|---|---|
| run_all.py | N1/N2 | 重跑 12 关键行一致；两次 md5"一致" |
| src/chem/smiles_graph.py | N4 | §3.1 五用例全 OK |
| docs/02_model_notes.md | N5 | 超参口径表：与 gnn.py 代码逐项互查 |
| src/models/gnn.py、src/models/dataset.py | N5 | 超参 p_drop=0.3/T=30/epoch=300 与 02 文档一致；全精度输出 |
| src/models/baseline.py | N1 | 重跑指标与 metrics/baseline.csv 一致（模块主：代维斯丹复核） |
| src/scoring/fuse.py | N6 | 权重 0.45/0.35/0.20、域外×0.9（模块主：衣思淼复核） |
| reports/pdf_build/verify.py | N3 | 独立复算"通过 45 项；不符 0 项"（旧工作库口径·F11） |
| results/metrics/baseline.csv、reliability_curve.csv | N1/N3 | 数字由重跑与 verify.py 双重覆盖（模块主：代维斯丹复核） |
| results/predictions/test_predictions.csv、fullpool_predictions.csv | N1 | 重跑后逐字节一致（npy 为缓存不入库） |
| learning/宁显泷/（10 文件） | — | 名下学习练习骨架 W2/3/4/5/6/8/9/10/11＋状态文件：`semester_flow.py --member 宁显泷 check N` 判定 [FLOW]（学习线，非核验任务） |

### A2 王启龙 · 辅助/工程（99 文件＝原90＋学习练习11－已删 revise 与 exe）

| 路径 | 任务号 | 看什么 |
|---|---|---|
| README.md、CONTRIBUTORS.md、requirements.txt、.gitignore | L1/L2 | Top-3 与排名表一致；shortlog 与分工表一致；结果 CSV 未被忽略 |
| docs/00_environment.md | L1 | 按文档装环境能跑 run_all.py |
| docs/MANIFEST.md、PHASE_PLAN.md、VERIFY_MANUAL.md、VERIFY_TASKS.md | L2/L4 | 总纲四件：与实际分工/文件无冲突（本表附录A即 MANIFEST 的校验视角） |
| docs/minutes/week1-2、3-4、5-6.md | L4 | 时间线与 PHASE_PLAN 里程碑一致 |
| docs/personal/（6 文件：总表+P1–P5） | L2 | 各成员自维护；王启龙汇总核对存在性与口径一致 |
| phase2_semester/（6 文件：WP1–WP5+推进程序） | L4 | 计划文档：周次/主责/验收三要素齐全（各 WP 主责人执行时验收） |
| tools/（5 文件：semester_flow.py、gen_member_pages.py、snapshot_member_files.py、push_incremental_api.py、使用说明）＋五人打卡页（各自全名文件夹/打卡_姓名.html）＋五份 待核文件/ 快照 | L1 | `check 1 --deep` 全过；成员页与分工一致；快照数=附录A 各线文件数（工程工具与快照，非科学结论） |
| learning/王启龙/（14 文件） | L4 | 台账自管；ledger 可回放；各周练习骨架已生成（W1 完整版＋W2–W14 骨架） |
| reports/pdf_build/（verify.py 之外的 23 文件：build/merge/上传脚本、中间产物、文件备注清单） | L1 | 构建工具链与中间产物：能再生成、与 md 源一致即可，不核科学数字 |
| reports/pdf_all/（27 个 PDF 镜像） | L2 | md 为源：md 变更后重跑 md2pdf.py 同步；不单独核验数字 |
| reports/midterm_report.md、暑假阶段报告汇总.pdf、课题详解与阶段结果说明.pdf | L2 | 报告引用数字与 results/ 一致（发现不符→B级登记） |
| results/logs/（L2 新建） | L2 | verify.py 截图与汇总记录落位 |

### A3 衣思淼 · 数据线A（21 文件＝原14＋学习练习6＋状态1）

| 路径 | 任务号 | 看什么 |
|---|---|---|
| data/raw/tcm_seed_compounds.csv | Y1 | 89 行；HP 48/DC 40；HP-15 行 label=1、evidence=A |
| data/processed/cleaned_compounds.csv、screening_pool.csv、rejected.csv | Y1 | 89/13/仅表头；label 只 0/1；scaffold 非空 |
| data/splits/train、val、test.csv | Y2 | 59/14/18 行；黄芩苷 scaffold 不跨集合 |
| src/data/clean.py、split.py、ad.py | Y1/Y2/Y6 | 重跑产物不变（seed=42）；h*=0.362 与 ad_report 一致 |
| src/chem/descriptors.py | Y5 | 槲皮素 MW=302.24/nHBD=5/nHBA=7/nHeavy=22 |
| docs/01_data_dictionary.md | Y1 | 字段口径与 CSV 表头逐列对照 |
| results/ad/ad_report.csv | Y6 | h*=0.362；域外 7/12 标记 |
| results/rankings/final_ranking.csv | Y3/Y4 | 61 行 rank 连续；Top-3 与第 0 节一致；手工验算 ±0.002 |
| learning/衣思淼/（7 文件） | — | 名下学习练习骨架 W2/4/7/8/10/12＋状态文件：`--member 衣思淼 check N`（学习线，非核验任务） |

### A4 代维斯丹 · 数据线B（22 文件＝原18＋学习练习3＋状态1）

| 路径 | 任务号 | 看什么 |
|---|---|---|
| src/chem/fingerprints.py | D1 | 同分子两次指纹一致 |
| src/docking/grid_box.py | D4 | FXR=1OSH、Keap1=2FLU 中心/尺寸与 03 文档一致 |
| src/docking/mock_docking.py | D2 | 哈希定种子重跑逐字节一致；-5.46 vs -5.05 |
| src/docking/run_vina.sh | D5 | 下学期 WP2 执行，本次只核脚本与 03 协议一致 |
| src/viz/plots.py、results/figures/（4 张 png） | D3 | 图与 CSV 逐图对照（§3.6） |
| results/docking/docking_scores.csv | D2 | 均值/分靶点分与文档口径一致 |
| docs/03_docking_protocol.md | D4/D5 | 盒子参数一致；演示模式局限性已写明 |
| src/ 各级 __init__.py（7 个） | — | 存在即可（随 D 线顺带） |
| learning/代维斯丹/（4 文件） | — | 名下学习练习骨架 W3(bash)/W7/W8＋状态文件：`--member 代维斯丹 check N`；W3 服务器跑后 record 补录（学习线，非核验任务） |

### A5 王散曼 · 文献（6 文件＝原4＋学习练习1＋状态1）

| 路径 | 任务号 | 看什么 |
|---|---|---|
| literature/01_classic_evidence.md | M1/M2/M3 | 抽 10 条正样本 PubMed/CNKI 溯源回填；Top-10 逐条对照；声明口径更新 |
| literature/02_novel_terpenes_lignans.md | M2 | NV-009 松脂素、NV-010 落叶松脂素重点溯源 |
| literature/03_top_candidate_mechanisms.md | M2 | Top-10 机制描述与 01/02 证据不矛盾 |
| data/raw/novel_terpenes_lignans.csv | M2 | 13 行含表头；NV-011=奥贝胆酸（与 A3 衣思淼 Y1 交叉） |
| learning/王散曼/（2 文件） | — | 名下学习练习骨架 W5（大模型辅助文献闭环表）＋状态文件：`--member 王散曼 check 5`（学习线，非核验任务） |

### A6 覆盖性对账

| 校验线 | 文件数 | 对账说明 |
|---|---|---|
| A1 宁显泷 | 22（12＋学习9＋状态1） | run_all+核心 src+模型产物+02 模型文档 |
| A2 王启龙 | 99（90＋学习11－revise/exe已删） | 总纲/工具/PDF镜像/报告为主，多为工程与再生产物 |
| A3 衣思淼 | 21（14＋学习6＋状态1） | 数据集全链+描述符+数据字典+排名表 |
| A4 代维斯丹 | 22（18＋学习3＋状态1） | 对接/指纹/图+03 对接文档+7 个 __init__ |
| A5 王散曼 | 6（4＋练习1＋状态1） | 文献三件+新分子池源表 |
| 合计 | **170** | 附录A 名下文件＝原 138 ＋ 学习练习骨架 30 ＋ 成员状态文件 4 － 已删 revise_plain_leader.py 与 exe；另有不入本表的 git 跟踪文件（五人 待核文件/ 快照副本与 reports/pdf_build 中间产物），`git ls-files \| wc -l` = 271；快照以各自 快照清单.md 对账；3 处交叉复核已标注（fuse→衣、baseline→代、novel CSV→衣） |
