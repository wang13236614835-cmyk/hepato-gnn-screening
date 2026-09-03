# -*- coding: utf-8 -*-
# 第 7 周 学习练习骨架 · 由 semester_flow.py scaffold 7 生成（王启龙）
# 任务: week07_torch_lr.py：PyTorch手写逻辑回归(2048bit指纹，splits同划分seed=42)，输出测试AUC
# 预期契约: [FLOW] auc_torch={f} base_lr=0.967 delta={f} abs_le_003={bool}
#           判定: [('abs_le_003', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 7
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def load_split():
    """TODO 1: 读 splits/train,val,test.csv + 2048bit指纹特征(src/chem/fingerprints.py同口径)，seed=42"""
    raise NotImplementedError("TODO: 按验证卡实现")

def torch_lr():
    """TODO 2: nn.Linear+SGD/早停训练逻辑回归（手写训练循环）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def compare():
    """TODO 3: 测试AUC vs sklearn基线0.967，delta=auc_torch-0.967，|delta|≤0.03；调参过程全部记录"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['abs_le_003']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
