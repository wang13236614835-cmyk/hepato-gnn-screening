# -*- coding: utf-8 -*-
"""一键复现全流程(最终融合版, 按 AIDD 课程 8 步 SOP 组织)

课程对照(复旦 MOOC《人工智能药物设计》第 11 章实战 SOP):
  步骤1 靶点档案        -> s1_target_profile (FXR 1OSH / Keap1 4IQK, 证据四栏)
  步骤2 结构+redock门控 -> s2_prep_redock (RMSD<2Å 才放行)
  步骤3 数据+建模       -> s3_model (scaffold split + ECFP/RF 基线 + GNN/MC Dropout
                            + 温度校准 + 杠杆值适用域)
  步骤4 虚拟筛选        -> s4_dock (Lipinski/PAINS 预过滤 + 真实 Vina 批量对接)
  步骤5 多目标共识打分  -> s5_fuse_select (模型 0.45/对接 0.35/类药 0.20, 域外降权)
  步骤6 多样性挑选      -> s5_fuse_select (Butina 骨架簇代表 Top-10)
  步骤7 可得性          -> 数据列自带药材来源(天然产物, 逆合成不适用)
  步骤8 报告            -> s6_report + REPORT.md

运行: python run_all.py            # 全流程(首次含受体制备与 120 次真实对接, 约 10-20 分钟)
      python run_all.py --model    # 只重跑建模/评分/报告(对接结果缓存复用)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from s1_target_profile import run as s1
from s2_prep_redock import run as s2
from s3_model import run as s3
from s4_dock import run as s4
from s5_fuse_select import run as s5
from s6_report import run as s6


def banner(msg):
    print("=" * 64)
    print(msg)
    print("=" * 64, flush=True)


def main():
    fast = "--model" in sys.argv
    t0 = time.time()
    banner("SOP-1/8 靶点档案 (证据四栏)")
    s1()
    banner("SOP-2/8 结构-口袋-redock 门控 (RMSD<2Å)")
    s2(download_structures=not fast)
    banner("SOP-3/8 骨架划分-基线-GNN(MC Dropout)-校准-适用域")
    s3()
    banner("SOP-4/8 预过滤(Lipinski/PAINS) + 真实 Vina 批量对接")
    s4()
    banner("SOP-5/8+6/8 三源共识评分 + 骨架多样性 Top-10")
    s5()
    banner("SOP-7/8+8/8 可得性说明 + 图表汇总")
    s6()
    banner(f"全流程完成, 用时 {time.time()-t0:.0f}s; 结果见 results/, 解读见 REPORT.md")


if __name__ == "__main__":
    main()
