# -*- coding: utf-8 -*-
"""公共模块: 路径、数据装载、RDKit 图/描述符/指纹

数据来源: 待人工复核的统一结构注册表。规范骨架和描述符均由实际结构重算。
默认阻止未审数据；proposed 模式仅用于诊断旧标签下的程序变化。
"""
import csv
import json
import os
import shutil

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Descriptors, Lipinski, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
RUN_ROOT = os.path.abspath(os.environ.get("HEPATO_RUN_ROOT", os.path.join(ROOT, "results", "revised")))
SPLITS = os.path.join(RUN_ROOT, "splits")
DOCK = os.path.join(RUN_ROOT, "docking")
RES = os.path.join(RUN_ROOT, "results")
SOURCE_DOCK = os.path.join(ROOT, "docking")
VINA = os.environ.get("VINA_BIN") or shutil.which("vina") or os.path.join(SOURCE_DOCK, "vina.exe")
REGISTRY = os.path.join(ROOT, "..", "data", "curation", "compound_registry.csv")

ELEMS = ["C", "N", "O", "S", "P", "F", "Cl", "Br", "I", "B"]
DESC_FEATS = ["MW", "logP_est", "TPSA_est", "nHBD", "nHBA", "nRot", "nAromSystems"]


def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


_SMILES_FIX = None


def apply_smiles_fix(rows):
    """数据校准: 5 条记录采用 PubChem 权威结构(留档 data/smiles_fix.json,
    可溯源;对应课程第 2 章'数据质量'对策)。"""
    global _SMILES_FIX
    if _SMILES_FIX is None:
        p = os.path.join(DATA, "smiles_fix.json")
        _SMILES_FIX = {}
        if os.path.exists(p):
            _SMILES_FIX = json.load(open(p, encoding="utf-8"))
    for r in rows:
        if r["compound_id"] in _SMILES_FIX:
            r["smiles"] = _SMILES_FIX[r["compound_id"]]["new"]
    return rows


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def load_registry():
    rows = read_csv(REGISTRY)
    diagnostic = os.environ.get("HEPATO_DATA_MODE") == "proposed"
    included = [r for r in rows if r.get("role") != "excluded"]
    if not diagnostic:
        problems = []
        for r in included:
            if (r.get("identity_status") != "verified" or not r.get("identity_reviewer")
                    or not r.get("identity_reviewed_at") or not r.get("source_url") or not r.get("inchikey")):
                problems.append(r["compound_id"] + ":身份未复核")
            if r.get("legacy_label") and r.get("role") != "screening":
                if (r.get("label_status") != "verified" or r.get("label") not in ("0","1")
                        or not r.get("label_reviewer") or not r.get("label_reviewed_at")
                        or not r.get("endpoint") or not r.get("evidence_url")):
                    problems.append(r["compound_id"] + ":标签/终点未复核")
        endpoints = {r["endpoint"] for r in included if r.get("label") in ("0","1")}
        if len(endpoints) != 1:
            problems.append("带标签数据必须使用同一明确终点")
        if problems:
            raise ValueError("研究数据尚未放行：" + "; ".join(problems[:6]) + "。见 data/curation/compound_registry.csv；诊断模式不构成科学验证。")
    out = []
    for r in included:
        q = dict(r, smiles=r["proposed_smiles"], label=r["legacy_label"] if diagnostic else r["label"])
        if not diagnostic and r.get("role") == "screening":
            q["label"] = ""
        m = mol_of(q["smiles"])
        q.update(rdkit_descriptors(m)); q["scaffold"] = scaffold_smiles(m)
        out.append(q)
    return out


def load_labeled():
    return [r for r in load_registry() if r["label"] in ("0", "1")]


def load_pool():
    return [r for r in load_registry() if r["label"] == ""]


def load_candidates():
    return [r for r in load_registry() if r["label"] in ("1", "")]


def mol_of(smiles):
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError(f"SMILES 解析失败: {smiles}")
    return m


