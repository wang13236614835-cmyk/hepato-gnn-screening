# -*- coding: utf-8 -*-
# W1 学习验证卡 · 环境自检（本骨架开箱即用，本地与服务器各跑一遍）
# 预期: [FLOW] env=ok ... 零 ImportError（来源: docs/00_environment.md §1/§2）
import sys
def v(mod):
    try:
        m = __import__(mod); return getattr(m, "__version__", "ok")
    except Exception:
        return "MISSING"
mods = dict(numpy="numpy", rdkit="rdkit", torch="torch",
            pyg="torch_geometric", vina="vina")
vers = {k: v(m) for k, m in mods.items()}
env_ok = "ok" if vers["numpy"] != "MISSING" else "MISSING"
print("[FLOW] env=" + env_ok + " python=" + sys.version.split()[0] +
      " numpy=" + str(vers["numpy"]) +
      " rdkit=" + ("ok" if vers["rdkit"] != "MISSING" else "MISSING") +
      " torch=" + ("ok" if vers["torch"] != "MISSING" else "MISSING") +
      " pyg=" + ("ok" if vers["pyg"] != "MISSING" else "MISSING") +
      " vina=" + ("ok" if vers["vina"] != "MISSING" else "MISSING"))
