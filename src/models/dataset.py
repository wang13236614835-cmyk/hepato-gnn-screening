# -*- coding: utf-8 -*-
"""训练数据的公共装载: SMILES -> 图对象 + 节点特征矩阵

负责人: 宁显泷（算法组）

2026-09-17 v0.6 修复：未知元素不再回退到元素槽位 0（等价于按碳处理）。
历史行为会把 Na/Zn/Se/* 等静默当成碳，造成不可察觉的化学错误。现在：
- 默认（unknown_element="raise"）：遇到 ELEMS 之外的元素直接抛
  UnsupportedElementError，显式失败，不产生静默错误；
- 显式 opt-in（unknown_element="unk_slot"）：使用第 11 个 one-hot 槽位
  作为独立 UNK 特征，节点特征变为 14 维（只用于重新训练新模型的场景，
  旧 13 维模型/历史结果不迁移、不复用）。
历史数据（C/N/O/S/P/F/Cl/Br/I/B）两条路径结果与旧代码完全一致。
"""
import csv
import os

import numpy as np

from chem.smiles_graph import parse_smiles

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPLITS = os.path.join(ROOT, "data", "splits")
PROC = os.path.join(ROOT, "data", "processed")

ELEMS = ["C", "N", "O", "S", "P", "F", "Cl", "Br", "I", "B"]

# 已知元素 one-hot(10) + 芳香 + 度/6 + 氢数/4 = 13 维（历史布局，不迁移）
KNOWN_FEATURE_DIM = 13
# UNK 槽位布局：one-hot(10+1=11) + 芳香 + 度 + 氢 = 14 维（新训练专用）
UNK_FEATURE_DIM = 14


class UnsupportedElementError(ValueError):
    """SMILES 含 ELEMS 之外的元素，且未显式启用 UNK 槽位。

    携带未知元素列表，调用方可以决定拒绝该分子还是以 UNK 模式重新装载。
    """

    def __init__(self, elements, smiles=""):
        self.elements = sorted(set(elements))
        self.smiles = smiles
        super().__init__(
            "未知元素 {} 不在特征表 ELEMS 中；默认按 unsupported 拒绝，"
            "不会静默按碳处理。如需独立 UNK 特征，请显式传 "
            "unknown_element='unk_slot'（14 维，仅用于重新训练新模型）。"
            "SMILES: {}".format("/".join(self.elements), smiles)
        )


def node_features(g, unknown_element="raise"):
    """节点特征矩阵。

    unknown_element="raise"（默认）: 未知元素抛 UnsupportedElementError。
    unknown_element="unk_slot": 未知元素使用独立 UNK one-hot 槽位，返回
    (n_atoms, 14)；已知元素部分与历史 13 维布局逐位一致（前 10 位 one-hot、
    第 11 位芳香、第 12 位度、第 13 位氢数），UNK 槽位插在 one-hot 末尾。

    历史兼容性：对只含 ELEMS 内元素的分子，unknown_element="raise" 的
    输出与旧版 node_features 完全相同（13 维）。
    """
    if unknown_element not in ("raise", "unk_slot"):
        raise ValueError("unknown_element 必须是 'raise' 或 'unk_slot'")
    deg = g.degrees()
    nH = g.num_h()
    dim = KNOWN_FEATURE_DIM if unknown_element == "raise" else UNK_FEATURE_DIM
    unk_slot = len(ELEMS)  # 10：unk_slot 模式下的独立 UNK one-hot 槽位
    # raise 模式保持历史布局：onehot 0-9、芳香 10、度 11、氢数 12。
    # unk_slot 模式：onehot 0-9、UNK 10、芳香 11、度 12、氢数 13。
    aromatic_col = 10 if unknown_element == "raise" else unk_slot + 1
    deg_col = aromatic_col + 1
    nh_col = aromatic_col + 2
    X = np.zeros((len(g.atoms), dim))
    unknown = [a.element for a in g.atoms if a.element not in ELEMS]
    if unknown:
        if unknown_element == "raise":
            smiles = getattr(g, "_source_smiles", "")
            raise UnsupportedElementError(unknown, smiles)
        for a in g.atoms:
            if a.element not in ELEMS:
                X[a.idx, unk_slot] = 1.0
    for a in g.atoms:
        if a.element in ELEMS:
            X[a.idx, ELEMS.index(a.element)] = 1.0
        X[a.idx, aromatic_col] = 1.0 if a.aromatic else 0.0
        X[a.idx, deg_col] = min(deg[a.idx] / 6.0, 1.5)
        X[a.idx, nh_col] = min(nH[a.idx] / 4.0, 1.5)
    return X


class GraphRecord:
    __slots__ = ("cid", "name", "label", "g", "X", "A")

    def __init__(self, row, unknown_element="raise"):
        self.cid = row["compound_id"]
        self.name = row["name_cn"]
        self.label = int(row["label"]) if row.get("label", "") != "" else None
        self.g = parse_smiles(row["smiles"])
        if self.g is None:
            raise ValueError("无法解析 SMILES: {!r} (compound_id={})".format(row["smiles"], self.cid))
        self.g._source_smiles = row["smiles"]
        self.X = node_features(self.g, unknown_element=unknown_element)
        A = self.g.adjacency(weighted=False) + np.eye(len(self.g.atoms))
        d = A.sum(1)
        d[d == 0] = 1.0
        dinv = 1.0 / np.sqrt(d)
        self.A = A * np.outer(dinv, dinv)  # D^-1/2 (A+I) D^-1/2


def load_split(name, unknown_element="raise"):
    with open(os.path.join(SPLITS, f"{name}.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r, unknown_element=unknown_element) for r in csv.DictReader(f)]


def load_pool(unknown_element="raise"):
    with open(os.path.join(PROC, "screening_pool.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r, unknown_element=unknown_element) for r in csv.DictReader(f)]


def load_labeled_actives(unknown_element="raise"):
    """清洗后有标签集中的正样本(HP系)，用于最终批量推理。"""
    with open(os.path.join(PROC, "cleaned_compounds.csv"), encoding="utf-8-sig") as f:
        return [GraphRecord(r, unknown_element=unknown_element) for r in csv.DictReader(f) if r["label"] == "1"]
