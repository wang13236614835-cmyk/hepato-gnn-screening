# -*- coding: utf-8 -*-
"""把工作区全部内容分类打包上传到 aidd 仓库（Git Data API 通道）。

- 源->目标路径按分类规则映射（见 build_mapping）
- blob上传断点续传（缓存已传sha）
- 超100MB的单文件跳过并生成说明
- 基于 aidd 现有 HEAD 的 base_tree 合并，不删除远端已有文件
用法: TOKEN=ghp_xxx python upload_aidd.py
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

TOKEN = os.environ["TOKEN"]
USER, REPO = "wang13236614835-cmyk", "aidd"
API = f"https://api.github.com/repos/{USER}/{REPO}"
WS = r"D:\zcode-workspace"
HEADERS = {"Authorization": f"token {TOKEN}",
           "Accept": "application/vnd.github+json",
           "Content-Type": "application/json",
           "User-Agent": "aidd-uploader"}
CACHE_PATH = os.path.join(WS, "hepato-gnn-screening", "reports", "pdf_build", "aidd_blobs.json")
SKIP_LIST_PATH = os.path.join(WS, "hepato-gnn-screening", "reports", "pdf_build", "aidd_skipped.md")


REQ_TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "aidd_req.json")


def api(path, payload=None, method="GET", raw=False, _path=""):
    """全部走curl通道（Python urllib的TLS指纹会被本网络重置）。"""
    import subprocess
    import tempfile
    for attempt in range(5):
        args = ["curl", "-s", "--max-time", "300", "-X", method,
                "-H", "Authorization: " + HEADERS["Authorization"],
                "-H", "Accept: " + HEADERS["Accept"],
                "-H", "User-Agent: aidd-uploader"]
        if payload is not None:
            with open(REQ_TMP, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            args += ["-H", "Content-Type: application/json",
                     "--data-binary", "@" + REQ_TMP]
        args.append(API + path)
        out = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        body = out.stdout.strip()
        if not body:
            print(f"  curl空响应({out.returncode}), 重试{attempt}", flush=True)
            time.sleep(8)
            continue
        try:
            res = json.loads(body)
        except json.JSONDecodeError:
            print(f"  非JSON响应前80字: {body[:80]}", flush=True)
            time.sleep(8)
            continue
        if isinstance(res, dict) and (res.get("documentation_url") or (
                "message" in res and "sha" not in res and "tree" not in res
                and "object" not in res and "content" not in res)):
            msg = res.get("message", "")
            print(f"  API错误: {msg[:80]}, 重试{attempt}", flush=True)
            low = msg.lower()
            if "too large to process" in low or "fewer" in low or "abuse" in low:
                time.sleep(90)
            elif "in time" in low or "couldn" in low:
                time.sleep(20)  # 504网关超时，短退避重试
            elif "rate" in low:
                time.sleep(45)
            else:
                time.sleep(8)
            continue
        return res
    raise RuntimeError(f"api调用失败: {method} {path} 文件={_path}")


def git_blob_sha(path):
    """本地计算git blob sha（与远端一致性校验用）。"""
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest(), data


EXCLUDE_DIRS = {".git", "__pycache__", ".zcode", ".ipynb_checkpoints", ".venv", "node_modules"}


def walk_files(src_root, rel_prefix):
    out = []
    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, src_root).replace("\\", "/")
            out.append((full, f"{rel_prefix}/{rel}"))
    return out


def build_mapping():
    m = []
    m += walk_files(os.path.join(WS, "hepato-gnn-screening"), "01-课题-保肝中药成分虚拟筛选")
    m += walk_files(os.path.join(WS, "mash_research"), "02-课题-MASH研究-v1")
    m += walk_files(os.path.join(WS, "mash_v2_new"), "03-课题-MASH研究-v2")
    m += walk_files(os.path.join(WS, "paper"), "04-论文")
    guochuang = ["国创赛项目计划书_基于贝叶斯图神经网络的抗MASH天然药物筛选.pdf",
                 "国创赛报名信息填写对照表.md", "国创赛项目计划书_封面源文件.html",
                 "国创赛学生操作手册2026(1).pdf",
                 "基于贝叶斯图神经网络的抗MASH天然药物筛选项目_20260608212055.pdf",
                 "generate_国创赛项目计划书.py"]
    m += [(os.path.join(WS, f), f"05-申报-国创赛/{f}") for f in guochuang if os.path.exists(os.path.join(WS, f))]
    dachuang = ["医疗器械学院-​基于贝叶斯图神经网络的抗MASH天然药物筛选-匿名版.pdf",
                "医疗器械学院-姜希伟-王启龙-​基于贝叶斯图神经网络的抗MASH天然药物筛选.pdf",
                "大创全流程综合结题分析报告.pdf", "大创汇报与湿实验路线图.pdf",
                "A_anon.txt", "B_named.txt", "C_full.txt", "extracted_full.txt"]
    m += [(os.path.join(WS, f), f"06-申报-大创结题/{f}") for f in dachuang if os.path.exists(os.path.join(WS, f))]
    zhenghe = ["抗MASH研究最终整合报告.md", "抗MASH研究最终整合报告.pdf",
               "抗MASH研究最终整合报告_封面.html", "抗MASH研究最终整合报告_封面.pdf",
               "抗MASH研究最终整合报告_正文.pdf", "generate_抗MASH研究最终整合报告.py"]
    m += [(os.path.join(WS, f), f"07-整合报告/{f}") for f in zhenghe if os.path.exists(os.path.join(WS, f))]
    m += walk_files(os.path.join(WS, "抗MASH研究最终整合报告_qa_preview"), "07-整合报告/qa预览图")
    tools = ["generate_final_report.py", "generate_fpdf.py", "generate_playwright_pdf.py",
             "generate_roadmap_pdf.py", "report.html", "roadmap.html"]
    m += [(os.path.join(WS, f), f"08-工具脚本/{f}") for f in tools if os.path.exists(os.path.join(WS, f))]
    for d in ("roundtable", "roundtable2", "roundtable3", "verify_repro"):
        m += walk_files(os.path.join(WS, d), f"09-过程资料/{d}")
    return m


def main():
    mapping = build_mapping()
    print(f"映射条目: {len(mapping)}", flush=True)
    cache = {}
    if os.path.exists(CACHE_PATH):
        cache = json.load(open(CACHE_PATH))
        print(f"断点续传: 已缓存{len(cache)}个blob", flush=True)

    skipped = []
    mismatched = []
    entries = []
    done = 0
    t0 = time.time()
    for src, dst in mapping:
        size = os.path.getsize(src)
        if size > 30 * 1024 * 1024:  # 实测上限30-40MB之间，取30MB安全值
            skipped.append((dst, size))
            print(f"  跳过(>30MB): {dst} ({size//1048576}MB)", flush=True)
            continue
        sha, data = git_blob_sha(src)
        if sha not in cache:
            b64 = base64.b64encode(data).decode()
            ok = False
            for tryi in range(3):
                res = api("/git/blobs", {"content": b64, "encoding": "base64"}, method="POST", _path=dst)
                if res.get("sha") == sha:
                    ok = True
                    break
                print(f"  sha不一致重试{tryi}: {dst}", flush=True)
                time.sleep(3)
            if not ok:
                mismatched.append(dst)
                print(f"  记录跳过(sha持续不一致): {dst}", flush=True)
                continue
            cache[sha] = True
            json.dump(cache, open(CACHE_PATH, "w"))
            time.sleep(0.5)  # 内容创建节流，防触发防滥用限制
        entries.append({"path": dst, "mode": "100644", "type": "blob", "sha": sha})
        done += 1
        if done % 50 == 0:
            rate = done / (time.time() - t0)
            print(f"  进度 {done}/{len(mapping)} ({rate:.1f}个/秒, 已缓存{len(cache)})", flush=True)

    # 跳过文件说明
    if skipped:
        lines = ["# 未上传的大文件说明\n",
                 "以下文件超过GitHub API单文件50MB实际上限，未随归档上传，可在本地工作区或通过流水线再生：\n"]
        for dst, size in skipped:
            lines.append(f"- `{dst}` ({size/1048576:.0f} MB)")
        for dst in mismatched:
            lines.append(f"- `{dst}` (上传时sha校验持续不一致，需人工复查)")
        api("/contents/" + "09-过程资料/未上传大文件说明.md", {
            "message": "docs: 未上传大文件说明",
            "content": base64.b64encode("\n".join(lines).encode()).decode()}, method="PUT")

    # 索引文件
    index = INDEX_MD
    entries.append({"path": "00-索引.md", "mode": "100644", "type": "blob",
                    "sha": api("/git/blobs", {"content": base64.b64encode(index.encode()).decode(),
                                              "encoding": "base64"}, method="POST")["sha"]})

    # 基于现有HEAD合并
    head = api("/git/ref/heads/main")
    base_tree = api("/git/commits/" + head["object"]["sha"])["tree"]["sha"]
    tree = api("/git/trees", {"base_tree": base_tree, "tree": entries}, method="POST")["sha"]
    commit = api("/git/commits", {"message": "chore: 工作区全量整理归档（分类上传）",
                                  "tree": tree, "parents": [head["object"]["sha"]],
                                  "author": {"name": "wangqilong", "email": "wang13236614835@gmail.com",
                                             "date": "2026-08-27T22:00:00+08:00"}}, method="POST")["sha"]
    api("/git/refs/heads/main", {"sha": commit, "force": False}, method="PATCH")
    print(f"DONE 提交={commit} 新增条目={len(entries)} 跳过={len(skipped)} 用时{(time.time()-t0)/60:.1f}分", flush=True)


INDEX_MD = """# 工作区归档索引

本仓库归档 `D:\\zcode-workspace` 全部研究工作内容，按九类组织：

| 目录 | 内容 | 规模 |
|---|---|---|
| 01-课题-保肝中药成分虚拟筛选 | 暑期课题完整仓库：代码/数据/文档/29份PDF/两阶段规划 | 含reports与pdf_all |
| 02-课题-MASH研究-v1 | MASH课题v1：src/docking/research/报告（data与results大体量文件已含） | 760MB |
| 03-课题-MASH研究-v2 | MASH课题v2 | 85MB |
| 04-论文 | 手稿与图表生成 | |
| 05-申报-国创赛 | 项目计划书/报名对照/封面/操作手册/申报PDF | |
| 06-申报-大创结题 | 署名与匿名版PDF/结题分析/路线图/文本提取 | |
| 07-整合报告 | 抗MASH最终整合报告全套（md/pdf/封面/正文/qa预览） | |
| 08-工具脚本 | 各类PDF生成脚本与HTML | |
| 09-过程资料 | 三轮圆桌讨论/复现校验脚本 | |

说明：超过GitHub API单文件50MB实际上限的文件未上传，见 `09-过程资料/未上传大文件说明.md`。
上传时间：2026-08-27。
"""

if __name__ == "__main__":
    main()
