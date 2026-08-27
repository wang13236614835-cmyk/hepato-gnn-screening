# -*- coding: utf-8 -*-
"""数据清洗管线: 解析校验 -> 规范化去重 -> 骨架标记

负责人: 衣思淼（数据组）
输入: data/raw/*.csv
输出: data/processed/cleaned_compounds.csv (带标签训练集)
      data/processed/screening_pool.csv  (无标签筛选池)
      data/processed/rejected.csv        (被剔除记录+原因)
"""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from chem.smiles_graph import parse_smiles          # noqa: E402
from chem.descriptors import compute_descriptors    # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_LABELED = os.path.join(ROOT, "data", "raw", "tcm_seed_compounds.csv")
RAW_NOVEL = os.path.join(ROOT, "data", "raw", "novel_terpenes_lignans.csv")
PROC = os.path.join(ROOT, "data", "processed")


def _norm_name(s):
    return (s or "").strip().lower()


def clean():
    os.makedirs(PROC, exist_ok=True)
    rejected, kept_labeled, kept_pool = [], [], []
    seen_canon = {}

    def process(path, has_label, sink):
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            smi = r["smiles"].strip()
            g = parse_smiles(smi)
            if g is None or len(g.atoms) == 0:
                rejected.append({**r, "reject_reason": "SMILES解析失败"})
                continue
            canon = g.canonical_string()
            if canon in seen_canon:
                rejected.append({**r, "reject_reason": f"与{seen_canon[canon]}结构重复"})
                continue
            seen_canon[canon] = r["compound_id"]
            desc = compute_descriptors(g)
            out = dict(r)
            out["scaffold"] = g.scaffold_key()
            out["n_atoms"] = len(g.atoms)
            out.update(desc)
            if has_label:
                out["label"] = int(r["label"])
                sink.append(out)
            else:
                out["label"] = ""
                sink.append(out)

    process(RAW_LABELED, True, kept_labeled)
    process(RAW_NOVEL, False, kept_pool)

    def dump(path, rows):
        if not rows:
            return
        cols = list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    dump(os.path.join(PROC, "cleaned_compounds.csv"), kept_labeled)
    dump(os.path.join(PROC, "screening_pool.csv"), kept_pool)
    rr = [{k: r.get(k, "") for k in ("compound_id", "name_cn", "reject_reason")}
          for r in rejected]
    dump(os.path.join(PROC, "rejected.csv"), rr)

    pos = sum(1 for r in kept_labeled if r["label"] == 1)
    print(f"[clean] 带标签集: {len(kept_labeled)} 条 (正样本 {pos} / 负样本 "
          f"{len(kept_labeled)-pos})；筛选池: {len(kept_pool)} 条；剔除 {len(rr)} 条")
    return kept_labeled, kept_pool


if __name__ == "__main__":
    clean()
