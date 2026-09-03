# -*- coding: utf-8 -*-
# 第 10 周 学习练习骨架 · 由 semester_flow.py scaffold 10 生成（衣思淼）
# 任务: 全库体检脚本：空值/单位错/极端值/来源分布扫描，问题分级全处置（零未处置）
# 预期契约: [FLOW] issues={n} unresolved=0
#           判定: [('unresolved', '==', '0')]   过关标准与打卡页一致
# 依赖: 标准库（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 10
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def scan():
    """TODO 1: 全库逐列扫：空值/单位异常/极端值/来源分布"""
    raise NotImplementedError("TODO: 按验证卡实现")

def grade():
    """TODO 2: 问题分级：错误/口径说明/笔误"""
    raise NotImplementedError("TODO: 按验证卡实现")

def dispose():
    """TODO 3: 逐条处置(修或标注)，unresolved计数"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: unresolved=0"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['unresolved']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
