# -*- coding: utf-8 -*-
# 第 4 周 学习练习骨架 · 由 semester_flow.py scaffold 4 生成（衣思淼）
# 任务: 全部分子配标准 SMILES＋InChIKey 并查重；重复处置有规则（优先正式来源）并留清单
# 预期契约: [FLOW] inchikey_dup=0 rule_written=True
#           判定: [('inchikey_dup', '==', '0')]   过关标准与打卡页一致
# 依赖: 网络+rdkit（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py --member 衣思淼 check 4
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/衣思淼/ → 仓库根

def fetch():
    """TODO 1: PUG-REST批量取CanonicalSMILES+InChIKey，status记成功/失败原因"""
    raise NotImplementedError("TODO: 按验证卡实现")

def dedup():
    """TODO 2: InChIKey重复检测与处置(优先正式来源，留清单)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rule():
    """TODO 3: 去重规则文字化(rule_written)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def check():
    """TODO 4: inchikey_dup=0"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['inchikey_dup']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
