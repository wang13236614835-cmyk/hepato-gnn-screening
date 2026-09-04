# -*- coding: utf-8 -*-
"""SOP 步骤 5-6 · 三源共识评分 -> 骨架聚类多样性 Top-10

融合(与主线组会决议同公式, 对接项换为真实 Vina 分):
  model_term = pred_mean * (0.5 + 0.5*confidence)          # GNN+MC Dropout
  dock_term  = 1 - rank_pct(两靶点真实对接分均值)             # Vina 1.2.7
  dl_term    = 1 - 0.25*Lipinski 违规数
  final = 0.45*model + 0.35*dock + 0.20*dl;域外分子再乘 0.9
多样性(课程步骤 6): ECFP4 Tanimoto Butina 聚类, 每簇取总分最高代表, 得跨骨架 Top-10。
"""
import json
import os

import numpy as np
from rdkit import DataStructs
from rdkit.Chem import AllChem

from common import (RES, ecfp_bits, load_candidates, mol_of, read_csv,
                    scaffold_smiles, spearman, write_csv)

W_MODEL, W_DOCK, W_DL = 0.45, 0.35, 0.20
AD_PENALTY = 0.9
N_SELECT = 10


def butina_clusters(mols, cutoff=0.55):
    """ECFP4 Tanimoto Butina 聚类, 返回每分子的簇编号。"""
    fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) for m in mols]
    dists = []
    n = len(fps)
    for i in range(1, n):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        dists.extend(1 - x for x in sims)
    from rdkit.ML.Cluster import Butina
    clusters = Butina.ClusterData(dists, n, cutoff, isDistData=True)
    labels = [0] * n
    for ci, members in enumerate(clusters):
        for mi in members:
            labels[mi] = ci
    return labels, fps


def run():
    pred = {r["compound_id"]: r for r in read_csv(
        os.path.join(RES, "predictions", "fullpool_predictions.csv"))}
    dock = read_csv(os.path.join(RES, "tables", "docking_real_scores.csv"))
    pre = {r["compound_id"]: r for r in read_csv(
        os.path.join(RES, "tables", "prefilter_report.csv"))}
    cand_rows = load_candidates()

    davg = {}
    for r in dock:
        if r["affinity_kcal_mol"] in ("", None):
            continue
        davg.setdefault(r["compound_id"], []).append(float(r["affinity_kcal_mol"]))
    davg = {k: float(np.mean(v)) for k, v in davg.items()}

    cands = [r for r in cand_rows if r["compound_id"] in pred and r["compound_id"] in davg]
    ids = [r["compound_id"] for r in cands]
    order = sorted(ids, key=lambda k: davg[k])
    rank_pct = {k: i / max(1, len(order) - 1) for i, k in enumerate(order)}

    rows = []
    for r in cands:
        cid = r["compound_id"]
        p = pred[cid]
        mu, var = float(p["pred_mean"]), float(p["pred_var"])
        conf = 1.0 - min(1.0, np.sqrt(var) / 0.25)
        li = int(pre[cid]["lipinski_violations"])
        score = (W_MODEL * mu * (0.5 + 0.5 * conf)
                 + W_DOCK * (1.0 - rank_pct[cid])
                 + W_DL * (1.0 - 0.25 * li))
        in_ad = int(p["in_domain"])
        if not in_ad:
            score *= AD_PENALTY
        m = mol_of(r["smiles"])
        rows.append({"rank": None, "compound_id": cid, "name_cn": r["name_cn"],
                     "category": r["category"], "source_herb": r.get("source_herb", ""),
                     "scaffold": scaffold_smiles(m),
                     "pred_mean": round(mu, 4), "pred_var": round(var, 4),
                     "confidence": round(conf, 3),
                     "dock_avg_kcal": round(davg[cid], 2),
                     "lipinski_violations": li, "pains_alert": pre[cid]["pains_alert"],
                     "ad_warning": "" if in_ad else "域外",
                     "final_score": round(score, 4)})
    rows.sort(key=lambda x: -x["final_score"])
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    write_csv(os.path.join(RES, "tables", "final_ranking_v2_real.csv"), rows)

    # ---- 骨架聚类多样性挑选(课程步骤 6) ----
    mols = [mol_of(r["smiles"]) for r in cand_rows
            if r["compound_id"] in {x["compound_id"] for x in rows}]
    idx_by_id = {r["compound_id"]: i for i, r in enumerate(cand_rows)}
    labels, fps = butina_clusters([mol_of(r["smiles"]) for r in cand_rows])
    label_of = {cid: labels[idx_by_id[cid]] for cid in idx_by_id}

    picked, seen_clusters = [], set()
    for r in rows:
        cl = label_of[r["compound_id"]]
        if cl not in seen_clusters:
            picked.append(dict(r, cluster=cl))
            seen_clusters.add(cl)
        if len(picked) >= N_SELECT:
            break
    write_csv(os.path.join(RES, "tables", "diverse_top10.csv"), picked)

    # 模型分与真实对接分的一致性(两证据源独立性参考)
    ms = np.array([r["pred_mean"] for r in rows])
    ds = np.array([r["dock_avg_kcal"] for r in rows])
    rho = spearman(ms, -ds)  # 对接分越负越强, 取负号统一方向

    summary = {"n_candidates": len(rows), "n_clusters": len(set(label_of.values())),
               "spearman_model_dock": round(rho, 3),
               "top10": [{"name": r["name_cn"], "score": r["final_score"],
                          "pains": r["pains_alert"], "ad": r["ad_warning"]} for r in picked]}
    json.dump(summary, open(os.path.join(RES, "metrics", "fusion_summary.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[s5] 共识排名 v2(真实对接): {len(rows)} 候选, 骨架簇 {summary['n_clusters']} 个")
    print(f"[s5] 模型分-真实对接分 Spearman={rho:.3f} (两证据源独立性强弱参考)")
    print(f"[s5] 多样性 Top-10(每簇最优):")
    for r in picked:
        flags = (" [PAINS]" if r["pains_alert"] else "") + (" [域外]" if r["ad_warning"] else "")
        print(f"  #{r['rank']:>2} {r['name_cn']:<8} 模型{r['pred_mean']:.3f} "
              f"对接{r['dock_avg_kcal']:.2f} 总分{r['final_score']:.4f}{flags}")
    return rows, picked


if __name__ == "__main__":
    run()
