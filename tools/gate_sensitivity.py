# -*- coding: utf-8 -*-
"""门控采样敏感性检查：固定受体/盒子/种子，只提高 exhaustiveness。

用途：当 exh=16 多种子门控处于 2Å 边界时，区分"采样不足"与"协议不适配"。
不修改放行门槛(2Å)与多种子政策(≥3/5且中位数<2)；结果无论过否全部留档。
用法: python tools/gate_sensitivity.py <run_dir> <exh> [target ...]
"""
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]).resolve()
exh = int(sys.argv[2])
targets = sys.argv[3:] or ["FXR_LBD", "KEAP1_KELCH"]

src = run_dir.parents[2] / "src"  # final-aidd-screening/src
sys.path.insert(0, str(src))

import os
os.environ["HEPATO_RUN_ROOT"] = str(run_dir)
import importlib

import common

importlib.reload(common)
import redock

importlib.reload(redock)
from rdkit import Chem
from rdkit.Chem import AllChem

boxes = json.loads((run_dir / "docking" / "boxes.json").read_text(encoding="utf-8"))
out = {"run_dir": str(run_dir), "exhaustiveness": exh, "policy": redock.GATE_POLICY,
       "threshold_angstrom": 2.0, "targets": {}}

for t in targets:
    pdb, lig = redock.STRUCTS[t]
    box = boxes[t]
    receptor = redock.RCP / f"{t}_{pdb}.pdbqt"
    ref = redock.RCP / f"{t}_{pdb}_{lig}_crystal.sdf"
    ref_mol = next(iter(Chem.SDMolSupplier(str(ref), removeHs=False)))
    per_seed = {}
    for s in redock.GATE_SEEDS:
        initial = Chem.Mol(ref_mol)
        initial.RemoveAllConformers()
        p = AllChem.ETKDGv3()
        p.randomSeed = s
        if AllChem.EmbedMolecule(initial, p) != 0:
            raise SystemExit(f"{lig} seed={s} 构象失败")
        AllChem.MMFFOptimizeMolecule(initial, maxIters=500)
        lq = redock.LGD / f"{t}_{lig}_sens{exh}_s{s}.pdbqt"
        redock.pdbqt_from_mol(initial, lq)
        op = redock.OUT / f"{t}_{lig}_sens{exh}_s{s}_out.pdbqt"
        aff, _ = redock.run_vina(receptor, lq, op, box, exh=exh, seed=s)
        rms = redock.rmsd_first_pose(op, ref)
        per_seed[s] = {"rmsd": round(rms, 4), "affinity": aff}
        print(f"{t} exh={exh} seed={s}: RMSD={rms:.4f} score={aff}", flush=True)
    rmsds = sorted(v["rmsd"] for v in per_seed.values())
    n = len(rmsds)
    median = rmsds[n // 2] if n % 2 else (rmsds[n // 2 - 1] + rmsds[n // 2]) / 2
    out["targets"][t] = {"per_seed": per_seed, "median_rmsd": round(median, 4),
                         "n_pass": sum(1 for r in rmsds if r < 2.0),
                         "pass": bool(sum(1 for r in rmsds if r < 2.0) >= 3 and median < 2.0)}

dst = run_dir / "docking" / f"gate_sensitivity_exh{exh}.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"结果写入 {dst}")
for t, v in out["targets"].items():
    print(f"{t}: 中位 {v['median_rmsd']} 过门 {v['n_pass']}/{len(v['per_seed'])} -> {'PASS' if v['pass'] else 'FAIL'}")
