# -*- coding: utf-8 -*-
# 第 7 周 学习练习骨架 · 由 semester_flow.py scaffold 7 生成（衣思淼）
# 任务: bootstrap 反复抽样给考试分数配 95% 可信区间；数据≥1000、考试集≥150、区间较暑假更窄
# 预期契约: [FLOW] ge1000=True test_ge150=True ci95=True
#           判定: [('ge1000', '==', 'True'), ('test_ge150', '==', 'True')]   过关标准与打卡页一致
# 依赖: numpy(建议服务器)（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 7
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def bootstrap():
    """TODO 1: 测试指标AUC等B=1000次重抽样95%CI"""
    raise NotImplementedError("TODO: 按验证卡实现")

def scale_gate():
    """TODO 2: 数据行数与考试集行数门槛判定"""
    raise NotImplementedError("TODO: 按验证卡实现")

def compare():
    """TODO 3: CI宽度与暑假版对比"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: ge1000/test_ge150/ci95"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['ge1000', 'test_ge150']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
