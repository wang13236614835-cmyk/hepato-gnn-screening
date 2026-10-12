# -*- coding: utf-8 -*-
"""把每人名下要核验的具体文件快照复制到 <姓名>/待核文件/（各自一份）。

约定（与 docs/文件清单.md §12 一致）：
- 根目录是工作原件，流水线（run_all.py/verify.py）依赖根目录路径，不可删；
  个人文件夹里的快照只用于阅读/逐条勾核，勾完在 <姓名>/工作台.md 签名。
- 大体积可再生产物（exe、reports/pdf_all/ 全部PDF镜像、pdf_build 中间产物）
  不入快照，在快照清单中标注"以根目录为准"，避免镜像的镜像这种纯冗余数据。
- 改动 核验任务分派 附录A 后重跑：python tools/snapshot_member_files.py

用法: python tools/snapshot_member_files.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 各人核验文件（= docs/核验任务分派.md 附录A 的 A1/A3/A4/A5；A2 大件见 NO_COPY）
FILES = {
    "宁显泷": [
        "run_all.py",
        "src/chem/smiles_graph.py",
        "src/models/gnn.py", "src/models/dataset.py", "src/models/baseline.py",
        "src/scoring/fuse.py",
        "reports/pdf_build/verify.py",
        "docs/02_模型笔记.md",
        "results/metrics/基线指标.csv", "results/metrics/可靠性曲线.csv",
        "results/predictions/测试预测.csv", "results/predictions/全池预测.csv",
    ],
    "衣思淼": [
        "data/raw/中药种子化合物.csv",
        "data/processed/清洗后化合物.csv", "data/processed/筛选池.csv",
        "data/processed/已剔除.csv",
        "data/splits/训练集.csv", "data/splits/验证集.csv", "data/splits/测试集.csv",
        "src/data/clean.py", "src/data/split.py", "src/data/ad.py",
        "src/chem/descriptors.py",
        "docs/01_数据字典.md",
        "results/ad/适用域报告.csv",
        "results/rankings/最终排名.csv",
    ],
    "代维斯丹": [
        "src/chem/fingerprints.py",
        "src/docking/grid_box.py", "src/docking/mock_docking.py", "src/docking/run_vina.sh",
        "docs/03_对接协议.md",
        "src/viz/plots.py",
        "results/docking/对接分数表.csv",
        "results/figures/top_candidates.png", "results/figures/reliability_diagram.png",
        "results/figures/uncertainty_vs_error.png", "results/figures/model_dock_scatter.png",
        "src/__init__.py", "src/chem/__init__.py", "src/data/__init__.py",
        "src/docking/__init__.py", "src/models/__init__.py",
        "src/scoring/__init__.py", "src/viz/__init__.py",
    ],
    "王散曼": [
        "literature/01_经典证据.md",
        "literature/02_新三萜木脂素.md",
        "literature/03_候选机制.md",
        "data/raw/新三萜木脂素.csv",
    ],
    "王启龙": [
        # 总纲与配置（9）
        "README.md", "成员与分工.md", "requirements.txt", ".gitignore",
        "docs/文件清单.md", "docs/阶段计划.md", "docs/核验手册.md",
        "docs/核验任务分派.md", "docs/00_环境配置.md",
        # 纪要与计划（9）
        "docs/纪要/第1-2周.md", "docs/纪要/第3-4周.md", "docs/纪要/第5-6周.md",
        "phase2_semester/WP1_基线核验.md", "phase2_semester/WP2_真实对接.md",
        "phase2_semester/WP3_数据扩充.md", "phase2_semester/WP4_模型升级.md",
        "phase2_semester/WP5_实验衔接.md", "phase2_semester/推进程序_负责人_王启龙.md",
        # 个人档案（6）
        "docs/个人档案/00_工作量与成果总表.md", "docs/个人档案/P1_王启龙.md",
        "docs/个人档案/P2_宁显泷.md", "docs/个人档案/P3_衣思淼.md",
        "docs/个人档案/P4_代维斯丹.md", "docs/个人档案/P5_王散曼.md",
        # 工具与学习（轻量部分；exe 与成员打卡页不入快照）
        "tools/semester_flow.py", "tools/gen_member_pages.py",
        "tools/使用说明_学期推进流.md",
        "learning/王启龙/flow_state.json", "learning/王启龙/week01_exercise.py",
        "learning/王启龙/week03_rdkit_recalc.py",
        # 报告（reports/ 根 3 件中的 md；两份大 PDF 以根目录为准）
        "reports/期中报告.md",
    ],
}

# 王启龙名下体积大/可再生产物：不复制，清单中标注以根目录为准
NO_COPY = {
    "王启龙": [
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
