# -*- coding: utf-8 -*-
"""增量 API 推送：把本地未推送的提交经 GitHub Git Data API 逐个补到远端
（用于 github.com:443 被间歇封锁、但 api.github.com 可达时）。

与 push_via_api.py 的区别：不重建全部历史，只把 origin/main..HEAD 的
提交按 blob→tree(base_tree)→commit 链补上去，保持远端能 fast-forward。

凭据来源（二选一，不落盘到仓库）：
  1) 环境变量 TOKEN
  2) git credential fill 输出文件（路径放环境变量 CRED_FILE）

用法: TOKEN=ghp_xxx python tools/push_incremental_api.py
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER, REPO = "wang13236614835-cmyk", "hepato-gnn-screening"
API = f"https://api.github.com/repos/{USER}/{REPO}"

TOKEN = os.environ.get("TOKEN", "")
if not TOKEN and os.environ.get("CRED_FILE"):
    for line in open(os.environ["CRED_FILE"], encoding="utf-8"):
        if line.startswith("password="):
            TOKEN = line.strip().split("=", 1)[1]
if not TOKEN:
    sys.exit("无凭据：请设 TOKEN 或 CRED_FILE 环境变量")


def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败: {r.stderr[:200]}")
    return r.stdout


def api(path, payload=None, method=None, retries=6):
    if payload is not None:
        method = method or "POST"
        data = json.dumps(payload).encode()
    else:
        method = method or "GET"
        data = None
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(API + path)
        req.add_header("Authorization", f"token {TOKEN}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "hepato-uploader")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        req.method = method
        try:
            with urllib.request.urlopen(req, data, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if 400 <= e.code < 500 and e.code not in (403, 409, 422):
                raise RuntimeError(f"API {method} {path} -> {e.code}: {body}")
            last = e  # 限流/冲突/服务端错误 → 重试
        except Exception as e:  # SSL EOF / 连接重置等瞬断
            last = e
        print(f"  [重试{attempt+1}] {method} {path}: {type(last).__name__}", flush=True)
        time.sleep(8 + attempt * 7)
    raise RuntimeError(f"API {method} {path} 多次失败: {last}")


def main():
    remote = api("/git/ref/heads/main")["object"]["sha"]
    local_parent_chain = git("rev-list", "--reverse", f"{remote}..HEAD").split()
    if not local_parent_chain:
        print("远端已同步，无需推送")
        return
    print(f"远端 main={remote[:8]}，待推 {len(local_parent_chain)} 个提交")
    prev = remote
    for ch in local_parent_chain:
        # 该提交相对父提交的文件变更
        parent = git("rev-parse", ch + "^").strip()
        entries = []
        for line in git("diff-tree", "-r", "--no-commit-id", parent, ch).splitlines():
            if not line.strip():
                continue
            meta, path = line.split("\t", 1)
            old_mode, new_mode, old_sha, new_sha = meta.split()[:4]
            path = path.strip('"')
            if new_sha == "0" * 40:            # 删除
                entries.append({"path": path, "mode": old_mode, "type": "blob", "sha": None})
            else:                               # 新增/修改（内容用 git 内部版本，避免 CRLF 干扰）
                entries.append({"path": path, "mode": new_mode, "type": "blob", "sha": new_sha})
        # 逐 blob 上传（跳过远端已有的：用 SHA 探测）
        for e in entries:
            if e["sha"] is None:
                continue
            content = subprocess.run(["git", "-C", ROOT, "cat-file", "blob", e["sha"]],
                                     capture_output=True).stdout
            b = api("/git/blobs", {"content": base64.b64encode(content).decode(),
                                   "encoding": "base64"})
            assert b["sha"] == e["sha"], f"blob sha 不一致 {e['path']}"
        tree = api("/git/trees", {"base_tree": git("rev-parse", parent + "^{tree}").strip(),
                                  "tree": entries})["sha"]
        an, ae, ad = git("log", "-1", "--format=%an%x1f%ae%x1f%aI", ch).split("\x1f")
        msg = git("log", "-1", "--format=%B", ch).rstrip("\n")
        c = api("/git/commits", {"message": msg, "tree": tree, "parents": [prev],
                                 "author": {"name": an, "email": ae, "date": ad},
                                 "committer": {"name": an, "email": ae,
                                               "date": git("log", "-1", "--format=%cI", ch).strip()}})
        prev = c["sha"]
        same = "（SHA与本地一致）" if prev == ch else f"（SHA与本地不同：本地{ch[:8]}）"
        print(f"  提交 {prev[:8]} {an} {same}", flush=True)
        time.sleep(1)
    api("/git/refs/heads/main", {"sha": prev, "force": False}, method="PATCH")
    print("DONE 远端 main =", prev)


if __name__ == "__main__":
    main()
