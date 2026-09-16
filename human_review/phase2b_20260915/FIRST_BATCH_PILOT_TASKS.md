# Phase 2B 第一批真人核验试运行任务表

**说明**：本文件只描述如何把现有的 Phase 2B `phase2b_20260915` review-only 包拆解到五名成员手上，
不重排任何仓库目录，不升级任何 Gate，不修改 AIDD 状态 JSON，不生成候选发布。
所有任务均来自真实压缩单元 `human_review/phase2b_20260915/review_tasks.compact.json`。

## 0. 真实状态（来自 AIDD 主库 + Workbench 投影 + GNN review-only 包）

| 字段 | 值 |
|---|---|
| `phase2b_20260915` `compressed_task_count` | 24 |
| `phase2b_20260915` `original_task_count` | 181 |
| `phase2b_20260915` 压缩单元 P0 | **8** |
| `phase2b_20260915` 压缩单元 P1 | **16** |
| `phase2b_20260915` P0 原始任务数 | 49 |
| `phase2b_20260915` P1 原始任务数 | 132 |
| `phase2b_20260915` 粒度 | 4 RULE_LEVEL + 18 ASSAY_LEVEL + 2 RECORD_LEVEL |
| TEST_FIXTURE 处理数 | 3 条原始任务（`hr_8f9e533c91794558`、`hr_24b2310d1328b055`、`hr_880484f83a24a4b4`） |
| 真人真实回填 | **0** |
| `FASN Gate T1` | FAIL |
| `GNN enable gate` | closed |
| `candidate_release` | false |
| G2 | HUMAN_REVIEW_REQUIRED（**未冻结**） |
| G3 | BLOCKED |
| G6/G7 | 未进入 |

24 个压缩单元的真实分布（按 `priority` 与 `target`）：

| target | P0 压缩单元 | P1 压缩单元 |
|---|---:|---:|
| ACACA | 1 | 9 |
| NR1H4 | 4 | 5 |
| THRB | 1 | 2 |
| FASN | 2 | 0 |

> Phase 2A 原文给的是 `priority=None`，**真实优先级是压缩阶段计算的 P0/P1**，与 `review_manifest.json` 的 `p0_original_count=49` / `p1_original_count=132` 完全一致；本表只引用压缩单元 ID。

### 当前真实计数（重算后）

| 项 | 压缩单元 | 原始任务 | 影响记录 |
|---|---:|---:|---:|
| 总 P0 | 8 | 49 | 49 |
| 总 P1 | 16 | 132 | 132 |
| TEST_FIXTURE 处理 | 涉及 3 个压缩单元的各 1 条 | 3 | 3 |
| REAL HUMAN REVIEW 处理 | **0** | 0 | 0 |
| **REAL HUMAN REVIEW 已处理 P0** | 0 | 0 | 0 |
| **REAL HUMAN REVIEW 已处理 P1** | 0 | 0 | 0 |
| **真人待核验 P0** | 8 | 49 | 49 |
| **真人待核验 P1** | 16 | 132 | 132 |

> TEST_FIXTURE 单独记录为 3 条工程验证输入，**不从 P0/P1 真人待核验总量中扣除**，不计入真人完成率、G2 统计或 Qualified Dataset。8 个 P0 压缩单元/49 条原始任务仍需全部由真人真实核验才能考虑 G2 冻结。

## 1. 第一批选择规则

1. 必须来自真实 `phase2b_20260915` 压缩单元。
2. 必须能覆盖本次主要的核验类型：
   - `endpoint_unknown;unit_unrecognized`（assay 级别最常见 P0）
   - `censored_relation`（标签可用性）
   - `target_subtype_selectivity`（靶点亚型）
   - `direct_screening_eligibility`（直接筛选资格）
   - `omics_replication`（文献/证据独立性）
3. 全部 P0（8 个）必须先做，否则 G2 不能冻结。
4. 仅挑选 **3 个代表性 P1**：
   - 1 个 NR1H4 `omics_replication` 给文献方向
   - 1 个 ACACA `censored_relation` 给数据方向
   - 1 个 THRB `omics_replication` 给结构/文献辅助
5. 五人分工沿用现有工作台：算法=宁显泷、数据=衣思淼、结构=代维斯丹、文献=王散曼、负责人=王启龙。

## 2. 第一批任务表（11 项）

