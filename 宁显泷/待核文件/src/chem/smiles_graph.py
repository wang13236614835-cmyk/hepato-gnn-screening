# -*- coding: utf-8 -*-
r"""SMILES -> 分子图 解析器（纯Python零依赖实现）

负责人: 宁显泷（算法组）
用途: 在本地无 RDKit 的环境下，把 SMILES 解析成原子-键图，
      供图神经网络节点特征、Murcko骨架裁剪与指纹计算使用。
说明: 支持 OpenSMILES 常用子集——有机子集原子、芳香小写原子、
      方括号原子（同位素/立体/电荷/H计数）、分支、环闭合（含 %nn）、
      键级 - = # :、'.' 断连。立体标记 @ / \ 仅跳过不解析。
"""
import re

_BRACKET_RE = re.compile(r"\[(\d*)([A-Za-z][a-z]?)(@{0,2})?(H\d*)?([+-]+)?\]")
TWO_LETTER = ("Cl", "Br")
ORGANIC = set("BCNOSPFI")
AROMATIC_ORGANIC = set("c n o s p".split())

# 演示级隐式氢价键表（P/S 取常见高价态）
VALENCE = {"B": 3, "C": 4, "N": 3, "O": 2, "P": 5, "S": 2,
           "F": 1, "Cl": 1, "Br": 1, "I": 1}


class Atom:
    __slots__ = ("idx", "element", "aromatic", "charge", "explicit_h")

    def __init__(self, idx, element, aromatic=False, charge=0, explicit_h=None):
        self.idx = idx
        self.element = element
        self.aromatic = aromatic
        self.charge = charge
        self.explicit_h = explicit_h  # None -> 未指定，用价键规则推断

    def num_h(self, bond_sum):
        if self.explicit_h is not None:
            return self.explicit_h
        eff = VALENCE.get(self.element, 4)
        if self.aromatic:
            eff -= 1
        return max(0, eff - int(round(bond_sum)))


class MolGraph:
    def __init__(self):
        self.atoms = []
        self.bonds = []  # (i, j, order) order: 1/1.5/2/3

    def add_atom(self, element, aromatic=False, charge=0, explicit_h=None):
        a = Atom(len(self.atoms), element, aromatic, charge, explicit_h)
        self.atoms.append(a)
        return a.idx

    def add_bond(self, i, j, order):
        if i is None or j is None or i == j:
            raise ValueError("invalid bond")
        self.bonds.append((i, j, order))

    # ---------- 派生量 ----------
    def neighbors(self):
        nbr = {a.idx: [] for a in self.atoms}
        for i, j, o in self.bonds:
            nbr[i].append(j)
            nbr[j].append(i)
        return nbr

    def bond_sum(self):
        s = {a.idx: 0.0 for a in self.atoms}
        for i, j, o in self.bonds:
            s[i] += o
            s[j] += o
        return s

    def degrees(self):
        d = {a.idx: 0 for a in self.atoms}
        for i, j, _ in self.bonds:
            d[i] += 1
            d[j] += 1
        return d

    def adjacency(self, weighted=True):
        import numpy as np
        n = len(self.atoms)
        A = np.zeros((n, n), dtype=np.float64)
        for i, j, o in self.bonds:
            w = o if weighted else 1.0
            A[i, j] = w
            A[j, i] = w
        return A

    def num_h(self):
        s = self.bond_sum()
        return [self.atoms[a.idx].num_h(s[a.idx]) for a in self.atoms]

    def murcko_prune(self):
        """反复剪除度<=1的重原子，剩余子图即 Bemis-Murcko 骨架（近似）。"""
        alive = set(a.idx for a in self.atoms)
        bonds = list(self.bonds)
        while True:
            deg = {i: 0 for i in alive}
            for i, j, _ in bonds:
                if i in alive and j in alive:
                    deg[i] += 1
                    deg[j] += 1
            drop = {i for i in alive if deg[i] <= 1}
            if not drop:
                break
            alive -= drop
            bonds = [(i, j, o) for i, j, o in bonds if i in alive and j in alive]
        return alive

    def scaffold_key(self):
        """骨架签名: 裁剪后子图的确定性序列化（用于去重与骨架划分）。"""
        alive = self.murcko_prune()
        if not alive:
            return "ACYCLIC"
        nbr = self.neighbors()
        order = sorted(alive)
        base = {i: k for k, i in enumerate(order)}
        edges = sorted(tuple(sorted((base[i], base[j]))) for i, j, _ in self.bonds
                       if i in alive and j in alive)
        nodes = "".join(
            (self.atoms[i].element.lower() if self.atoms[i].aromatic else self.atoms[i].element)
            for i in order)
        return nodes + "|" + ",".join(f"{a}-{b}" for a, b in edges)

    def canonical_string(self):
        """DFS 重编号的规范化串，用于数据去重（演示级，非严格同构）。"""
        nbr = self.neighbors()
        if not self.atoms:
            return ""
        visited = set()
        out = []
        stack = [(0, None)]
        while stack:
            i, parent = stack.pop()
            if i in visited:
                continue
            visited.add(i)
            a = self.atoms[i]
            sym = a.element.lower() if a.aromatic else a.element
            out.append(f"{sym}{i}")
            if parent is not None:
                out.append(f"~{parent}")
            for j in sorted(nbr[i]):
                if j not in visited:
                    stack.append((j, i))
        return ";".join(out)


