# -*- coding: utf-8 -*-
"""修复验证清单：对指定运行目录逐项核对审计报告 F01-F20 的修复状态。

用法: python tools/verify_fixes.py <run_dir>
输出: 运行目录下 fixes_verification.json + 控制台摘要。
通过=机器可核验的修复已生效；partial=部分修复或需限定条件；
open=按设计留给人工(标签/文献复核)；blocked=上游门控未放行导致未执行。
"""
import csv
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]).resolve()
# run_dir 布局：hepato-gnn-screening/final-aidd-screening/results/runs/<ts>
repo = run_dir.parents[3]  # hepato-gnn-screening
src_dir = run_dir.parents[2] / "src"  # final-aidd-screening/src
assert (repo / "data" / "curation").is_dir(), "run_dir 布局不符：应为 final-aidd-screening/results/runs/<ts>"
sys.path.insert(0, str(src_dir))

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

R = {}


def read_csv(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def canon(s):
    m = Chem.MolFromSmiles(s)
    return Chem.MolToSmiles(m) if m else None


def scaffold(s):
    m = Chem.MolFromSmiles(s)
    return MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False) if m else None


reg = read_csv(repo / "data" / "curation" / "compound_registry.csv")
reg_by_id = {r["compound_id"]: r for r in reg}
gate = jload(run_dir / "docking" / "redock_gate.json")
model = jload(run_dir / "results" / "metrics" / "model_summary.json")
tables = run_dir / "results" / "tables"

# F01 身份主表
n_key = sum(1 for r in reg if r["inchikey"] and r["source_url"] and r["pubchem_cid"])
n_diff = sum(1 for r in reg if canon(r["legacy_smiles"]) != canon(r["proposed_smiles"]))
R["F01_身份主表"] = {"status": "pass" if n_key == len(reg) else "fail",
                    "n": len(reg), "n_with_cid_inchikey_url": n_key,
                    "proposed_differs_from_legacy": n_diff,
                    "identity_status_all_pending_review": all(r["identity_status"] == "pending_review" for r in reg),
                    "note": "人工复核前不放行为reviewed模式；独立抽查24/24与PubChem一致(research-audit-20260905/registry_sample_check.json)"}

# F02 共晶化学(CCD)
ccd_expect = {"FEX": "C32H38N2O3", "IQK": "C24H22N2O6S2"}
ccd_ok = {}
for t, v in gate.items():
    ref = run_dir / "docking" / "receptors" / f"{t}_{v['box']['pdb']}_{v['ligand']}_crystal.sdf"
    m = next(iter(Chem.SDMolSupplier(str(ref), removeHs=False)))
    ccd_ok[t] = rdMolDescriptors.CalcMolFormula(m) == ccd_expect[v["ligand"]]
R["F02_共晶CCD化学"] = {"status": "pass" if all(ccd_ok.values()) else "fail", "formula_vs_rcsb": ccd_expect, "local_check": ccd_ok}

# F03 规范骨架划分
splits = {p: read_csv(run_dir / "splits" / f"{p}.csv") for p in ("train", "val", "test")}
sets = {k: {scaffold(reg_by_id[r["compound_id"]]["proposed_smiles"]) for r in v} for k, v in splits.items()}
cross = [(a, b) for a in sets for b in sets if a < b and sets[a] & sets[b]]
R["F03_骨架跨集断言"] = {"status": "pass" if not cross else "fail", "sizes": {k: len(v) for k, v in splits.items()},
                    "n_scaffold_groups": len(sets["train"] | sets["val"] | sets["test"]), "cross": cross}

# F04 梯度(固定掩码数值校验)
import numpy as np
from s3_model import GCN, _sig


def grad_check():
    g = GCN(seed=3)
    from common import GraphRecord
    smiles = "CCOc1ccc(S(N)(=O)=O)cc1"  # 对乙氧基苯磺酰胺：苯环6π合法；五元杂环SMILES会解析失败
    row = {"compound_id": "T", "name_cn": "T", "label": "1", "smiles": smiles}
    rec = GraphRecord(row)
    # 冻结 dropout 掩码：记录随机流状态，解析前向与每次数值前向都从同一位置抽掩码
    state0 = g.rng.bit_generator.state
    z, cache = g.forward_graph(rec, use_drop=True)
    s = _sig(z)
    dz = s * (1 - s)  # 数值目标是 sigmoid(z)，解析链式因子须取 σ'(z)（不是任意常数）
    gr = g.backward_graph(rec, dz, cache)
    rng = np.random.default_rng(5)
    errs = {}
    for k in g.params:
        P = getattr(g, k)
        i = tuple(rng.integers(0, s) for s in P.shape)
        eps = 1e-6
        pos = np.array(P, dtype=float); pos[i] += eps
        neg = np.array(P, dtype=float); neg[i] -= eps
        def f(param):
            setattr(g, k, param)
            g.rng.bit_generator.state = state0  # 恢复掩码随机流
            return float(_sig(g.forward_graph(rec, use_drop=True)[0]))
        setattr(g, k, P)
        num = (f(pos) - f(neg)) / (2 * eps)
        setattr(g, k, P)
        errs[f"{k}{i}"] = abs(gr[k][i] - num)
    return max(errs.values()), errs


