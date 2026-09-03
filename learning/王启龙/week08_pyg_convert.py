# -*- coding: utf-8 -*-
# 第 8 周 学习练习骨架 · 由 semester_flow.py scaffold 8 生成（王启龙）
# 任务: week08_pyg_convert.py：numpy版分子图(smiles_graph.py输出)→PyG Data→还原稠密邻接矩阵
# 预期契约: [FLOW] match=5/5 adj_ok=5/5 feat_ok=5/5
#           判定: [('match', '==', '5/5'), ('adj_ok', '==', '5/5'), ('feat_ok', '==', '5/5')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 8
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def pick_cases():
    """TODO 1: 取5个测试SMILES（含VERIFY_MANUAL §3.1最小用例）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def convert():
    """TODO 2: smiles_graph.py输出 → PyG Data(edge_index+13维节点特征)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def verify_adj():
    """TODO 3: edge_index还原稠密邻接矩阵，与numpy版逐位比对"""
    raise NotImplementedError("TODO: 按验证卡实现")

def verify_feat():
    """TODO 4: 节点特征13维逐位比对"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['match', 'adj_ok', 'feat_ok']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
