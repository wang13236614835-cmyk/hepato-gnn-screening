# -*- coding: utf-8 -*-
# 第 8 周 学习练习骨架 · 由 semester_flow.py scaffold 8 生成（代维斯丹）
# 任务: 自写一版 ECE/覆盖率重算，与存档对账（浮点误差内一致）＋分箱边界规则写清楚
# 预期契约: [FLOW] ece_match=True cov_match=True binning_note=True
#           判定: [('ece_match', '==', 'True'), ('cov_match', '==', 'True')]   过关标准与打卡页一致
# 依赖: numpy（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 代维斯丹 check 8
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/代维斯丹/ → 仓库根

def load_pred():
    """TODO 1: 读results/predictions/test_predictions.csv与mean/var"""
    raise NotImplementedError("TODO: 按验证卡实现")

def ece():
    """TODO 2: 自写分箱ECE(写清左闭右开边界)与存档0.210对账"""
    raise NotImplementedError("TODO: 按验证卡实现")

def coverage():
    """TODO 3: 覆盖率曲线重算对账"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: ece_match/cov_match；binning_note=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['ece_match', 'cov_match']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
