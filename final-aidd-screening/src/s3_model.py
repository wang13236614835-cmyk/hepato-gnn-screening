# -*- coding: utf-8 -*-
"""暑假方法诊断模块。课程对应主题见 learning/共享；不宣称未经核实的课程章号或原话。
PAINS命中仅为干扰风险提示，不能称为已证实假阳性。研究身份/标签审核独立于代码运行。"""
import csv
import json
import os
import random
from collections import defaultdict

import numpy as np
from rdkit.Chem import Descriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from common import (DATA, RES, SPLITS, GraphRecord, auc, ece, ecfp_bits,
                    load_labeled, load_pool, metrics, read_csv, records_of, scaffold_smiles, mol_of,
                    rdkit_descriptors, spearman, write_csv, DESC_FEATS)

SEED = 42


# ---------------- GCN(纯 numpy, 与主线同实现) ----------------
def _sig(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


class GCN:
    def __init__(self, d_in=13, d_hid=32, d_out=16, p_drop=0.3, seed=SEED):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2 / d_in), (d_in, d_hid))
        self.W2 = rng.normal(0, np.sqrt(2 / d_hid), (d_hid, d_out))
        self.W3 = rng.normal(0, np.sqrt(2 / d_out), (d_out, 1))
        self.b1 = np.zeros(d_hid); self.b2 = np.zeros(d_out); self.b3 = np.zeros(1)
        self.p = p_drop; self.rng = rng
        self.params = ["W1", "b1", "W2", "b2", "W3", "b3"]
        self.m = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.v = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.t = 0

    def _dropout(self, H):
        mask = (self.rng.random(H.shape) > self.p).astype(np.float64) / (1 - self.p)
        return H * mask, mask

    def forward_graph(self, rec, use_drop):
        Xp = rec.A @ rec.X
        Z1 = Xp @ self.W1 + self.b1; H1 = np.tanh(Z1)
        m1 = None
        if use_drop:
            H1, m1 = self._dropout(H1)
        U = (rec.A @ H1) @ self.W2 + self.b2
        H2 = np.tanh(U)
        pooled = H2.mean(0)
        m2 = None
        if use_drop:
            pooled, m2 = self._dropout(pooled)
        z = float((pooled @ self.W3 + self.b3).item())
        return z, (Xp, Z1, H1, m1, U, H2, pooled, m2)

    def forward_batch(self, recs, use_drop=False):
        zs, caches = zip(*(self.forward_graph(r, use_drop) for r in recs))
        return np.array(zs), caches

    def backward_graph(self, rec, dz, cache):
        Xp, Z1, H1, m1, U, H2, pooled, m2 = cache
        n = len(rec.X)
        g = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        g["W3"] += np.outer(pooled, dz); g["b3"] += dz
        dpool = self.W3[:, 0] * dz
        dpool = dpool if m2 is None else dpool * m2
        dU = np.tile(dpool / n, (n, 1)) * (1 - H2 ** 2)
        H1d = H1  # 前向缓存已施加 Dropout
        g["W2"] += (rec.A @ H1d).T @ dU; g["b2"] += dU.sum(0)
        dH1d = rec.A.T @ (dU @ self.W2.T)
        dZ1 = (dH1d if m1 is None else dH1d * m1) * (1 - np.tanh(Z1) ** 2)
        g["W1"] += Xp.T @ dZ1; g["b1"] += dZ1.sum(0)
        return g

    def train_step(self, recs, ys, w_pos, lr=0.01, wd=1e-4):
        zs, caches = self.forward_batch(recs, use_drop=True)
        ps = _sig(zs)
        w = np.where(ys == 1, w_pos, 1.0)
        eps = 1e-9
        dz = (w * (ps - ys) / len(ys)).reshape(-1)
        grads = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        for r, dzk, ck in zip(recs, dz, caches):
            gg = self.backward_graph(r, dzk, ck)
            for k in self.params:
                grads[k] += gg[k]
        self.t += 1
        for k in self.params:
            g = grads[k] + wd * getattr(self, k)
            self.m[k] = 0.9 * self.m[k] + 0.1 * g
            self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh = self.m[k] / (1 - 0.9 ** self.t); vh = self.v[k] / (1 - 0.999 ** self.t)
            setattr(self, k, getattr(self, k) - lr * mh / (np.sqrt(vh) + 1e-8))
        return float(-np.mean(w * (ys * np.log(ps + eps) + (1 - ys) * np.log(1 - ps + eps))))

    def fit(self, recs, ys, epochs=300, w_pos=1.0, lr=0.01):
        for _ in range(epochs):
            self.train_step(recs, ys, w_pos, lr)
        return self

    def predict_mc(self, recs, T=30):
        runs = [_sig(self.forward_batch(recs, use_drop=True)[0]) for _ in range(T)]
        P = np.array(runs)
        return P.mean(0), P.var(0)

    def predict_mean(self, recs):
        return _sig(self.forward_batch(recs, use_drop=False)[0])


