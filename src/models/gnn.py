# -*- coding: utf-8 -*-
"""图神经网络(纯numpy实现) + MC Dropout 不确定性估计

负责人: 宁显泷（算法组）
结构: 2层GCN(对称归一化邻接) -> 均值池化 -> Dropout -> 线性输出 sigmoid
不确定性: 推理时保持Dropout开启做T次前向(蒙特卡洛Dropout)，输出预测均值与方差
损失: 加权BCE；正类权重 w_pos 在 {1.0, 1.25, 1.5} 中按验证集F1选优
说明: 本地零依赖演示实现；服务器端迁移 PyTorch Geometric 版本(接口一致)。
"""
import csv
import os

import numpy as np

from models.dataset import load_split, load_pool, load_labeled_actives


def _sig(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


class GCN:
    def __init__(self, d_in=13, d_hid=32, d_out=16, p_drop=0.3, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2.0 / d_in), (d_in, d_hid))
        self.W2 = rng.normal(0, np.sqrt(2.0 / d_hid), (d_hid, d_out))
        self.W3 = rng.normal(0, np.sqrt(2.0 / d_out), (d_out, 1))
        self.b1 = np.zeros(d_hid)
        self.b2 = np.zeros(d_out)
        self.b3 = np.zeros(1)
        self.p = p_drop
        self.rng = rng
        self.params = ["W1", "b1", "W2", "b2", "W3", "b3"]
        self.m = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.v = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.t = 0
        self.mc = False

    # ---------- 前向（单个图） ----------
    def _dropout(self, H):
        if self.p <= 0:
            return H, None
        mask = (self.rng.random(H.shape) > self.p).astype(np.float64) / (1.0 - self.p)
        return H * mask, mask

    def _undropout(self, G, mask):
        return G if mask is None else G * mask

    def forward_graph(self, rec, use_drop):
        Xp = rec.A @ rec.X
        Z1 = Xp @ self.W1 + self.b1
        H1 = np.tanh(Z1)
        m1 = None
        if use_drop:
            H1, m1 = self._dropout(H1)
        U = (rec.A @ H1) @ self.W2 + self.b2
        H2 = np.tanh(U)
        pooled = H2.mean(0)
        m2 = None
        if use_drop:
            pooled, m2 = self._dropout(pooled)
        z = float(pooled @ self.W3 + self.b3)
        cache = (Xp, Z1, H1, m1, U, H2, pooled, m2)
        return z, cache

    def forward_batch(self, recs, use_drop=False):
        zs, caches = [], []
        for r in recs:
            z, c = self.forward_graph(r, use_drop)
            zs.append(z)
            caches.append(c)
        return np.array(zs), caches

    # ---------- 反向（单个图） ----------
    def backward_graph(self, rec, dz, cache):
        Xp, Z1, H1, m1, U, H2, pooled, m2 = cache
        n = len(rec.g.atoms)
        gW1 = np.zeros_like(self.W1); gb1 = np.zeros_like(self.b1)
        gW2 = np.zeros_like(self.W2); gb2 = np.zeros_like(self.b2)
        gW3 = np.zeros_like(self.W3); gb3 = np.zeros_like(self.b3)
        # 输出层
        gW3 += np.outer(pooled, dz)
        gb3 += dz
        dpool = self.W3[:, 0] * dz
        dpool = self._undropout(dpool, m2)
        # 池化: pooled = mean_i H2[i]
        dU = np.tile(dpool / n, (n, 1)) * (1.0 - H2 ** 2)
        H1d = H1  # 前向缓存已包含 Dropout；W2 梯度不得重复乘掩码
        gW2 += (rec.A @ H1d).T @ dU
        gb2 += dU.sum(0)
        dH1d = rec.A.T @ (dU @ self.W2.T)
        dZ1 = self._undropout(dH1d, m1) * (1.0 - np.tanh(Z1) ** 2)
        gW1 += Xp.T @ dZ1
        gb1 += dZ1.sum(0)
        return {"W1": gW1, "b1": gb1, "W2": gW2, "b2": gb2, "W3": gW3, "b3": gb3}

    # ---------- 训练 ----------
    def train_step(self, recs, ys, w_pos, lr=0.01, wd=1e-4):
        zs, caches = self.forward_batch(recs, use_drop=True)
        ps = _sig(zs)
        eps = 1e-9
        w = np.where(ys == 1, w_pos, 1.0)
        loss = float(-np.mean(w * (ys * np.log(ps + eps) + (1 - ys) * np.log(1 - ps + eps))))
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
            mh = self.m[k] / (1 - 0.9 ** self.t)
            vh = self.v[k] / (1 - 0.999 ** self.t)
            setattr(self, k, getattr(self, k) - lr * mh / (np.sqrt(vh) + 1e-8))
        return loss

    def fit(self, recs, ys, epochs=300, w_pos=1.0, lr=0.01, verbose=False):
        for ep in range(epochs):
            loss = self.train_step(recs, ys, w_pos, lr)
            if verbose and ep % 100 == 0:
                print(f"  epoch {ep:3d} loss={loss:.4f}")
        return self

    # ---------- 推理 ----------
    def predict_mc(self, recs, T=30):
        self.mc = True
        runs = [_sig(self.forward_batch(recs, use_drop=True)[0]) for _ in range(T)]
        self.mc = False
        P = np.array(runs)  # (T, n)
        return P.mean(0), P.var(0)


