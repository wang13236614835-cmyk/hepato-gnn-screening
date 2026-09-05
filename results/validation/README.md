# 软件验证与诊断结果

software_checks.json：软件检查通过不等于科学验证。

gnn_model_diagnostic：PubChem建议结构 + 旧一般保肝标签，仅诊断；GNN AUC 0.929，17条测试仅3条旧阴性。不能与旧0.950作单因素比较，也不能称为MASH效力。

gnn_redock_diagnostic：正确CCD、独立ETKDG、固定受体坐标RMSD；FXR 0.8507通过，KEAP1 2.0822未过原2 angstrom。退出失败是正确拦截行为，不放行批量筛选。单种子不足以证明稳健性。

所有运行日志/命令/输入哈希用于追溯，机器完成不代替成员签核。
