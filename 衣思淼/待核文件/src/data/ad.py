# -*- coding: utf-8 -*-
"""适用域(Applicability Domain)判定: 训练集描述符杠杆值法

负责人: 衣思淼（边界定义）；王启龙（预警代码集成）
方法: h_i = x_i^T (X^T X)^-1 x_i，阈值 h* = 3p/n (p=特征维数, n=训练样本数)。
      杠杆值超过 h* 判为域外，推理结果打"预警"标记。
"""
import csv
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROC = os.path.join(ROOT, "data", "processed")
SPLITS = os.path.join(ROOT, "data", "splits")
OUT = os.path.join(ROOT, "results", "ad")

FEATS = ["MW", "logP_est", "TPSA_est", "nHBD", "nHBA", "nRot", "nAromSystems"]


def _load(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _matrix(rows, mu=None, sd=None):
    X = np.array([[float(r[c]) for c in FEATS] for r in rows])
    if mu is None:
        mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    return Z, mu, sd


def run():
    train = _load(os.path.join(SPLITS, "train.csv"))
    Xtr, mu, sd = _matrix(train)
    p = Xtr.shape[1]
    n = Xtr.shape[0]
    h_star = 3.0 * p / n
    try:
        inv = np.linalg.inv(Xtr.T @ Xtr + 1e-6 * np.eye(p))
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(Xtr.T @ Xtr)

    def leverage(rows):
        Z, _, _ = _matrix(rows, mu, sd)
        return np.einsum("ij,jk,ik->i", Z, inv, Z)

    os.makedirs(OUT, exist_ok=True)
    report = []
    for name in ("train", "val", "test"):
        rows = _load(os.path.join(SPLITS, f"{name}.csv"))
        h = leverage(rows)
        for r, hi in zip(rows, h):
            report.append({"compound_id": r["compound_id"], "name_cn": r["name_cn"],
                           "split": name, "leverage": round(float(hi), 3),
                           "h_star": round(h_star, 3),
                           "in_domain": int(hi <= h_star)})
    pool = _load(os.path.join(PROC, "screening_pool.csv"))
    h = leverage(pool)
    for r, hi in zip(pool, h):
        report.append({"compound_id": r["compound_id"], "name_cn": r["name_cn"],
                       "split": "screening_pool", "leverage": round(float(hi), 3),
                       "h_star": round(h_star, 3),
                       "in_domain": int(hi <= h_star)})

    with open(os.path.join(OUT, "ad_report.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(report[0].keys()))
        w.writeheader()
        w.writerows(report)

    out_rate = sum(1 for r in report if r["split"] == "screening_pool" and not r["in_domain"])
    print(f"[ad] h*={h_star:.3f}；筛选池域外分子 {out_rate}/{len(pool)} "
          f"({100*out_rate/max(1,len(pool)):.0f}%) 已标记预警")
    return report


if __name__ == "__main__":
    run()
