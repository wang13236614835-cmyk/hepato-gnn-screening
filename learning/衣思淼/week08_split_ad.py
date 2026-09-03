# -*- coding: utf-8 -*-
# 第 8 周 学习练习骨架 · 由 semester_flow.py scaffold 8 生成（衣思淼）
# 任务: 新数据重新骨架切分自查零泄漏；陌生结构判定线新旧两版对比如实记
# 预期契约: [FLOW] leak=0 compared=True
#           判定: [('leak', '==', '0')]   过关标准与打卡页一致
# 依赖: rdkit+numpy（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 8
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def scaffold_split():
    """TODO 1: 新数据骨架分组切分(口径同src/data/split.py,seed=42)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def leak_audit():
    """TODO 2: 任一骨架跨train/val/test即泄漏，计数leak"""
    raise NotImplementedError("TODO: 按验证卡实现")

def ad_compare():
    """TODO 3: 陌生结构判定线旧(h*)vs新算法对比表"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: leak=0；compared=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['leak']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
