# -*- coding: utf-8 -*-
"""aidd上传收尾：blob已全部缓存，只做 建树(分级) -> 提交 -> 指针。"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TOKEN", "x")
import upload_aidd as u  # 复用mapping/api

u.TOKEN = os.environ["TOKEN"]
u.HEADERS["Authorization"] = f"token {u.TOKEN}"

mapping = u.build_mapping()
cache = set(json.load(open(u.CACHE_PATH)))
print("缓存blob:", len(cache))

TRANSIENT = ("aidd_blobs.json", "aidd_run", "finalize_aidd.py", "api_blobs_done.json")
entries, skipped = [], []
for src, dst in mapping:
    if any(t in dst for t in TRANSIENT):
        continue  # 运行期瞬态文件不入库
    size = os.path.getsize(src)
    if size > 30 * 1024 * 1024:
        skipped.append(dst)
        continue
    sha, _ = u.git_blob_sha(src)
    if sha not in cache:  # 自身脚本等最后版本，现传
        data = open(src, "rb").read()
        res = u.api("/git/blobs", {"content": base64.b64encode(data).decode(),
                                   "encoding": "base64"}, method="POST")
        assert res["sha"] == sha, dst
        cache.add(sha)
        json.dump(list(cache), open(u.CACHE_PATH, "w"))
    entries.append({"path": dst, "mode": "100644", "type": "blob", "sha": sha})
print(f"条目{len(entries)} 跳过{len(skipped)}")

# 索引blob（含跳过清单）
note = ["# 未上传的大文件说明\n",
        "以下文件超过GitHub API单文件约30-40MB实际上限，未随归档上传，"
        "均可在本地工作区找到或通过流水线/官方数据库再生：\n"]
note += [f"- `{d}`" for d in skipped]
idx = u.INDEX_MD.replace("超过GitHub API单文件50MB实际上限的文件未上传",
                         "超过GitHub API单文件约30-40MB实际上限的文件未上传")
for name, content in (("00-索引.md", idx),
                      ("09-过程资料/未上传大文件说明.md", "\n".join(note))):
    b64 = base64.b64encode(content.encode()).decode()
    res = u.api("/git/blobs", {"content": b64, "encoding": "base64"}, method="POST")
    entries.append({"path": name, "mode": "100644", "type": "blob", "sha": res["sha"]})

# 分级建树：先按一级目录建子树，再建根树（避免单次大payload）
from collections import defaultdict
groups = defaultdict(list)
root_blobs = []
for e in entries:
    top = e["path"].split("/", 1)[0]
    if "/" in e["path"]:
        groups[top].append({**e, "path": e["path"].split("/", 1)[1]})
    else:
        root_blobs.append(e)

head = u.api("/git/ref/heads/main")
base_commit = u.api("/git/commits/" + head["object"]["sha"])
base_tree = base_commit["tree"]["sha"]
base_entries = u.api("/git/trees/" + base_tree)["tree"]
base_top = [e for e in base_entries if e["type"] == "tree"]

def build_tree_chunked(ents, chunk=250):
    """分块链式建树：每次<=chunk条，base_tree串联（大载荷一次建会504）。"""
    sha = None
    for i in range(0, len(ents), chunk):
        payload = {"tree": ents[i:i + chunk]}
        if sha:
            payload["base_tree"] = sha
        sha = u.api("/git/trees", payload, method="POST")["sha"]
    return sha


root_entries = list(root_blobs)
for top, ents in groups.items():
    sub_sha = build_tree_chunked(ents)
    root_entries.append({"path": top, "mode": "040000", "type": "tree", "sha": sub_sha})
    print("  子树OK:", top, len(ents), "条", flush=True)
# 保留远端已有的一级目录
have = {e["path"] for e in root_entries}
for e in base_top:
    if e["path"] not in have:
        root_entries.append({"path": e["path"], "mode": "040000", "type": "tree", "sha": e["sha"]})

tree = build_tree_chunked(root_entries)
commit = u.api("/git/commits", {
    "message": "chore: 工作区全量整理归档（九类分类上传，含未上传大文件说明）",
    "tree": tree, "parents": [head["object"]["sha"]],
    "author": {"name": "wangqilong", "email": "wang13236614835@gmail.com",
               "date": "2026-08-27T23:59:00+08:00"}}, method="POST")["sha"]
u.api("/git/refs/heads/main", {"sha": commit, "force": False}, method="PATCH")
print("DONE commit =", commit)
