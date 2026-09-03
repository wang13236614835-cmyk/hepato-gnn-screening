# -*- coding: utf-8 -*-
# 第 12 周 学习练习骨架 · 由 semester_flow.py scaffold 12 生成（衣思淼）
# 任务: 三个融合权重各±0.05 微调实验：前 10 名变化逐条解释（大变=偏科风险，如实记）
# 预期契约: [FLOW] combos={n} changes={n} all_explained=True
#           判定: [('all_explained', '==', 'True')]   过关标准与打卡页一致
# 依赖: 标准库（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 12
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def perturb():
    """TODO 1: 三权重0.45/0.35/0.20各±0.05重算final_score"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rank_shift():
    """TODO 2: 各组合Top-10与基线对比，变化逐条记录"""
    raise NotImplementedError("TODO: 按验证卡实现")

def explain():
    """TODO 3: 每条变化解释(偏科/域外系数影响)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: combos/changes条数；all_explained=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['all_explained']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
