# -*- coding: utf-8 -*-
"""把每人名下要核验的具体文件快照复制到 <姓名>/待核文件/（各自一份）。

约定（与 docs/MANIFEST.md §12 一致）：
- 根目录是工作原件，流水线（run_all.py/verify.py）依赖根目录路径，不可删；
  个人文件夹里的快照只用于阅读/逐条勾核，勾完在 <姓名>/工作台.md 签名。
- 大体积可再生产物（exe、reports/pdf_all/ 全部PDF镜像、pdf_build 中间产物）
  不入快照，在快照清单中标注"以根目录为准"，避免镜像的镜像这种纯冗余数据。
- 改动 VERIFY_TASKS 附录A 后重跑：python tools/snapshot_member_files.py

用法: python tools/snapshot_member_files.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 各人核验文件（= docs/VERIFY_TASKS.md 附录A 的 A1/A3/A4/A5；A2 大件见 NO_COPY）
FILES = {
    "宁显泷": [
        "run_all.py",
        "src/chem/smiles_graph.py",
        "src/models/gnn.py", "src/models/dataset.py", "src/models/baseline.py",
        "src/scoring/fuse.py",
        "reports/pdf_build/verify.py",
        "docs/02_model_notes.md",
        "results/metrics/baseline.csv", "results/metrics/reliability_curve.csv",
        "results/predictions/test_predictions.csv", "results/predictions/fullpool_predictions.csv",
    ],
    "衣思淼": [
        "data/raw/tcm_seed_compounds.csv",
        "data/processed/cleaned_compounds.csv", "data/processed/screening_pool.csv",
        "data/processed/rejected.csv",
        "data/splits/train.csv", "data/splits/val.csv", "data/splits/test.csv",
        "src/data/clean.py", "src/data/split.py", "src/data/ad.py",
        "src/chem/descriptors.py",
        "docs/01_data_dictionary.md",
        "results/ad/ad_report.csv",
        "results/rankings/final_ranking.csv",
    ],
    "代维斯丹": [
        "src/chem/fingerprints.py",
        "src/docking/grid_box.py", "src/docking/mock_docking.py", "src/docking/run_vina.sh",
        "docs/03_docking_protocol.md",
        "src/viz/plots.py",
        "results/docking/docking_scores.csv",
        "results/figures/top_candidates.png", "results/figures/reliability_diagram.png",
        "results/figures/uncertainty_vs_error.png", "results/figures/model_dock_scatter.png",
        "src/__init__.py", "src/chem/__init__.py", "src/data/__init__.py",
        "src/docking/__init__.py", "src/models/__init__.py",
        "src/scoring/__init__.py", "src/viz/__init__.py",
    ],
    "王散曼": [
        "literature/01_classic_evidence.md",
        "literature/02_novel_terpenes_lignans.md",
        "literature/03_top_candidate_mechanisms.md",
        "data/raw/novel_terpenes_lignans.csv",
    ],
    "王启龙": [
        # 总纲与配置（9）
        "README.md", "CONTRIBUTORS.md", "requirements.txt", ".gitignore",
        "docs/MANIFEST.md", "docs/PHASE_PLAN.md", "docs/VERIFY_MANUAL.md",
        "docs/VERIFY_TASKS.md", "docs/00_environment.md",
        # 纪要与计划（9）
        "docs/minutes/week1-2.md", "docs/minutes/week3-4.md", "docs/minutes/week5-6.md",
        "phase2_semester/WP1_verify_baseline.md", "phase2_semester/WP2_real_docking.md",
        "phase2_semester/WP3_data_expansion.md", "phase2_semester/WP4_model_upgrade.md",
        "phase2_semester/WP5_experiment_bridge.md", "phase2_semester/推进程序_负责人_王启龙.md",
        # 个人档案（6）
        "docs/personal/00_工作量与成果总表.md", "docs/personal/P1_王启龙.md",
        "docs/personal/P2_宁显泷.md", "docs/personal/P3_衣思淼.md",
        "docs/personal/P4_代维斯丹.md", "docs/personal/P5_王散曼.md",
        # 工具与学习（轻量部分；exe 与成员打卡页不入快照）
        "tools/semester_flow.py", "tools/gen_member_pages.py",
        "tools/revise_plain_leader.py", "tools/使用说明_学期推进流exe.md",
        "learning/王启龙/flow_state.json", "learning/王启龙/week01_exercise.py",
        "learning/王启龙/week03_rdkit_recalc.py",
        # 报告（reports/ 根 3 件中的 md；两份大 PDF 以根目录为准）
        "reports/midterm_report.md",
    ],
}

# 王启龙名下体积大/可再生产物：不复制，清单中标注以根目录为准
NO_COPY = {
    "王启龙": [
        ("tools/学期推进流_王启龙.exe", "8MB 工具二进制；双击核验即可，不需副本"),
        ("reports/暑假阶段报告汇总.pdf", "大 PDF；以根目录为准"),
        ("reports/课题详解与阶段结果说明.pdf", "大 PDF；以根目录为准"),
        ("reports/pdf_build/（23 个中间产物）", "构建链中间物；核验方法=能再生成"),
        ("reports/pdf_all/（27 个 PDF 镜像）", "md 的阅读版镜像；核验方法=md 变更后重跑 md2pdf.py"),
    ],
}

SUMMARY = {
    "宁显泷": "代码验证（附录A·A1）", "衣思淼": "数据线A（附录A·A3）",
    "代维斯丹": "数据线B（附录A·A4）", "王散曼": "文献（附录A·A5）",
    "王启龙": "辅助/工程（附录A·A2）",
}


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:10]


def main():
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip() or "n/a"
    for name, rels in FILES.items():
        base = ROOT / name / "待核文件"
        n_ok = 0
        lines = [f"# {name} · 待核文件快照清单", "",
                 f"> 校验线：{SUMMARY[name]} ｜ 快照：git {git}（重跑 tools/snapshot_member_files.py 更新）｜ 根目录为工作原件，本副本供勾核，md5 供比对", "",
                 "| # | 原路径（根目录） | 大小 | md5前10位 |", "|---|---|---|---|"]
        for i, rel in enumerate(rels, 1):
            src = ROOT / rel
            if not src.exists():
                print(f"[缺] {name}: {rel}")
                continue
            dst = base / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            lines.append(f"| {i} | {rel} | {src.stat().st_size} B | {md5(src)} |")
            n_ok += 1
        for rel, why in NO_COPY.get(name, []):
            lines.append(f"| — | {rel} | 不入快照 | {why} |")
        (base / "快照清单.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[ok] {name}: {n_ok} 个文件入快照 + 快照清单.md")
    print("done")


if __name__ == "__main__":
    sys.exit(main())