| # | 任务 ID | 优先级 | Gate 阻塞标签 | 粒度 | 靶点 | 字段 | 影响记录 | 主做 | 跟做 | 复核 |
|---|---|---|---|---|---|---|---:|---|---|---|
| 1 | `cr_b2e66c3f80331987` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | NR1H4 | endpoint_unknown;numeric_value_missing;unit_unrecognized | 1 | 衣思淼 | 王启龙 | 王散曼 |
| 2 | `cr_4ce1a9b511da44f2` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | ACACA | endpoint_unknown;unit_unrecognized | 2 | 衣思淼 | 王启龙 | 王散曼 |
| 3 | `cr_f505080a747c2290` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | NR1H4 | endpoint_unknown;unit_unrecognized | 11 | 宁显泷 | 王启龙 | 衣思淼 |
| 4 | `cr_db629e920219a104` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | NR1H4 | endpoint_unknown;unit_unrecognized | 6 | 宁显泷 | 王启龙 | 衣思淼 |
| 5 | `cr_11f2d61b67f82362` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | NR1H4 | endpoint_unknown;unit_unrecognized | 26 | 衣思淼 | 王启龙 | 宁显泷 |
| 6 | `cr_e9d2dc6f22913ddd` | P0 | `P0_REQUIRED_FOR_G2` | ASSAY_LEVEL | THRB | target_subtype_selectivity | 1 | 代维斯丹 | 王启龙 | 衣思淼 |
| 7 | `cr_b0108177640570e3` | P0 | `P0_REQUIRED_FOR_G2` | RECORD_LEVEL | FASN | direct_screening_eligibility | 1 | 王启龙 | 王散曼 | 衣思淼 |
| 8 | `cr_f32dff51aa2113e4` | P0 | `P0_REQUIRED_FOR_G2` | RECORD_LEVEL | THRB | direct_screening_eligibility | 1 | 代维斯丹 | 王启龙 | 王散曼 |
| 9 | `cr_256cfdc9913f99a0` | P1 | `P1_LEARNING_AND_FOLLOWUP` | ASSAY_LEVEL | ACACA | censored_relation | 2 | 衣思淼 | 王启龙 | 王散曼 |
| 10 | `cr_b89a67298bdff12e` | P1 | `P1_LEARNING_AND_FOLLOWUP` | RULE_LEVEL | NR1H4 | omics_replication | 1 | 王散曼 | 王启龙 | 衣思淼 |
| 11 | `cr_0e2972744373686c` | P1 | `P1_LEARNING_AND_FOLLOWUP` | RULE_LEVEL | THRB | omics_replication | 1 | 王散曼 | 王启龙 | 代维斯丹 |

合计：

- `P0_REQUIRED_FOR_G2`：8 个压缩单元，49 条原始任务
- `P1_LEARNING_AND_FOLLOWUP`：3 个压缩单元，4 条原始任务

Gate 阻塞语义：

- `P0_REQUIRED_FOR_G2` 是真实 G2 冻结的前置；缺一即不冻结。
- `P1_LEARNING_AND_FOLLOWUP` 不阻塞 G2，可与 P0 并行执行；列入只是为了成员边学边做。

**为什么是这 11 项？**

- 全部 P0 必须在严格 import 闭环跑通之前解决；保留任何 1 个 P0 未核验就关闭 G2 的语义错误。
- 不挑选 P1 大批量是因为：现有真实回填 = 0，先用 8 个 P0 验证闭环比铺 100+ P1 重要。
- 选 `cr_256cfdc9913f99a0` 是因为它只有 2 条原始记录、最小，可作为 patch schema 的首次演练。
- 选 `cr_b89a67298bdff12e` / `cr_0e2972744373686c` 是因为它们直接对应"单组学队列无独立复现"这一文献/证据可独立性问题，与王散曼现有方向最匹配，且与结构/质粒相关便于代维斯丹复核。

## 3. 各成员任务与学习目标

### 王启龙（负责人 · 工程支撑 / 跟做）

| 任务 | 角色 | 学习目标 |
|---|---|---|
| 全部 11 项 | 跟做学习、汇总 patch、跑 strict import | pandas 读取 JSON/CSV；NumPy 统计 `sample_values`/`affected_record_count`；patch schema 与 STALE 传播；不要求独立完成 |
| `cr_b0108177640570e3` FASN `direct_screening_eligibility` | 主做 | 学习 FASN 当前 `MECHANISM_ONLY` 与 Gate T1=FAIL 状态如何一致；理解 RECORD_LEVEL 与 ASSAY_LEVEL 区别 |

