# -*- coding: utf-8 -*-
# 第 5 周 学习练习骨架 · 由 semester_flow.py scaffold 5 生成（王启龙）
# 任务: week05_redock_selftest.py：1OSH共晶配体抽出→重对接回原盒子→算RMSD，验证链路自洽
# 预期契约: [FLOW] rmsd={f} protocol_lt2={bool}
#           判定: [('protocol_lt2', '==', 'True')]   过关标准与打卡页一致
# 依赖: 服务器Vina/obabel（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py check 5
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/王启龙/ → 仓库根

def extract_ligand():
    """TODO 1: 从1OSH共晶结构抽出原配体(留原始坐标)"""
    raise NotImplementedError("TODO: 按验证卡实现")

def prepare():
    """TODO 2: 受体/配体pdbqt准备（prepare_receptor4/prepare_ligand4，盒子用grid_box.py中心，勿手改）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def redock():
    """TODO 3: Vina重对接（同盒子同种子exh=16）"""
    raise NotImplementedError("TODO: 按验证卡实现")

def rmsd():
    """TODO 4: 对接口袋构象 vs 原配象计算RMSD；<2通过，≥2按WP2排查清单记录排查过程"""
    raise NotImplementedError("TODO: 按验证卡实现")


def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {}
    keys = ['protocol_lt2']
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {missing}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{k}={vals[k]}" for k in keys))

if __name__ == "__main__":
    main()
