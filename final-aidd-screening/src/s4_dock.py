# -*- coding: utf-8 -*-
"""暑假方法诊断模块。课程对应主题见 learning/共享；不宣称未经核实的课程章号或原话。
PAINS命中仅为干扰风险提示，不能称为已证实假阳性。研究身份/标签审核独立于代码运行。"""
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
    m = Chem.AddHs(mol_of(smiles))
    p = AllChem.ETKDGv3(); p.randomSeed = seed
    if AllChem.EmbedMolecule(m, p) != 0:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(m, p) != 0:
            raise ValueError("EMBED_FAIL: ETKDG常规和随机坐标均失败")
    if not AllChem.MMFFHasAllMoleculeParams(m):
        raise ValueError("MMFF_PARAMS_MISSING: 不静默忽略缺少参数")
    status = AllChem.MMFFOptimizeMolecule(m, mmffVariant="MMFF94s", maxIters=500)
    if status != 0:
        raise ValueError(f"MMFF_NOT_CONVERGED:{status}")
    setups = MK(m)
    text, ok, error = PDBQTWriterLegacy.write_string(setups[0])
    if not ok:
        raise ValueError("MEEKO_WRITE_FAIL:" + str(error))
    from pathlib import Path
    Path(path).write_text(text)
    return m


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
    print(f"[s4] 预过滤: {len(rows)} 候选中 Lipinski 违规 {n_lic} 个, PAINS 预警 {n_pains} 个(标记保留)")
    return {x["compound_id"]: x for x in out}


def run():
    from batch_docking import run as execute
    return execute()

if __name__ == "__main__":
    run()
