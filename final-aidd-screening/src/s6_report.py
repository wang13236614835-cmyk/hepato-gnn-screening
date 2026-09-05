# -*- coding: utf-8 -*-
"""SOP 步骤 7-8 · 结果可视化与报告数据汇总（大修版）

审查整改(20260905 大修)：
- 项46 图轴不再写"预测活性/真实对接分":模型输出的是未审核历史标签的诊断分数,
  对接是 Vina 计算评分;主图按数据角色(训练/测试/未标注)着色。
- 项47 可靠性图 ECE 分箱与 summary 数值统一(10箱),标注每箱样本量;T=1时两线重合须说明。
- 项37 多样性图标题改"指纹相似性簇代表",不称骨架簇。
- 项34 Top10 条形图按榜着色,已知回顾条目不得视觉上冒充新发现。

图: 模型分-对接分散点 / 可靠性曲线 / Top-10 条形图
表: summary.json(全指标汇总, 供 REPORT.md 引用)
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import RES, ece, ece_bins_detail, read_csv

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
FIG = os.path.join(RES, "figures")
ECE_BINS = 10  # 项47: 图与 metrics/model_summary.json 中 ECE 同一分箱

BOARD_COLORS = {"known_retrospective": "#c05621",
                "independent_test": "#2b6cb0",
                "unlabeled_screening": "#38a169"}
BOARD_LABELS = {"known_retrospective": "已知回顾(训练/验证)",
                "independent_test": "独立测试",
                "unlabeled_screening": "未标注候选池"}


def fig_scatter(rank_rows):
    ms = np.array([float(r["pred_mean"]) for r in rank_rows])
    ds = np.array([float(r["dock_avg_kcal"]) for r in rank_rows])
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    boards = [r.get("board", "unlabeled_screening") for r in rank_rows]
    for board, c in BOARD_COLORS.items():
        idx = [i for i, b in enumerate(boards) if b == board]
        if not idx:
            continue
        ax.scatter(ms[idx], ds[idx], s=30, c=c, alpha=0.75,
                   label=BOARD_LABELS[board])
    for r in rank_rows[:10]:
        ax.annotate(r["name_cn"], (float(r["pred_mean"]), float(r["dock_avg_kcal"])),
                    fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel("历史标签模型输出·诊断 (MC Dropout 均值，非实测活性)")
    ax.set_ylabel("Vina 计算评分均值 (kcal/mol，非实测亲和力)")
    ax.set_title(f"模型诊断输出与计算对接评分 ({len(rank_rows)} 候选；FXR 单靶；未经实验验证)")
    ax.legend(fontsize=8, loc="best")
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
    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    for q, lab, c in ((p, f"校准前 ECE={summary['gnn']['ECE_before_cal']} ({ECE_BINS}箱)", "#c53030"),
                      (p_cal, f"温度缩放后 T={T}" + ("(与校准前重合)" if abs(T - 1.0) < 1e-9 else ""), "#2f855a")):
        bins = np.linspace(0, 1, ECE_BINS + 1)
        centers, accs, ns = [], [], []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (q >= lo) & (q <= hi if hi == 1 else q < hi)
            if m.sum():
                centers.append(q[m].mean()); accs.append(y[m].mean()); ns.append(int(m.sum()))
        ax.plot(centers, accs, "o-", label=lab, color=c)
        for cx, cy, n in zip(centers, accs, ns):
            ax.annotate(f"n={n}", (cx, cy), fontsize=6.5, xytext=(2, -10),
                        textcoords="offset points", color="#718096")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("预测概率"); ax.set_ylabel("观测正例率")
    ax.set_title(f"可靠性曲线 (测试集 n={len(y)}，骨架划分；ECE 分箱={ECE_BINS})")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "reliability_diagram.png"), dpi=160)
    plt.close(fig)
    # 项47: 逐箱明细同步入 metrics, 数值与图可由同一参数复算
    json.dump({"bins": ECE_BINS, "before": ece_bins_detail(y, p, ECE_BINS),
               "after_temperature": ece_bins_detail(y, p_cal, ECE_BINS)},
              open(os.path.join(RES, "metrics", "ece_bin_detail.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)


def fig_top10(picked):
    names = [r["name_cn"] for r in picked][::-1]
    scores = [float(r["final_score"]) for r in picked][::-1]
    rows = picked[::-1]
    boards = [r.get("board", "unlabeled_screening") for r in rows]
    colors = [BOARD_COLORS.get(b, "#718096") for b in boards]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    bars = ax.barh(names, scores, color=colors, alpha=0.85)
    for bar, r in zip(bars, rows):
        if r["pains_alert"]:
            bar.set_edgecolor("#c53030"); bar.set_linewidth(1.6)
    for i, (s, r) in enumerate(zip(scores, rows)):
        ax.text(s + 0.003, i, f"{s:.3f}", va="center", fontsize=8)
    ax.set_xlabel("探索性融合总分 (模型0.45/对接0.35/类药0.20；启发式权重，未经外部验证)")
    ax.set_title("多样性 Top-10 (ECFP4 指纹相似性簇代表；红边=PAINS 结构预警；按数据角色着色)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.85)
               for c in BOARD_COLORS.values()]
    ax.legend(handles, BOARD_LABELS.values(), fontsize=8, loc="lower right")
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
                           "diverse_top10.png"],
               "figure_notes": {"model_vs_dock_real": "诊断输出对计算评分,非实测活性(项46)",
                                "reliability_diagram": f"ECE {ECE_BINS}箱与metrics一致(项47)",
                                "diverse_top10": "指纹相似性簇代表,按榜着色(项34/37)"}}
    json.dump(summary, open(os.path.join(RES, "summary.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(RES, "RUN_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("# 本次计算记录\n\n数据模式：" + os.environ.get("HEPATO_DATA_MODE", "reviewed")
                + "。计算完成不代表药效或湿实验准入。\n\n"
                "榜单已按数据角色分三榜(board_*.csv)：已知回顾 / 独立测试 / 未标注候选；"
                "候选发现只能来自未标注榜(审查项34)。\n"
                "本榜为单靶(FXR)探索性融合排序：KEAP1 未过门控，权重未经外部标签验证(项35/36)；"
                "Top10 中历史阳性条目属于回顾性复现，不是新发现(项34)。\n"
                "聚类口径为 ECFP4 指纹相似性簇，非 Murcko 骨架(项37)。\n\n"
                "指标与排名见本目录 summary.json 和 tables；历史 REPORT.md 不适用于此次运行。\n")
    print(f"[s6] 图 3 张与 summary.json 已生成: {FIG}")
    return summary


if __name__ == "__main__":
    run()
