# -*- coding: utf-8 -*-
# 第 10 周 学习练习骨架 · 由 semester_flow.py scaffold 10 生成（宁显泷）
# 任务: 27 种参数组合 × 5 折交叉验证：结果表 135 行＋汇总行入库
# 预期契约: [FLOW] rows=135 summary=1
#           判定: [('rows', '==', '135')]   过关标准与打卡页一致
# 依赖: torch(建议服务器)（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 10
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def grid():
    """TODO 1: 27组合(隐藏维×层数×dropout等3×3×3)×5折"""
    raise NotImplementedError("TODO: 按验证卡实现")

def run():
    """TODO 2: 逐组合训练评估(建议服务器)，结果追加CSV"""
    raise NotImplementedError("TODO: 按验证卡实现")

def summary():
    """TODO 3: 汇总最优组合与各折均值行"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: rows=135(数据行)；summary=1"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['rows']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
