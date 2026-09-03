# -*- coding: utf-8 -*-
# 第 5 周 学习练习骨架 · 由 semester_flow.py scaffold 5 生成（宁显泷）
# 任务: 同一份数据 GCN式 vs 求和式(GIN) 各训一次小模型：两条曲线+考试分如实记（学习实验不预设谁赢）
# 预期契约: [FLOW] curves=2 auc_gcn={f} auc_gin={f} recorded=True
#           判定: [('curves', '==', '2'), ('recorded', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 5
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def load_data():
    """TODO 1: 读splits/三表与特征(与暑假口径一致，seed=42)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def train_gcn():
    """TODO 2: GCN式(GCNConv或自实现)训练并记录学习曲线"""
    raise NotImplementedError("TODO: 按验证卡实现")

def train_sum():
    """TODO 3: 求和式(GIN/SumAggregate)同数据训练记录曲线"""
    raise NotImplementedError("TODO: 按验证卡实现")

def record():
    """TODO 4: auc_gcn/auc_gin如实打印；curves=2；只记录不下结论"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['curves', 'recorded']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
