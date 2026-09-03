# -*- coding: utf-8 -*-
# 第 6 周 学习练习骨架 · 由 semester_flow.py scaffold 6 生成（宁显泷）
# 任务: 新框架完整训练暑假模型（演练允许差距）：指标对照表＋结构/参数/代码三方面差距清单
# 预期契约: [FLOW] table_rows={n} gap_list={n} recorded=True
#           判定: [('recorded', '==', 'True')]   过关标准与打卡页一致
# 依赖: torch+torch_geometric（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 宁显泷 check 6
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/宁显泷/ → 仓库根

def full_train():
    """TODO 1: PyG完整复刻暑假训练流程(88条，固定种子)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def metrics():
    """TODO 2: AUC/ACC/BACC/F1/ECE/ρ主要项与results/metrics基线对照表"""
    raise NotImplementedError("TODO: 按验证卡实现")

def gaps():
    """TODO 3: 差距清单：结构/参数/代码三方面各至少1条"""
    raise NotImplementedError("TODO: 按验证卡实现")

def record():
    """TODO 4: table_rows/gap_list条目数；recorded=True"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['recorded']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
