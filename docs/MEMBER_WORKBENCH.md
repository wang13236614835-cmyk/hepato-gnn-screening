# 全员工作台（按人导航）MEMBER WORKBENCH

> 一句话：**一级目录就是人**——仓库根目录五个全名文件夹
> （王启龙/ 宁显泷/ 衣思淼/ 代维斯丹/ 王散曼），各自里面放自己的
> `工作台.md`（任务/记录一份）＋`打卡.html`（学习·打卡）＋
> `待核文件/`（**名下要核验的具体文件快照副本**＋快照清单.md）。
> 数据、文献、代码、结果**全队公用一份**（根目录 data/ literature/ src/
> results/ docs/，为流水线工作原件，不可删）；总表在
> `docs/VERIFY_TASKS.md`，文件映射见其附录A，操作手册
> `docs/VERIFY_MANUAL.md`。


> **2026-09-03 新增**:真实对接已完成 144 次(`results/docking/real/`),新任务 D6/D7/N7/Y7/M5/L6
> 于 9/20 暑假复核完成后开展(见 `reports/真实对接与统一筛选报告.md`);暑假任务与学习打卡照旧。

## 全队速查表

| 成员 | 我的文件夹 | 角色 | 校验线 | 任务编号 | 名下文件 | 分项时限 |
|---|---|---|---|---|---|---|
| 王启龙 | [王启龙/](../王启龙/工作台.md) | 负责人·工程支撑 | 辅助/工程（A2） | L1–L5 | 90 | 09-20 |
| 宁显泷 | [宁显泷/](../宁显泷/工作台.md) | 算法 | 代码验证（A1） | N1–N6 | 12 | 09-13 |
| 衣思淼 | [衣思淼/](../衣思淼/工作台.md) | 数据 | 数据线A：数据集与排名（A3） | Y1–Y6 | 14 | 09-13 |
| 代维斯丹 | [代维斯丹/](../代维斯丹/工作台.md) | 验证 | 数据线B：对接·指纹·图（A4） | D1–D5 | 18 | 09-13 |
| 王散曼 | [王散曼/](../王散曼/工作台.md) | 文献 | 文献（A5） | M1–M4 | 4 | 09-20 |

通用五步（每人相同，细节见自己那节）：
① 拿到仓库（clone 或 Download ZIP）→ ② 先读 `docs/VERIFY_TASKS.md`
自己的小节＋附录A → ③ 按任务表逐条核验（预期值以 VERIFY_MANUAL 为准）→
④ 结果记 VERIFY_TASKS 第 4 节、问题记第 5 节（A 级先停线报告）→
⑤ 每周在自己打卡页打勾、周五生成周报发导师。

---

## 王启龙（负责人 · 工程支撑）

- **要做什么**：环境排障、汇总五人核验记录、verify.py 截图存 `results/logs/`、
  打 `v1.0-summer` 基线标签、每周日 `git push` 备份、周一组会派活；
  A/B 级问题的工程修复与全量复跑（L1–L5，明细见 VERIFY_TASKS §2.2）。
- **是什么**：全流程托底人——别人核验卡住时由你修到能继续。
- **怎么操作**：`python tools/semester_flow.py check 1 --deep`（工具自检）；
  `python reports/pdf_build/verify.py`（45 项截图存档；旧工作库口径·审计F11，最终包另以 `tools/verify_fixes.py` 20 项验收）；`git tag -a v1.0-summer`。
- **名下文件（90 个，明细附录A·A2）**：总纲四件＋环境、组会纪要、WP 计划、
  personal 档案、tools/ 工具链、reports/ 报告与 27 个 PDF 镜像；learning/ 按人五份（练习骨架已全部生成）。
- **学习线**：Git 进阶→校验自动化→RDKit→数据库 API→对接→PyTorch→PyG→
  校准→大模型辅助核验→打包结题（16 周逐周见打卡页）。

## 宁显泷（算法 · 代码验证）

- **要做什么**：N1 一键复现 12 关键行逐字一致；N2 连跑两次 md5"一致"；
  N3 `verify.py` 45 项全过（旧库口径·F11）；N4 解析器 5 用例；N5 超参（p_drop=0.3/T=30/epoch=300）
  代码与文档互查；N6 融合公式（0.45/0.35/0.20、域外×0.9）核对。
- **是什么**：证明"代码跑得对、结果可复现"的第一责任人。
- **怎么操作**：`python run_all.py`；`python reports/pdf_build/verify.py`；
  按 VERIFY_MANUAL §2–§3.1 逐条执行；输出存 `results/logs/`。
