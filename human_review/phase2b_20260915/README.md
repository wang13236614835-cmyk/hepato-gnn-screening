# Phase 2B Human Review Compression (review-only)

- Project: `MASH_2026_002`
- Run: `phase2b_20260915`
- Original tasks: `181`
- Compressed units: `24`
- Compression ratio: `0.1326`
- This package is non-authoritative and does not change AIDD/GNN state.

## Repository boundary

This is a review-only staging package. It is not an authoritative scientific state, does not modify AIDD, does not modify historical GNN results, and must not be used for candidate release or model qualification. Completed reviews must be returned to Workbench for strict import.

Use `review_return.template.csv` or `review_return.template.json` for the canonical return interface; preserve all immutable AI/provenance fields and fill only the documented decision fields.


## 演示件（2026-09-22，非真人核验）

`demo_review_return_20260922.json`：AI 按完整核验流程做的**演示样例**（2 个压缩单元、3 条原始任务），
- `cr_b2e66c3f80331987`（P0，NR1H4）：REJECTED——ChEMBL 438711 原始记录无值/无单位/无关系符，assay 自注 "ND = No data"，排除出定量建模池；
- `cr_256cfdc9913f99a0`（P1，ACACA）：VERIFIED——ChEMBL 5104823/5104835 的 `IC50 > 30000 nM` 为真实删失记录，但建模须按删失处理、不得当精确值。
reviewer 已标"AI演示（非真人，不计入完成数）"；行级严格校验 3/3 通过（review_id/字段/必填项/不可变字段）。
用途：给组员展示核验路径（拉原始 JSON → 逐字段对照 → 判定 → 按格式回填）。**不得导入正式核验统计，不计入 real_human_review。**