# ----------------- 评估工具 -----------------
def auc(y, s):
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    ranks[order] = np.arange(1, len(s) + 1)
    for v in np.unique(s):
        m = s == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def metrics(y, p, thr=0.5):
    yh = (p >= thr).astype(int)
    tp = int(((yh == 1) & (y == 1)).sum()); fp = int(((yh == 1) & (y == 0)).sum())
    fn = int(((yh == 0) & (y == 1)).sum()); tn = int(((yh == 0) & (y == 0)).sum())
    acc = (tp + tn) / max(1, len(y))
    rec = tp / max(1, tp + fn); prec = tp / max(1, tp + fp)
    f1 = 2 * prec * rec / max(1e-9, prec + rec)
    bacc = 0.5 * (rec + tn / max(1, tn + fp))
    return {"AUC": round(auc(y, p), 3), "ACC": round(acc, 3),
            "BACC": round(bacc, 3), "F1": round(f1, 3)}


def ece(y, p, bins=10):
    e, n = 0.0, len(p)
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (p >= lo) & ((p < hi) if b < bins - 1 else (p <= 1.0))
        if m.sum() == 0:
            continue
        e += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return round(e, 3)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


# ----------------- 主流程 -----------------
def run(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    train = load_split("train"); val = load_split("val"); test = load_split("test")
    ytr = np.array([r.label for r in train])
    yva = np.array([r.label for r in val])
    yte = np.array([r.label for r in test])

    # --- 损失权重选择（验证集F1最优） ---
    best = None
    for wp in (1.0, 1.25, 1.5):
        m = GCN(seed=42).fit(train, ytr, epochs=300, w_pos=wp)
        pv, _ = m.predict_mc(val, T=10)
        f1 = metrics(yva, pv)["F1"]
        print(f"[gnn] w_pos={wp}: 验证集F1={f1}")
        if best is None or f1 > best[1]:
            best = (wp, f1)
    wp, f1_val = best
    print(f"[gnn] 选定正类损失权重 w_pos={wp} (验证集F1={f1_val})")

    model = GCN(seed=7).fit(train, ytr, epochs=300, w_pos=wp)
    pm, pv = model.predict_mc(test, T=30)
    te_m = metrics(yte, pm)
    te_m["ECE"] = ece(yte, pm)
    rho = spearman(pv, np.abs(yte - pm))

    pool = load_pool()
    pm_pool, pv_pool = model.predict_mc(pool, T=30)

    # 最终批量推理: 全候选池 = HP活性分子 + NV新分子（模型冻结后统一出分）
    actives = load_labeled_actives()
    pm_act, pv_act = model.predict_mc(actives, T=30)

    with open(os.path.join(out_dir, "test_predictions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["compound_id", "name_cn", "label", "pred_mean", "pred_var"])
        for r, mu, var in zip(test, pm, pv):
            # 全精度写出：固定小数位会让近零方差并列，导致第三方复算指标出现偏差
            w.writerow([r.cid, r.name, r.label, repr(float(mu)), repr(float(var))])
    with open(os.path.join(out_dir, "fullpool_predictions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["compound_id", "name_cn", "pred_mean", "pred_var"])
        for r, mu, var in zip(actives + pool,
                              np.concatenate([pm_act, pm_pool]),
                              np.concatenate([pv_act, pv_pool])):
            w.writerow([r.cid, r.name, repr(float(mu)), repr(float(var))])

    np.save(os.path.join(out_dir, "test_mean.npy"), pm)
    np.save(os.path.join(out_dir, "test_var.npy"), pv)
    print(f"[gnn] 测试集: {te_m}；方差-|误差| Spearman rho={rho:.3f}")
    return {"w_pos": wp, "f1_val": f1_val, "test": te_m,
            "spearman_var_err": round(rho, 3)}


if __name__ == "__main__":
    run(os.path.join(os.path.dirname(__file__), "..", "..", "results", "predictions"))