def parse_smiles(smiles):
    """解析 SMILES。失败返回 None。"""
    g = MolGraph()
    prev = None
    pending_order = None
    ring_map = {}   # 编号 -> (原子idx, 键级)
    stack = []
    i, n = 0, len(smiles)
    try:
        while i < n:
            ch = smiles[i]
            if ch == "(":
                stack.append(prev)
                i += 1
            elif ch == ")":
                if not stack:
                    return None
                prev = stack.pop()
                i += 1
            elif ch == ".":
                prev = None
                i += 1
            elif ch in "-=#:":
                pending_order = {"-": 1.0, "=": 2.0, "#": 3.0, ":": 1.5}[ch]
                i += 1
            elif ch in "/\\":
                i += 1  # 立体双键信息跳过
            elif ch == "%":
                num = int(smiles[i + 1:i + 3])
                _handle_ring(g, prev, num, ring_map, pending_order)
                i += 3
                pending_order = None
            elif ch.isdigit():
                _handle_ring(g, prev, int(ch), ring_map, pending_order)
                i += 1
                pending_order = None
            elif ch == "[":
                m = _BRACKET_RE.match(smiles, i)
                if not m:
                    return None
                iso, elem, _stereo, hpart, charge = m.groups()
                aromatic = elem[0].islower()
                elem = elem[0].upper() + elem[1:]
                if elem not in VALENCE and elem not in TWO_LETTER:
                    elem = elem if elem in VALENCE else "*"
                explicit_h = None
                if hpart:
                    explicit_h = 1 if hpart == "H" else int(hpart[1:])
                chg = (charge.count("+") - charge.count("-")) if charge else 0
                idx = g.add_atom(elem, aromatic, chg, explicit_h)
                _connect(g, prev, idx, pending_order)
                prev = idx
                pending_order = None
                i = m.end()
            elif ch in ORGANIC or ch in AROMATIC_ORGANIC or ch in ("c", "n", "o", "s", "p"):
                two = smiles[i:i + 2]
                if two in TWO_LETTER:
                    idx = g.add_atom(two)
                    i += 2
                else:
                    idx = g.add_atom(ch.upper(), aromatic=ch.islower())
                    i += 1
                _connect(g, prev, idx, pending_order)
                prev = idx
                pending_order = None
            else:
                return None
        if ring_map:
            return None  # 有未闭合的环
        return g
    except (ValueError, KeyError, IndexError):
        return None


def _connect(g, prev, idx, pending_order):
    if prev is not None:
        if pending_order is None:
            both_arom = g.atoms[prev].aromatic and g.atoms[idx].aromatic
            order = 1.5 if both_arom else 1.0
        else:
            order = pending_order
        g.add_bond(prev, idx, order)


def _handle_ring(g, prev, num, ring_map, pending_order):
    if prev is None:
        raise ValueError("ring digit without atom")
    if num in ring_map:
        other, order = ring_map.pop(num)
        both_arom = g.atoms[prev].aromatic and g.atoms[other].aromatic
        if pending_order is None and order is None:
            o = 1.5 if both_arom else 1.0
        else:
            o = max(pending_order or 1.0, order or 1.0)
        g.add_bond(prev, other, o)
    else:
        ring_map[num] = (prev, pending_order)
