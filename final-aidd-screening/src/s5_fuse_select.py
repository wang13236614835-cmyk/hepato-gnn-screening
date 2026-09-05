# -*- coding: utf-8 -*-
"""SOP 步骤 5-6 · 探索性融合排序 -> 指纹相似性簇多样性 Top-10（大修版）

审查整改(20260905 大修)：
- 项34 榜单按数据角色分三榜：已知回顾榜(train/val)、独立测试榜(test)、未标注候选榜(screening_pool)。
  候选发现只从未标注榜提出；混排总榜仅作诊断视图，不再当作新发现。
- 项35 权重(0.45/0.35/0.20)与域外罚分0.9为启发式，无外部标签验证。
  本步输出权重扰动与协议变体的排名稳定性(描述性)，不得称可靠共识。
- 项36 模型-对接相关为描述性统计，不证明证据独立或融合有效。
- 项37 聚类为 ECFP4 Tanimoto Butina 指纹相似性簇，不等于 Murcko 骨架；同时报告骨架数。
- 项39 完整纳排流与失败名单入库，保留全部运行，不挑最好榜。

融合公式(与主线组会决议同公式, 对接项换为真实 Vina 分):
  model_term = pred_mean * (0.5 + 0.5*confidence)          # GNN+MC Dropout
  dock_term  = 1 - rank_pct(单靶真实对接分)                  # Vina 1.2.7
  dl_term    = 1 - 0.25*Lipinski 违规数
  final = 0.45*model + 0.35*dock + 0.20*dl;域外分子再乘 0.9
confidence 为人为设置的方差降权启发式，不是校准后的正确概率。
"""
import json
import os

import numpy as np
from rdkit import DataStructs
from rdkit.Chem import AllChem

from common import (RES, DOCK, SPLITS, load_candidates, mol_of, read_csv,
                    scaffold_smiles, spearman, write_csv)

W_MODEL, W_DOCK, W_DL = 0.45, 0.35, 0.20
AD_PENALTY = 0.9
N_SELECT = 10
N_WEIGHT_DRAWS = 200
WEIGHT_KAPPA = 20.0  # Dirichlet 集中度:越大越贴近基准权重
RNG_SEED = 42


def butina_clusters(mols, cutoff=0.55):
    """ECFP4 Tanimoto Butina 指纹相似性聚类, 返回每分子的簇编号。"""
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


def board_of(split):
    """项34: 数据角色 -> 榜名。train/val 参与过拟合与选模, 只能回顾。"""
    return {"train": "known_retrospective", "val": "known_retrospective",
            "test": "independent_test"}.get(split, "unlabeled_screening")


def _score_rows(comp, w_model, w_dock, w_dl, use_ad_penalty=True):
    scored = []
    for c in comp:
        s = (w_model * c["model_term"] + w_dock * c["dock_term"]
             + w_dl * c["dl_term"])
        if use_ad_penalty and not c["in_ad"]:
            s *= AD_PENALTY
        scored.append((c["compound_id"], s))
    scored.sort(key=lambda x: -x[1])
    return [k for k, _ in scored]


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a or b) else 1.0


def _overlap_at_k(order_a, order_b, k):
    return len(set(order_a[:k]) & set(order_b[:k])) / k


