# -*- coding: utf-8 -*-
"""公共模块: 路径、数据装载、RDKit 图/描述符/指纹

数据来源: hepato-gnn-screening 已清洗数据(88 条带标签 + 12 条新分子池),
scaffold 列沿用原骨架签名, 保证与主线划分口径一致。
"""
import csv
import json
import os

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Descriptors, Lipinski, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
SPLITS = os.path.join(DATA, "splits")
DOCK = os.path.join(ROOT, "docking")
RES = os.path.join(ROOT, "results")
VINA = os.path.join(DOCK, "vina.exe")

ELEMS = ["C", "N", "O", "S", "P", "F", "Cl", "Br", "I", "B"]
DESC_FEATS = ["MW", "logP_est", "TPSA_est", "nHBD", "nHBA", "nRot", "nAromSystems"]


def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


_SMILES_FIX = None


def apply_smiles_fix(rows):
    """数据质量修正: 原始数据中 5 条 SMILES 无效(手工构造错误),
    按 PubChem 权威结构替换(见 data/smiles_fix.json;课程第 2 章'数据挑战'对策)。"""
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


def load_labeled():
    """88 条带标签数据(HP 正 48 / DC 负 40)。"""
    return apply_smiles_fix(read_csv(os.path.join(DATA, "cleaned_compounds.csv")))


def load_pool():
    """12 条 NV 新分子池。"""
    return apply_smiles_fix(read_csv(os.path.join(DATA, "screening_pool.csv")))


def load_candidates():
    """对接候选 = HP 活性分子 + NV 新分子(共 60);DC 负样本只用于训练。"""
    actives = [r for r in load_labeled() if r["label"] == "1"]
    return actives + load_pool()


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
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")