def rdkit_descriptors(mol):
    """七维描述符(与原数据列同口径, 用 RDKit 独立复算)。"""
    return {
        "MW": Descriptors.MolWt(mol),
        "logP_est": Descriptors.MolLogP(mol),
        "TPSA_est": rdMolDescriptors.CalcTPSA(mol),
        "nHBD": Lipinski.NumHDonors(mol),
        "nHBA": Lipinski.NumHAcceptors(mol),
        "nRot": Lipinski.NumRotatableBonds(mol),
        "nAromSystems": rdMolDescriptors.CalcNumAromaticRings(mol),
    }


def lipinski_violations(d):
    v = int(d["MW"] > 500) + int(d["logP_est"] > 5)
    v += int(d["nHBD"] > 5) + int(d["nHBA"] > 10)
    return v


def ecfp_bits(mol, radius=2, nbits=2048):
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
    arr = np.zeros(nbits, dtype=np.float64)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr


def scaffold_smiles(mol):
    from rdkit.Chem.Scaffolds import MurckoScaffold
    return MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)


# ---------------- GNN 图记录 ----------------
class GraphRecord:
    __slots__ = ("cid", "name", "label", "mol", "X", "A")

    def __init__(self, row):
        self.cid = row["compound_id"]
        self.name = row["name_cn"]
        self.label = int(row["label"]) if row.get("label", "") != "" else None
        self.mol = mol_of(row["smiles"])
        self.X = self._features(self.mol)
        A = self._adjacency(self.mol)
        d = A.sum(1)
        d[d == 0] = 1.0
        dinv = 1.0 / np.sqrt(d)
        self.A = A * np.outer(dinv, dinv)  # D^-1/2 (A+I) D^-1/2

    @staticmethod
    def _features(mol):
        """[元素 onehot(10), 芳香, 度/6, 氢数/4] -> 13 维(与主线 GNN 同口径)"""
        X = np.zeros((mol.GetNumAtoms(), 13))
        for a in mol.GetAtoms():
            sym = a.GetSymbol()
            idx = ELEMS.index(sym) if sym in ELEMS else 0
            X[a.GetIdx(), idx] = 1.0
            X[a.GetIdx(), 10] = 1.0 if a.GetIsAromatic() else 0.0
            X[a.GetIdx(), 11] = min(a.GetDegree() / 6.0, 1.5)
            X[a.GetIdx(), 12] = min((a.GetNumImplicitHs() + a.GetNumExplicitHs()) / 4.0, 1.5)
        return X

    @staticmethod
    def _adjacency(mol):
        n = mol.GetNumAtoms()
        A = np.zeros((n, n))
        for b in mol.GetBonds():
            i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
            A[i, j] = A[j, i] = 1.0
        A += np.eye(n)
        return A


def records_of(rows):
    return [GraphRecord(r) for r in rows]


# ---------------- 评价指标(与主线同口径) ----------------
def auc(y, s):
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    ranks[order] = np.arange(1, len(s) + 1)
    for v in np.unique(s):
        m = s == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def metrics(y, p, thr=0.5):
    yh = (p >= thr).astype(int)
    tp = int(((yh == 1) & (y == 1)).sum()); fp = int(((yh == 1) & (y == 0)).sum())
    fn = int(((yh == 0) & (y == 1)).sum()); tn = int(((yh == 0) & (y == 0)).sum())
    rec = tp / max(1, tp + fn); prec = tp / max(1, tp + fp)
    return {"AUC": round(auc(y, p), 3),
            "BACC": round(0.5 * (rec + tn / max(1, tn + fp)), 3),
            "F1": round(2 * prec * rec / max(1e-9, prec + rec), 3)}


def ece(y, p, bins=10):
    e, n = 0.0, len(p)
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (p >= lo) & ((p < hi) if b < bins - 1 else (p <= 1.0))
        if m.sum() == 0:
            continue
        e += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return round(e, 3)


def spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)
