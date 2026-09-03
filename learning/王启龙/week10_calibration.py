# -*- coding: utf-8 -*-
# 第 10 周 学习练习骨架 · 由 semester_flow.py scaffold 10 生成（王启龙）
# 任务: week10_calibration.py：验证集网格搜T∈[0.5,3.0]步长0.1最小化NLL，输出校准前后ECE+可靠性图(图内英文标签)
# 预期契约: [FLOW] T={f} ece_before={f} ece_after={f} rho={f} pass_ece={bool} pass_rho={bool}
#           判定: [('pass_ece', '==', 'True'), ('pass_rho', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch+numpy（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 10
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def grid_T():
    """TODO 1: 验证集T∈[0.5,3.0]步长0.1网格搜最小NLL，p_cal=sigmoid(z/T)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def ece():
    """TODO 2: 自写分箱ECE（校准前/后）+可靠性图（图内英文标签）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rho():
    """TODO 3: 方差-|误差|Spearman（校准后口径）；pass_ece=ece_after<0.10，pass_rho=rho>=0.6"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['pass_ece', 'pass_rho']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
