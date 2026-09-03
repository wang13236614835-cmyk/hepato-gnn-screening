# -*- coding: utf-8 -*-
# 第 11 周 学习练习骨架 · 由 semester_flow.py scaffold 11 生成（王启龙）
# 任务: week11_receptor_audit.py：1OSH/2FLU质量表 + 共晶配体质心 vs grid_box盒子中心距离
# 预期契约: [FLOW] fxr_dist={f} keap1_dist={f} both_lt3={bool}
#           判定: [('both_lt3', '==', 'True')]   过关标准与打卡页一致
# 依赖: 网络/Gemmi或Biopython可选（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 11
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def fetch():
    """TODO 1: RCSB拉1OSH/2FLU，记录分辨率/共晶配体/口袋残基"""
    raise NotImplementedError("TODO: 按验证卡实现")

def centroid():
    """TODO 2: 共晶配体质心计算"""
    raise NotImplementedError("TODO: 按验证卡实现")

def dist():
    """TODO 3: 质心 vs grid_box.py中心([15.2,3.8,24.5]/[-11.5,20.4,-6.2])欧氏距离"""
    raise NotImplementedError("TODO: 按验证卡实现")

def admet_side():
    """TODO 4: 60候选Lipinski违规清单与数据字典已知偏差对照（重点三萜类）"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['both_lt3']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
