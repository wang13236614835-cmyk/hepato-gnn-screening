# -*- coding: utf-8 -*-
# 第 2 周 学习练习骨架 · 由 semester_flow.py scaffold 2 生成（宁显泷）
# 任务: 2层小网络：纸上手算梯度 vs PyTorch autograd 自动算，逐位对比
# 预期契约: [FLOW] max_delta={f} lt_1e_6={bool}
#           判定: [('lt_1e_6', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 2
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def build_net():
    """TODO 1: 定义2层小网络(如2-3-1)与小批量输入，权重手动设成简单数"""
    raise NotImplementedError("TODO: 按验证卡实现")

def hand_grad():
    """TODO 2: 按链式法则在纸上/注释里手算各参数梯度，代码里填入手算值数组"""
    raise NotImplementedError("TODO: 按验证卡实现")

def auto_grad():
    """TODO 3: PyTorch autograd 反向传播自动梯度同输入计算"""
    raise NotImplementedError("TODO: 按验证卡实现")

def compare():
    """TODO 4: max_delta=两者最大绝对差；lt_1e_6=max_delta<1e-6"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['lt_1e_6']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