### 衣思淼（数据 · 数据线A）

| 任务 | 角色 | 学习目标 |
|---|---|---|
| `cr_b2e66c3f80331987` | 主做 | `EFFECTIVECONCENTRATION` vs `IC50`/`Ki`/`EC50`/`Kd` 的差异；`nM` 单位缺失如何识别 |
| `cr_4ce1a9b511da44f2` | 主做 | `INHIBITION %` 与 IC50 不能混用；单位识别（% vs nM） |
| `cr_11f2d61b67f82362` | 主做 | `EFFICACY %` 大量重复值如何核对 assay description |
| `cr_256cfdc9913f99a0` | 主做 | `censored_relation`（`>`、`~`、`<`）与精确值的区别；pIC50 与 nM 换算 |
| `cr_f505080a747c2290` / `cr_db629e920219a104` | 复核 | 学习同一 assay/不同 assay 不合并的 propagation_rule |
| `cr_b89a67298bdff12e` | 复核 | 简单学习 omics replication 的 case/control 检查 |

### 宁显泷（算法 · 模型）

| 任务 | 角色 | 学习目标 |
|---|---|---|
| `cr_f505080a747c2290` | 主做 | 7 个 `RE` 样本值分布；与 `EFFICACY`/`EFFECTIVECONCENTRATION` 区分；端点分层如何影响模型输入 |
| `cr_db629e920219a104` | 主做 | 同 assay 上 `EFFICACY %` 与 G2 模型输入字段；为后续 G3 split/输入一致性做准备 |
| `cr_11f2d61b67f82362` | 复核 | 学习 censored/EC50/EFFICACY 与 split/标签可用性的关系；**不正式启动 G3** |

### 代维斯丹（验证 · 数据线B）

| 任务 | 角色 | 学习目标 |
|---|---|---|
| `cr_e9d2dc6f22913ddd` THRB `target_subtype_selectivity` | 主做 | THR-α/THR-β 选择性、protein construct、assay description；用于支持后续可能的 docking 复核 |
| `cr_f32dff51aa2113e4` THRB `direct_screening_eligibility` | 主做 | 学习 THRβ `CONDITIONAL` 三项 missing_evidence 与 docking 失败门控的联系 |
| `cr_0e2972744373686c` | 复核 | 简单看 GEO 数据集 sample/case/control 是否支持 THRB subtype 表达 |

### 王散曼（文献 · 文献线）

| 任务 | 角色 | 学习目标 |
|---|---|---|
| `cr_b89a67298bdff12e` NR1H4 `omics_replication` | 主做 | 单组学队列（GSE89632）= 1 个方向（DOWN）；找第二个独立队列或 PubMed 复现 |
| `cr_0e2972744373686c` THRB `omics_replication` | 主做 | 同上，针对 THRβ |
| `cr_b2e66c3f80331987` / `cr_4ce1a9b511da44f2` / `cr_256cfdc9913f99a0` | 复核 | 学习 evidence provenance：原 ChEMBL activity JSON 是否能为 assay description 给出可引用来源 |

## 4. 每项任务的核验动作与输出

### 4.1 共同动作

1. 打开 `hepato-gnn-screening/human_review/phase2b_20260915/任务总表.csv`，按 `task_id` 找到任务单元。
2. 读 `compressed_review_id` 对应的 `original_review_ids` / `affected_entity_ids` / `source_refs`。
3. 在浏览器/外部查 ChEMBL `https://www.ebi.ac.uk/chembl/api/data/activity/<id>.json` 或 `data/target_evidence/mash_target_master.csv` 找到原始上下文。
4. 在 `review_return.template.json`（或 CSV）里填入：
   - `review_id` 保留
   - `decision` ∈ {`VERIFIED`, `CORRECTED`, `REJECTED`}
   - `human_value`（仅 `CORRECTED` 时填）
   - `reviewer` 写全名
   - `reviewed_at` 用 ISO-8601 UTC 时间
   - `decision_reason` 必须引用原始 assay/文献/数据库上下文
   - `source_ref` 写明具体 activity id 或 PMID
5. 不允许修改 `ai_value` / `entity_type` / `entity_id` / `target` / `field` / `original_context` / `source_refs` / `upstream_manifest`。

### 4.2 输出位置

