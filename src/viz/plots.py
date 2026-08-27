# -*- coding: utf-8 -*-
"""结果可视化: 可靠性图 / 不确定性-误差关系 / Top候选条形图 / 模型-对接一致性

负责人: 王启龙（工程）；代维斯丹（科学审校）
说明: 图内标签用英文避免服务器无中文字体时出现乱码；
      reliability diagram 同时输出 CSV 供报告引用。
"""
import csv
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRED = os.path.join(ROOT, "results", "predictions")
MET = os.path.join(ROOT, "results", "metrics")
RANK = os.path.join(ROOT, "results", "rankings")
FIG = os.path.join(ROOT, "results", "figures")

BINS = 10


def _read(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def reliability_diagram():
    rows = _read(os.path.join(PRED, "test_predictions.csv"))
    p = np.array([float(r["pred_mean"]) for r in rows])
    y = np.array([int(r["label"]) for r in rows])
    xs, ys = [], []
    for b in range(BINS):
        lo, hi = b / BINS, (b + 1) / BINS
        m = (p >= lo) & ((p < hi) if b < BINS - 1 else (p <= 1.0))
        if m.sum() == 0:
            continue
        xs.append(p[m].mean()); ys.append(y[m].mean())
    with open(os.path.join(MET, "reliability_curve.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["bin_center", "empirical_accuracy"])
        w.writerows(zip(xs, ys))
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfect calibration")
    ax.plot(xs, ys, "o-", color="#2563eb", label="GNN + MC-Dropout")
    ax.set_xlabel("Predicted probability"); ax.set_ylabel("Observed fraction")
    ax.set_title("Reliability diagram (test set)")
    ax.legend(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "reliability_diagram.png"), dpi=150)
    plt.close(fig)


def uncertainty_error():
    rows = _read(os.path.join(PRED, "test_predictions.csv"))
    v = np.array([float(r["pred_var"]) for r in rows])
    p = np.array([float(r["pred_mean"]) for r in rows])
    y = np.array([int(r["label"]) for r in rows])
    err = np.abs(y - p)
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.scatter(v, err, s=28, c="#dc2626", alpha=0.75)
    ax.set_xlabel("MC-Dropout variance"); ax.set_ylabel("|prediction error|")
    ax.set_title("Uncertainty vs. error (test set)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "uncertainty_vs_error.png"), dpi=150)
    plt.close(fig)


def top_candidates_bar(n=15):
    rows = _read(os.path.join(RANK, "final_ranking.csv"))[:n]
    names = [r["name_cn"] for r in rows][::-1]
    vals = [float(r["final_score"]) for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    ax.barh(range(len(vals)), vals, color="#16a34a")
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Fused score"); ax.set_title(f"Top-{n} candidates (fused)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "top_candidates.png"), dpi=150)
    plt.close(fig)


def model_dock_scatter():
    rows = _read(os.path.join(RANK, "final_ranking.csv"))
    m = np.array([float(r["pred_mean"]) for r in rows])
    d = np.array([float(r["dock_avg_kcal"]) for r in rows])
    ad = [r["ad_warning"] == "" for r in rows]
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    ax.scatter(m[ad], d[ad], s=30, c="#2563eb", label="in domain")
    ax.scatter(m[[not a for a in ad]], d[[not a for a in ad]], s=30, c="#f59e0b",
               marker="x", label="out of domain")
    ax.set_xlabel("GNN predicted probability"); ax.set_ylabel("Docking score (kcal/mol)")
    ax.set_title("Model vs. docking consistency")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "model_dock_scatter.png"), dpi=150)
    plt.close(fig)


def run():
    os.makedirs(FIG, exist_ok=True)
    reliability_diagram()
    uncertainty_error()
    top_candidates_bar()
    model_dock_scatter()
    print(f"[plots] 4 张图输出至 {FIG}")


if __name__ == "__main__":
    run()
