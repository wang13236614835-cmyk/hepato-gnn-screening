# 核验填写说明

1. 使用 `任务总表.csv` 选择一个裁决单元；不要按影响记录数重复填写。
2. 去 `where_to_check`/`original_review_ids` 对应的原始上下文核对。
3. `review_return.template.csv`/`review_return.template.json` 是标准回填接口；也可以提交保留同一字段的自定义 CSV/JSON。
4. 只填写 `回填格式.json` 中允许变更的字段：decision、human_value、decision_reason、reviewer、reviewed_at、source_ref、optional_note。
5. 保留 ai_value/AI 暂定判断、entity、field、original_context、source_refs 和 upstream manifest，不得覆盖。
6. `VERIFIED`=原值被原始来源确认；`CORRECTED`=来源支持新值；`REJECTED`=排除并写明理由。
7. 必须写 reviewer、reviewed_at、source_ref 和可追溯理由；Workbench 会拒绝不完整回填。
8. 提交前保留 `review_id`；压缩单元也可使用 `compressed_review_id`，Workbench 会按 `original_review_ids` 无损展开。