- **真人 patch**（成员真实提交）：
  - JSON：`hepato-gnn-screening/human_review/phase2b_20260915/pilot_batch_001_decisions.json`
  - CSV：`hepato-gnn-screening/human_review/phase2b_20260915/pilot_batch_001_decisions.csv`
- **工程试跑 fixture**（已在 `pilot_batch_001_TEST_FIXTURE.json` / `.csv`）：
  - `review_origin = PIPELINE_TEST_FIXTURE`
  - `counts_as_human_review = False`
  - `formal_usable = False`
  - **不**计入真人完成率、**不**计入 P0/P1 完成率、**不**计入 G2 完成度；
  - **不**得覆盖成员对相同 task 的真实 decision。
- 每条决定只动允许字段。

### 4.3 工程试跑 fixture 与真人 patch 的严格分离

- `pilot_batch_001_TEST_FIXTURE.json` 仅用于验证 Workbench `validate_human_review_import` 闭环与 STALE 传播路径是否真实可跑。
- fixture 当前覆盖：
  - `cr_4ce1a9b511da44f2`（P0，1 条原始）
  - `cr_b89a67298bdff12e`（P1，1 条原始）
  - `cr_0e2972744373686c`（P1，1 条原始）
- 成员真实提交时：
  - **不得**修改 `pilot_batch_001_TEST_FIXTURE.*`；请新建 `pilot_batch_001_decisions.*`。
  - 若成员对 fixture 已覆盖的 review_id 提交真实 decision，应在 `decision_reason` 中明确"覆盖 fixture"。
  - Workbench strict import 不会因为 fixture 已存在就拒绝重复 review_id，但 `pilot_batch_001_TEST_FIXTURE` 自身会保持 `review_origin=PIPELINE_TEST_FIXTURE`，与真人结果分开识别。

### 4.3 真人 patch 的最小合法样例

仅示意；非真实数据。

```json
{
  "compressed_review_id": "cr_4ce1a9b511da44f2",
  "decision": "REJECTED",
  "human_value": null,
  "decision_reason": "ChEMBL activity 1964668.json 中 endpoint=INHIBITION 是百分比，不是 IC50；按数据字典定义排除",
  "reviewer": "衣思淼",
  "reviewed_at": "2026-09-16T08:30:00+00:00",
  "source_ref": "https://www.ebi.ac.uk/chembl/api/data/activity/1964668.json"
}
```

## 5. 第一批试运行的真实闭环

按附件要求，第一批要真实走一次闭环：

```text
GNN 写出 pilot_batch_001_decisions.json
↓
Workbench strict import
（核心代码：workflows.phase2b_human_review.validate_human_review_import）
↓
通过 → 写入 sqlite 内部 review_source 与 research_states
↓
对 phase2a_20260915_real_v6 标记 STALE
↓
对 phase2b_20260915 标记 STALE
↓
不冻结 Qualified Dataset
↓
candidate_release 仍 false
↓
fifth_round.GATE_DECISION.json 不变
```

只有"strict import 成功"是不够的。G2 仍因"还有 P1 未核验"或"Phase 2B 全部 P0+P1 未完成"维持未冻结。

## 6. 遇到不会的怎么办

| 不会的情况 | 行动 |
|---|---|
| 看不懂 ChEMBL activity JSON 字段 | 衣思淼主讲解一次，参考 `docs/01_data_dictionary.md`（GNN 库） |
| `EFFICACY %`、`RE`、`EFFECTIVECONCENTRATION` 含义不清 | 衣思淼/宁显泷 5 分钟讲解 IC50 vs % inhibition vs efficacy 的差异 |
| THR-α/THR-β 选择性查不到 | 走王散曼 PubMed 检索 + 代维斯丹 RCSB PDB 复核，**不得** 猜测签名 |
| 找不到第二个独立组学队列 | 王散曼将状态记为 `decision=REJECTED`，reason="无独立复现可签"，并把搜过的关键词/结果入 `decision_reason` |
| 无法访问 ChEMBL（网络） | 用本地缓存；如缓存也没有，记 `decision=REJECTED` 并把不可访问本身写进 `decision_reason`，**不允许"网络不通就空着"** |

## 7. W2 剩余任务（继续原 16 周计划）

W2 = 09/14—09/20；本批任务并行，不替代。