def rank_stability(comp, base_order):
    """项35/39: 权重扰动 + 协议变体稳定性。全部为描述性诊断。"""
    rng = np.random.default_rng(RNG_SEED)
    base_w = np.array([W_MODEL, W_DOCK, W_DL])
    jac, rho, top5, top10 = [], [], [], []
    for _ in range(N_WEIGHT_DRAWS):
        w = rng.dirichlet(base_w * WEIGHT_KAPPA)
        order = _score_rows(comp, *w)
        jac.append(_jaccard(base_order[:10], order[:10]))
        # 两序列同向编码(第i位=排名i), 顺序一致时 rho=+1
        rho.append(spearman(np.array([base_order.index(k) for k in order], dtype=float),
                            np.arange(len(order), dtype=float)))
        top5.append(_overlap_at_k(base_order, order, 5))
        top10.append(_overlap_at_k(base_order, order, 10))
    weight_perturbation = {
        "n_draws": N_WEIGHT_DRAWS, "dirichlet_kappa": WEIGHT_KAPPA,
        "top10_jaccard_median": round(float(np.median(jac)), 3),
        "top10_jaccard_p05_p95": [round(float(np.percentile(jac, 5)), 3),
                                  round(float(np.percentile(jac, 95)), 3)],
        "top5_overlap_median": round(float(np.median(top5)), 3),
        "top10_overlap_median": round(float(np.median(top10)), 3),
        "full_rank_spearman_median": round(float(np.median(rho)), 3),
    }
    variants = {
        "model_only": (1.0, 0.0, 0.0, True),
        "dock_only": (0.0, 1.0, 0.0, True),
        "equal_weights": (1 / 3, 1 / 3, 1 / 3, True),
        "base_without_ad_penalty": (W_MODEL, W_DOCK, W_DL, False),
    }
    variant_report = {}
    for name, (wm, wd, wl, ad) in variants.items():
        order = _score_rows(comp, wm, wd, wl, use_ad_penalty=ad)
        variant_report[name] = {
            "top10_jaccard_vs_base": round(_jaccard(base_order[:10], order[:10]), 3),
            "top10_overlap_vs_base": round(_overlap_at_k(base_order, order, 10), 3),
            "full_rank_spearman_vs_base": round(spearman(
                np.array([base_order.index(k) for k in order], dtype=float),
                np.arange(len(order), dtype=float)), 3),
        }
    return {"weight_perturbation": weight_perturbation,
            "protocol_variants": variant_report,
            "note": "无外部标签可验证融合优劣;以上仅为排序稳定性诊断,不构成融合有效性证据"}


