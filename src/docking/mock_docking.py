# -*- coding: utf-8 -*-
"""批量"对接"评分（本地演示模式 = 物理启发打分函数）

负责人: 代维斯丹（验证组）
重要说明:
  本地演示机未部署 AutoDock Vina / ADFR 桶。为保证全流程可跑通，
  此处以靶点口袋类型加权的物理启发打分替代:
      score ≈ 基线 + 口袋偏好项(疏水/芳香/极性) + 大分子渗透罚 + 重复种子噪声
  评分单位标定到 kcal/mol 量级仅供排序参考，服务器端运行 run_vina.sh 复算覆盖。
噪声种子由(分子ID+靶点)哈希决定，保证结果可复现。
"""
import csv
import hashlib
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "results", "docking")

FEATS = ["MW", "logP_est", "TPSA_est", "nHBD", "nHBA", "nRot", "nAromSystems"]

# 口袋类型 -> 描述符权重（正=偏好），对应物理直觉:
#   FXR疏水口袋偏好高logP/多芳香环；Keap1极性口袋偏好HBA/HBD、容忍较小分子
POCKET_W = {
    "FXR_LBD": {"logP_est": 0.55, "nAromSystems": 0.50, "MW": 0.25,
                "TPSA_est": -0.30, "nHBA": -0.10},
    "KEAP1_KELCH": {"nHBA": 0.45, "nHBD": 0.25, "nAromSystems": 0.25,
                    "logP_est": 0.10, "MW": -0.20},
}
BASELINE = -5.6
SCALE = 1.9
MW_PENALTY = 0.8  # MW>550 每超100追加罚分(kcal/mol)


def _seeded_noise(cid, target):
    h = int(hashlib.md5(f"{cid}|{target}".encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(h)
    return float(rng.normal(0.0, 0.35))


def _zscore(vals):
    a = np.array(vals, dtype=float)
    mu, sd = a.mean(), a.std() + 1e-9
    return (a - mu) / sd


def score_all():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for fname in ("cleaned_compounds.csv", "screening_pool.csv"):
        with open(os.path.join(PROC, fname), encoding="utf-8-sig") as f:
            rows.extend(list(csv.DictReader(f)))
    z = {c: _zscore([r[c] for r in rows]) for c in FEATS}

    out = []
    for i, r in enumerate(rows):
        mw = float(r["MW"])
        for target, w in POCKET_W.items():
            lig = sum(wc * z[c][i] for c, wc in w.items())
            pen = MW_PENALTY * max(0.0, (mw - 550.0) / 100.0)
            score = BASELINE - SCALE * lig + pen + _seeded_noise(r["compound_id"], target)
            out.append({"compound_id": r["compound_id"], "name_cn": r["name_cn"],
                        "target": target, "score_kcal": round(score, 2),
                        "mode": "mock_local"})

    with open(os.path.join(OUT, "docking_scores.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    lab = [r for r in rows if r.get("label") == "1"]
    dec = [r for r in rows if r.get("label") == "0"]
    ix_lab = {r["compound_id"] for r in lab}
    fxr = {r["compound_id"]: r["score_kcal"] for r in out if r["target"] == "FXR_LBD"}
    m_act = np.mean([fxr[c] for c in ix_lab])
    m_dec = np.mean([fxr[c] for c in {r["compound_id"] for r in dec}])
    print(f"[docking] FXR演示评分均值: 保肝活性分子 {m_act:.2f} vs 负参照 {m_dec:.2f} kcal/mol "
          f"(差距 {abs(m_act-m_dec):.2f})")
    return out


if __name__ == "__main__":
    score_all()
