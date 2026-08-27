# -*- coding: utf-8 -*-
"""二维理化描述符（纯Python计算）

负责人: 衣思淼（数据组）
说明: 演示级原子贡献法估算 logP / TPSA，正式运行以服务器端
      RDKit Crippen / Ertl 实现为准（接口列名保持一致以便替换）。
"""
import math

ATOMIC_MASS = {"B": 10.81, "C": 12.011, "N": 14.007, "O": 15.999,
               "F": 19.0, "P": 30.974, "S": 32.06, "Cl": 35.45,
               "Br": 79.90, "I": 126.90, "H": 1.008}

# 原子贡献常数（演示标定: 对黄酮/萜类/生物碱类 logP 误差约±1）
LOGP_ATOM = {"C": 0.27, "N": -0.55, "O": -0.42, "S": 0.25,
             "F": 0.10, "Cl": 0.50, "Br": 0.70, "I": 1.00, "B": 0.0, "P": 0.0}

DESCRIPTOR_COLS = ["MW", "logP_est", "TPSA_est", "nHBD", "nHBA",
                   "nRot", "nAromSystems", "nHeavy"]


def compute_descriptors(g):
    """输入 MolGraph，输出描述符 dict。"""
    nH = g.num_h()
    deg = g.degrees()
    nbr = g.neighbors()

    mw = 0.0
    logp = -0.55  # 截距
    hbd = hba = 0
    arom_atoms = set()
    for a in g.atoms:
        e = a.element
        mw += ATOMIC_MASS.get(e, 12.0) + ATOMIC_MASS["H"] * nH[a.idx]
        logp += LOGP_ATOM.get(e, 0.0)
        if a.charge <= 0:
            if e == "O":
                hba += 1
            elif e == "N":
                hba += 1
        if nH[a.idx] > 0 and e in ("O", "N") and a.charge <= 0:
            hbd += 1
        if a.aromatic:
            arom_atoms.add(a.idx)
    mw += 1.008 * sum(nH)

    # TPSA: N/O 原子贡献近似
    tpsa = 0.0
    for a in g.atoms:
        if a.element == "O":
            tpsa += 20.2
        elif a.element == "N":
            tpsa += 12.5
        if a.element in ("O", "N") and nH[a.idx] > 0:
            tpsa += 1.5

    # 可旋转键: 非环单键且两端重原子度>1（近似: 键不属于三元环即可）
    ring_atoms = g.murcko_prune()
    nrot = 0
    seen = set()
    for i, j, o in g.bonds:
        key = (min(i, j), max(i, j))
        if key in seen:
            continue
        seen.add(key)
        if o != 1.0:
            continue
        if i in ring_atoms and j in ring_atoms:
            continue  # 环内键不计（近似）
        if deg[i] > 1 and deg[j] > 1:
            nrot += 1

    # 芳香体系数 = 芳香原子子图的连通分量数
    n_arom_sys = 0
    vis = set()
    for aidx in arom_atoms:
        if aidx in vis:
            continue
        n_arom_sys += 1
        st = [aidx]
        vis.add(aidx)
        while st:
            u = st.pop()
            for v in nbr[u]:
                if v in arom_atoms and v not in vis:
                    vis.add(v)
                    st.append(v)

    logp += 0.12 * n_arom_sys
    if mw > 650:
        logp -= 0.5  # 大分子/糖苷渗透性经验修正

    return {"MW": round(mw, 2), "logP_est": round(logp, 2),
            "TPSA_est": round(tpsa, 1), "nHBD": hbd, "nHBA": hba,
            "nRot": nrot, "nAromSystems": n_arom_sys,
            "nHeavy": len(g.atoms)}
