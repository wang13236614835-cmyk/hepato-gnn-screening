# -*- coding: utf-8 -*-
# 第 4 周 学习练习骨架 · 由 semester_flow.py scaffold 4 生成（宁显泷）
# 任务: 纯 numpy 徒手一层图卷积（对称归一化），与公式硬算对答案
# 预期契约: [FLOW] shape_ok={bool} coef_sum={f} eq_formula={bool}
#           判定: [('shape_ok', '==', 'True'), ('eq_formula', '==', 'True')]   过关标准与打卡页一致
# 依赖: numpy（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 4
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def build_adj():
    """TODO 1: 构造小图邻接矩阵A(含自环)与度矩阵D"""
    raise NotImplementedError("TODO: 按验证卡实现")

def gcn_layer():
    """TODO 2: numpy实现 H'=D^-0.5·(A+I)·D^-0.5·H·W（对称归一化）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def formula():
    """TODO 3: 同一公式硬算一遍（循环逐元素）对照"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: shape_ok=输出形状正确；coef_sum=归一化系数和；eq_formula=两版一致"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['shape_ok', 'eq_formula']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
