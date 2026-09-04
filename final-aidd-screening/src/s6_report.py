# -*- coding: utf-8 -*-
"""SOP 步骤 7-8 · 结果可视化与报告数据汇总

图: 模型分-真实对接分散点 / 可靠性曲线 / Top-10 条形图
表: summary.json(全指标汇总, 供 REPORT.md 引用)
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import RES, read_csv

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
FIG = os.path.join(RES, "figures")


def fig_scatter(rank_rows):
    ms = np.array([r["pred_mean"] for r in rank_rows])
    ds = np.array([r["dock_avg_kcal"] for r in rank_rows])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(ms, ds, s=28, c="#2b6cb0", alpha=0.75)
    for r in rank_rows[:10]:
        ax.annotate(r["name_cn"], (r["pred_mean"], r["dock_avg_kcal"]),
                    fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel("GNN 预测活性 (MC Dropout 均值)")
    ax.set_ylabel("真实 Vina 对接分均值 (kcal/mol)")
    ax.set_title("模型证据 × 结构证据 (60 候选, AutoDock Vina 1.2.7)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "model_vs_dock_real.png"), dpi=160)
    plt.close(fig)


def fig_reliability():
    pred = read_csv(os.path.join(RES, "predictions", "test_predictions.csv"))
    y = np.array([int(r["label"]) for r in pred])
    p = np.array([float(r["pred_mean"]) for r in pred])
    summary = json.load(open(os.path.join(RES, "metrics", "model_summary.json"),
                             encoding="utf-8"))
    T = summary.get("temperature", 1.0)
    p_cal = 1 / (1 + np.exp(-(np.log(p / (1 - p + 1e-9)) / T)))
    fig, ax = plt.subplots(figsize=(5, 4.6))
    for q, lab, c in ((p, f"校准前 ECE={summary['gnn']['ECE_before_cal']}", "#c53030"),
                      (p_cal, f"温度缩放后 T={T}", "#2f855a")):
        bins = np.linspace(0, 1, 6)
        centers, accs = [], []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (q >= lo) & (q <= hi if hi == 1 else q < hi)
            if m.sum():
                centers.append(q[m].mean()); accs.append(y[m].mean())
        ax.plot(centers, accs, "o-", label=lab, color=c)
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("预测概率"); ax.set_ylabel("观测正例率")
    ax.set_title("可靠性曲线 (测试集, 骨架划分)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "reliability_diagram.png"), dpi=160)
    plt.close(fig)


def fig_top10(picked):
    names = [r["name_cn"] for r in picked][::-1]
    scores = [float(r["final_score"]) for r in picked][::-1]
    colors = ["#c53030" if r["pains_alert"] else "#2b6cb0" for r in picked][::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(names, scores, color=colors, alpha=0.85)
    for i, (s, r) in enumerate(zip(scores, picked[::-1])):
        ax.text(s + 0.003, i, f"{s:.3f}", va="center", fontsize=8)
    ax.set_xlabel("三源共识总分 (模型 0.45 / 真实对接 0.35 / 类药 0.20)")
    ax.set_title("多样性 Top-10 (骨架簇代表; 红色=PAINS 预警)")
    ax.set_xlim(0, max(scores) * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "diverse_top10.png"), dpi=160)
    plt.close(fig)


def run():
    os.makedirs(FIG, exist_ok=True)
    rank_rows = read_csv(os.path.join(RES, "tables", "final_ranking_v2_real.csv"))
    picked = read_csv(os.path.join(RES, "tables", "diverse_top10.csv"))
    gate = json.load(open(os.path.join(DOCK := os.path.join(RES, "..", "docking"),
                                       "redock_gate.json"), encoding="utf-8"))
    model = json.load(open(os.path.join(RES, "metrics", "model_summary.json"),
                           encoding="utf-8"))
    fusion = json.load(open(os.path.join(RES, "metrics", "fusion_summary.json"),
                            encoding="utf-8"))

    fig_scatter(rank_rows)
    fig_reliability()
    fig_top10(picked)

    summary = {"redock_gate": gate, "model": model, "fusion": fusion,
               "figures": ["model_vs_dock_real.png", "reliability_diagram.png",
                           "diverse_top10.png"]}
    json.dump(summary, open(os.path.join(RES, "summary.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[s6] 图 3 张与 summary.json 已生成: {FIG}")
    return summary


if __name__ == "__main__":
    run()
