# -*- coding: utf-8 -*-
"""哈希环形指纹（Morgan型, radius=2, 2048bit）

负责人: 代维斯丹（验证组）
用途: 传统机器学习基准线的分子表征。MD5 哈希保证跨平台确定性。
"""
import hashlib

ATOMIC_NUM = {"B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15,
              "S": 16, "Cl": 17, "Br": 35, "I": 53}


def _h(s):
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:12], 16)


def morgan_fp(g, radius=2, nbits=2048):
    """返回 0/1 列表（长度 nbits）。"""
    if not g.atoms:
        return [0] * nbits
    nbr = g.neighbors()
    deg = g.degrees()
    labels = [_h(f"{ATOMIC_NUM.get(a.element, 0)}|{int(a.aromatic)}|{deg[a.idx]}")
              for a in g.atoms]
    bits = set()
    for r in range(radius + 1):
        for lab in labels:
            bits.add(lab % nbits)
        if r == radius:
            break
        new = []
        for i in range(len(g.atoms)):
            env = sorted(labels[j] for j in nbr[i])
            new.append(_h(f"{labels[i]}>>{','.join(map(str, env))}"))
        labels = new
    fp = [0] * nbits
    for b in bits:
        fp[b] = 1
    return fp


def tanimoto(a, b):
    inter = sum(x & y for x, y in zip(a, b))
    union = sum(x | y for x, y in zip(a, b))
    return inter / union if union else 1.0
