# -*- coding: utf-8 -*-
# 第 11 周 学习练习骨架 · 由 semester_flow.py scaffold 11 生成（宁显泷）
# 任务: GNNExplainer 对前 10 名候选标最看重原子；季铵氮方向与旧课题模块G对照（新分子如实记）
# 预期契约: [FLOW] top10=10 first_atom_table=True direction_note=True
#           判定: [('top10', '==', '10')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 11
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def load_model():
    """TODO 1: 载入正式版模型与Top-10候选"""
    raise NotImplementedError("TODO: 按验证卡实现")

def explain():
    """TODO 2: GNNExplainer(或注意力权重替代)得各原子重要性"""
    raise NotImplementedError("TODO: 按验证卡实现")

def table():
    """TODO 3: 前10名'最看重原子'表(名称/原子序号/是否季铵氮)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def note():
    """TODO 4: direction_note=与旧课题模块G季铵氮结论方向对照说明"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['top10']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