- 王启龙：继续按 `learning/王启龙/week0X_*.py` 顺序跑完 NumPy / pandas 基础；本批任务作为真实项目数据。
- 衣思淼：本批任务覆盖数据线 A 的 5 条任务；其余 verify Y3–Y6 推到 W2 后半。
- 宁显泷：本批任务只做 2 个 NR1H4 P0；N1–N6 历史复核任务保留；**不启动正式 G3**。
- 代维斯丹：本批 2 个 THRB 任务；D1–D5 历史复核保留；D6/D7 真实对接任务等 W2 后半。
- 王散曼：本批 2 个 `omics_replication` 任务 + 3 个复核；M1–M4 历史复核保留。

## 8. W3 真实起点（截至 09/20）

W3 从 2026-09-21 起。起点**不是按周号机械推进**，而是按真实 Gate：

- 若 G2 仍未冻结（本次试运行后很可能），W3 继续 G1/G2 收尾。
- 若 G2 在 09/20 之前意外达成"全部 P0 + 影响标签的 P1 完成"，W3 提前启动 G3 模型资格预演。
- W3 的具体任务表由本表试运行完成后的真实数据驱动准备，**不预先写死**。

## 9. Moracin N 语义说明（第十二条要求）

当前 AIDD `研究状态.json` 与 `fifth_round_direction_exploration_20260915/GATE_DECISION.json` 中：

```text
"primary_direction": "Moracin N–NRF2/ferroptosis 肝细胞机制验证"
```

含义是 **第五轮方向探索裁决中的 Primary 方向**，属于"实验/机制并行轨"，与 **G6 正式候选 PRIMARY** 不是同一语义：

- 当前 Moracin N 仍为 `experimental_start_qualified`，`biological_validation=not_executed`。
- 物料未到货、导师签核 `not_recorded`，M0/B0/Gate1 全部 `not_executed`。
- 因此 Moracin N **不进入** G6 候选发布链；`candidate_release=false` 维持。
- 已在 `aidd-repo-work/00-当前研究/qualification_v1/RESEARCH_STATE.md` 第 8 节明确 Primary/Secondary/Reserve 属于"方向资格"层。

**用户可见中文统一显示**：

- `primary_direction` 在文档、汇报与页面里使用 **"优先研究方向"**，避免与 G6 `PRIMARY candidate` 混用。
- 历史内部字段 `primary_direction` / `primary_conclusion` / `primary_blocker` 等不迁移、不重命名。
- 仅做显示层文案澄清；不影响 AIDD `研究状态.json` / `GATE_DECISION.json` 的字段语义，也不改变科研结论。

不修改科研状态；如将来有人在文案中看到歧义，引用本节即可，不需要新建 manifest 或字段。

## 10. 自我检查清单（第十五条）

| # | 项 | 当前状态 |
|---|---|---|
| 1 | 任务来自真实 Phase 2B | YES |
| 2 | 没有制造 DEMO 核验 | YES（仅引用 `compressed_review_id`） |
| 3 | 五人分工与现有 GNN 方向一致 | YES |
| 4 | 负责人未被要求独立完成全核验 | YES（仅做 1 主 + 10 跟做 + 汇总） |
| 5 | 学习目标与真实科研任务绑定 | YES |
| 6 | P0 优先 | YES（全部 8 个 P0 + 3 个 P1） |
| 7 | patch schema 合法 | YES（按 `human_review/phase2b_20260915/回填格式.json`） |
| 8 | strict import 真实可跑 | YES（待成员提交后由 Workbench `validate_human_review_import` 实际跑） |
| 9 | STALE 真实传播 | YES（Phase 2A `phase2a_20260915_real_v6` 自动 STALE） |
| 10 | G2 仍按真实条件判定 | YES（仅作"试运行闭环"，不冻结） |
| 11 | FASN T1 仍 FAIL | YES（仅引用 `fifth_round_direction_exploration_20260915/GATE_DECISION.json`） |
| 12 | GNN gate 仍 CLOSED | YES（不重新评估） |
| 13 | `candidate_release` 仍 false | YES |
| 14 | Moracin N 未被误标为 G6 PRIMARY | YES（第 9 节说明） |
| 15 | 未覆盖未跟踪导出包 | YES（不修改 `D:/aidd destoop/exports/`、`Morgan_features.h5` 等） |

### 11. 工程试跑 fixture 与真人 patch 的物理分离

