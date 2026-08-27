# -*- coding: utf-8 -*-
"""训练数据的公共装载: SMILES -> 图对象 + 节点特征矩阵

负责人: 宁显泷（算法组）
"""
import csv
import os

import numpy as np

from chem.smiles_graph import parse_smiles

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPLITS = os.path.join(ROOT, "data", "splits")
PROC = os.path.join(ROOT, "data", "processed")

ELEMS = ["C", "N", "O", "S", "P", "F", "Cl", "Br", "I", "B"]


def node_features(g):
    """[onehot元素(10), 芳香, 度/6, 氢数/4] -> 13维"""
    deg = g.degrees()
    nH = g.num_h()
    X = np.zeros((len(g.atoms), 13))
    for a in g.atoms:
        idx = ELEMS.index(a.element) if a.element in ELEMS else 0
        X[a.idx, idx] = 1.0
        X[a.idx, 10] = 1.0 if a.aromatic else 0.0
        X[a.idx, 11] = min(deg[a.idx] / 6.0, 1.5)
        X[a.idx, 12] = min(nH[a.idx] / 4.0, 1.5)
    return X


class GraphRecord:
    __slots__ = ("cid", "name", "label", "g", "X", "A")

    def __init__(self, row):
        self.cid = row["compound_id"]
        self.name = row["name_cn"]
        self.label = int(row["label"]) if row.get("label", "") != "" else None
        self.g = parse_smiles(row["smiles"])
        self.X = node_features(self.g)
        A = self.g.adjacency(weighted=False) + np.eye(len(self.g.atoms))
        d = A.sum(1)
        d[d == 0] = 1.0
        dinv = 1.0 / np.sqrt(d)
        self.A = A * np.outer(dinv, dinv)  # D^-1/2 (A+I) D^-1/2


def load_split(name):
    with open(os.path.join(SPLITS, f"{name}.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r) for r in csv.DictReader(f)]


def load_pool():
    with open(os.path.join(PROC, "screening_pool.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r) for r in csv.DictReader(f)]


def load_labeled_actives():
    """清洗后有标签集中的正样本(HP系)，用于最终批量推理。"""
    with open(os.path.join(PROC, "cleaned_compounds.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r) for r in csv.DictReader(f) if r["label"] == "1"]
