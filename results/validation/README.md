# 软件验证与诊断结果

software_checks.json：软件检查通过不等于科学验证。

gnn_model_diagnostic：PubChem建议结构 + 旧一般保肝标签，仅诊断；GNN AUC 0.929，17条测试仅3条旧阴性。不能与旧0.950作单因素比较，也不能称为MASH效力。

gnn_redock_diagnostic：正确CCD、独立ETKDG、固定受体坐标RMSD；FXR 0.8507通过，KEAP1 2.0822未过原2 angstrom。退出失败是正确拦截行为，不放行批量筛选。单种子不足以证明稳健性。

keap1_gate_20260905：多种子门控(exh16)与exh32敏感性、逐原子偏差归因、决策备忘录——KEAP1 2/5过、非采样问题、含核心错位；四选项待全组议定。

fxr_single_target_diagnostic_20260905：FXR单靶诊断全链(门控5/5过)——60候选制备/59对接/58进榜；产物与run_manifest源哈希。单靶榜不得当双靶共识结论。

fixes_verification_20260905.json：门控被拦那次运行的验证(pass 12/全榜blocked)；fixes_verification_20260905_fxr_run.json：FXR单靶运行验证(**18 pass / 1 partial / 1 open**)，F01-F20逐项明细。

所有运行日志/命令/输入哈希用于追溯，机器完成不代替成员签核。
