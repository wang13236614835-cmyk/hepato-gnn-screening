# -*- coding: utf-8 -*-
"""通过 GitHub Git Data API 重建完整提交历史（绕过被封锁的 github.com 443）。

用法: TOKEN=ghp_xxx python push_via_api.py
- 逐blob上传(去重) -> 每个commit建全量tree -> 按原始作者/邮箱/日期建commit -> 建main分支
"""
import base64
import json
import os
import subprocess
import sys
import time

import urllib.request

TOKEN = os.environ["TOKEN"]
USER, REPO = "wang13236614835-cmyk", "hepato-gnn-screening"
API = f"https://api.github.com/repos/{USER}/{REPO}"
HEADERS = {"Authorization": f"token {TOKEN}",
           "Accept": "application/vnd.github+json",
           "Content-Type": "application/json"}


def git(*args):
    return subprocess.run(["git", "-C", r"D:\zcode-workspace\hepato-gnn-screening", *args],
                          capture_output=True, text=True, encoding="utf-8").stdout


REQ_TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "hepato_req.json")


def _curl(path, payload, method):
    import subprocess
    for attempt in range(5):
        args = ["curl", "-s", "--max-time", "300", "-X", method,
                "-H", "Authorization: " + HEADERS["Authorization"],
                "-H", "Accept: " + HEADERS["Accept"],
                "-H", "User-Agent: hepato-uploader"]
        if payload is not None:
            with open(REQ_TMP, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            args += ["-H", "Content-Type: application/json",
                     "--data-binary", "@" + REQ_TMP]
        args.append(API + path)
        out = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        body = out.stdout.strip()
        if not body:
            time.sleep(8)
            continue
        try:
            res = json.loads(body)
        except json.JSONDecodeError:
            time.sleep(8)
            continue
        if isinstance(res, dict) and "sha" not in res and "tree" not in res and "object" not in res and "commit" not in res:
            print("  API错误:", str(res.get("message", ""))[:70], "重试", attempt, flush=True)
            time.sleep(20)
            continue
        return res
    raise RuntimeError(f"api调用失败 {method} {path}")


def api_post(path, payload, method="POST"):
    return _curl(path, payload, method)


def api_get(path):
    return _curl(path, None, "GET")


commits = git("rev-list", "--reverse", "main").split()
meta_lines = git("log", "--reverse", "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%cI",
                 "main").strip().split("\n")
meta = {}
for line in meta_lines:
    h, an, ae, ad, cd = line.split("\x1f")
    meta[h] = (an, ae, ad, cd)
print(f"本地提交数: {len(commits)}", flush=True)

# 0) 空仓库必须先经 Contents API 初始化分支，否则 blob/tree/commit/refs 全部409
branch_ready = False
try:
    r = api_get("/git/ref/heads/main")
    branch_ready = True
    print("  远端main已存在，跳过初始化")
except Exception as e:
    print("  探测main:", type(e).__name__, str(e)[:60])
if not branch_ready:
    readme = subprocess.run(
        ["git", "-C", r"D:\zcode-workspace\hepato-gnn-screening", "show", "main:README.md"],
        capture_output=True).stdout
    init = api_post("/contents/README.md", {
        "branch": "main", "message": "chore: init branch",
        "content": base64.b64encode(readme).decode()}, method="PUT")
    print("  远端main已初始化(临时commit", init["commit"]["sha"][:8] + ")")

# 1) 收集全部blob并去重上传（本地缓存已上传sha，支持断点续传）
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_blobs_done.json")
blobs_done = {}
if os.path.exists(CACHE):
    blobs_done = {k: True for k in json.load(open(CACHE))}
    print(f"  断点续传: 已有{len(blobs_done)}个blob", flush=True)
for ci, ch in enumerate(commits, 1):
    for line in git("ls-tree", "-r", ch).strip().split("\n"):
        info, path = line.split("\t", 1)
        mode, typ, sha = info.split()
        if sha in blobs_done:
            continue
        content = subprocess.run(
            ["git", "-C", r"D:\zcode-workspace\hepato-gnn-screening",
             "cat-file", "blob", sha], capture_output=True).stdout
        b64 = base64.b64encode(content).decode()
        res = api_post("/git/blobs", {"content": b64, "encoding": "base64"})
        assert res["sha"] == sha, f"blob sha mismatch {path}"
        blobs_done[sha] = True
    json.dump(list(blobs_done), open(CACHE, "w"))
    print(f"  [{ci}/{len(commits)}] blob就绪(累计{len(blobs_done)})", flush=True)

# 2) 逐commit建tree与commit对象
prev = None
for ci, ch in enumerate(commits, 1):
    entries = []
    for line in git("ls-tree", "-r", ch).strip().split("\n"):
        info, path = line.split("\t", 1)
        mode, typ, sha = info.split()
        entries.append({"path": path, "mode": mode, "type": "blob", "sha": sha})
    tree = api_post("/git/trees", {"tree": entries})["sha"]
    an, ae, ad, cd = meta[ch]
    msg = git("log", "-1", "--format=%B", ch).rstrip("\n")
    payload = {
        "message": msg, "tree": tree,
        "author": {"name": an, "email": ae, "date": ad},
        "committer": {"name": an, "email": ae, "date": cd},
    }
    if prev:
        payload["parents"] = [prev]
    for attempt in range(3):
        try:
            prev = api_post("/git/commits", payload)["sha"]
            break
        except Exception as e:
            print("  重试commit", attempt, e)
            time.sleep(3)
    print(f"  [{ci}/{len(commits)}] commit {prev[:8]} ({an})", flush=True)

# 3) 把 main 强制指向重建好的历史链顶端（端点必须用复数 refs）
api_post("/git/refs/heads/main", {"sha": prev, "force": True}, method="PATCH")
print("FULLTIP=" + prev, flush=True)
print("DONE 远端main =", prev, flush=True)

