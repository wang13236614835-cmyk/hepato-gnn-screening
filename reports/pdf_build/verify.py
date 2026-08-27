# -*- coding: utf-8 -*-
"""独立复核脚本：不导入项目任何模块，仅用 csv+numpy 从结果文件重算全部指标，
与 PDF/报告中引用的数值逐条比对。"""
import csv
import os

import numpy as np

ROOT = r"D:\zcode-workspace\hepato-gnn-screening"
R = lambda *p: os.path.join(ROOT, *p)  # noqa: E731
ok, bad = [], []


def check(claim, actual, tol=0.0):
    if isinstance(actual, (bool, np.bool_)):
        good = bool(actual)
    else:
        good = (abs(claim - actual) <= tol) if isinstance(claim, float) else (claim == actual)
    (ok if good else bad).append((claim, actual))


def rows(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


print("=" * 60)
print("A. 数据规模")
cleaned = rows(R("data", "processed", "cleaned_compounds.csv"))
pool = rows(R("data", "processed", "screening_pool.csv"))
hp = [r for r in cleaned if r["compound_id"].startswith("HP")]
dc = [r for r in cleaned if r["compound_id"].startswith("DC")]
check("cleaned=88", len(cleaned) == 88)
check("HP=48", len(hp) == 48)
check("DC=40", len(dc) == 40)
check("pool=12", len(pool) == 12)
rej_path = R("data", "processed", "rejected.csv")
check("rejected=0", 0 if not os.path.exists(rej_path) else len(rows(rej_path)) == 0)
ev_a = [r for r in hp if r["evidence_level"] == "A"]
check("A级=3(水飞蓟宾/甘草酸/姜黄素)",
      sorted(r["name_cn"] for r in ev_a) == ["姜黄素", "水飞蓟宾", "甘草酸"])
scaf = {r["scaffold"] for r in cleaned}
check("骨架组=53", len(scaf) == 53)
check("无环组=1", sum(1 for s in scaf if s == "ACYCLIC") == 1)
sp = {}
for n in ("train", "val", "test"):
    rr = rows(R("data", "splits", n + ".csv"))
    sp[n] = (len(rr), sum(1 for r in rr if r["label"] == "1"))
check("train=(58,28)", sp["train"] == (58, 28))
check("val=(13,8)", sp["val"] == (13, 8))
check("test=(17,12)", sp["test"] == (17, 12))
# 新分子池构成
cat = {}
for r in pool:
    cat[r["category"]] = cat.get(r["category"], 0) + 1
print("  新分子池类别构成:", cat)

print("B. 测试集指标（从test_predictions.csv独立重算）")
tp = rows(R("results", "predictions", "test_predictions.csv"))
y = np.array([int(r["label"]) for r in tp])
p = np.array([float(r["pred_mean"]) for r in tp])
v = np.array([float(r["pred_var"]) for r in tp])
check("n_test=17", len(tp) == 17)


def auc(yy, ss):
    order = np.argsort(ss, kind="mergesort")
    rk = np.empty(len(ss)); rk[order] = np.arange(1, len(ss) + 1)
    for val in np.unique(ss):
        m = ss == val
        if m.sum() > 1:
            rk[m] = rk[m].mean()
    n1 = yy.sum(); n0 = len(yy) - n1
    return (rk[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


yh = (p >= 0.5).astype(int)
tpn = ((yh == 1) & (y == 1)).sum(); fp = ((yh == 1) & (y == 0)).sum()
fn = ((yh == 0) & (y == 1)).sum(); tn = ((yh == 0) & (y == 0)).sum()
rec = tpn / (tpn + fn); prec = tpn / (tpn + fp)
f1 = 2 * prec * rec / (prec + rec)
bacc = 0.5 * (rec + tn / (tn + fp))
print(f"  重算: AUC={auc(y,p):.3f} ACC={(tpn+tn)/17:.3f} BACC={bacc:.3f} F1={f1:.3f}")
# 注: CSV中pred_mean保留4位小数会产生并列秩，AUC与全精度(0.967)相差约0.008
check("AUC=0.967(全精度CSV)", round(auc(y, p), 3) == 0.967)
check("ACC=0.824", round((tpn + tn) / 17, 3) == 0.824)
check("BACC=0.875", round(bacc, 3) == 0.875)
check("F1=0.857", round(f1, 3) == 0.857)
e = 0.0
for b in range(10):
    m = (p >= b / 10) & ((p < (b + 1) / 10) if b < 9 else (p <= 1.0))
    if m.sum():
        e += m.sum() / 17 * abs(p[m].mean() - y[m].mean())
print(f"  重算 ECE={e:.3f}")
check("ECE=0.210", round(e, 3) == 0.210)
ra = np.argsort(np.argsort(v)).astype(float)
rb = np.argsort(np.argsort(np.abs(y - p))).astype(float)
ra -= ra.mean(); rb -= rb.mean()
rho = float((ra * rb).sum() / np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))
print(f"  重算 Spearman(方差,|误差|)={rho:.3f}")
check("rho=0.718(全精度CSV)", round(rho, 3) == 0.718)

print("C. 基准线（baseline.csv）")
bl = {r["model"]: r for r in rows(R("results", "metrics", "baseline.csv"))}
check("NB AUC=0.850", bl["高斯朴素贝叶斯(描述符)"]["AUC"] == "0.85")
check("LR AUC=0.967", bl["逻辑回归(2048bit指纹)"]["AUC"] == "0.967")
check("LR F1=0.737", bl["逻辑回归(2048bit指纹)"]["F1"] == "0.737")
check("NB F1=0.762", bl["高斯朴素贝叶斯(描述符)"]["F1"] == "0.762")

print("D. 对接（docking_scores.csv）")
dock = rows(R("results", "docking", "docking_scores.csv"))
lab = {r["compound_id"]: r["label"] for r in cleaned}
fx = {r["compound_id"]: float(r["score_kcal"]) for r in dock if r["target"] == "FXR_LBD"}
m1 = np.mean([fx[k] for k, l in lab.items() if l == "1"])
m0 = np.mean([fx[k] for k, l in lab.items() if l == "0"])
print(f"  重算: 活性{m1:.2f} vs 负参照{m0:.2f} (差{abs(m1-m0):.2f})")
check("活性均值=-5.46", round(m1, 2) == -5.46)
check("负参照均值=-5.05", round(m0, 2) == -5.05)
check("靶点数=2", len({r["target"] for r in dock}) == 2)

print("E. 适用域（ad_report.csv）")
ad = rows(R("results", "ad", "ad_report.csv"))
nv_ad = [r for r in ad if r["compound_id"].startswith("NV")]
out = [r["name_cn"] for r in nv_ad if r["in_domain"] == "0"]
check("h*=0.362", round(float(ad[0]["h_star"]), 3) == 0.362)
check("NV域外=7", len(out) == 7)
print("  域外新分子:", out)

print("F. 排名总表（final_ranking.csv）")
rk = rows(R("results", "rankings", "final_ranking.csv"))
check("候选总数=60", len(rk) == 60)
pdf_top10 = [
    ("黄芩苷", "0.9612", "0.0012", "0.863", "-6.86", "0.9291"),
    ("二氢杨梅素", "0.9653", "0.0017", "0.837", "-7.14", "0.899"),
    ("葛根素", "0.9614", "0.0018", "0.832", "-7.03", "0.8903"),
    ("姜黄素", "0.8898", "0.005", "0.718", "-6.94", "0.8821"),
    ("柚皮素", "0.9413", "0.0021", "0.815", "-6.54", "0.8811"),
    ("木犀草素", "0.9783", "0.0008", "0.887", "-6.43", "0.8704"),
    ("水飞蓟宾", "0.9666", "0.0011", "0.869", "-6.39", "0.8497"),
    ("松脂素", "0.8814", "0.0068", "0.67", "-6.64", "0.8397"),
    ("槲皮素", "0.9718", "0.0031", "0.776", "-6.37", "0.8198"),
    ("落叶松脂素", "0.7912", "0.0097", "0.606", "-6.89", "0.8181"),
]
for i, (name, mu, var, conf, dk, fs) in enumerate(pdf_top10):
    r = rk[i]
    got = (r["name_cn"] == name, r["pred_mean"] == mu, r["pred_var"] == var,
           r["confidence"] == conf, r["dock_avg_kcal"] == dk, r["final_score"] == fs)
    if not all(got):
        bad.append((f"Top{i+1}", (name, mu, var, conf, dk, fs),
                    (r["name_cn"], r["pred_mean"], r["pred_var"], r["confidence"],
                     r["dock_avg_kcal"], r["final_score"])))
    else:
        ok.append(f"Top{i+1}全对")
fp_ = rows(R("results", "predictions", "fullpool_predictions.csv"))
mus = {r["compound_id"]: float(r["pred_mean"]) for r in fp_}
vs = {r["compound_id"]: float(r["pred_var"]) for r in fp_}
mx = max(mus, key=mus.get); mn = min(vs, key=vs.get)
nm = {r["compound_id"]: r["name_cn"] for r in fp_}
print(f"  全场最高模型分: {nm[mx]} {mus[mx]:.4f}；最低方差: {nm[mn]} {vs[mn]:.4f}")
check("全场最高分=大黄素", nm[mx] == "大黄素")
check("全场最低方差=苦参碱", nm[mn] == "苦参碱")
check("fullpool=60", len(fp_) == 60)
ob = [r for r in rk if r["compound_id"] == "NV-011"][0]
check("奥贝胆酸分≈0.26", abs(float(ob["pred_mean"]) - 0.26) < 0.01)
check("奥贝胆酸域外", ob["ad_warning"] != "")
nv_rank = {r["name_cn"]: int(r["rank"]) for r in rk if r["compound_id"].startswith("NV")}
print("  NV排名:", nv_rank)
check("松脂素#8", nv_rank.get("松脂素") == 8)
check("落叶松脂素#10", nv_rank.get("落叶松脂素") == 10)

print("=" * 60)
print(f"通过 {len(ok)} 项；不符 {len(bad)} 项")
for b in bad:
    print("  ✗ 声称:", b[0] if len(b) == 2 else b[0], "| 实际:", b[1] if len(b) == 2 else b[2])
