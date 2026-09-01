# -*- coding: utf-8 -*-
"""生成并上传 aidd 全文件中文备注清单（文件备注清单.csv）+ 更新索引。"""
import base64
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TOKEN", "x")
import upload_aidd as u

u.TOKEN = os.environ["TOKEN"]
u.HEADERS["Authorization"] = f"token {u.TOKEN}"

# 1) 远端全量文件树
tree = u.api("/git/trees/main?recursive=1")
paths = sorted(e["path"] for e in tree["tree"] if e["type"] == "blob")
print("远端文件数:", len(paths))

# 2) 解析hepato的MANIFEST（01类的逐文件用途与负责人）
man = {}
mp = os.path.join(u.WS, "hepato-gnn-screening", "docs", "MANIFEST.md")
for line in io.open(mp, encoding="utf-8"):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) >= 5 and cells[0] and not cells[0].startswith("-") and "/" in cells[0] + cells[0]:
        pass
    if len(cells) >= 4 and re.match(r"^[\w\-./（）()]+\.\w+$|^.+/.+$", cells[0]):
        man["01-课题-保肝中药成分虚拟筛选/" + cells[0]] = (cells[2], cells[3])
print("MANIFEST映射条数:", len(man))

CAT = {"01-": "保肝中药筛选课题", "02-": "MASH研究v1", "03-": "MASH研究v2",
       "04-": "论文", "05-": "国创赛申报", "06-": "大创结题",
       "07-": "整合报告", "08-": "工具脚本", "09-": "过程资料"}
EXT = [(".pdbqt", "分子对接输出构象"), (".csv.gz", "压缩CSV数据"), (".csv", "CSV数据表"),
       (".gz", "压缩数据文件"), (".tar", "原始数据打包"), (".pdf", "PDF文档"),
       (".md", "Markdown文档"), (".py", "Python脚本/模块"), (".html", "HTML页面/报告源文件"),
       (".png", "图片"), (".jpg", "图片"), (".svg", "矢量图"), (".docx", "Word文档"),
       (".txt", "文本文件"), (".npy", "NumPy数组"), (".json", "JSON数据"),
       (".xlsx", "Excel表格"), (".sh", "Shell脚本"), (".log", "日志文件"),
       (".smi", "分子库SMILES"), (".sdf", "分子结构库"), (".mol2", "分子结构文件"),
       (".pdb", "蛋白结构文件"), (".ipynb", "Jupyter笔记本"), (".yml", "配置文件"),
       (".gitignore", "Git忽略配置"), (".ttf", "字体文件"), (".tif", "图片")]
SUBDIR_HINT = [("data/geo", "GEO转录组数据"), ("docking", "分子对接"), ("src/", "源代码"),
               ("results", "结果数据"), ("reports", "报告材料"), ("research", "研究笔记"),
               ("figures", "图表"), ("logs", "日志"), ("tools", "工具脚本"),
               ("models", "模型文件"), ("report_build", "报告构建"), ("paper", "论文材料"),
               ("qa预览", "报告质检预览图"), ("roundtable", "圆桌讨论记录"),
               ("pdf_all", "全量PDF文档镜像"), ("personal", "个人工作档案"),
               ("phase2", "下学期工作包"), ("minutes", "组会纪要"), ("literature", "文献库")]


def describe(path):
    for k, v in man.items():
        if path == k:
            return v[1]
    cat = next((v for k, v in CAT.items() if path.startswith(k)), "其他")
    low = path.lower()
    hint = next((v for k, v in SUBDIR_HINT if k in low), "")
    ext_desc = next((v for e, v in EXT if low.endswith(e)), "数据/资料文件")
    base = os.path.basename(path)
    if base in ("README.md",):
        return f"{cat}·项目说明文档"
    if base == "FINAL_REPORT.md":
        return f"{cat}·最终报告"
    if base == "00-索引.md":
        return "归档总索引"
    if base == "文件备注清单.csv":
        return "全文件中文备注清单（本文件）"
    if base.startswith(("generate_", "make_", "build_")):
        return f"{cat}·{hint or ''}生成脚本".replace("··", "·")
    return f"{cat}·{hint + '相关' if hint else ext_desc}"


def owner(path):
    for k, v in man.items():
        if path == k:
            return v[0]
    if path.startswith("01-"):
        return "王启龙"
    if path.startswith("06-"):
        return "王启龙、姜希伟（前期申报）"
    return "王启龙（前期工作区）"


rows = [(p, describe(p), owner(p), p.split("/", 1)[0]) for p in paths]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "文件备注清单.csv")
with io.open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["相对路径", "中文说明（是什么）", "负责人（谁弄的）", "所属分类"])
    w.writerows(rows)
print("清单行数:", len(rows), "->", out)

# 3) 上传：清单CSV + 更新后的索引
entries = []
csv_bytes = io.open(out, "rb").read()
res = u.api("/git/blobs", {"content": base64.b64encode(csv_bytes).decode(),
                           "encoding": "base64"}, method="POST")
entries.append({"path": "文件备注清单.csv", "mode": "100644", "type": "blob", "sha": res["sha"]})

idx = u.INDEX_MD.replace("上传时间：2026-08-27。",
    "上传时间：2026-08-27。\n\n**逐文件中文备注**：每个文件\"是什么、谁弄的\"见根目录"
    "《文件备注清单.csv》（Excel可直接打开）。01类课题的逐文件核验方法另见其仓库内 "
    "`docs/MANIFEST.md`；02-09类为前期工作区归档，负责人按工作区归属标注。")
res2 = u.api("/git/blobs", {"content": base64.b64encode(idx.encode()).decode(),
                            "encoding": "base64"}, method="POST")
entries.append({"path": "00-索引.md", "mode": "100644", "type": "blob", "sha": res2["sha"]})

head = u.api("/git/ref/heads/main")
base_tree = u.api("/git/commits/" + head["object"]["sha"])["tree"]["sha"]
t = u.api("/git/trees", {"base_tree": base_tree, "tree": entries}, method="POST")["sha"]
c = u.api("/git/commits", {"message": "docs: 全文件中文备注清单（是什么+谁弄的，1609文件全覆盖）",
                           "tree": t, "parents": [head["object"]["sha"]],
                           "author": {"name": "wangqilong", "email": "wang13236614835@gmail.com",
                                      "date": "2026-08-28T00:30:00+08:00"}}, method="POST")["sha"]
u.api("/git/refs/heads/main", {"sha": c, "force": False}, method="PATCH")
print("DONE commit =", c)
