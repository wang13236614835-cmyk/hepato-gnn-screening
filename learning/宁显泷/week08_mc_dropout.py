# -*- coding: utf-8 -*-
# 第 8 周 学习练习骨架 · 由 semester_flow.py scaffold 8 生成（宁显泷）
# 任务: 新框架 MC Dropout 连答30遍：ρ（方差-|误差|排序相关）实测＋可靠性图入库（图内英文）
# 预期契约: [FLOW] rho={f} ge_057={bool} fig_saved=True
#           判定: [('ge_057', '==', 'True'), ('fig_saved', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 8
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def mc_infer():
    """TODO 1: MC Dropout连答30遍(T=30，与暑假口径一致)收集预测"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rho():
    """TODO 2: 方差-|误差|Spearman ρ计算"""
    raise NotImplementedError("TODO: 按验证卡实现")

def figure():
    """TODO 3: 可靠性图(英文标签)存learning/宁显泷/"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: ge_057=ρ>=0.57(暑假0.718八成)；fig_saved=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['ge_057', 'fig_saved']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