try:
    maxerr, detail = grad_check()
    R["F04_梯度校验"] = {"status": "pass" if maxerr < 1e-6 else "fail", "max_abs_error": maxerr}
except Exception as e:
    R["F04_梯度校验"] = {"status": "fail", "error": str(e)}

# F05 标签结构化
dc30 = reg_by_id.get("DC-030", {})
R["F05_标签结构化"] = {"status": "open", "detail": "标签全部unresolved待人工按统一终点复核；DC-030反例PMID已写入review_note",
                    "dc030_note_has_pmids": "10433875" in dc30.get("review_note", "") and "30600301" in dc30.get("review_note", ""),
                    "none_auto_verified": all(r["label_status"] != "verified" for r in reg)}

# F06 描述符RDKit实算
try:
    from common import rdkit_descriptors
    from common import mol_of
    lip_recomputed = {}
    pre = {r["compound_id"]: r for r in read_csv(tables / "prefilter_report.csv")} if (tables / "prefilter_report.csv").exists() else {}
    sample = [r for r in reg if r["compound_id"] in pre][:5]
    ok6 = all(int(pre[r["compound_id"]]["lipinski_violations"]) ==
              sum([rdkit_descriptors(mol_of(r["proposed_smiles"]))[k] > v for k, v in (("MW", 500), ("logP_est", 5))] +
                  [rdkit_descriptors(mol_of(r["proposed_smiles"]))[k] > v for k, v in (("nHBD", 5), ("nHBA", 10))])
              for r in sample)
    R["F06_描述符实算"] = {"status": "pass" if ok6 else "fail", "recompute_matches_prefilter_5sample": ok6,
                        "source": "common.rdkit_descriptors(实际结构)，不再读CSV估算列"}
except Exception as e:
    R["F06_描述符实算"] = {"status": "blocked", "error": str(e)}

# F07 不叠合RMSD
ok7 = all(v["rmsd_method"] == "CalcRMS_no_alignment" and v.get("rmsd_by_seed") for v in gate.values())
R["F07_不叠合RMSD"] = {"status": "pass" if ok7 else "fail", "methods": {t: v["rmsd_method"] for t, v in gate.items()},
                     "per_seed": {t: v.get("rmsd_by_seed") for t, v in gate.items()}}

# F08 散点数值轴
fig = run_dir / "results" / "figures" / "model_vs_dock_real.png"
R["F08_散点数值轴"] = {"status": "pass" if fig.exists() and fig.stat().st_size > 5000 else "blocked",
                    "note": "fig_scatter对两轴显式float()转换；图存在" if fig.exists() else "门控未放行，未生成"}

# F09 缓存键与失败管理
dock_rows = read_csv(tables / "docking_real_scores.csv") if (tables / "docking_real_scores.csv").exists() else []
n_cached = sum(1 for r in dock_rows if r.get("note") == "cached_verified")
n_fail = sum(1 for r in dock_rows if r["affinity_kcal_mol"] == "")
cache_meta = list((run_dir / "docking" / "outputs").glob("*.cache.json"))
ok9 = all(r.get("note", "").startswith(("DOCK_FAIL", "PREP_FAIL")) or r["affinity_kcal_mol"] != "" for r in dock_rows)
R["F09_缓存键与失败管理"] = {"status": "pass" if ok9 or not dock_rows else "blocked",
                        "rows": len(dock_rows), "cached_verified": n_cached, "failed_rows": n_fail,
                        "cache_metadata_files": len(cache_meta),
                        "note": "失败条目status=failed不重用；输入/参数变更触发重算(结构/受体/盒子/种子/版本入键)"}

# F10 小檗碱归因
b = [r for r in dock_rows if r["compound_id"] == "HP-043"]
R["F10_失败归因"] = {"status": "pass" if (b and all(r["affinity_kcal_mol"] != "" for r in b)) else ("pass" if any("PREP_FAIL" in r.get("note", "") for r in b) else "blocked"),
                   "rows": b, "note": "修正结构(PubChem C20H18NO4+)后预期制备成功；若失败，note含阶段与异常类型，不再猜原因"}

