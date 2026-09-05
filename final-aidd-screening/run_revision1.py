"""大修批1运行器(20260905 核心期刊审查整改)。

与 run_revised.py 的区别: 冻结既有 FXR 诊断运行的对接证据(哈希留档继承),
不重跑对接, 只重跑 s3 建模指标 / s5 三榜融合 / s6 图表口径。
对接姿势验证结论(redock_gate)随继承证据一并入 summary。

用法:
  python run_revision1.py --source ../results/validation/fxr_single_target_diagnostic_20260905 \
      --output ../results/validation/fxr_revision1_20260905

科学定位: 诊断运行, scientific_validation=not_granted, 不构成湿实验放行。
"""
import argparse
import datetime
import hashlib
import os
import shutil
import sys
from pathlib import Path


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, help="被冻结的既有运行目录(含真实对接结果)")
    ap.add_argument("--output", required=True, help="全新输出目录")
    a = ap.parse_args()
    here = Path(__file__).resolve().parent
    src = Path(a.source).resolve()
    out = Path(a.output).resolve()
    if out.exists() and any(out.iterdir()):
        ap.error("输出目录非空，请使用新目录")

    # 源目录为冻结运行的 RES 层(结果文件平铺); 靶点定义取仓库 docking/boxes.json
    inherited = [
        ("docking_real_scores.csv", "results/tables/docking_real_scores.csv"),   # 真实 Vina 计算评分(冻结证据)
        ("prefilter_report.csv", "results/tables/prefilter_report.csv"),         # Lipinski/PAINS 预筛(冻结证据)
        ("redock_gate.json", "docking/redock_gate.json"),                        # 共晶姿势验证门控结论
    ]
    boxes = here / "docking" / "boxes.json"
    if not boxes.exists():
        ap.error(f"缺少靶点定义 {boxes}")
    for rel, _ in inherited:
        if not (src / rel).exists():
            ap.error(f"源运行缺少 {rel}")

    # 冻结证据中实际完成的靶点 = 本次继承的靶点域(与源运行 --targets 一致)
    import csv as _csv
    with open(src / "docking_real_scores.csv", encoding="utf-8-sig") as f:
        _frozen_targets = sorted({r["target"] for r in _csv.DictReader(f)})
    _boxes_all = __import__("json").load(open(boxes, encoding="utf-8"))
    _boxes = {t: _boxes_all[t] for t in _frozen_targets if t in _boxes_all}
    if set(_boxes) != set(_frozen_targets):
        ap.error(f"boxes.json 缺少冻结靶点 {_frozen_targets}")

    os.environ["HEPATO_RUN_ROOT"] = str(out)
    os.environ["HEPATO_DATA_MODE"] = "proposed"  # 与源运行同模式: 建议结构+旧标签诊断
    sys.path.insert(0, str(here / "src"))
    from common import load_registry, REGISTRY
    try:
        load_registry()
    except ValueError as e:
        ap.exit(2, str(e) + "\n")

    out.mkdir(parents=True, exist_ok=True)
    for rel, dst_rel in inherited:
        dst = out / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, dst)
    (out / "docking").mkdir(exist_ok=True)
    (out / "docking" / "boxes.json").write_text(
        __import__("json").dumps(_boxes, ensure_ascii=False, indent=1), encoding="utf-8")

    record = {
        "mode": "revision1_frozen_docking_rerun",
        "scientific_validation": "not_granted_by_this_run",
        "wetlab_ready": False,
        "base_run": str(src),
        "revision_note": "核心期刊审查20260905大修批1: 项34三榜/35稳定性/37口径/39纳排流/46图轴/47分箱/17指标",
        "inherited_evidence": {dst_rel: {"sha256": sha256(out / dst_rel),
                                         "inherited_from": str((src / rel).resolve())}
                               for rel, dst_rel in inherited},
        "registry_sha256": sha256(Path(REGISTRY)),
        "argv": sys.argv[1:],
        "status": "running",
        "rerun_steps": ["s3_model (指标补强)", "s5_fuse_select (三榜+稳定性)", "s6_report (口径修复)"],
        "frozen_steps": ["s1_target_profile", "s2_prep_redock", "s4_dock (对接证据继承,见 inherited_evidence)"],
    }
    record["inherited_evidence"]["docking/boxes.json"] = {
        "sha256": sha256(boxes), "inherited_from": str(boxes)}
    record["source_sha256"] = {f.relative_to(here).as_posix(): sha256(f)
                               for f in sorted((here / "src").glob("*.py"))}
    record["source_sha256"]["run_revision1.py"] = sha256(Path(__file__))
    record["python"] = sys.version
    record["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out / "run_manifest.json").write_text(
        __import__("json").dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")

    try:
        from s3_model import run as model
        from s5_fuse_select import run as fuse
        from s6_report import run as report
        model()
        fuse()
        report()
        record["status"] = "completed"
    except BaseException as e:
        record.update(status="failed", error=f"{type(e).__name__}: {e}")
        (out / "run_manifest.json").write_text(
            __import__("json").dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        raise
    (out / "run_manifest.json").write_text(
        __import__("json").dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"大修批1计算记录：{out}。对接证据冻结继承，计算完成不等于研究有效性。")


if __name__ == "__main__":
    main()
