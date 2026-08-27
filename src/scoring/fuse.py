# -*- coding: utf-8 -*-
"""协同评分矩阵与最终排名

负责人: 衣思淼（融合规则）；王启龙（自动化脚本）
融合规则(与组会决议一致):
  model_term = pred_mean * (0.5 + 0.5*confidence)      # 方差转置信度权重
  dock_term  = 1 - rank_pct(两靶点对接分均值)           # 越低(结合越强)分越高
  dl_term    = 1 - 0.25*Lipinski违规数
  final = 0.45*model + 0.35*dock + 0.20*dl；适用域外分子再乘 0.9 预警降权
筛选范围: 保肝活性分子(HP) + 新分子池(NV)；阳性参照药单独列出不占候选名额。
"""
import csv
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROC = os.path.join(ROOT, "data", "processed")
PRED = os.path.join(ROOT, "results", "predictions")
DOCK = os.path.join(ROOT, "results", "docking")
AD = os.path.join(ROOT, "results", "ad")
OUT = os.path.join(ROOT, "results", "rankings")

W_MODEL, W_DOCK, W_DL = 0.45, 0.35, 0.20
AD_PENALTY = 0.9


def _read(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def lipinski_violations(r):
    v = 0
    v += float(r["MW"]) > 500
    v += float(r["logP_est"]) > 5
    v += int(r["nHBD"]) > 5
    v += int(r["nHBA"]) > 10
    return int(v)


def run():
    os.makedirs(OUT, exist_ok=True)
    pool = _read(os.path.join(PROC, "screening_pool.csv"))
    labeled = [r for r in _read(os.path.join(PROC, "cleaned_compounds.csv"))
               if r["label"] == "1" and r["compound_id"].startswith("HP")]
    pred_by_id = {}
    # HP 系(有标签活性池)+NV 新分子池统一来自 fullpool_predictions.csv
    full_path = os.path.join(PRED, "fullpool_predictions.csv")
    pred_by_id = {r["compound_id"]: r for r in _read(full_path)}
    dock = _read(os.path.join(DOCK, "docking_scores.csv"))
    ad = {r["compound_id"]: r for r in _read(os.path.join(AD, "ad_report.csv"))}

    davg = {}
    for r in dock:
        if r["compound_id"].startswith("DC"):
            continue
        davg.setdefault(r["compound_id"], []).append(float(r["score_kcal"]))
    davg = {k: float(np.mean(v)) for k, v in davg.items()}

    cands = [dict(r, pred=pred_by_id.get(r["compound_id"])) for r in labeled + pool]
    cands = [c for c in cands if c["pred"] is not None and c["compound_id"] in davg]

    # 对接分名次百分比(分越低排名越前)
    ids = [c["compound_id"] for c in cands]
    order = sorted(ids, key=lambda k: davg[k])
    rank_pct = {k: i / max(1, len(order) - 1) for i, k in enumerate(order)}

    rows = []
    for c in cands:
        cid = c["compound_id"]
        mu = float(c["pred"]["pred_mean"]); var = float(c["pred"]["pred_var"])
        conf = 1.0 - min(1.0, np.sqrt(var) / 0.25)
        model_term = mu * (0.5 + 0.5 * conf)
        dock_term = 1.0 - rank_pct[cid]
        dl_term = 1.0 - 0.25 * lipinski_violations(c)
        score = W_MODEL * model_term + W_DOCK * dock_term + W_DL * dl_term
        in_ad = int(ad[cid]["in_domain"])
        if not in_ad:
            score *= AD_PENALTY
        rows.append({
            "rank": None, "compound_id": cid, "name_cn": c["name_cn"],
            "category": c["category"], "source_herb": c.get("source_herb", ""),
            "pred_mean": round(mu, 4), "pred_var": round(var, 4),
            "confidence": round(conf, 3),
            "dock_avg_kcal": round(davg[cid], 2),
            "lipinski_violations": lipinski_violations(c),
            "ad_warning": "" if in_ad else "域外",
            "final_score": round(score, 4),
        })
    rows.sort(key=lambda r: -r["final_score"])
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    with open(os.path.join(OUT, "final_ranking.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"[fuse] 协同评分完成: {len(rows)} 个候选入库")
    print(f"[fuse] Top-10:")
    for r in rows[:10]:
        flag = " [域外]" if r["ad_warning"] else ""
        print(f"  #{r['rank']:>2} {r['name_cn']:<8} 模型分{r['pred_mean']:.3f} "
              f"方差{r['pred_var']:.4f} 对接{r['dock_avg_kcal']:.2f} "
              f"总评{r['final_score']:.4f}{flag}")
    return rows


if __name__ == "__main__":
    run()
