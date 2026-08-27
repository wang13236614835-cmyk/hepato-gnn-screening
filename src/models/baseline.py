# -*- coding: utf-8 -*-
"""传统机器学习基准线

负责人: 代维斯丹（验证组）
模型: (1) 二维描述符 + 高斯朴素贝叶斯；(2) 2048bit环形指纹 + L2逻辑回归
用途: 为图神经网络提供可比基准；在GNN结果之前先出分，保证最后能并表对比。
"""
import csv
import os

import numpy as np

from chem.smiles_graph import parse_smiles
from chem.fingerprints import morgan_fp
from chem.descriptors import compute_descriptors, DESCRIPTOR_COLS
from data.ad import FEATS
from models.dataset import load_split
from models.gnn import metrics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPLITS = os.path.join(ROOT, "data", "splits")


def _matrices(name):
    recs = load_split(name)
    with open(os.path.join(SPLITS, f"{name}.csv"), encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    D = np.array([[float(r[c]) for c in FEATS] for r in rows])
    F = np.array([morgan_fp(parse_smiles(r["smiles"])) for r in rows], dtype=np.float64)
    y = np.array([int(r["label"]) for r in rows])
    ids = [(r["compound_id"], r["name_cn"]) for r in rows]
    return recs, ids, D, F, y


class GaussianNB:
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.mu = {}; self.sd = {}; self.prior = {}
        for c in self.classes:
            m = y == c
            self.mu[c] = X[m].mean(0)
            self.sd[c] = X[m].std(0) + 1e-6
            self.prior[c] = np.log(m.sum() / len(y))
        return self

    def predict_proba(self, X):
        ll = []
        for c in self.classes:
            z = -0.5 * (((X - self.mu[c]) / self.sd[c]) ** 2 + np.log(2 * np.pi * self.sd[c] ** 2)).sum(1)
            ll.append(z + self.prior[c])
        ll = np.array(ll).T
        e = np.exp(ll - ll.max(1, keepdims=True))
        return (e / e.sum(1, keepdims=True))[:, 1]


class LogReg:
    """L2正则逻辑回归，Adam优化。"""

    def __init__(self, d, lr=0.05, wd=1e-3, seed=0):
        rng = np.random.default_rng(seed)
        self.w = rng.normal(0, 0.01, d)
        self.b = 0.0
        self.lr, self.wd = lr, wd
        self.mw = np.zeros_like(self.w); self.vw = np.zeros_like(self.w)
        self.mb = 0.0; self.vb = 0.0; self.t = 0

    def fit(self, X, y, epochs=400):
        for _ in range(epochs):
            p = 1 / (1 + np.exp(-(X @ self.w + self.b)))
            g = X.T @ (p - y) / len(y) + self.wd * self.w
            gb = (p - y).mean()
            self.t += 1
            for nm, gr in (("w", g), ("b", gb)):
                if nm == "w":
                    m = self.mw; v = self.vw
                    m[:] = 0.9 * m + 0.1 * gr
                    v[:] = 0.999 * v + 0.001 * gr * gr
                    mh = m / (1 - 0.9 ** self.t); vh = v / (1 - 0.999 ** self.t)
                    self.w = self.w - self.lr * mh / (np.sqrt(vh) + 1e-8)
                else:
                    self.mb = 0.9 * self.mb + 0.1 * gr
                    self.vb = 0.999 * self.vb + 0.001 * gr * gr
                    mh = self.mb / (1 - 0.9 ** self.t); vh = self.vb / (1 - 0.999 ** self.t)
                    self.b = self.b - self.lr * mh / (np.sqrt(vh) + 1e-8)
        return self

    def predict_proba(self, X):
        return 1 / (1 + np.exp(-(X @ self.w + self.b)))


def run(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    _, _, Dtr, Ftr, ytr = _matrices("train")
    _, _, Dte, Fte, yte = _matrices("test")

    nb = GaussianNB().fit(Dtr, ytr)
    p_nb = nb.predict_proba(Dte)
    lr = LogReg(Ftr.shape[1]).fit(Ftr, ytr)
    p_lr = lr.predict_proba(Fte)

    rows = [("高斯朴素贝叶斯(描述符)", metrics(yte, p_nb)),
            ("逻辑回归(2048bit指纹)", metrics(yte, p_lr))]
    with open(os.path.join(out_dir, "baseline.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "AUC", "ACC", "BACC", "F1"])
        for name, m in rows:
            w.writerow([name, m["AUC"], m["ACC"], m["BACC"], m["F1"]])
            print(f"[baseline] {name}: {m}")
    return {name: m for name, m in rows}


if __name__ == "__main__":
    run(os.path.join(ROOT, "results", "metrics"))