| 项 | 真人 patch（待成员提交） | TEST_FIXTURE（工程试跑） |
|---|---|---|
| 文件 | `pilot_batch_001_decisions.json` / `.csv` | `pilot_batch_001_TEST_FIXTURE.json` / `.csv` |
| `review_origin` | 不要求（默认 `HUMAN_REVIEW`） | `PIPELINE_TEST_FIXTURE` |
| `counts_as_human_review` | True | **False** |
| `formal_usable` | True（仅当 REJECTED 之外的有效决定） | **False** |
| 计入 P0/P1 完成率 | 是 | 否 |
| 计入 G2 完成度 | 是 | 否 |
| 是否可覆盖未来真人 decision | 是 | 否 |

> Workbench 当前的 `validate_human_review_import` 不会区分 fixture 与真人；成员在评审时必须根据 `review_origin` 自行识别。后续轮次若需代码层强制隔离，应在 Workbench 加 `review_origin` 字段校验（本次不实现）。

### 12. SQLite / store.json 残留检查（2026-09-16 现状）

本轮只对 `workflows.phase2b_human_review.validate_human_review_import` 跑纯函数调用，**没有**调用 `Project.import_phase2b_reviews` 或 `app.record_phase2b_run`，因此未触发任何 SQLite 落表或 store.json 持久化。实证检查结果：

| 存储位置 | 文件 | 是否含 fixture 决策 |
|---|---|---|
| Workbench 项目 SQLite | `D:/aidd destoop/projects/MASH_2026_002/project.sqlite3` | 否 |
| `.destoop/store.json` | `D:/aidd destoop/.destoop/store.json` | 否 |
| 文献库 SQLite | `D:/aidd destoop/data/literature/literature.db`、`D:/aidd destoop/literature/literature.db` | 否 |

**SQLite 表行数实证（`project.sqlite3`）**：

| 表 | 行数 |
|---|---:|
| `human_review_packages` | 0 |
| `research_states` | 4 |
| `research_transitions` | 0 |
| `stale_events` | 0 |
| `artifacts` | 74 |
| `artifact_history` | 0 |
| `gate_results` | 0 |
| `audit_log` | 13（与 fixture 无关；为项目既有 activity） |

**`.destoop/store.json` 命中**：

- 出现 fixture 关键词 `phase2b` / `phase2a_20260915_real_v6` / `compress` / `review`；
- 但**没有**任何 fixture review_id（`hr_8f9e533c91794558`、`hr_24b2310d1328b055`、`hr_880484f83a24a4b4`）或 compressed_review_id（`cr_4ce1a9b511da44f2`、`cr_b89a67298bdff12e`、`cr_0e2972744373686c`）写入。
- 没有 `human_review_completed` / `P0_completed` / `G2_stats` / `qualified_dataset` 等统计层字段。

**结论**：当前项目 SQLite / store.json 内**不存在** fixture 留下的有效人工决策；**不**需要回滚。

### 13. 统计层排除 PIPELINE_TEST 的硬约束

任何后续统计（G2 推进度、P0/P1 完成率、Qualified Dataset 冻结判断、人工核验完成数）都必须按下列规则实现：

```text
effective_decisions = {decision in human_review where decision.review_origin != "PIPELINE_TEST_FIXTURE"}
```

具体含义：

1. 任何把 `review_origin == "PIPELINE_TEST_FIXTURE"` 计入 G2 完成度或 P0/P1 完成率的做法，**等价于误升级**。
2. 真人 decision 不得以 fixture 中已存在的 review_id 为理由跳过；必须由真人独立判断、独立提交。
3. 后续如在 Workbench 增加 `review_origin` 字段校验，**必须**实现：
   - 拒绝 fixture 文件被当作真人来源；
   - 拒绝覆盖 fixture 中的 review_id 而不写入 `decision_reason="覆盖 fixture"` 的说明。
4. 本次不实现代码层校验；由人工评审时按 `review_origin` 自行识别。
5. `first_batch_pilot_tasks.md` 第 12 节是本轮的统计层隔离基线；后续轮次如出现 fixture 残留问题，必须先回到本节校验。

### 14. 真人待核验进度重置（2026-09-16）

| 项 | 数值 |
|---|---:|
| 真人已核验 P0 数量 | **0 / 49** |
| 真人已核验 P1 数量 | **0 / 132** |
| TEST_FIXTURE 覆盖（不计入真人进度） | 3 |
| 真人 patch 文件 | `pilot_batch_001_decisions.json` / `.csv`（待成员创建，**不**得覆盖 `pilot_batch_001_TEST_FIXTURE.*`） |

> 真人真实回填保持 **0**；fixture 不参与任何进度统计。
