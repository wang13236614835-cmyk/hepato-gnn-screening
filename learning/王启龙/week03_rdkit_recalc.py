# -*- coding: utf-8 -*-
# 第 3 周 学习练习骨架 · 由 semester_flow.py scaffold 3 生成
# 任务: week03_rdkit_recalc.py：100条(88+12) RDKit 重算描述符，与存档列对照出Δ分布
# 预期契约: [FLOW] rows=100 parse_fail=0 mw_dev={f} logp_dev={f}
#           判定: [('rows', '==', '100'), ('parse_fail', '==', '0')]   依据: data/processed/*.csv 存档列；README 复核清单第2条
# 依赖: rdkit（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 3
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def load_data():
    """TODO 1: 读 processed/cleaned_compounds.csv(88)+screening_pool.csv(12)，取SMILES与存档描述符列"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rdkit_recalc():
    """TODO 2: RDKit重算 MW/LogP/TPSA/HBD/HBA；解析失败计数（预期0）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def deviation():
    """TODO 3: 计算各描述符Δ均值/最大值，方向性结论写3行摘要"""
    raise NotImplementedError("TODO: 按验证卡实现")

def handoff():
    """TODO 4: Δ结论移交衣思淼(WP3)——在笔记中记录"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['rows', 'parse_fail']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