def run():
    pred = {r["compound_id"]: r for r in read_csv(
        os.path.join(RES, "predictions", "fullpool_predictions.csv"))}
    dock = read_csv(os.path.join(RES, "tables", "docking_real_scores.csv"))
    pre = {r["compound_id"]: r for r in read_csv(
        os.path.join(RES, "tables", "prefilter_report.csv"))}
    cand_rows = load_candidates()
    split_of = {}
    for part in ("train", "val", "test"):
        path = os.path.join(SPLITS, part + ".csv")
        if os.path.exists(path):
            split_of.update({r["compound_id"]: part for r in read_csv(path)})

    required_targets = set(json.load(open(os.path.join(DOCK, "boxes.json"))))
    available = {}
    for r in dock:
        if r["affinity_kcal_mol"] not in ("", None):
            available.setdefault(r["compound_id"], set()).add(r["target"])
    davg = {}
    for r in dock:
        if r["affinity_kcal_mol"] in ("", None):
            continue
        davg.setdefault(r["compound_id"], []).append(float(r["affinity_kcal_mol"]))
    davg = {k: float(np.mean(v)) for k, v in davg.items()}

    # ---- 项39 完整纳排流 ----
    registered = [r for r in cand_rows if r["compound_id"] in pred]
    dock_failed = sorted(r["compound_id"] for r in registered
                         if available.get(r["compound_id"]) != required_targets)
    controls = sorted(r["compound_id"] for r in registered
                      if r.get("role") == "positive_control"
                      and r["compound_id"] not in dock_failed)
    cands = [r for r in registered if r["compound_id"] not in dock_failed
             and r.get("role") != "positive_control"]
    if not cands:
        raise ValueError("没有具备全部靶点结果的非对照候选")
    inclusion_flow = {
        "registered_candidates": len(registered),
        "docking_incomplete": {"n": len(dock_failed), "compound_ids": dock_failed},
        "positive_control_excluded": {"n": len(controls), "compound_ids": controls},
        "ranked": len(cands),
        "note": "对接失败按缺测处理,不按无活性处理;全部名单保留",
    }

    ids = [r["compound_id"] for r in cands]
    order = sorted(ids, key=lambda k: davg[k])
    from scipy.stats import rankdata
    rr = rankdata([davg[k] for k in order], method="average") - 1
    rank_pct = {k: float(i) / max(1, len(order) - 1) for k, i in zip(order, rr)}

    comp = []
    for r in cands:
        cid = r["compound_id"]
        p = pred[cid]
        mu, var = float(p["pred_mean"]), float(p["pred_var"])
        conf = 1.0 - min(1.0, np.sqrt(var) / 0.25)
        li = int(pre[cid]["lipinski_violations"])
        comp.append({"compound_id": cid, "name_cn": r["name_cn"],
                     "category": r["category"], "source_herb": r.get("source_herb", ""),
                     "role": r.get("role", "candidate"), "legacy_label": r.get("legacy_label", ""),
                     "model_split": split_of.get(cid, "screening_pool"),
                     "pubchem_cid": r.get("pubchem_cid", ""),
                     "data_mode": os.environ.get("HEPATO_DATA_MODE", "reviewed"),
                     "model_term": mu * (0.5 + 0.5 * conf),
                     "dock_term": 1.0 - rank_pct[cid],
                     "dl_term": 1.0 - 0.25 * li,
                     "in_ad": int(p["in_domain"]) == 1,
                     "pred_mean": mu, "pred_var": var, "confidence": conf,
                     "lipinski_violations": li, "pains_alert": pre[cid]["pains_alert"],
                     "dock_avg_kcal": davg[cid]})

    base_order = _score_rows(comp, W_MODEL, W_DOCK, W_DL)
    base_map = {}
    for c in comp:
        s = (W_MODEL * c["model_term"] + W_DOCK * c["dock_term"] + W_DL * c["dl_term"])
        if not c["in_ad"]:
            s *= AD_PENALTY
        base_map[c["compound_id"]] = s

    rows = []
    for c in comp:
        cid = c["compound_id"]
        m = mol_of(next(r["smiles"] for r in cands if r["compound_id"] == cid))
        rows.append({"rank": None, "compound_id": cid, "name_cn": c["name_cn"],
                     "category": c["category"], "source_herb": c["source_herb"],
                     "role": c["role"], "legacy_label": c["legacy_label"],
                     "model_split": c["model_split"],
                     "board": board_of(c["model_split"]),
                     "pubchem_cid": c["pubchem_cid"], "data_mode": c["data_mode"],
                     "murcko_scaffold": scaffold_smiles(m),
                     "pred_mean": round(c["pred_mean"], 4),
                     "pred_var": round(c["pred_var"], 4),
                     "confidence": round(c["confidence"], 3),
                     "dock_avg_kcal": round(c["dock_avg_kcal"], 2),
                     "lipinski_violations": c["lipinski_violations"],
                     "pains_alert": c["pains_alert"],
                     "ad_warning": "" if c["in_ad"] else "域外",
                     "final_score": round(base_map[cid], 4)})
    rows.sort(key=lambda x: -x["final_score"])
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    write_csv(os.path.join(RES, "tables", "final_ranking_v2_real.csv"), rows)

    # ---- 项34 三榜分离 ----
    boards = {"known_retrospective": "已知回顾榜(参与过训练/选模,禁止当新发现)",
              "independent_test": "独立测试榜(未参与训练,标签未审核)",
              "unlabeled_screening": "未标注候选榜(唯一可提候选发现的池)"}
    for board, desc in boards.items():
        sub = [r for r in rows if r["board"] == board]
        write_csv(os.path.join(RES, "tables", f"board_{board}.csv"), sub)

    # ---- 指纹相似性簇多样性挑选(课程步骤 6; 项37口径) ----
    idx_by_id = {r["compound_id"]: i for i, r in enumerate(cands)}
    labels, fps = butina_clusters([mol_of(r["smiles"]) for r in cands])
    label_of = {cid: labels[idx_by_id[cid]] for cid in idx_by_id}
    murcko_of = {r["compound_id"]: r["murcko_scaffold"] for r in rows}

    picked, seen_clusters = [], set()
    for r in rows:
        cl = label_of[r["compound_id"]]
        if cl not in seen_clusters:
            picked.append(dict(r, cluster=cl))
            seen_clusters.add(cl)
        if len(picked) >= N_SELECT:
            break
    write_csv(os.path.join(RES, "tables", "diverse_top10.csv"), picked)

    # 未标注榜单独的多样性挑选: 候选发现唯一合法来源
    unlabeled = [r for r in rows if r["board"] == "unlabeled_screening"]
    picked_u, seen_u = [], set()
    for r in unlabeled:
        cl = label_of[r["compound_id"]]
        if cl not in seen_u:
            picked_u.append(dict(r, cluster=cl))
            seen_u.add(cl)
    write_csv(os.path.join(RES, "tables", "diverse_top10_unlabeled.csv"), picked_u)

    # ---- 项35/39 稳定性诊断 ----
    stability = rank_stability(comp, base_order)

    # ---- 项36 描述性相关(不证明独立) ----
    ms = np.array([r["pred_mean"] for r in rows])
    ds = np.array([r["dock_avg_kcal"] for r in rows])
    rho = spearman(ms, -ds)  # 对接分越负越强, 取负号统一方向

    murcko_all = len({r["murcko_scaffold"] for r in rows})
    murcko_top10 = len({r["murcko_scaffold"] for r in picked})
    board_counts = {}
    for r in rows:
        board_counts[r["board"]] = board_counts.get(r["board"], 0) + 1
    top10_board_counts = {}
    for r in picked:
        top10_board_counts[r["board"]] = top10_board_counts.get(r["board"], 0) + 1

    summary = {
        "interpretation": "探索性融合排序(diagnostic):权重与罚分为启发式,无外部标签验证,不得称三源共识或可靠排序",
        "n_candidates": len(rows), "n_fingerprint_clusters": len(set(label_of.values())),
        "fingerprint_cluster_note": "ECFP4 Tanimoto Butina(阈值0.55)指纹相似性簇,不等于Murcko骨架",
        "n_murcko_scaffolds_all": murcko_all, "n_murcko_scaffolds_top10": murcko_top10,
        "board_counts": board_counts, "top10_board_counts": top10_board_counts,
        "boards_desc": boards,
        "top10_historical_positives": sum(1 for r in picked if r["legacy_label"] == "1"),
        "targets": sorted(required_targets),
        "single_target_note": "单靶诊断运行：KEAP1未过多种子门控，本榜仅FXR证据，不得当双靶共识结论" if len(required_targets) == 1 else "",
        "spearman_model_dock": round(rho, 3) if np.isfinite(rho) else None,
        "spearman_note": "描述性相关,不证明两证据源独立,也不支持融合有效性",
        "inclusion_flow": inclusion_flow,
        "rank_stability": stability,
        "top10": [{"name": r["name_cn"], "board": r["board"], "split": r["model_split"],
                   "legacy_label": r["legacy_label"], "score": r["final_score"],
                   "pains": r["pains_alert"], "ad": r["ad_warning"]} for r in picked],
    }
    json.dump(summary, open(os.path.join(RES, "metrics", "fusion_summary.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[s5] 探索性融合排名: {len(rows)} 候选 (已知回顾{board_counts.get('known_retrospective',0)}"
          f"/独立测试{board_counts.get('independent_test',0)}/未标注{board_counts.get('unlabeled_screening',0)})")
    print(f"[s5] 指纹相似性簇 {summary['n_fingerprint_clusters']} 个; Murcko 骨架 {murcko_all} 个(口径分离,项37)")
    print(f"[s5] 纳排流: 注册{inclusion_flow['registered_candidates']} -> 对接缺失{len(dock_failed)}"
          f" -> 对照剔除{len(controls)} -> 入榜{len(rows)} (项39)")
    wp = stability["weight_perturbation"]
    print(f"[s5] 权重扰动Top10 Jaccard中位={wp['top10_jaccard_median']}"
          f" (p05-p95 {wp['top10_jaccard_p05_p95']}); 全秩Spearman中位={wp['full_rank_spearman_median']} (项35)")
    print(f"[s5] 模型分-真实对接分 Spearman={rho:.3f} (描述性相关，不证明独立性)")
    print(f"[s5] 多样性 Top-10(每指纹簇最优; 括号内=数据角色):")
    for r in picked:
        flags = (" [PAINS预警]" if r["pains_alert"] else "") + (" [域外]" if r["ad_warning"] else "")
        print(f"  #{r['rank']:>2} {r['name_cn']:<8} [{r['board']}] 总分{r['final_score']:.4f}{flags}")
    return rows, picked


if __name__ == "__main__":
    run()
