#!/usr/bin/env bash
# 服务器端真实对接脚本（批量 Vina）
# 负责人: 代维斯丹（验证组）
# 依赖: AutoDock Vina >= 1.2, ADFR suite (prepare_receptor4/prepare_ligand4)
# 用法: bash run_vina.sh <ligand_dir> <output_dir>
set -euo pipefail

LIG_DIR="${1:?用法: run_vina.sh <配体pdbqt目录> <输出目录>}"
OUT_DIR="${2:?用法: run_vina.sh <配体pdbqt目录> <输出目录>}"
mkdir -p "$OUT_DIR"

# 受体预处理(一次性):
#   prepare_receptor4.py -r 1OSH_fxr.pdb -o fxr.pdbqt -A hydrogens
#   prepare_receptor4.py -r 2FLU_keap1.pdb -o keap1.pdbqt -A hydrogens
# 盒子参数见 src/docking/grid_box.py

run_target () {
    local REC="$1" CENTER="$2" SIZE="$3" TAG="$4"
    for lig in "$LIG_DIR"/*.pdbqt; do
        base=$(basename "$lig" .pdbqt)
        vina --receptor "$REC" \
             --ligand "$lig" \
             --center_x "$(echo "$CENTER" | cut -d, -f1)" \
             --center_y "$(echo "$CENTER" | cut -d, -f2)" \
             --center_z "$(echo "$CENTER" | cut -d, -f3)" \
             --size_x "$(echo "$SIZE" | cut -d, -f1)" \
             --size_y "$(echo "$SIZE" | cut -d, -f2)" \
             --size_z "$(echo "$SIZE" | cut -d, -f3)" \
             --exhaustiveness 16 --num_modes 3 \
             --out "$OUT_DIR/${TAG}_${base}_out.pdbqt" \
             > "$OUT_DIR/${TAG}_${base}.log" 2>&1
    done
}

# FXR (PDB 1OSH):  center 15.2,3.8,24.5  size 22,22,24
run_target fxr.pdbqt "15.2,3.8,24.5" "22,22,24" FXR
# Keap1 (PDB 2FLU): center -11.5,20.4,-6.2 size 20,20,20
run_target keap1.pdbqt "-11.5,20.4,-6.2" "20,20,20" KEAP1

# 汇总打分: python src/docking/collect_vina_logs.py "$OUT_DIR"
