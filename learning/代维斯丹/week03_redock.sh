#!/usr/bin/env bash
# 第 3 周 学习练习骨架 · 由 semester_flow.py scaffold 3 生成（代维斯丹）
# 任务: 两蛋白去水加氢＋原配体取重塞回（重对接）：偏移各<2埃，排查过程留痕
# 预期契约: [FLOW] fxr_rmsd={f} keap1_rmsd={f} both_lt2={bool}
#           判定: [('both_lt2', '==', 'True')]
# 依赖: 服务器 Vina/obabel（服务器运行；跑通后本机可 check 3 或 record 补录）
# 完成后核验: python tools/semester_flow.py --member 代维斯丹 check 3
set -euo pipefail
# TODO 1: 两个蛋白结构处理（去水、加氢、转 pdbqt）——盒子中心用 src/docking/grid_box.py，勿手改
# TODO 2: 抽出 1OSH / 2FLU 各自的原配体（保留原始坐标作参照）
# TODO 3: Vina 重对接（同盒子同种子，exh=16）
# TODO 4: 对接口袋构象 vs 原配体 计算 RMSD（fxr_rmsd / keap1_rmsd）
# TODO 5: both_lt2=两个 RMSD 都 <2 才为 True；≥2 按 WP2 排查清单记录过程
echo "[FLOW] 未完成：先实现上方 TODO（实测值禁止手填）"; exit 1
# 实现后把上一行替换为:
# echo "[FLOW] fxr_rmsd=<实测> keap1_rmsd=<实测> both_lt2=<True|False>"
