# -*- coding: utf-8 -*-
"""KEAP1 redock 偏差模式分析：无叠合、对称匹配下逐原子偏差，按基团归类。

目的：刻画"未过2Å门控"的失败模式（核心药效团错位 vs 外围芳环翻转），
供全组决定换结构/改判据/换靶点时参考。不修改门控。
"""
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(run_dir.parents[2] / "src"))

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolAlign
from meeko import PDBQTMolecule
from meeko.rdkit_mol_create import RDKitMolCreate

RDLogger.DisableLog("rdApp.*")

ref = next(iter(Chem.SDMolSupplier(str(run_dir / "docking/receptors/KEAP1_KELCH_4IQK_IQK_crystal.sdf"), removeHs=False)))
ref = Chem.RemoveHs(ref)
ref_smiles = Chem.MolToSmiles(ref)
conf_ref = ref.GetConformer()

GROUPS = {
    "naphthalene_core": Chem.MolFromSmarts("c1ccc2ccccc2c1"),
    "sulfonamide_S": Chem.MolFromSmarts("[SX4](=O)(=O)[NX3]"),
    "methoxy_O": Chem.MolFromSmarts("COc"),
    "benzene_ring": Chem.MolFromSmarts("c1ccccc1"),
}


def pose_mol(seed):
    p = run_dir / f"docking/outputs/KEAP1_KELCH_IQK_redock_s{seed}_out.pdbqt"
    txt = p.read_text()
    first = "MODEL" + txt.split("MODEL")[1].split("ENDMDL")[0] + "ENDMDL\n"
    return Chem.RemoveHs(RDKitMolCreate.from_pdbqt_mol(PDBQTMolecule(first, skip_typing=True))[0])


def best_mapping_distances(pose):
    """同一分子对称匹配中，取无叠合距离最小的映射，返回逐原子距离。"""
    matches = ref.GetSubstructMatches(pose, uniquify=False, useChirality=False)
    if not matches:  # 反向
        matches = [(j, i) for i, j in pose.GetSubstructMatches(ref, uniquify=False)]
    conf_p = pose.GetConformer()
    best = None
    for m in matches:
        d = np.array([[conf_p.GetAtomPosition(i).x, conf_p.GetAtomPosition(i).y, conf_p.GetAtomPosition(i).z] for i in range(pose.GetNumAtoms())])
        r = np.array([[conf_ref.GetAtomPosition(j).x, conf_ref.GetAtomPosition(j).y, conf_ref.GetAtomPosition(j).z] for j in m])
        dist = np.linalg.norm(d - r, axis=1)
        if best is None or dist.max() < best.max():
            best = dist
    return best


out = {"reference_smiles": ref_smiles, "overall_rmsd_recorded": {}, "seeds": {}}
for seed in (42, 7, 123, 2026, 555):
    m = pose_mol(seed)
    assert Chem.MolToSmiles(m) == ref_smiles, f"seed{seed} 姿态分子与参照不一致"
    dist = best_mapping_distances(m)
    atoms = list(ref.GetAtoms())
    groups = {}
    for gi, (gname, patt) in enumerate(GROUPS.items()):
        idx = set()
        for match in ref.GetSubstructMatches(patt, uniquify=True):
            idx.update(match)
        for i in idx:
            lab = gname
            groups.setdefault(lab, []).append(round(float(dist[i]), 3))
    stats = {k: {"n": len(v), "max": round(max(v), 2), "mean": round(float(np.mean(v)), 2)} for k, v in groups.items()}
    # 无环/链原子归入 other
    assigned = set().union(*[set() for _ in ()]) if False else set()
    for k, patt in GROUPS.items():
        for match in ref.GetSubstructMatches(patt, uniquify=True):
            assigned.update(match)
    other = [round(float(dist[i]), 3) for i in range(ref.GetNumAtoms()) if i not in assigned]
    if other:
        stats["other"] = {"n": len(other), "max": round(max(other), 2), "mean": round(float(np.mean(other)), 2)}
    out["seeds"][seed] = {"rmsd_noalign": round(float(np.sqrt((dist ** 2).mean())), 4),
                          "max_atom_dev": round(float(dist.max()), 2),
                          "groups": stats}
    print(f"seed={seed}: 无叠合RMSD {out['seeds'][seed]['rmsd_noalign']}  最大原子偏差 {out['seeds'][seed]['max_atom_dev']}Å")
    for k, v in stats.items():
        print(f"    {k:18s} n={v['n']:2d} max={v['max']:.2f} mean={v['mean']:.2f}")

dst = run_dir / "docking" / "keap1_deviation_analysis.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"写入 {dst}")