- **名下文件（12 个，附录A·A1）**：run_all.py、smiles_graph.py、gnn.py、
  dataset.py、baseline.py（代维斯丹复核）、fuse.py（衣思淼复核）、
  verify.py、docs/02_model_notes.md、metrics×2、predictions×2。
- **学习线**：比全队早三周学 PyTorch→PyG 分子图→GCN/GIN 对照→正式迁移
  （AUC≥0.967）→MC Dropout 把握度→温度校准（ECE<0.10 且 ρ≥0.6）→收工。

## 衣思淼（数据 · 数据线A）

- **要做什么**：Y1 原始表抽查（89 行/HP 48/DC 40/HP-015 口径）；Y2 骨架划分
  隔离（黄芩苷 scaffold 不跨集合）；Y3 排名表核验（61 行/Top-3/第 7 行水飞蓟宾/
  NV-011 域外）；Y4 融合公式手工验算 ±0.002（第 1/7/10 名）；Y5 描述符复算
  （槲皮素 MW=302.24）；Y6 适用域（h*=0.362、域外 7/12）。
- **是什么**：证明"数字没被编造"的第一责任人。
- **怎么操作**：Excel 打开 CSV 按口径数行筛选；`python -c` 跑 §3.2 描述符用例；
  验算过程（截图/手算照片）存 `results/logs/`。
- **名下文件（14 个，附录A·A3）**：raw/tcm_seed_compounds.csv、processed×3、
  splits×3、src/data×3、descriptors.py、docs/01_data_dictionary.md、
  ad_report.csv、final_ranking.csv。
- **学习线**：Pandas→RDKit→ChEMBL/PubChem→数据扩充（≥1000 条）→新切分
  零泄漏→全库体检→SwissADME 对照→融合权重敏感性→数据章节。

## 代维斯丹（验证 · 数据线B）

- **要做什么**：D1 指纹确定性（两次调用一致）；D2 演示对接重跑
  （-5.46 vs -5.05 逐字节复现）；D3 四张图与 CSV 逐图对照；D4 盒子参数
  （FXR=1OSH、Keap1=2FLU）代码与文档互查；D5 演示模式局限性确认＋
  WP2 真实对接排期建议。
- **是什么**：证明"打分与图忠实于代码输出"的第一责任人。
- **怎么操作**：按 VERIFY_MANUAL §3.3/§3.6；重跑 `src/docking/mock_docking.py`
  比对 `results/docking/docking_scores.csv`；逐图结论一行记录。
- **名下文件（18 个，附录A·A4）**：fingerprints.py、grid_box.py、
  mock_docking.py、run_vina.sh、docs/03_docking_protocol.md、plots.py、
  docking_scores.csv、figures×4、`__init__.py`×7。
- **学习线**：Vina 入门→受体/配体准备→重对接 RMSD<2Å→服务器批量对接
  （100 分子×2 靶点）→真实分数换演示分→排名 v2→结合图。

## 王散曼（文献 · 文献线）

- **要做什么**：M1 抽 10 条正样本到 PubMed/CNKI 溯源（化合物名＋
  hepatoprotective/liver injury），literature/01 回填"已核对"；M2 Top-10 逐条
  证据专查（重点 NV-009 松脂素、NV-010 落叶松脂素）；M3"引用为整理稿"声明
  口径更新；M4 evidence_level 分布 CSV 与文献稿交叉计数。
- **是什么**：证明"每条证据可溯源"的第一责任人。
- **怎么操作**：PubMed 检索→拿 PMID/链接→在 literature/01 对应条目回填
  "已核对✓＋PMID"；核对台账随核随记；核不了的降级或删除进处置台账。
- **名下文件（4 个，附录A·A5）**：literature/01、02、03＋
  data/raw/novel_terpenes_lignans.csv（与衣思淼 Y1 交叉复核）。
- **学习线**：PubMed 检索→证据分级规则→12 新分子文献地图→标签抽检 30 条
  →双靶点机制精读（各 5 篇）→A 级 100% 核对→实验衔接一页纸。

---

## 问题与记录去哪

- 完成：`docs/VERIFY_TASKS.md` §4 完成记录表（日期/任务编号/签名）；
- 问题：`docs/VERIFY_TASKS.md` §5 问题登记表（A 致命停线 / B 偏差登记 / C 建议）；
- 每周证据：各打卡页「✅ 打卡台账」＋ `learning/<姓名>/` 学习产物（骨架已生成；核验 `python tools/semester_flow.py --member <姓名> check <周号>`，负责人不加 --member）；
- 汇总：王启龙每周五收齐，周日 `git push`。