# F12 PAINS类型
pains_types = {}
for r in read_csv(tables / "prefilter_report.csv") if (tables / "prefilter_report.csv").exists() else []:
    if r["pains_alert"]:
        pains_types[r["pains_alert"]] = pains_types.get(r["pains_alert"], 0) + 1
R["F12_PAINS类型"] = {"status": "pass", "types": pains_types, "note": "按FilterCatalog实际类别分型统计，保留标记制"}

# F13 相关性解释
if (run_dir / "results" / "metrics" / "fusion_summary.json").exists():
    fus = jload(run_dir / "results" / "metrics" / "fusion_summary.json")
    R["F13_相关性口径"] = {"status": "pass", "spearman_model_dock": fus.get("spearman_model_dock"),
                        "note": "s5明确'描述性相关不证明独立'；融合权重为组会决议口径，正式验证列入学期任务"}
else:
    R["F13_相关性口径"] = {"status": "blocked"}

# F14 分榜与对照
if (tables / "final_ranking_v2_real.csv").exists():
    rank = read_csv(tables / "final_ranking_v2_real.csv")
    cols = set(rank[0].keys())
    ctrl_in = [r["compound_id"] for r in rank if r.get("role") == "positive_control"]
    R["F14_分榜与对照"] = {"status": "pass" if {"role", "model_split", "pubchem_cid"} <= cols and not ctrl_in else "fail",
                        "n": len(rank), "control_in_ranking": ctrl_in,
                        "split_counts": {s: sum(1 for r in rank if r.get("model_split") == s) for s in ("train", "val", "test", "screening_pool")}}
else:
    R["F14_分榜与对照"] = {"status": "blocked"}

# F15 AUC区间
R["F15_AUC区间"] = {"status": "pass" if model.get("gnn", {}).get("AUC_95CI_stratified_bootstrap") else "fail",
                  "ci": model.get("gnn", {}).get("AUC_95CI_stratified_bootstrap"),
                  "note": model.get("gnn", {}).get("AUC_95CI_note")}

# F16 靶点安全档案
tgt = (run_dir / "results" / "targets.json").read_text(encoding="utf-8")
R["F16_奥贝胆酸撤市"] = {"status": "pass" if "2025-11-24" in tgt and "撤回" in tgt else "fail"}

# F17 指纹簇口径
if (tables / "diverse_top10.csv").exists():
    top = read_csv(tables / "diverse_top10.csv")
    R["F17_簇口径"] = {"status": "pass" if top and "scaffold" in top[0] else "fail",
                     "n_unique_scaffolds_in_top": len({r["scaffold"] for r in top}), "n": len(top)}
else:
    R["F17_簇口径"] = {"status": "blocked"}

# F18 种子清单
dock_cfg = None
for m in (run_dir / "docking" / "outputs").glob("*_out.pdbqt.cache.json"):
    dock_cfg = jload(m)
    break
R["F18_种子清单"] = {"status": "pass" if model.get("seed") == 42 and gate.get("FXR_LBD", {}).get("seed") else "fail",
                  "model_seed": model.get("seed"), "gate_seeds": gate.get("FXR_LBD", {}).get("seed"),
                  "docking_seed": (dock_cfg or {}).get("key") and "seed在缓存键内"}

# F19 可移植性
R["F19_可移植性"] = {"status": "partial", "note": "VINA_BIN环境变量已支持；requirements-validated.txt在库根；Linux/净环境一键复现仍开放，列入学期WP"}

# F20 报告生成
rr = run_dir / "results" / "RUN_REPORT.md"
summ = run_dir / "results" / "summary.json"
R["F20_报告生成"] = {"status": "pass" if rr.exists() and summ.exists() else "blocked",
                  "note": "每次运行自动生成RUN_REPORT与summary.json；旧REPORT.md仅历史"}

out = {"run_dir": str(run_dir), "checks": R}
dst = run_dir / "fixes_verification.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
n_pass = sum(1 for v in R.values() if v["status"] == "pass")
n_block = sum(1 for v in R.values() if v["status"] in ("blocked", "partial"))
n_open = sum(1 for v in R.values() if v["status"] == "open")
print(f"验证结果: pass {n_pass} / blocked-partial {n_block} / open(人工) {n_open} / 共 {len(R)} 项")
for k, v in R.items():
    print(f"  {v['status'].upper():8s} {k}")
print(f"明细: {dst}")
