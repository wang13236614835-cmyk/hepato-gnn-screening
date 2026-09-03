# -*- coding: utf-8 -*-
# 第 3 周 学习练习骨架 · 由 semester_flow.py scaffold 3 生成（宁显泷）
# 任务: 暑假手写分子图 ↔ PyG Data 往返翻译，5 个分子零差异（邻接+13维特征）
# 预期契约: [FLOW] match=5/5 adj_ok=5/5 feat_ok=5/5
#           判定: [('match', '==', '5/5'), ('adj_ok', '==', '5/5'), ('feat_ok', '==', '5/5')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric+仓库src（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 3
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def pick_cases():
    """TODO 1: 取5个测试SMILES（含VERIFY_MANUAL §3.1最小用例）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def to_pyg():
    """TODO 2: 用src/chem/smiles_graph.py产出 → 组装PyG Data(edge_index+13维节点特征)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def back_numpy():
    """TODO 3: PyG Data还原numpy邻接与特征"""
    raise NotImplementedError("TODO: 按验证卡实现")

def verify():
    """TODO 4: 往返逐位比对：match/adj_ok/feat_ok各5/5"""
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
