# -*- coding: utf-8 -*-
"""SOP 步骤 4 · 五级漏斗中段: 预过滤(Lipinski/PAINS) -> 真实 Vina 批量对接

预过滤: Lipinski 违规计数 + RDKit FilterCatalog PAINS 预警(课程五级漏斗第 2 级;
        天然多酚常被 PAINS 误报, 故采取"标记不剔除", 排名保留、报告披露)。
对接: AutoDock Vina 1.2.7 真实打分(exh=8, seed=42), 替换主线演示分;
      只有通过 s2 redock 门控(RMSD<2Å)的靶点才参与。
断点续跑: 已有条目(状态表)自动跳过, 中断后重跑即可续。
"""
import csv
import json
import os
import re
import subprocess
import sys

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem import FilterCatalog
from meeko import MoleculePreparation, PDBQTWriterLegacy

from common import (DOCK, RES, load_candidates, lipinski_violations,
                    mol_of, rdkit_descriptors, write_csv)

RDLogger.DisableLog("rdApp.*")
LGD = os.path.join(DOCK, "ligands")
OUT = os.path.join(DOCK, "outputs")
AFF_RE = re.compile(r"^\s+\d+\s+(-?\d+\.\d+)\s+")
MK = MoleculePreparation()

params = FilterCatalog.FilterCatalogParams()
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
PAINS_CATALOG = FilterCatalog.FilterCatalog(params)


def pains_alert(mol):
    """返回 PAINS 命中类别;无命中返回空串。"""
    entry = PAINS_CATALOG.GetFirstMatch(mol)
    return entry.GetDescription() if entry else ""


def embed_and_prep(smiles, path, seed=42):
    """SMILES -> ETKDGv3/MMFF 3D 构象 -> meeko pdbqt。"""
    m = mol_of(smiles)
    m = Chem.AddHs(m)
    p = AllChem.ETKDGv3(); p.randomSeed = seed
    if AllChem.EmbedMolecule(m, p) != 0:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(m, p) != 0:
            return None
    try:
        AllChem.MMFFOptimizeMolecule(m, mmffVariant="MMFF94s", maxIters=500)
    except Exception:
        pass
    try:
        setups = MK(m)
        s, ok, _ = PDBQTWriterLegacy.write_string(setups[0])
        if not ok:
            return None
        open(path, "w").write(s)
        return m
    except Exception:
        return None


def prefilter():
    """五级漏斗第 2 级: 类药/预警预过滤(标记制)。"""
    rows = load_candidates()
    out = []
    for r in rows:
        m = mol_of(r["smiles"])
        d = rdkit_descriptors(m)
        out.append({"compound_id": r["compound_id"], "name_cn": r["name_cn"],
                    "lipinski_violations": lipinski_violations(d),
                    "pains_alert": pains_alert(m)})
    write_csv(os.path.join(RES, "tables", "prefilter_report.csv"), out)
    n_pains = sum(1 for x in out if x["pains_alert"])
    n_lic = sum(1 for x in out if x["lipinski_violations"] > 0)
    print(f"[s4] 预过滤: 60 候选中 Lipinski 违规 {n_lic} 个, PAINS 预警 {n_pains} 个(标记保留)")
    return {x["compound_id"]: x for x in out}


def run_vina(receptor, lig_pdbqt, out_pdbqt, box, exh=8, cpu=4):
    cmd = [os.path.join(DOCK, "vina.exe"), "--receptor", receptor, "--ligand", lig_pdbqt,
           "--out", out_pdbqt,
           "--center_x", str(box["center"][0]), "--center_y", str(box["center"][1]),
           "--center_z", str(box["center"][2]),
           "--size_x", str(box["size"][0]), "--size_y", str(box["size"][1]),
           "--size_z", str(box["size"][2]),
           "--exhaustiveness", str(exh), "--seed", "42", "--num_modes", "9",
           "--cpu", str(cpu)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200,
                           errors="ignore")
        affs = [float(AFF_RE.match(l).group(1)) for l in r.stdout.splitlines() if AFF_RE.match(l)]
        return affs[0] if affs else None
    except Exception:
        return None


def run():
    boxes = json.load(open(os.path.join(DOCK, "boxes.json")))
    gate = json.load(open(os.path.join(DOCK, "redock_gate.json")))
    targets = {k: v for k, v in boxes.items() if gate[k]["pass_gate"]}
    assert targets, "无通过 redock 门控的靶点, 终止批量对接"
    pre = prefilter()

    cands = load_candidates()
    state_path = os.path.join(RES, "tables", "docking_real_scores.csv")
    done = {}
    if os.path.exists(state_path):
        for r in csv.DictReader(open(state_path, encoding="utf-8-sig")):
            done[(r["compound_id"], r["target"])] = r["affinity_kcal_mol"]

    rows, n_new = [], 0
    for r in cands:
        cid = r["compound_id"]
        lq = os.path.join(LGD, f"{cid}.pdbqt")
        if not os.path.exists(lq):
            if embed_and_prep(r["smiles"], lq) is None:
                for t in targets:
                    rows.append({"compound_id": cid, "name_cn": r["name_cn"],
                                 "target": t, "affinity_kcal_mol": "", "note": "PREP_FAIL"})
                continue
        for tname, box in targets.items():
            if (cid, tname) in done:
                rows.append({"compound_id": cid, "name_cn": r["name_cn"], "target": tname,
                             "affinity_kcal_mol": done[(cid, tname)], "note": "cached"})
                continue
            receptor = os.path.join(DOCK, "receptors", f"{tname}_{box['pdb']}.pdbqt")
            out_pdbqt = os.path.join(OUT, f"{cid}_{tname}_out.pdbqt")
            aff = run_vina(receptor, lq, out_pdbqt, box)
            rows.append({"compound_id": cid, "name_cn": r["name_cn"], "target": tname,
                         "affinity_kcal_mol": aff if aff is not None else "",
                         "note": "" if aff is not None else "DOCK_FAIL"})
            n_new += 1
        if n_new and n_new % 10 == 0:
            write_csv(state_path, rows)
            print(f"[s4] 进度: 已新增 {n_new} 次对接", flush=True)
    write_csv(state_path, rows)

    ok = [r for r in rows if r["affinity_kcal_mol"] not in ("", None)]
    arr = np.array([float(r["affinity_kcal_mol"]) for r in ok])
    print(f"[s4] 真实 Vina 对接完成: {len(ok)}/{len(rows)} 次成功 "
          f"(范围 {arr.min():.2f} ~ {arr.max():.2f} kcal/mol)")
    for t in targets:
        a = np.array([float(r["affinity_kcal_mol"]) for r in ok if r["target"] == t])
        print(f"[s4] {t}: n={len(a)} 中位={np.median(a):.2f} 最优={a.min():.2f}")
    return rows


if __name__ == "__main__":
    run()
