# ACACA Phase 2B 人工核验任务

## cr_4ce1a9b511da44f2 · P0 · ASSAY_LEVEL

- 影响原任务：2；影响记录：2；阻塞 G2：是
- 当前 AI 判断：{'unique_value_count': 2, 'sample_values': [{'endpoint': 'INHIBITION', 'value': '35.0', 'relation': '='}, {'endpoint': 'INHIBITION', 'value': '7.0', 'relation': '='}]}
- 为什么需要人工：ACACA 的 endpoint/type 无法从当前记录可靠判定。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/1964668.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964669.json
- 具体检查：核对原始 assay description/原文，确认 IC50、Ki、EC50、Kd 或排除。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_300bb09225b6f90a · P1 · ASSAY_LEVEL

- 影响原任务：9；影响记录：9；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/3013212.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013213.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013214.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013234.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013239.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013243.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013249.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013256.json; https://www.ebi.ac.uk/chembl/api/data/activity/3013297.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_256cfdc9913f99a0 · P1 · ASSAY_LEVEL

- 影响原任务：2；影响记录：2；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/5104823.json; https://www.ebi.ac.uk/chembl/api/data/activity/5104835.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_62cdfc25ac220ee0 · P1 · ASSAY_LEVEL

- 影响原任务：19；影响记录：19；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/1810279.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810280.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810281.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810286.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810289.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810293.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810294.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810295.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810296.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810297.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810306.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810307.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810308.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810309.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810310.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810311.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810312.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810313.json; https://www.ebi.ac.uk/chembl/api/data/activity/1810316.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_4fac4db2eaf26ef9 · P1 · ASSAY_LEVEL

- 影响原任务：13；影响记录：13；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/1733352.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733768.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733796.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733801.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733809.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733819.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733825.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733835.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733859.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733879.json; https://www.ebi.ac.uk/chembl/api/data/activity/1734026.json; https://www.ebi.ac.uk/chembl/api/data/activity/1735157.json; https://www.ebi.ac.uk/chembl/api/data/activity/1735178.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_d27d0bfce693a39a · P1 · ASSAY_LEVEL

- 影响原任务：20；影响记录：20；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/1964584.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964614.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964616.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964617.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964618.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964619.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964620.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964621.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964622.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964623.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964624.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964625.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964626.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964628.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964629.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964630.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964631.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964632.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964633.json; https://www.ebi.ac.uk/chembl/api/data/activity/1964634.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_14c54e7bf8e0c424 · P1 · ASSAY_LEVEL

- 影响原任务：27；影响记录：27；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/2019270.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019272.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019273.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019274.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019275.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019276.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019277.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019278.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019279.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019280.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019281.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019282.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019283.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019284.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019285.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019286.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019287.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019288.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019289.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019290.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019291.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019292.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019293.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019294.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019295.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019296.json; https://www.ebi.ac.uk/chembl/api/data/activity/2019297.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_50bee0bf3d106579 · P1 · ASSAY_LEVEL

- 影响原任务：6；影响记录：6；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': '30000.0', 'relation': '>'}
- 为什么需要人工：ACACA 的同类 assay 记录含 <、> 或 ~，不能自动当作精确标签。
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/1820431.json; https://www.ebi.ac.uk/chembl/api/data/activity/1820440.json; https://www.ebi.ac.uk/chembl/api/data/activity/1820441.json; https://www.ebi.ac.uk/chembl/api/data/activity/1820444.json; https://www.ebi.ac.uk/chembl/api/data/activity/1820445.json; https://www.ebi.ac.uk/chembl/api/data/activity/1820446.json
- 具体检查：核对原始 assay 数值和 relation；决定保留 censored、修正 relation，或排除记录。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_c6b42c3f46de46e8 · P1 · ASSAY_LEVEL

- 影响原任务：1；影响记录：1；阻塞 G2：否
- 当前 AI 判断：{'endpoint': 'IC50', 'value': None, 'relation': '='}
- 为什么需要人工：numeric_value_missing；unit_unrecognized
- 去哪里查：https://www.ebi.ac.uk/chembl/api/data/activity/5104831.json
- 具体检查：核对原始 assay 上下文；决定 VERIFIED、CORRECTED 或 REJECTED。censored/endpoint/subtype 未关闭前不得进入正式训练。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

## cr_25179fb49214bd5c · P1 · RULE_LEVEL

- 影响原任务：1；影响记录：1；阻塞 G2：否
- 当前 AI 判断：{'datasets': [{'dataset': 'GSE89632', 'logFC': 1.9, 'adjusted_p': 0.003, 'species': 'Homo sapiens', 'sample_count': '45', 'case_definition': 'MASH liver biopsy', 'control_definition': 'healthy liver tissue', 'platform': 'RNA-seq'}], 'replication_count': 1, 'direction': 'UP'}
- 为什么需要人工：ACACA 只有单一或未确认的疾病组学队列。
- 去哪里查：D:/aidd destoop/data/pilot/03_targets.csv#row=5:Q13085; D:/aidd destoop/data/target_evidence/mash_target_master.csv#row=1:Q13085; D:/aidd destoop/data/target_evidence/mash_target_master.csv#row=2:Q13085; D:/aidd destoop/data/target_evidence/mash_target_master.csv#row=3:Q13085; D:/aidd destoop/data/targets_pilot.csv#row=4:Q13085; https://www.ebi.ac.uk/chembl/api/data/activity/1733352.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733768.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733796.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733801.json; https://www.ebi.ac.uk/chembl/api/data/activity/1733809.json
- 具体检查：补充独立队列并核对样本、case/control 和方向。
- 填写：`VERIFIED` / `CORRECTED` / `REJECTED`，理由必须引用原始上下文。

