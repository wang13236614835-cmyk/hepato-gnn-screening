# -*- coding: utf-8 -*-
"""按骨架划分数据集（组级划分避免同骨架泄漏）

负责人: 衣思淼（数据组）
策略: 以 Murcko 骨架签名为分组单位，按组贪心装入
      test(约20%) / val(约15%) / train(其余)，尽量保持标签比例。
"""
import csv
import os
import random
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROC = os.path.join(ROOT, "data", "processed")
SPLITS = os.path.join(ROOT, "data", "splits")


def split(frac_test=0.20, frac_val=0.15, seed=42):
    random.seed(seed)
    with open(os.path.join(PROC, "cleaned_compounds.csv"), encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for r in rows:
        groups[r["scaffold"]].append(r)

    keys = sorted(groups, key=lambda k: (-len(groups[k]), k))
    random.shuffle(keys)
    n = len(rows)
    caps = {"test": n * frac_test, "val": n * frac_val}
    assign = {}
    count = defaultdict(int)
    for k in keys:
        g = groups[k]
        for split_name in ("test", "val", "train"):
            if count[split_name] + len(g) <= caps.get(split_name, 1e9) or split_name == "train":
                assign[k] = split_name
                count[split_name] += len(g)
                break

    os.makedirs(SPLITS, exist_ok=True)
    stats = {}
    for split_name in ("train", "val", "test"):
        sel = [r for r in rows if assign[r["scaffold"]] == split_name]
        stats[split_name] = (len(sel), sum(1 for r in sel if r["label"] == "1"))
        with open(os.path.join(SPLITS, f"{split_name}.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(sel)
    for k, (tot, pos) in stats.items():
        print(f"[split] {k}: {tot} 条 (正 {pos})")
    n_groups = len(keys)
    print(f"[split] 骨架组总数 {n_groups}；ACLYCIC(无环)组 "
          f"{sum(1 for k in keys if k == 'ACYCLIC')}")
    return stats


if __name__ == "__main__":
    split()
