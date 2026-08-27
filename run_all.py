# -*- coding: utf-8 -*-
"""一键复现全流程（阶段结果入口）

负责人: 王启龙（工程支撑）
阶段: (1)数据清洗 -> (2)骨架划分 -> (3)基准线 -> (4)GNN+MC Dropout
      -> (5)批量"对接" -> (6)适用域预警 -> (7)协同评分融合 -> (8)出图
运行: python run_all.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from data import clean, split, ad            # noqa: E402
from models import baseline, gnn             # noqa: E402
from docking import mock_docking, grid_box   # noqa: E402
from scoring import fuse                     # noqa: E402
from viz import plots                        # noqa: E402

RES = os.path.join(HERE, "results")


def banner(msg):
    print("=" * 64)
    print(msg)
    print("=" * 64)


def main():
    t0 = time.time()
    banner("Stage 1/8 数据清洗 (衣思淼)")
    clean.clean()
    banner("Stage 2/8 骨架划分 (衣思淼)")
    split.split()
    banner("Stage 3/8 传统基准线 (代维斯丹)")
    baseline.run(os.path.join(RES, "metrics"))
    banner("Stage 4/8 GNN + MC Dropout (宁显泷)")
    gnn_res = gnn.run(os.path.join(RES, "predictions"))
    banner("Stage 5/8 批量对接评分·演示模式 (代维斯丹)")
    grid_box.summarize()
    mock_docking.score_all()
    banner("Stage 6/8 适用域预警 (衣思淼/王启龙)")
    ad.run()
    banner("Stage 7/8 协同评分矩阵 (衣思淼/王启龙)")
    fuse.run()
    banner("Stage 8/8 结果图 (王启龙/代维斯丹)")
    plots.run()
    banner(f"全流程完成，用时 {time.time()-t0:.1f}s；结果见 results/")
    return gnn_res


if __name__ == "__main__":
    main()