# ---------------- 骨架划分(组级贪心, 与主线同口径) ----------------
def make_splits():
    random.seed(SEED)
    rows = load_labeled()
    groups = defaultdict(list)
    for r in rows:
        r["scaffold"] = scaffold_smiles(mol_of(r["smiles"]))
        groups[r["scaffold"]].append(r)
    keys = sorted(groups, key=lambda k: (-len(groups[k]), k))
    random.shuffle(keys)
    n = len(rows)
    caps = {"test": n * 0.20, "val": n * 0.15}
    assign, count = {}, defaultdict(int)
    for k in keys:
        for split_name in ("test", "val", "train"):
            if count[split_name] + len(groups[k]) <= caps.get(split_name, 1e9) or split_name == "train":
                assign[k] = split_name
                count[split_name] += len(groups[k])
                break
    os.makedirs(SPLITS, exist_ok=True)
    stats = {}
    for split_name in ("train", "val", "test"):
        sel = [r for r in rows if assign[r["scaffold"]] == split_name]
        stats[split_name] = (len(sel), sum(1 for r in sel if r["label"] == "1"))
        write_csv(os.path.join(SPLITS, f"{split_name}.csv"), sel)
        print(f"[s3] {split_name}: {len(sel)} 条 (正 {stats[split_name][1]})")
    print(f"[s3] 骨架组总数 {len(keys)}(组级划分, 无同骨架跨集)")
    return stats


def _desc_matrix(rows):
    return np.array([[rdkit_descriptors(mol_of(r["smiles"]))[k] for k in DESC_FEATS] for r in rows])


def applicability_domain(train_rows, eval_rows_list):
    """训练集描述符杠杆值 h* = 3p/n;超限判域外(OECD 适用域声明)。"""
    Xtr = _desc_matrix(train_rows)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    Z = (Xtr - mu) / sd
    p, n = Z.shape[1], Z.shape[0]
    h_star = 3.0 * p / n
    inv = np.linalg.pinv(Z.T @ Z + 1e-6 * np.eye(p))
    out = {}
    for name, rows in eval_rows_list:
        Ze = (_desc_matrix(rows) - mu) / sd
        h = np.einsum("ij,jk,ik->i", Ze, inv, Ze)
        out[name] = {r["compound_id"]: int(hi <= h_star) for r, hi in zip(rows, h)}
    return h_star, out


def fit_temperature(z_val, y_val):
    """温度缩放: 网格搜索 T 最小化验证集 NLL;仅当验证集 ECE 实际改善(>=0.02)才启用。

    小验证集下参数有较高方差；本规则仅在验证集上决定，测试集不参与选择。
    同一验证集用于模型选择与校准，当前仅为诊断，正式研究需独立校准设计。
    """
    p_val = _sig(z_val)
    ece_before = ece(y_val, p_val)
    best_T, best_nll = 1.0, float("inf")
    for T in np.arange(0.5, 5.01, 0.1):
        q = _sig(z_val / T)
        nll = -np.mean(y_val * np.log(q + 1e-9) + (1 - y_val) * np.log(1 - q + 1e-9))
        if nll < best_nll:
            best_T, best_nll = round(float(T), 2), nll
    q = _sig(z_val / best_T)
    ece_after = ece(y_val, q)
    return best_T if (ece_before - ece_after) >= 0.02 else 1.0


