# -*- coding: utf-8 -*-
# 第 2 周 学习练习骨架 · 由 semester_flow.py scaffold 2 生成（衣思淼）
# 任务: 100 个分子 5 性质 RDKit 重算 vs 暑假表：0 失败＋差距表＋3 句话规律
# 预期契约: [FLOW] rows=100 parse_fail=0
#           判定: [('rows', '==', '100'), ('parse_fail', '==', '0')]   过关标准与打卡页一致
# 依赖: rdkit（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 2
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def load_data():
    """TODO 1: 读processed/cleaned_compounds.csv(88)+screening_pool.csv(12)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rdkit_recalc():
    """TODO 2: RDKit重算 MW/LogP/TPSA/HBD/HBA；解析失败计数(预期0)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def deviation():
    """TODO 3: 各描述符Δ统计表＋3句规律(三萜体重方向等)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def handoff():
    """TODO 4: 差距结论写进数据字典'已知偏差'节"""
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
