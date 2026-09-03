# -*- coding: utf-8 -*-
# 第 4 周 学习练习骨架 · 由 semester_flow.py scaffold 4 生成（王启龙）
# 任务: week04_pubchem_fetch.py：筛选池12条按名称取标准SMILES+InChIKey，输出 week04_pubchem_result.csv
# 预期契约: [FLOW] rows=12 nv011=hit inchikey_dup=0 hit_rate={f}
#           判定: [('rows', '==', '12'), ('nv011', '==', 'hit'), ('inchikey_dup', '==', '0')]   过关标准与打卡页一致
# 依赖: 网络+标准库（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 4
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def load_pool():
    """TODO 1: 读 data/raw/novel_terpenes_lignans.csv 12条（NV-011=奥贝胆酸）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def fetch_pubchem():
    """TODO 2: PUG-REST 按名称取 CanonicalSMILES+InChIKey，status列记录成功/失败原因"""
    raise NotImplementedError("TODO: 按验证卡实现")

def dedup_check():
    """TODO 3: inchikey 列内部去重检查（预期0重复）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def write_csv():
    """TODO 4: 输出 week04_pubchem_result.csv：compound_id,name,std_smiles,inchikey,source_db,status"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['rows', 'nv011', 'inchikey_dup']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