def auc_bootstrap_ci(y, p, n_boot=3000, seed=SEED):
    """分层有放回自助法AUC区间(固定预测重抽样；不含训练/划分/身份修订不确定性)。"""
    rng = np.random.default_rng(seed)
    y = np.asarray(y); p = np.asarray(p)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    vals = []
    for _ in range(n_boot):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        v = auc(y[idx], p[idx])
        if np.isfinite(v):
            vals.append(v)
    if not vals:
        return None, 0
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return (round(float(lo), 3), round(float(hi), 3)), len(vals)


def run():
    os.makedirs(os.path.join(RES, "metrics"), exist_ok=True)
    os.makedirs(os.path.join(RES, "predictions"), exist_ok=True)
    make_splits()

    train_rows = read_csv(os.path.join(SPLITS, "train.csv"))
    val_rows = read_csv(os.path.join(SPLITS, "val.csv"))
    test_rows = read_csv(os.path.join(SPLITS, "test.csv"))
    ytr = np.array([int(r["label"]) for r in train_rows])
    yva = np.array([int(r["label"]) for r in val_rows])
    yte = np.array([int(r["label"]) for r in test_rows])
    if any(len(np.unique(y)) < 2 for y in (ytr, yva, yte)):
        raise ValueError("规范骨架划分后某集合不足两类；需要更多经核验数据或另行预注册分组方案，不能回退到泄漏划分")
    sets = [{scaffold_smiles(mol_of(r["smiles"])) for r in rs} for rs in (train_rows,val_rows,test_rows)]
    assert all(not sets[i] & sets[j] for i in range(3) for j in range(i)), "骨架跨集"

    train = [GraphRecord(r) for r in train_rows]
    val = [GraphRecord(r) for r in val_rows]
    test = [GraphRecord(r) for r in test_rows]

    # ---- 基线 1: ECFP4 + 随机森林(课程推荐基线) ----
    Xtr = np.stack([ecfp_bits(r.mol) for r in train])
    Xte = np.stack([ecfp_bits(r.mol) for r in test])
    rf = RandomForestClassifier(n_estimators=400, random_state=SEED, n_jobs=2)
    rf.fit(Xtr, ytr)
    p_rf = rf.predict_proba(Xte)[:, 1]
    m_rf = metrics(yte, p_rf); m_rf["ECE"] = ece(yte, p_rf)

    # ---- 基线 2: 描述符 + 逻辑回归 ----
    Dtr, Dte = _desc_matrix(train_rows), _desc_matrix(test_rows)
    mu, sd = Dtr.mean(0), Dtr.std(0) + 1e-9
    lr = LogisticRegression(max_iter=2000, random_state=SEED)
    lr.fit((Dtr - mu) / sd, ytr)
    p_lr = lr.predict_proba((Dte - mu) / sd)[:, 1]
    m_lr = metrics(yte, p_lr); m_lr["ECE"] = ece(yte, p_lr)

    # ---- GNN + MC Dropout(正类损失权重按验证集 F1 选优) ----
    best = None
    for wp in (1.0, 1.25, 1.5):
        m = GCN(seed=SEED).fit(train, ytr, epochs=300, w_pos=wp)
        pv, _ = m.predict_mc(val, T=10)
        f1v = metrics(yva, pv)["F1"]
        if best is None or f1v > best[1]:
            best = (wp, f1v)
    wp, _ = best
    gnn = GCN(seed=SEED).fit(train, ytr, epochs=300, w_pos=wp)
    pm, pv = gnn.predict_mc(test, T=30)
    m_gnn = metrics(yte, pm); m_gnn["ECE"] = ece(yte, pm)
    ci95, n_eff = auc_bootstrap_ci(yte, pm)
    rho = spearman(pv, np.abs(yte - pm))

    # ---- 温度校准(验证集拟合 T, 测试集只报指标) ----
    p_val_mc, _ = gnn.predict_mc(val, T=30)
    p_val_mc = np.clip(p_val_mc, 1e-9, 1 - 1e-9)
    z_val = np.log(p_val_mc / (1 - p_val_mc))
    T_best = fit_temperature(z_val, yva.astype(float))
    pm_cal = _sig(np.log(np.clip(pm, 1e-9, 1 - 1e-9) / np.clip(1 - pm, 1e-9, None)) / T_best)
    ece_cal = ece(yte, pm_cal)

    # ---- 适用域 ----
    pool_rows = load_pool()
    h_star, ad = applicability_domain(
        train_rows, [("test", test_rows), ("pool", pool_rows)])

    # ---- 全池推理(HP 活性 48 + NV 新分子 12) ----
    from common import load_candidates
    cand_rows = load_candidates()
    cands = [GraphRecord(r) for r in cand_rows]
    pm_c, pv_c = gnn.predict_mc(cands, T=30)
    ad_cand = {}
    hp_rows = [r for r in load_labeled() if r["label"] == "1"]
    _, ad_hv = applicability_domain(train_rows, [("hp", hp_rows), ("pool", pool_rows)])
    ad_map = {**ad_hv["hp"], **ad_hv["pool"]}

    write_csv(os.path.join(RES, "predictions", "test_predictions.csv"),
              [{"compound_id": r.cid, "name_cn": r.name, "label": r.label,
                "pred_mean": repr(float(a)), "pred_var": repr(float(b)),
                "in_domain": ad["test"].get(r.cid, 1)}
               for r, a, b in zip(test, pm, pv)])
    write_csv(os.path.join(RES, "predictions", "fullpool_predictions.csv"),
              [{"compound_id": r.cid, "name_cn": r.name,
                "pred_mean": repr(float(a)), "pred_var": repr(float(b)),
                "in_domain": ad_map.get(r.cid, 1)}
               for r, a, b in zip(cands, pm_c, pv_c)])

    np.savez(os.path.join(RES, "metrics", "gnn_weights.npz"), **{k: getattr(gnn,k) for k in gnn.params})
    write_csv(os.path.join(RES, "predictions", "baseline_test_predictions.csv"),
              [{"compound_id": r["compound_id"], "label": int(r["label"]), "rf": float(a), "lr": float(b)} for r,a,b in zip(test_rows,p_rf,p_lr)])
    summary = {
        "w_pos": wp, "temperature": T_best, "seed": SEED, "data_mode": os.environ.get("HEPATO_DATA_MODE", "reviewed"),
        "baselines": {"ECFP+RF": m_rf, "Desc+LR": m_lr},
        "gnn": {**m_gnn, "ECE_before_cal": m_gnn["ECE"], "ECE_after_cal": ece_cal,
                "spearman_var_err": round(rho, 3),
                "AUC_95CI_stratified_bootstrap": list(ci95) if ci95 else None,
                "AUC_95CI_note": "固定预测重抽样3000次；不含训练/划分/身份修订不确定性"},
        "ad_h_star": round(h_star, 3),
        "ad_pool_out": sum(1 for v in ad["pool"].values() if not v),
        "splits": {k: {"n": v[0], "pos": v[1]} for k, v in
                   {"train": (len(train_rows), int(ytr.sum())),
                    "val": (len(val_rows), int(yva.sum())),
                    "test": (len(test_rows), int(yte.sum()))}.items()},
    }
    json.dump(summary, open(os.path.join(RES, "metrics", "model_summary.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[s3] 基线 ECFP+RF: {m_rf}")
    print(f"[s3] 基线 Desc+LR: {m_lr}")
    print(f"[s3] GNN+MC-Dropout: {m_gnn} | 方差-|误差| Spearman={rho:.3f}")
    if T_best > 1.0 and ece_cal > m_gnn["ECE"]:
        print(f"[s3] 温度校准 T={T_best}(验证集拟合): 测试集 ECE {m_gnn['ECE']} -> {ece_cal} "
              f"未迁移(小样本局限, 如实记录;排名仍用未校准 MC 均值/方差)")
    else:
        print(f"[s3] 温度校准 T={T_best}: ECE {m_gnn['ECE']} -> {ece_cal}")
    print(f"[s3] 适用域 h*={h_star:.3f};新分子池域外 {summary['ad_pool_out']}/{len(pool_rows)}")
    return summary


if __name__ == "__main__":
    run()
