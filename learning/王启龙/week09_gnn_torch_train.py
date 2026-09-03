# -*- coding: utf-8 -*-
# 第 9 周 学习练习骨架 · 由 semester_flow.py scaffold 9 生成（王启龙）
# 任务: week09_gnn_torch_train.py：PyG版GNN在splits(seed=42)完整训练+MC Dropout，输出对照表
# 预期契约: [FLOW] torch_auc={f} numpy_auc=0.967 ge_base={bool} rerun_stable={bool}
#           判定: [('ge_base', '==', 'True'), ('rerun_stable', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 9
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def train_torch():
    """TODO 1: PyG GNN在splits(seed=42)训练+MC Dropout推理，固定种子"""
    raise NotImplementedError("TODO: 按验证卡实现")

def compare():
    """TODO 2: torch_auc vs numpy_auc=0.967，ge_base=torch_auc>=0.967"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rerun():
    """TODO 3: 同种子重跑一次，指标一致则rerun_stable=True；低于下界按架构/超参/实现三因素隔离记录"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['ge_base', 'rerun_stable']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
