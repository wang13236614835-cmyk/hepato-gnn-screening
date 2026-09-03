# -*- coding: utf-8 -*-
# 第 7 周 学习练习骨架 · 由 semester_flow.py scaffold 7 生成（代维斯丹）
# 任务: 新数据重跑朴素贝叶斯＋逻辑回归两个参照模型，对照表入库（旧分数列保留，README 同步）
# 预期契约: [FLOW] nb_auc={f} lr_auc={f} table_updated=True
#           判定: [('table_updated', '==', 'True')]   过关标准与打卡页一致
# 依赖: sklearn（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 代维斯丹 check 7
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/代维斯丹/ → 仓库根

def load_new():
    """TODO 1: 读新数据splits(扩库后)与特征管线"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rerun():
    """TODO 2: sklearn重跑GNB(描述符)+LR(2048bit指纹)两参照"""
    raise NotImplementedError("TODO: 按验证卡实现")

def table():
    """TODO 3: 新旧分数同表入库(nb_auc/lr_auc)，README指标表同步"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: table_updated=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['table_updated']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
