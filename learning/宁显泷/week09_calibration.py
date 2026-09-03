# -*- coding: utf-8 -*-
# 第 9 周 学习练习骨架 · 由 semester_flow.py scaffold 9 生成（宁显泷）
# 任务: 验证集温度 T 网格搜索最优点：ECE<0.10 且 ρ≥0.6 两条同时过
# 预期契约: [FLOW] T={f} ece={f} rho={f} pass_ece={bool} pass_rho={bool}
#           判定: [('pass_ece', '==', 'True'), ('pass_rho', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 9
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def split_val():
    """TODO 1: 验证集划分与已训练模型加载(口径同week08)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def grid_T():
    """TODO 2: T∈[0.5,3.0]步长0.1网格搜最小NLL"""
    raise NotImplementedError("TODO: 按验证卡实现")

def ece_rho():
    """TODO 3: 校准前后ECE+校准后ρ"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: pass_ece=ece_after<0.10；pass_rho=rho>=0.6"""
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
