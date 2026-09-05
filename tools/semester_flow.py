#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学期学习推进流工具（负责人·王启龙版）
========================================================================
一个能独立运行的程序：把「AIDD 学习线 × 工作包推进线 × 重头校验线」
三线合一的 16 周学期程序内置为数据，并提供：

  1. 按日期自动定位周次，输出本周看板（学习卡 / 推进任务 / 统筹事项）
  2. 任务勾选与状态持久化（flow_state.json）
  3. 自动核验引擎：真实执行仓库命令并逐项比对【存档基线数字】，
     不信任自报完成——通过/不符都给出实测值与依据来源
  4. 学习练习骨架生成（scaffold）：练习脚本与核验契约 [FLOW] 同源生成，
     保证"每周学习验证准确"可机器判定
  5. 台账与周报生成（markdown，直接发导师）

用法（在仓库任意目录）：
  python tools/semester_flow.py                 # 本周看板
  python tools/semester_flow.py plan            # 学期总览 + 里程碑
  python tools/semester_flow.py week 3          # 查看第 3 周完整卡片
  python tools/semester_flow.py next            # 下一个该做的事
  python tools/semester_flow.py check           # 本周快速核验
  python tools/semester_flow.py check 1 --deep  # 第 1 周深度核验(会跑 run_all.py)
  python tools/semester_flow.py check all --deep# 全学期核验
  python tools/semester_flow.py scaffold 3      # 生成第 3 周练习骨架
  python tools/semester_flow.py done W1-A1      # 勾选任务
  python tools/semester_flow.py undo W1-A1      # 取消勾选
  python tools/semester_flow.py record MAN-W14-01 pass "演练报告已存learning/王启龙/"
  python tools/semester_flow.py ledger          # 学习验证台账
  python tools/semester_flow.py report 1        # 生成周报 md
  python tools/semester_flow.py milestones      # 里程碑状态

准确性纪律（对应推进程序文档的"三原则"）：
  · 内置预期值全部来自仓库存档文件，并在输出中标注来源；
  · 尚未发生的目标态（如 vina 真实分）只判"目标态未达"，绝不预设数字；
  · 本地缺依赖（rdkit/torch 等）的练习判 [跳过]，提示到服务器跑后用 record 补录，
    不谎报通过。

零第三方依赖：仅 Python 标准库（与仓库"本地零依赖"哲学一致）。

exe 版（PyInstaller 打包）：
  · 双击 = 本周看板（看完回车退出）；
  · 命令行用法同上，如 `python tools/semester_flow.py check 1 --deep`；
  · 仓库探测：exe 所在目录 → 其上级 → 当前目录向上；也可 --repo 指定；
  · 快速核验（文件/行数/git/文本锚点）开箱即用；深度核验（run_all/
    verify45/练习运行/确定性重跑）需要本机装有 Python（自动从 PATH 找
    python / py -3，找不到则[跳过]并提示，不谎报通过）。
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- 基础配置

SEMESTER_START = dt.date(2026, 9, 7)   # 开学周一（校历变动时改这一处）
N_WEEKS = 16
TOOL_VERSION = "1.1"

# ---------------------------------------------------------------- 成员（--member）
# 全员 5 人：负责人版=完整三线数据（WEEKS/CHECKS/MILESTONES）；
# 成员版=各自练习契约（EXERCISES_BY_MEMBER）＋独立状态文件＋scaffold/check/report/ledger。
MEMBERS = ["王启龙", "宁显泷", "衣思淼", "代维斯丹", "王散曼"]
MEMBER_PREFIX = {"王启龙": "", "宁显泷": "N", "衣思淼": "Y", "代维斯丹": "D", "王散曼": "S"}  # 打卡页检查项前缀
MEMBER_ROLE = {"王启龙": "负责人·工程支撑", "宁显泷": "算法·模型线", "衣思淼": "数据·数据线A",
               "代维斯丹": "验证·数据线B（对接）", "王散曼": "文献·文献线"}
CURRENT_MEMBER = "王启龙"   # main() 里由 --member 覆盖；下方所有路径经由它取当前成员


def state_relpath(member=None):
    return Path("learning") / (member or CURRENT_MEMBER) / "flow_state.json"


def ledger_relpath(member=None):
    return Path("learning") / (member or CURRENT_MEMBER) / "VERIFY_LEDGER.md"

# 编码策略（防乱码）：
# · 直接在 cmd/PowerShell 窗口运行时（isatty），不强制改编码——Python 会用
#   Windows 控制台的 Unicode 接口输出中文，cmd 默认 GBK 代码页也不会乱码；
# · 输出被管道/重定向时（Git Bash、记日志），改成 UTF-8。
if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------- 基线事实
# 以下预期值全部实测/存档核对（核对日 2026-08-31），来源在每条 check 的
# source 字段注明。修改任何数字必须先改来源文件，再同步这里。

RUN_FLOW_REQUIRED = [  # run_all.py 控制台必含行（实测 2026-08-31，与 VERIFY_MANUAL §2.1 一致）
    "[clean] 带标签集: 88 条 (正样本 48 / 负样本 40)；筛选池: 12 条；剔除 0 条",
    "[split] train: 58 条 (正 28)",
    "[split] val: 13 条 (正 8)",
    "[split] test: 17 条 (正 12)",
    "[split] 骨架组总数 53",
    "[baseline] 高斯朴素贝叶斯(描述符): {'AUC': 0.85, 'ACC': 0.706, 'BACC': 0.733, 'F1': 0.762}",
    "[baseline] 逻辑回归(2048bit指纹): {'AUC': 0.967, 'ACC': 0.706, 'BACC': 0.792, 'F1': 0.737}",
    "[gnn] 测试集: {'AUC': 0.967, 'ACC': 0.824, 'BACC': 0.875, 'F1': 0.857, 'ECE': 0.21}；方差-|误差| Spearman rho=0.718",
    "[docking] FXR演示评分均值: 保肝活性分子 -5.46 vs 负参照 -5.05 kcal/mol (差距 0.42)",
    "[ad] h*=0.362；筛选池域外分子 7/12 (58%) 已标记预警",
    "[fuse] 协同评分完成: 60 个候选入库",
    "全流程完成，用时",
]

CSV_BASELINES = {  # 数据行数（不含表头）· 来源 docs/MANIFEST.md §2（2026-08-31 实测一致）
    "data/raw/tcm_seed_compounds.csv": 88,
    "data/raw/novel_terpenes_lignans.csv": 12,
    "data/processed/cleaned_compounds.csv": 88,
    "data/processed/screening_pool.csv": 12,
    "data/splits/train.csv": 58,
    "data/splits/val.csv": 13,
    "data/splits/test.csv": 17,
    "results/rankings/final_ranking.csv": 60,
}

VERIFY45_LINE = "通过 45 项；不符 0 项"          # reports/pdf_build/verify.py 实测末行
GRID_BOX_ANCHORS = ["[15.2, 3.8, 24.5]", "[-11.5, 20.4, -6.2]"]  # src/docking/grid_box.py:15/23 实测

# ---------------------------------------------------------------- 学期程序数据

WEEKS = [
    dict(no=1, dates="09/07–09/13", stage="AIDD①基础筑基", theme="复现核验启动 · 工程环境就位",
        learn=["Git 进阶：tag/branch/shortlog、署名提交规范", "Linux 服务器与 conda：按 docs/00_environment.md §2 建 hepato 环境(py3.11+rdkit+torch+PyG+vina)",
               "资源：Git Pro Book 第2/3章；conda 官方文档"],
        card=dict(task="week01_exercise.py 环境自检：打印 python/numpy/rdkit/torch/pyg/vina 版本，本地与服务器各跑一遍 run_all.py",
                  cmd="python learning/王启龙/week01_exercise.py",
                  expected="版本表完整、零 ImportError；run_all.py 约6秒完成",
                  source="docs/00_environment.md §1/§2；VERIFY_MANUAL §2.1",
                  criteria="env=ok 即通过；服务器端缺包逐个补装并记录", verifier="宁显泷"),
        tasks=[("W1-A1", "组织全员按 VERIFY_MANUAL §0–§2 复现并收集5人结果"),
               ("W1-A2", "收集 §3 深度核验各线结果，问题清单汇总登记入表"),
               ],
        coord=["周一组会宣讲学期排期（本程序）", "周五向导师报全员复现结果"]),
    dict(no=2, dates="09/14–09/20", stage="AIDD①基础筑基(收尾)", theme="WP1 收尾 · 基线固化 · 核验签名汇总",
        learn=["校验自动化思维：精读 reports/pdf_build/verify.py 的45项断言范式", "assert+期望值表：人工对数字→脚本断言"],
        card=dict(task="给 verify.py 45项断言逐条标注来源文件，产出 week02_notes.md 注释表",
                  cmd="python reports/pdf_build/verify.py",
                  expected="通过 45 项；不符 0 项（实测基线）",
                  source="reports/pdf_build/verify.py（2026-08-31 实测）",
                  criteria="注释表45行齐全；核验人抽5项对锚定CSV", verifier="衣思淼"),
        tasks=[("W2-A1", "汇总5人核验签名表；verify.py 通过截图存 results/logs/（新建并登记MANIFEST）"),
               ("W2-A2", "git tag -a v1.0-summer 固化暑假基线"),
               ],
        coord=["周五前收齐5人核验签名并存results/logs/", "45项注释表抽查5项对锚定CSV"]),
    dict(no=3, dates="09/21–09/27", stage="AIDD②数据与表征", theme="RDKit 上手 · 描述符重算",
        learn=["SMILES/InChI/InChIKey、规范化与立体化学", "RDKit：Mol对象、MW/LogP/TPSA/HBD/HBA、Morgan指纹", "资源：RDKit 官方 Getting Started/Cookbook"],
        card=dict(task="week03_rdkit_recalc.py：100条(88+12) RDKit 重算描述符，与存档列对照出Δ分布",
                  cmd="python learning/王启龙/week03_rdkit_recalc.py",
                  expected="rows=100 parse_fail=0；Δ分布如实记录（存档为教学估算版，预期存在系统偏差——这正是WP3描述符升级的实测依据）",
                  source="data/processed/*.csv 存档列；README 复核清单第2条",
                  criteria="机器判 rows=100 parse_fail=0；Δ结论3行摘要写入笔记并移交衣思淼", verifier="衣思淼"),
        tasks=[("W3-A2", "WP2启动会：确认服务器 ADFR/Vina 安装"),
               ("W3-A3", "WP3启动会：定 TCMSP/PubChem 导出字段(source_db/std_smiles/inchikey，保留HP/DC/NV前缀)")],
        coord=["周五汇报：WP2/WP3 启动"]),
    dict(no=4, dates="09/28–10/04", stage="AIDD②数据与表征", theme="国庆轻量周 · 数据库API（只排学习，不排服务器任务）",
        learn=["PubChem PUG-REST 按名称/InChIKey 批量取标准SMILES", "ChEMBL webresource client；TCMSP 导出规则", "去重键升级：规范化串→InChIKey（WP3步骤3口径）"],
        card=dict(task="week04_pubchem_fetch.py：筛选池12条按名称取标准SMILES+InChIKey，输出 week04_pubchem_result.csv",
                  cmd="python learning/王启龙/week04_pubchem_fetch.py",
                  expected="rows=12 nv011=hit inchikey_dup=0（命中率如实记录，不预设；NV-011奥贝胆酸必须命中，失败即脚本bug）",
                  source="data/raw/novel_terpenes_lignans.csv（12条，NV-011=奥贝胆酸）；WP3 步骤1/3",
                  criteria="机器判 rows=12/nv011=hit/inchikey_dup=0；脚本可重跑；结果移交衣思淼", verifier="王散曼"),
        tasks=[("W4-A1", "W3描述符Δ结论 + W4脚本框架移交衣思淼并入WP3工程件"),
               ("W4-A2", "检查WP2受体文件就绪（1OSH/2FLU，RCSB）")],
        coord=["假期产出=学习卡完成即可"]),
    dict(no=5, dates="10/05–10/11", stage="AIDD⑧分子对接", theme="Vina 对接工程",
        learn=["打分函数原理、网格盒子、exhaustiveness与种子", "受体准备(去水/加氢/pdbqt)与配体准备(构象→加氢→pdbqt)", "资源：AutoDock Vina 官方文档 autodock.github.io；docs/03_docking_protocol.md；grid_box.py 为盒子唯一准绳"],
        card=dict(task="week05_redock_selftest.py：1OSH共晶配体抽出→重对接回原盒子→算RMSD，验证链路自洽",
                  cmd="python learning/王启龙/week05_redock_selftest.py",
                  expected="rmsd<2.0（协议标准，WP2验收第1条同款；数值如实记录）",
                  source="WP2 验收标准第1条",
                  criteria="机器判 protocol_lt2；≥2Å按WP2排查清单(盒子/质子化/加氢)排查并记录——无排查记录的通过与无结论的失败都不算过", verifier="代维斯丹"),
        tasks=[("W5-A1", "维护 run_vina.sh 批量对接：100分子×2靶点配体pdbqt批量生成"),
               ("W5-A2", "服务器批量作业排程与日志落盘(results/docking/vina_out/)"),
               ("W5-A3", "批量脚本 dry-run 无误；首批10配体试跑零报错")],
        coord=["组会确认WP2/WP3中期进度", "向导师报演示分→真实分替换计划与风险"]),
    dict(no=6, dates="10/12–10/18", stage="AIDD⑧分子对接", theme="WP2 收尾 · 排名 v2",
        learn=["对接log解析、RMSD双口径(inplace/align)、回打分验证协议", "打分函数局限：v1课题verify_repro模块F已证 Vina对甾体/大环偏低——引以为鉴"],
        card=dict(task="collect_vina_logs.py：解析全部vina log→覆盖docking_scores.csv(mode: mock_local→vina，保留演示分列)",
                  cmd="python src/docking/collect_vina_logs.py",
                  expected="200数据行(100分子×2靶点)、mode全vina、零解析失败；阳性对照满足RMSD<2Å或打分进前20%",
                  source="results/docking/docking_scores.csv 实测现状200行/mode=mock_local（2026-08-31）；WP2 验收1/2/3条",
                  criteria="机器判 mode全vina；演示vs真实Spearman如实计算；重跑run_all出排名v2且Top-10变化逐条有解释", verifier="宁显泷"),
        tasks=[("W6-A1", "排名v2出表+WP2文件末尾对比分析+核验签字，WP2关闭"),
               ("W6-A2", "阳性对照(水飞蓟宾-FXR/已知Keap1配体)回打分记录在案")],
        coord=["里程碑M3汇报排名v2与变化解释", "启动WP4前置环境（W1脚本复用自检）"]),
    dict(no=7, dates="10/19–10/25", stage="AIDD③深度学习入门", theme="WP3 收尾验收 · PyTorch 起步",
        learn=["PyTorch 张量/autograd/nn.Module/训练循环/早停；与numpy映射（团队已有numpy GNN基础，重点在翻译）", "资源：PyTorch 官方 60 Minute Blitz"],
        card=dict(task="week07_torch_lr.py：PyTorch手写逻辑回归(2048bit指纹，splits同划分seed=42)，输出测试AUC",
                  cmd="python learning/王启龙/week07_torch_lr.py",
                  expected="auc_torch 与 sklearn LR基线0.967 差≤0.03；未达标允许调参但过程必须记录",
                  source="results/metrics/baseline.csv（LR AUC=0.967）",
                  criteria="机器判 abs_le_003；未达标附完整调参记录交核验人判", verifier="宁显泷"),
        tasks=[("W7-A1", "WP3验收四条逐项打勾：source_db标记/inchikey零重复/bootstrap置信区间收窄/抽检30条标签"),
               ("W7-A2", "新旧数据规模与指标对照表入库；三萜MW偏差在数据字典回填实测值")],
        coord=["组会宣布WP3关闭、WP4启动", "期中检查材料预备"]),
    dict(no=8, dates="10/26–11/01", stage="AIDD④图神经网络", theme="PyG 分子图（接口地基周）",
        learn=["图数据结构：邻接矩阵vs edge_index；PyG Data/DataLoader", "分子图表征：原子节点/键边", "资源：PyG 官方教程 Introduction by Example"],
        card=dict(task="week08_pyg_convert.py：numpy版分子图(smiles_graph.py输出)→PyG Data→还原稠密邻接矩阵",
                  cmd="python learning/王启龙/week08_pyg_convert.py",
                  expected="5个测试SMILES(含VERIFY_MANUAL §3.1最小用例)：match=5/5（邻接与13维节点特征逐位一致）",
                  source="src/chem/smiles_graph.py；src/models/dataset.py（节点特征13维口径）",
                  criteria="机器判 match=5/5——WP4迁移的接口地基必须零差异", verifier="宁显泷"),
        tasks=[("W8-A1", "src/models/gnn_torch.py 骨架：load_split/fullpool接口与CSV列名与numpy版一致(fuse.py零改动可切换)"),
               ("W8-A2", "接口冒烟测试：torch版在88条数据forward跑通、输出列名diff零差异")],
        coord=["期中检查材料提交(若本周收)", "周五汇报PyG迁移接口方案"]),
    dict(no=9, dates="11/02–11/08", stage="AIDD④图神经网络", theme="GNN 对照实验",
        learn=["GCN(Kipf2016)/MPNN(Gilmer2017)/GIN(Xu2018)消息传递；过平滑", "对照实验方法论：同数据同划分同指标，一次只变一个因素"],
        card=dict(task="week09_gnn_torch_train.py：PyG版GNN在splits(seed=42)完整训练+MC Dropout，输出对照表",
                  cmd="python learning/王启龙/week09_gnn_torch_train.py",
                  expected="ge_base=真：torch版AUC不低于numpy版0.967(WP4验收第1条)；种子固定重跑两次一致",
                  source="results/metrics 存档(numpy GNN AUC=0.967)；WP4 验收第1条",
                  criteria="机器判 ge_base 与 rerun_stable；低于下界按架构/超参/实现三因素隔离排查记录", verifier="宁显泷"),
        tasks=[("W9-A1", "超参搜索落库：hidden{32,64,128}×dropout{0.2,0.3,0.5}×T_MC{10,30,50}，5折=135行结果表"),
               ("W9-A2", "搜索作业批处理脚本与结果汇总自动化")],
        coord=["组会过对照表", "向导师汇报迁移不降性能证据链"]),
    dict(no=10, dates="11/09–11/15", stage="AIDD④图神经网络(评估)", theme="校准与可靠性 · WP4 收尾",
        learn=["温度缩放(Guo2017)、ECE、可靠性图", "不确定性质量：方差-|误差|Spearman（本项目特色ρ=0.718的来源）"],
        card=dict(task="week10_calibration.py：验证集网格搜T∈[0.5,3.0]步长0.1最小化NLL，输出校准前后ECE+可靠性图(图内英文标签)",
                  cmd="python learning/王启龙/week10_calibration.py",
                  expected="ece_after<0.10（基线0.21）且 rho≥0.6 同时满足（WP4验收第2/3条）",
                  source="WP4 验收标准第2/3条；README(当前ECE=0.21)",
                  criteria="机器判 pass_ece与pass_rho双过；ECE过但ρ<0.6退回重算MC方差口径，不许静默弃条", verifier="衣思淼"),
        tasks=[("W10-A1", "WP4四条验收全打勾：torch≥numpy / ECE<0.10图贴对角线 / ρ≥0.6 / 接口零改动"),
               ("W10-A2", "(可选)序数回归启动评估——不挤占验收")],
        coord=["里程碑M5汇报", "启动WP5：认领W11相互作用图工程"]),
    dict(no=11, dates="11/16–11/22", stage="AIDD⑦蛋白结构 + ⑥ADMET", theme="受体质量审计 + 相互作用图",
        learn=["PDB结构质量：分辨率/配体口袋/缺失残基；AlphaFold pLDDT与适用边界", "ADMET五规则(Lipinski)；swissadme.ch 对照", "资源：RCSB/AlphaFold DB 官方文档"],
        card=dict(task="week11_receptor_audit.py：1OSH/2FLU质量表 + 共晶配体质心 vs grid_box盒子中心距离",
                  cmd="python learning/王启龙/week11_receptor_audit.py",
                  expected="两受体距离均<3Å为优；≥3Å须书面解释（变构位点等），不许默认当错误也不许默认当通过",
                  source="src/docking/grid_box.py:15/23 实测中心；协议标准<3Å",
                  criteria="机器判 both_lt3；附ADMET副练习：60候选Lipinski违规清单与数据字典已知偏差对照", verifier="代维斯丹"),
        tasks=[("W11-A1", "PyMOL批处理出Top-10真实对接相互作用图(用vina_out构象)供王散曼更新literature/03"),
               ("W11-A2", "相互作用图10张入库：命名规范+标注配体/受体/PDBID/对接分")],
        coord=["组会确认湿实验衔接方案(HepG2 CCl4/APAP、ALT/AST/ROS、水飞蓟宾阳性对照，经导师确认)"]),
    dict(no=12, dates="11/23–11/29", stage="AIDD⑨大模型时代", theme="LLM 辅助文献核验",
        learn=["LLM辅助科研正确姿势：LLM出检索式/抽取候选，人核结论（幻觉引用是真实风险）", "Prompt模板化、RAG概念"],
        card=dict(task="week12_lit_llm_assist.md+模板集：literature/01抽10条A/B级，LLM生成PubMed检索式→人确认PMID→回填已核对✓",
                  cmd="人工闭环，工具记录 [FLOW] closed=10/10 pmid=10（在模板文件末行手填）",
                  expected="10/10条目闭环(PMID或书面处置)；命中率/修正率如实记录——这正是LLM可靠性实测数据",
                  source="WP5 步骤1核对口径(A/B级100%)",
                  criteria="零'LLM说了就信'条目，每条有PubMed页面证据；模板可复用；幻觉案例单独记录(答辩可用)", verifier="王散曼"),
        tasks=[("W12-A1", "模板移交王散曼全量跑literature/"),
               ("W12-A2", "结题报告工程框架：目录树+图表位+数字引用全部锚定results/文件(延续45项断言思路)")],
        coord=["文献核对进度表每周更新；数字引用规范草案过组会"]),
    dict(no=13, dates="11/30–12/06", stage="AIDD⑤生成(选修)+⑨Agent", theme="排名 v3 全链路整合",
        learn=["分子生成概览：RNN/VAE/扩散三类一句话原理+MOSES基准——定位论文未来工作，不在本学期实施范围", "Agent工作流：把W12模板抽象为检索→核验→回填三步固定流"],
        card=dict(task="week13_notes.md：生成模型500字读书笔记(三类各一句原理+对本课题候选扩充的潜在用法一段)，组会3分钟陈述",
                  cmd="python tools/semester_flow.py check 13",
                  expected="笔记400–600字；三问(如'VAE隐空间为何可插值')能答原理层",
                  source="AIDD文章阶段⑤；MOSES基准论文",
                  criteria="字数与概念正确性由核验人判", verifier="宁显泷"),
        tasks=[("W13-A1", "run_all.py 切换：数据v2(≥1000) + GNN torch校准版 + Vina真实分 → 排名v3"),
               ("W13-A2", "确定性核验：连跑两次md5一致(工具 deep check 13 自动执行)"),
               ("W13-A3", "verify.py 45项扩到学期版N项，每项锚定新results文件")],
        coord=["里程碑M6汇报；结题报告章节认领到人"]),
    dict(no=14, dates="12/07–12/13", stage="AIDD⑩实战与产出", theme="结题工程 · 可复现交付",
        learn=["可复现交付：环境锁定/README重写/发布打包", "科技图表规范：坐标轴/单位/色盲友好"],
        card=dict(task="交付包演练：找一名未参与者(或低年级同学)在空白环境仅凭VERIFY_MANUAL复现排名v3，计时并记卡点",
                  cmd="由演练者执行 §0→§2 全部命令",
                  expected="协议标准：30分钟内完成§0–§2关键行一致；卡点当日修复",
                  source="docs/VERIFY_MANUAL.md 全流程",
                  criteria="演练报告(耗时/卡点清单/修复状态)入库；存在未修复卡点即不通过", verifier="演练者签字+导师抽查"),
        tasks=[("W14-A1", "README更新：v2指标、复核清单逐条销项(真实对接✓/正式数据✓/文献核对✓/PyG迁移✓)"),
               ("W14-A2", "MANIFEST全量登记对账：登记数=实际新增文件数"),
               ("W14-A3", "git tag v2.0-semester")],
        coord=["确认文献100%核对(WP5验收第1条：A/B级100%附PMID)"]),
    dict(no=15, dates="12/14–12/20", stage="AIDD⑩实战与产出", theme="重头校验学期版（校验线主场）",
        learn=["方法论照搬verify_repro六原则：独立实现计算路径/引擎级重跑/逆推溯源/原目录零改动/问题三级分级/未覆盖范围声明"],
        card=dict(task="verify_semester/：对数据v2、GNN v2(同种子重训)、校准(ECE独立重算)、Vina(抽10配体同盒子同种子重跑)、排名v3(融合公式独立重编)、结题报告数字逆推——六模块独立复算",
                  cmd="python tools/semester_flow.py check 15",
                  expected="六模块产物≥6个入verify_semester/outputs/；每模块✅/⚠️/❌三级；❌清零才进W16",
                  source="verify_repro/复现验证报告.md 范式（v1课题已验证可行：7模块全过、2项引擎级逐位复现）",
                  criteria="产出自套v1报告格式《学期重头校验报告》", verifier="全员分工互验"),
        tasks=[("W15-A1", "六模块独立复算+逆推（不复用原脚本，产物独立落盘）"),
               ("W15-A2", "成员版推进程序执行情况总核验"),
               ("W15-A3", "《学期重头校验报告》成文")],
        coord=["导师结题材料倒排预警会"]),
    dict(no=16, dates="12/21–12/27", stage="AIDD⑩实战与产出", theme="结题定稿与预答辩",
        learn=["答辩表达：10分钟讲清问题-方法-证据-结论", "FAQ应答训练：项目简介md第六节四问为底线题库，扩到20问"],
        card=dict(task="结题材料包：结题报告(附W15校验报告——重头校验全过是最硬证据链)/排名v3/文献核对表/实验衔接一页纸/PPT",
                  cmd="python tools/semester_flow.py check 16",
                  expected="W15❌清零；结题报告数字100%有锚点；预答辩通过；git tag v2.0-semester存在",
                  source="W15校验结论；MANIFEST登记",
                  criteria="材料全入reports/并登记；FAQ 20问不卡壳；现场run_all一键复现演示彩排计时", verifier="导师+全员"),
        tasks=[("W16-A1", "结题报告定稿+材料包入reports/+MANIFEST登记"),
               ("W16-A2", "预答辩(导师+全员)并按意见修订"),
               ("W16-A3", "演示彩排：现场python run_all.py一键复现(耗时如实更新)")],
        coord=["向导师提交结题材料", "2027年1月结题答辩(M9)"]),
]

# 手工补录项（外部平台/线下动作，无法自动核验，必须 record 留痕）
MANUALS = [
    dict(id="MAN-W7-01", week=7, text="WP3 验收四条逐项打勾+核验人签字（WP3文件末尾核验表）", dead=None),
    dict(id="MAN-W9-01", week=9, text="期中检查材料提交（按学校通知时间，若变动按通知）", dead=None),
    dict(id="MAN-W10-01", week=10, text="WP4 验收四条逐项打勾+核验人签字", dead=None),
    dict(id="MAN-W14-01", week=14, text="第三方空白环境复现演练报告（耗时/卡点/修复状态）", dead=None),
    dict(id="MAN-W15-01", week=15, text="学期重头校验 ❌ 清零签字", dead=None),
    dict(id="MAN-W16-01", week=16, text="预答辩通过记录", dead=None),
]

# 学习练习契约（scaffold 生成骨架，check 机器判定；needs 列出依赖便于判断本地/服务器）
EXERCISES = {
    1: dict(file="week01_exercise.py", needs="标准库", flow="env=ok python={x} numpy={x} rdkit={ok} torch={ok} pyg={ok} vina={ok}",
            preds=[("env", "==", "ok")]),
    2: dict(file="week02_notes.md", needs="人工整理", flow=None, preds=[], md=True,
            task="45 项检查注释表：verify.py 每项断言对应哪个文件、对的是什么数字"),
    3: dict(file="week03_rdkit_recalc.py", needs="rdkit", flow="rows=100 parse_fail=0 mw_dev={f} logp_dev={f}",
            preds=[("rows", "==", "100"), ("parse_fail", "==", "0")]),
    4: dict(file="week04_pubchem_fetch.py", needs="网络+标准库", flow="rows=12 nv011=hit inchikey_dup=0 hit_rate={f}",
            preds=[("rows", "==", "12"), ("nv011", "==", "hit"), ("inchikey_dup", "==", "0")]),
    5: dict(file="week05_redock_selftest.py", needs="服务器Vina/obabel", flow="rmsd={f} protocol_lt2={bool}",
            preds=[("protocol_lt2", "==", "True")]),
    7: dict(file="week07_torch_lr.py", needs="torch", flow="auc_torch={f} base_lr=0.967 delta={f} abs_le_003={bool}",
            preds=[("abs_le_003", "==", "True")]),
    8: dict(file="week08_pyg_convert.py", needs="torch+torch_geometric", flow="match=5/5 adj_ok=5/5 feat_ok=5/5",
            preds=[("match", "==", "5/5"), ("adj_ok", "==", "5/5"), ("feat_ok", "==", "5/5")]),
    9: dict(file="week09_gnn_torch_train.py", needs="torch+torch_geometric", flow="torch_auc={f} numpy_auc=0.967 ge_base={bool} rerun_stable={bool}",
            preds=[("ge_base", "==", "True"), ("rerun_stable", "==", "True")]),
    10: dict(file="week10_calibration.py", needs="torch+numpy", flow="T={f} ece_before={f} ece_after={f} rho={f} pass_ece={bool} pass_rho={bool}",
            preds=[("pass_ece", "==", "True"), ("pass_rho", "==", "True")]),
    11: dict(file="week11_receptor_audit.py", needs="网络/Gemmi或Biopython可选", flow="fxr_dist={f} keap1_dist={f} both_lt3={bool}",
            preds=[("both_lt3", "==", "True")]),
    12: dict(file="week12_lit_llm_assist.md", needs="人工闭环", flow="closed=10/10 pmid=10 llm_hit_rate={f}",
            preds=[("closed", "==", "10/10"), ("pmid", "==", "10")], md=True),
    13: dict(file="week13_notes.md", needs="无", flow=None, preds=[], md=True, min_chars=400),
    14: dict(file="week14_drill_report.md", needs="人工演练", flow=None, preds=[], md=True,
            task="第三方空白环境复现演练报告：耗时/卡点/修复状态/结论"),
}

# 练习骨架的 TODO 说明（scaffold 用）
SCAFFOLD_TODO = {
    3: [("load_data", "读 processed/cleaned_compounds.csv(88)+screening_pool.csv(12)，取SMILES与存档描述符列"),
        ("rdkit_recalc", "RDKit重算 MW/LogP/TPSA/HBD/HBA；解析失败计数（预期0）"),
        ("deviation", "计算各描述符Δ均值/最大值，方向性结论写3行摘要"),
        ("handoff", "Δ结论移交衣思淼(WP3)——在笔记中记录")],
    4: [("load_pool", "读 data/raw/novel_terpenes_lignans.csv 12条（NV-011=奥贝胆酸）"),
        ("fetch_pubchem", "PUG-REST 按名称取 CanonicalSMILES+InChIKey，status列记录成功/失败原因"),
        ("dedup_check", "inchikey 列内部去重检查（预期0重复）"),
        ("write_csv", "输出 week04_pubchem_result.csv：compound_id,name,std_smiles,inchikey,source_db,status")],
    5: [("extract_ligand", "从1OSH共晶结构抽出原配体(留原始坐标)"),
        ("prepare", "受体/配体pdbqt准备（prepare_receptor4/prepare_ligand4，盒子用grid_box.py中心，勿手改）"),
        ("redock", "Vina重对接（同盒子同种子exh=16）"),
        ("rmsd", "对接口袋构象 vs 原配象计算RMSD；<2通过，≥2按WP2排查清单记录排查过程")],
    7: [("load_split", "读 splits/train,val,test.csv + 2048bit指纹特征(src/chem/fingerprints.py同口径)，seed=42"),
        ("torch_lr", "nn.Linear+SGD/早停训练逻辑回归（手写训练循环）"),
        ("compare", "测试AUC vs sklearn基线0.967，delta=auc_torch-0.967，|delta|≤0.03；调参过程全部记录")],
    8: [("pick_cases", "取5个测试SMILES（含VERIFY_MANUAL §3.1最小用例）"),
        ("convert", "smiles_graph.py输出 → PyG Data(edge_index+13维节点特征)"),
        ("verify_adj", "edge_index还原稠密邻接矩阵，与numpy版逐位比对"),
        ("verify_feat", "节点特征13维逐位比对")],
    9: [("train_torch", "PyG GNN在splits(seed=42)训练+MC Dropout推理，固定种子"),
        ("compare", "torch_auc vs numpy_auc=0.967，ge_base=torch_auc>=0.967"),
        ("rerun", "同种子重跑一次，指标一致则rerun_stable=True；低于下界按架构/超参/实现三因素隔离记录")],
    10: [("grid_T", "验证集T∈[0.5,3.0]步长0.1网格搜最小NLL，p_cal=sigmoid(z/T)"),
         ("ece", "自写分箱ECE（校准前/后）+可靠性图（图内英文标签）"),
         ("rho", "方差-|误差|Spearman（校准后口径）；pass_ece=ece_after<0.10，pass_rho=rho>=0.6")],
    11: [("fetch", "RCSB拉1OSH/2FLU，记录分辨率/共晶配体/口袋残基"),
         ("centroid", "共晶配体质心计算"),
         ("dist", "质心 vs grid_box.py中心([15.2,3.8,24.5]/[-11.5,20.4,-6.2])欧氏距离"),
         ("admet_side", "60候选Lipinski违规清单与数据字典已知偏差对照（重点三萜类）")],
}

# ---------------------------------------------------------------- 成员练习契约
# 与 tools/gen_member_pages.py 的 EX 登记及各成员打卡页周卡片同源；
# 过关标准（flow/preds）逐条取自打卡页"过关标准"栏，不新设标准。

EXERCISES_NXL = {  # 宁显泷（管模型）
    2: dict(file="week02_backprop.py", needs="torch",
            task="2层小网络：纸上手算梯度 vs PyTorch autograd 自动算，逐位对比",
            flow="max_delta={f} lt_1e_6={bool}", preds=[("lt_1e_6", "==", "True")]),
    3: dict(file="week03_pyg_convert.py", needs="torch+torch_geometric+仓库src",
            task="暑假手写分子图 ↔ PyG Data 往返翻译，5 个分子零差异（邻接+13维特征）",
            flow="match=5/5 adj_ok=5/5 feat_ok=5/5",
            preds=[("match", "==", "5/5"), ("adj_ok", "==", "5/5"), ("feat_ok", "==", "5/5")]),
    4: dict(file="week04_gcn_numpy.py", needs="numpy",
            task="纯 numpy 徒手一层图卷积（对称归一化），与公式硬算对答案",
            flow="shape_ok={bool} coef_sum={f} eq_formula={bool}",
            preds=[("shape_ok", "==", "True"), ("eq_formula", "==", "True")]),
    5: dict(file="week05_gcn_vs_gin.py", needs="torch+torch_geometric",
            task="同一份数据 GCN式 vs 求和式(GIN) 各训一次小模型：两条曲线+考试分如实记（学习实验不预设谁赢）",
            flow="curves=2 auc_gcn={f} auc_gin={f} recorded=True",
            preds=[("curves", "==", "2"), ("recorded", "==", "True")]),
    6: dict(file="week06_torch_trial.py", needs="torch+torch_geometric",
            task="新框架完整训练暑假模型（演练允许差距）：指标对照表＋结构/参数/代码三方面差距清单",
            flow="table_rows={n} gap_list={n} recorded=True", preds=[("recorded", "==", "True")]),
    8: dict(file="week08_mc_dropout.py", needs="torch",
            task="新框架 MC Dropout 连答30遍：ρ（方差-|误差|排序相关）实测＋可靠性图入库（图内英文）",
            flow="rho={f} ge_057={bool} fig_saved=True",
            preds=[("ge_057", "==", "True"), ("fig_saved", "==", "True")]),
    9: dict(file="week09_calibration.py", needs="torch",
            task="验证集温度 T 网格搜索最优点：ECE<0.10 且 ρ≥0.6 两条同时过",
            flow="T={f} ece={f} rho={f} pass_ece={bool} pass_rho={bool}",
            preds=[("pass_ece", "==", "True"), ("pass_rho", "==", "True")]),
    10: dict(file="week10_hpo.py", needs="torch(建议服务器)",
             task="27 种参数组合 × 5 折交叉验证：结果表 135 行＋汇总行入库",
             flow="rows=135 summary=1", preds=[("rows", "==", "135")]),
    11: dict(file="week11_explainer.py", needs="torch+torch_geometric",
             task="GNNExplainer 对前 10 名候选标最看重原子；季铵氮方向与旧课题模块G对照（新分子如实记）",
             flow="top10=10 first_atom_table=True direction_note=True", preds=[("top10", "==", "10")]),
}

EXERCISES_YSM = {  # 衣思淼（数据线A）
    2: dict(file="week02_rdkit_recalc.py", needs="rdkit",
            task="100 个分子 5 性质 RDKit 重算 vs 暑假表：0 失败＋差距表＋3 句话规律",
            flow="rows=100 parse_fail=0", preds=[("rows", "==", "100"), ("parse_fail", "==", "0")]),
    4: dict(file="week04_dedup.py", needs="网络+rdkit",
            task="全部分子配标准 SMILES＋InChIKey 并查重；重复处置有规则（优先正式来源）并留清单",
            flow="inchikey_dup=0 rule_written=True", preds=[("inchikey_dup", "==", "0")]),
    7: dict(file="week07_bootstrap.py", needs="numpy(建议服务器)",
            task="bootstrap 反复抽样给考试分数配 95% 可信区间；数据≥1000、考试集≥150、区间较暑假更窄",
            flow="ge1000=True test_ge150=True ci95=True",
            preds=[("ge1000", "==", "True"), ("test_ge150", "==", "True")]),
    8: dict(file="week08_split_ad.py", needs="rdkit+numpy",
            task="新数据重新骨架切分自查零泄漏；陌生结构判定线新旧两版对比如实记",
            flow="leak=0 compared=True", preds=[("leak", "==", "0")]),
    10: dict(file="week10_audit.py", needs="标准库",
             task="全库体检脚本：空值/单位错/极端值/来源分布扫描，问题分级全处置（零未处置）",
             flow="issues={n} unresolved=0", preds=[("unresolved", "==", "0")]),
    12: dict(file="week12_sensitivity.py", needs="标准库",
             task="三个融合权重各±0.05 微调实验：前 10 名变化逐条解释（大变=偏科风险，如实记）",
             flow="combos={n} changes={n} all_explained=True", preds=[("all_explained", "==", "True")]),
}

EXERCISES_DWS = {  # 代维斯丹（数据线B·对接）
    3: dict(file="week03_redock.sh", needs="服务器 Vina/obabel", sh=True,
            task="两蛋白去水加氢＋原配体取重塞回（重对接）：偏移各<2埃，排查过程留痕",
            flow="fxr_rmsd={f} keap1_rmsd={f} both_lt2={bool}", preds=[("both_lt2", "==", "True")]),
    7: dict(file="week07_baselines.py", needs="sklearn",
            task="新数据重跑朴素贝叶斯＋逻辑回归两个参照模型，对照表入库（旧分数列保留，README 同步）",
            flow="nb_auc={f} lr_auc={f} table_updated=True", preds=[("table_updated", "==", "True")]),
    8: dict(file="week08_reliability.py", needs="numpy",
            task="自写一版 ECE/覆盖率重算，与存档对账（浮点误差内一致）＋分箱边界规则写清楚",
            flow="ece_match=True cov_match=True binning_note=True",
            preds=[("ece_match", "==", "True"), ("cov_match", "==", "True")]),
}

EXERCISES_WSM = {  # 王散曼（文献线）
    5: dict(file="week05_llm_assist.md", needs="人工闭环", md=True,
            task="10 条重要文献闭环：大模型出检索词 → PubMed 人核 → 拿 PMID；命中率与编造案例如实记",
            flow="closed=10/10 pmid=10 llm_hit_rate={f}",
            preds=[("closed", "==", "10/10"), ("pmid", "==", "10")]),
}

EXERCISES_BY_MEMBER = {"王启龙": EXERCISES, "宁显泷": EXERCISES_NXL, "衣思淼": EXERCISES_YSM,
                       "代维斯丹": EXERCISES_DWS, "王散曼": EXERCISES_WSM}

SCAFFOLD_TODO_BY_MEMBER = {
    "宁显泷": {
        2: [("build_net", "定义2层小网络(如2-3-1)与小批量输入，权重手动设成简单数"),
            ("hand_grad", "按链式法则在纸上/注释里手算各参数梯度，代码里填入手算值数组"),
            ("auto_grad", "PyTorch autograd 反向传播自动梯度同输入计算"),
            ("compare", "max_delta=两者最大绝对差；lt_1e_6=max_delta<1e-6")],
        3: [("pick_cases", "取5个测试SMILES（含VERIFY_MANUAL §3.1最小用例）"),
            ("to_pyg", "用src/chem/smiles_graph.py产出 → 组装PyG Data(edge_index+13维节点特征)"),
            ("back_numpy", "PyG Data还原numpy邻接与特征"),
            ("verify", "往返逐位比对：match/adj_ok/feat_ok各5/5")],
        4: [("build_adj", "构造小图邻接矩阵A(含自环)与度矩阵D"),
            ("gcn_layer", "numpy实现 H'=D^-0.5·(A+I)·D^-0.5·H·W（对称归一化）"),
            ("formula", "同一公式硬算一遍（循环逐元素）对照"),
            ("check", "shape_ok=输出形状正确；coef_sum=归一化系数和；eq_formula=两版一致")],
        5: [("load_data", "读splits/三表与特征(与暑假口径一致，seed=42)"),
            ("train_gcn", "GCN式(GCNConv或自实现)训练并记录学习曲线"),
            ("train_sum", "求和式(GIN/SumAggregate)同数据训练记录曲线"),
            ("record", "auc_gcn/auc_gin如实打印；curves=2；只记录不下结论")],
        6: [("full_train", "PyG完整复刻暑假训练流程(88条，固定种子)"),
            ("metrics", "AUC/ACC/BACC/F1/ECE/ρ主要项与results/metrics基线对照表"),
            ("gaps", "差距清单：结构/参数/代码三方面各至少1条"),
            ("record", "table_rows/gap_list条目数；recorded=True")],
        8: [("mc_infer", "MC Dropout连答30遍(T=30，与暑假口径一致)收集预测"),
            ("rho", "方差-|误差|Spearman ρ计算"),
            ("figure", "可靠性图(英文标签)存learning/宁显泷/"),
            ("check", "ge_057=ρ>=0.57(暑假0.718八成)；fig_saved=True")],
        9: [("split_val", "验证集划分与已训练模型加载(口径同week08)"),
            ("grid_T", "T∈[0.5,3.0]步长0.1网格搜最小NLL"),
            ("ece_rho", "校准前后ECE+校准后ρ"),
            ("check", "pass_ece=ece_after<0.10；pass_rho=rho>=0.6")],
        10: [("grid", "27组合(隐藏维×层数×dropout等3×3×3)×5折"),
             ("run", "逐组合训练评估(建议服务器)，结果追加CSV"),
             ("summary", "汇总最优组合与各折均值行"),
             ("check", "rows=135(数据行)；summary=1")],
        11: [("load_model", "载入正式版模型与Top-10候选"),
             ("explain", "GNNExplainer(或注意力权重替代)得各原子重要性"),
             ("table", "前10名'最看重原子'表(名称/原子序号/是否季铵氮)"),
             ("note", "direction_note=与旧课题模块G季铵氮结论方向对照说明")],
    },
    "衣思淼": {
        2: [("load_data", "读processed/cleaned_compounds.csv(88)+screening_pool.csv(12)"),
            ("rdkit_recalc", "RDKit重算 MW/LogP/TPSA/HBD/HBA；解析失败计数(预期0)"),
            ("deviation", "各描述符Δ统计表＋3句规律(三萜体重方向等)"),
            ("handoff", "差距结论写进数据字典'已知偏差'节")],
        4: [("fetch", "PUG-REST批量取CanonicalSMILES+InChIKey，status记成功/失败原因"),
            ("dedup", "InChIKey重复检测与处置(优先正式来源，留清单)"),
            ("rule", "去重规则文字化(rule_written)"),
            ("check", "inchikey_dup=0")],
        7: [("bootstrap", "测试指标AUC等B=1000次重抽样95%CI"),
            ("scale_gate", "数据行数与考试集行数门槛判定"),
            ("compare", "CI宽度与暑假版对比"),
            ("check", "ge1000/test_ge150/ci95")],
        8: [("scaffold_split", "新数据骨架分组切分(口径同src/data/split.py,seed=42)"),
            ("leak_audit", "任一骨架跨train/val/test即泄漏，计数leak"),
            ("ad_compare", "陌生结构判定线旧(h*)vs新算法对比表"),
            ("check", "leak=0；compared=True")],
        10: [("scan", "全库逐列扫：空值/单位异常/极端值/来源分布"),
             ("grade", "问题分级：错误/口径说明/笔误"),
             ("dispose", "逐条处置(修或标注)，unresolved计数"),
             ("check", "unresolved=0")],
        12: [("perturb", "三权重0.45/0.35/0.20各±0.05重算final_score"),
             ("rank_shift", "各组合Top-10与基线对比，变化逐条记录"),
             ("explain", "每条变化解释(偏科/域外系数影响)"),
             ("check", "combos/changes条数；all_explained=True")],
    },
    "代维斯丹": {
        3: None,   # bash 脚本：骨架按注释步骤在服务器实现
        7: [("load_new", "读新数据splits(扩库后)与特征管线"),
            ("rerun", "sklearn重跑GNB(描述符)+LR(2048bit指纹)两参照"),
            ("table", "新旧分数同表入库(nb_auc/lr_auc)，README指标表同步"),
            ("check", "table_updated=True")],
        8: [("load_pred", "读results/predictions/test_predictions.csv与mean/var"),
            ("ece", "自写分箱ECE(写清左闭右开边界)与存档0.210对账"),
            ("coverage", "覆盖率曲线重算对账"),
            ("check", "ece_match/cov_match；binning_note=True")],
    },
    "王散曼": {},
}


def exercises(member=None):
    """当前成员（或指定成员）的练习契约表。"""
    return EXERCISES_BY_MEMBER[member or CURRENT_MEMBER]

MILESTONES = [
    dict(id="M1", week=2, name="基线固化 v1.0-summer（45项校验全过+标签）", checks=["C2-01", "C2-02"]),
    dict(id="M3", week=6, name="真实对接排名 v2", checks=["C6-01", "C6-02"]),
    dict(id="M4", week=7, name="数据≥1000条+置信区间（WP3验收签字）", checks=["MAN-W7-01"]),
    dict(id="M5", week=10, name="PyG版+ECE<0.10（WP4验收）", checks=["C10-01", "C8-02", "MAN-W10-01"]),
    dict(id="M6", week=13, name="排名v3一键复现（md5两次一致）", checks=["C13-01", "C13-02"]),
    dict(id="M7", week=15, name="学期重头校验全过（❌清零）", checks=["C15-01", "MAN-W15-01"]),
    dict(id="M8", week=16, name="结题材料提交+预答辩", checks=["C16-01", "C16-02", "MAN-W16-01"]),
    dict(id="M9", week=17, name="结题答辩（2027年1月，现场）", checks=[]),
]

# ---------------------------------------------------------------- 自动核验定义
# kind: file_exists / csv_rows / git_tag / git_commits / text_in_file /
#       run_flow(deep) / verify45(deep) / determinism(deep) / learning_flow /
#       dir_files / glob_min
# target=True 表示"目标态检查"——当前不符属预期（工作未到），输出标注而非报错口径。

CHECKS = [
    # W1
    dict(id="C1-01", week=1, kind="file_exists", target=False,
         desc="仓库骨架文件齐全", source="README 目录结构",
         params={"paths": ["run_all.py", "docs/VERIFY_MANUAL.md", "docs/PHASE_PLAN.md", "src/docking/run_vina.sh", "reports/pdf_build/verify.py"]}),
    dict(id="C1-02", week=1, kind="git_commits", target=False,
         desc="提交数≥12（VERIFY_MANUAL §1 口径）", source="VERIFY_MANUAL §1",
         params={"min": 12}),
    dict(id="C1-03", week=1, kind="csv_rows", target=False,
         desc="数据/排名 CSV 行数与 MANIFEST 基线一致", source="docs/MANIFEST.md §2（2026-08-31实测一致）",
         params={"baselines": CSV_BASELINES}),
    dict(id="C1-04", week=1, kind="learning_flow", target=False,
         desc="W1 学习验证卡：环境自检 env=ok", source="00_environment.md §1/§2",
         params={"week": 1}),
    dict(id="C1-05", week=1, kind="run_flow", target=False, deep=True,
         desc="run_all.py 一键复现：12条关键输出行逐字一致", source="VERIFY_MANUAL §2.1（2026-08-31实测）",
         params={"required": RUN_FLOW_REQUIRED}),
    # W2
    dict(id="C2-01", week=2, kind="git_tag", target=True,
         desc="基线标签 v1.0-summer 存在", source="WP1 步骤3",
         params={"tag": "v1.0-summer"}),
    dict(id="C2-02", week=2, kind="verify45", target=False, deep=True,
         desc="verify.py 45项校验全过", source="reports/pdf_build/verify.py（实测：通过45项；不符0项）",
         params={"expect": VERIFY45_LINE}),
    dict(id="C2-03", week=2, kind="file_exists", target=True,
         desc="results/logs/ 已建（verify截图存档处）", source="WP1 步骤2",
         params={"paths": ["results/logs"]}),
    dict(id="C2-04", week=2, kind="text_in_file", target=True,
         desc="week02_notes.md 断言注释表已成（含45行口径）", source="W2 学习验证卡",
         params={"path": "learning/王启龙/week02_notes.md", "all_of": ["45"]}),
    # W3
    dict(id="C3-01", week=3, kind="learning_flow", target=True,
         desc="W3 学习验证卡：RDKit重算 rows=100 parse_fail=0", source="W3 验证卡；data/processed 存档",
         params={"week": 3}),
    # W4
    dict(id="C4-01", week=4, kind="learning_flow", target=True,
         desc="W4 学习验证卡：PubChem 12条 NV-011命中 inchikey零重复", source="W4 验证卡；raw/novel_terpenes_lignans.csv",
         params={"week": 4}),
    # W5
    dict(id="C5-01", week=5, kind="learning_flow", target=True,
         desc="W5 学习验证卡：重对接自洽 RMSD<2Å", source="WP2 验收第1条（协议标准）",
         params={"week": 5}),
    dict(id="C5-02", week=5, kind="text_in_file", target=False,
         desc="grid_box.py 盒子中心未被手改（两个锚点常量在位）", source="src/docking/grid_box.py:15/23 实测",
         params={"path": "src/docking/grid_box.py", "all_of": GRID_BOX_ANCHORS}),
    # W6
    dict(id="C6-01", week=6, kind="csv_mode", target=True,
         desc="docking_scores.csv 200行且 mode 全部=vina（目标态）", source="WP2 步骤4；现状实测200行/mode=mock_local",
         params={"path": "results/docking/docking_scores.csv", "rows": 200, "mode": "vina"}),
    dict(id="C6-02", week=6, kind="file_exists", target=True,
         desc="src/docking/collect_vina_logs.py 已交付（目标态）", source="WP2 步骤4",
         params={"paths": ["src/docking/collect_vina_logs.py"]}),
    dict(id="C6-03", week=6, kind="csv_rows", target=False,
         desc="排名总表60候选仍在（防误删，基线61行含表头→60数据行）", source="MANIFEST §7；实测2026-08-31",
         params={"baselines": {"results/rankings/final_ranking.csv": 60}}),
    # W7
    dict(id="C7-01", week=7, kind="learning_flow", target=True,
         desc="W7 学习验证卡：PyTorch LR 与基线0.967 差≤0.03", source="results/metrics/baseline.csv",
         params={"week": 7}),
    # W8
    dict(id="C8-01", week=8, kind="learning_flow", target=True,
         desc="W8 学习验证卡：PyG↔numpy 图转换 5/5 逐位一致", source="smiles_graph.py / dataset.py",
         params={"week": 8}),
    dict(id="C8-02", week=8, kind="file_exists", target=True,
         desc="src/models/gnn_torch.py 已交付（目标态）", source="WP4 步骤1",
         params={"paths": ["src/models/gnn_torch.py"]}),
    # W9
    dict(id="C9-01", week=9, kind="learning_flow", target=True,
         desc="W9 学习验证卡：torch版AUC≥numpy下界0.967 且重跑稳定", source="WP4 验收第1条",
         params={"week": 9}),
    # W10
    dict(id="C10-01", week=10, kind="learning_flow", target=True,
         desc="W10 学习验证卡：ECE<0.10 且 ρ≥0.60 双过", source="WP4 验收第2/3条",
         params={"week": 10}),
    # W11
    dict(id="C11-01", week=11, kind="learning_flow", target=True,
         desc="W11 学习验证卡：盒子-配体质心距离双<3Å（或附书面解释）", source="grid_box.py 实测中心；协议<3Å",
         params={"week": 11}),
    # W12
    dict(id="C12-01", week=12, kind="learning_flow", target=True,
         desc="W12 学习验证卡：文献闭环 10/10 附PMID", source="WP5 步骤1 口径",
         params={"week": 12}),
    # W13
    dict(id="C13-01", week=13, kind="text_in_file", target=True,
         desc="week13_notes.md 生成模型笔记已成（≥400字）", source="W13 验证卡",
         params={"path": "learning/王启龙/week13_notes.md", "all_of": ["VAE"], "min_chars": 400}),
    dict(id="C13-02", week=13, kind="determinism", target=True, deep=True,
         desc="排名v3确定性：连跑两次 md5 全一致", source="VERIFY_MANUAL §2.2 范式（hashlib可移植实现）",
         params={}),
    # W14
    dict(id="C14-01", week=14, kind="file_exists", target=True,
         desc="演练报告已入库 learning/王启龙/week14_drill_report.md（目标态）", source="W14 验证卡",
         params={"paths": ["learning/王启龙/week14_drill_report.md"]}),
    # W15
    dict(id="C15-01", week=15, kind="dir_files", target=True,
         desc="verify_semester/outputs/ 六模块复算产物≥6个（目标态）", source="W15 重头校验学期版",
         params={"path": "verify_semester/outputs", "min": 6}),
    # W16
    dict(id="C16-01", week=16, kind="git_tag", target=True,
         desc="结题标签 v2.0-semester 存在（目标态）", source="W14-A3/W16",
         params={"tag": "v2.0-semester"}),
    dict(id="C16-02", week=16, kind="glob_min", target=True,
         desc="reports/ 下已有结题材料（目标态）", source="W16-A1",
         params={"pattern": "reports/*结题*", "min": 1}),
]

# ---------------------------------------------------------------- 通用工具

def dwidth(s):
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))


def pad(s, w):
    s = str(s)
    return s + " " * max(0, w - dwidth(s))


def now_str():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_repo(cli_path=None):
    cands = []
    if cli_path:
        cands.append(Path(cli_path))
    if is_frozen():  # exe 所在目录及其上级（exe 放 tools/ 里时上级即仓库根）
        exe_dir = Path(sys.executable).resolve().parent
        cands += [exe_dir, exe_dir.parent]
    if not is_frozen():
        cands.append(Path(__file__).resolve().parent.parent)  # tools/ 的上级
    d = Path.cwd()
    for _ in range(4):
        cands.append(d)
        d = d.parent
    for c in cands:
        if (c / "run_all.py").exists():
            return c.resolve()
    return None


def sh(cmd, cwd, timeout=300):
    """执行命令，返回 (rc, stdout+stderr)。UTF-8 容错。"""
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, f"命令不存在: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"超时({timeout}s)"


def is_frozen():
    """是否以 PyInstaller exe 方式运行。"""
    return bool(getattr(sys, "frozen", False))


_PY_CACHE = []


def python_exe():
    """深度核验需调用本机 Python。脚本模式=自身；exe 模式从 PATH 找。
    找不到返回 None（调用方据此 SKIP，不谎报通过）。"""
    if not is_frozen():
        return [sys.executable]
    if _PY_CACHE:
        return _PY_CACHE[0]
    found = None
    for cand in (["python"], ["py", "-3"], ["python3"]):
        rc, _ = sh(cand + ["-c", "1"], Path.cwd(), timeout=30)
        if rc == 0:
            found = cand
            break
    _PY_CACHE.append(found)
    return found


def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return Path(path).read_text(encoding=enc)
        except Exception:
            continue
    return ""


def week_of_today():
    d = (dt.date.today() - SEMESTER_START).days // 7 + 1
    return max(0, min(N_WEEKS + 1, d))


# ---------------------------------------------------------------- 状态

def load_state(repo):
    if repo:
        f = repo / state_relpath()
    else:
        base = Path(sys.executable).resolve().parent if is_frozen() else Path(__file__).resolve().parent
        f = base / f"semester_flow_state_{CURRENT_MEMBER}.json"
    if f.exists():
        try:
            return json.loads(read_text(f)), f
        except Exception:
            pass
    return {"done": {}, "records": {}, "notes": {}}, f


def save_state(state, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def record_verdict(state, cid, verdict, observed):
    state["records"][cid] = dict(verdict=verdict, observed=observed, ts=now_str())


def manual_status(state, mid):
    r = state["records"].get(mid)
    return r["verdict"] if r else None


# ---------------------------------------------------------------- 核验引擎

def _pred_ok(preds, flow):
    """按 ('key','cmp','value') 列表判定 [FLOW] 键值。"""
    kv = dict(part.split("=", 1) for part in flow.split() if "=" in part)
    for key, cmp_, val in preds:
        got = kv.get(key)
        if got is None:
            return False, f"缺键 {key}"
        a, b = got.strip(), str(val).strip()
        try:
            fa, fb = float(a), float(b)
            ok = {"==": fa == fb, "!=": fa != fb, "<=": fa <= fb, ">=": fa >= fb,
                  "<": fa < fb, ">": fa > fb}[cmp_]
        except ValueError:
            ok = {"==": a == b, "!=": a != b, "<=": a <= b, ">=": a >= b,
                  "<": a < b, ">": a > b}[cmp_]
        if not ok:
            return False, f"{key}={got} 不满足 {cmp_}{val}"
    return True, ""


def run_check(ck, repo, deep=False):
    """返回 dict(verdict, observed)。verdict: PASS/FAIL/SKIP"""
    k, p = ck["kind"], ck["params"]
    tag = ("【目标态】" if ck.get("target") else "")

    if not repo:
        return dict(verdict="SKIP", observed="未找到仓库（--repo 指定）")

    if ck.get("deep") and not deep:
        return dict(verdict="SKIP", observed="深度核验，加 --deep 执行")

    if k == "file_exists":
        miss = [s for s in p["paths"] if not (repo / s).exists()]
        if miss:
            return dict(verdict="FAIL", observed=f"{tag}缺失: {', '.join(miss)}")
        return dict(verdict="PASS", observed=f"{tag}{len(p['paths'])} 项全部存在")

    if k == "csv_rows":
        bad = []
        for rel, exp in p["baselines"].items():
            f = repo / rel
            if not f.exists():
                bad.append(f"{rel} 不存在")
                continue
            n = sum(1 for _ in read_text(f).splitlines()) - 1
            if n != exp:
                bad.append(f"{rel} 数据行={n} 预期={exp}")
        if bad:
            return dict(verdict="FAIL", observed=f"{tag}" + "; ".join(bad))
        return dict(verdict="PASS", observed=f"{tag}{len(p['baselines'])} 个CSV行数全部与基线一致")

    if k == "csv_mode":
        f = repo / p["path"]
        if not f.exists():
            return dict(verdict="FAIL", observed=f"{tag}{p['path']} 不存在")
        rows = list(csv.DictReader(read_text(f).splitlines()))
        n = len(rows)
        modes = sorted({r.get("mode", "") for r in rows})
        obs = f"{tag}数据行={n}（预期{p['rows']}）mode={modes}（预期全部={p['mode']}）"
        if n == p["rows"] and modes == [p["mode"]]:
            return dict(verdict="PASS", observed=obs)
        return dict(verdict="FAIL", observed=obs)

    if k == "git_tag":
        rc, out = sh(["git", "tag", "-l", p["tag"]], repo)
        if p["tag"] in out:
            return dict(verdict="PASS", observed=f"{tag}标签 {p['tag']} 存在")
        return dict(verdict="FAIL", observed=f"{tag}标签 {p['tag']} 尚未创建（git tag -a {p['tag']}）")

    if k == "git_commits":
        rc, out = sh(["git", "rev-list", "--count", "HEAD"], repo)
        n = out.strip()
        if rc == 0 and n.isdigit() and int(n) >= p["min"]:
            return dict(verdict="PASS", observed=f"提交数={n} ≥ {p['min']}")
        return dict(verdict="FAIL", observed=f"git rev-list 失败/不足: {out.strip()[:80]}")

    if k == "text_in_file":
        f = repo / p["path"]
        if not f.exists():
            return dict(verdict="FAIL", observed=f"{tag}{p['path']} 尚未创建")
        t = read_text(f)
        miss = [s for s in p.get("all_of", []) if s not in t]
        mc = p.get("min_chars", 0)
        if miss:
            return dict(verdict="FAIL", observed=f"{tag}缺少内容: {miss}")
        if len(t.strip()) < mc:
            return dict(verdict="FAIL", observed=f"{tag}正文仅{len(t.strip())}字 < {mc}")
        return dict(verdict="PASS", observed=f"{tag}锚点内容在位" + (f"，{len(t.strip())}字≥{mc}" if mc else ""))

    if k == "run_flow":
        py = python_exe()
        if not py:
            return dict(verdict="SKIP", observed="exe 模式未找到本机 Python：深度核验需装 Python（快速核验不受影响）")
        rc, out = sh(py + ["run_all.py"], repo, timeout=600)
        lines = [ln for ln in out.splitlines() if ln.strip()]
        miss = [req for req in p["required"] if not any(req in ln for ln in lines)]
        if rc == 0 and not miss:
            return dict(verdict="PASS", observed=f"run_all.py 全部{len(p['required'])}条关键行逐字一致（用时见输出）")
        return dict(verdict="FAIL", observed="不一致行: " + " || ".join(miss[:3]) + ("" if len(miss) <= 3 else f" 等{len(miss)}条") + f"；rc={rc}")

    if k == "verify45":
        py = python_exe()
        if not py:
            return dict(verdict="SKIP", observed="exe 模式未找到本机 Python：深度核验需装 Python（快速核验不受影响）")
        rc, out = sh(py + ["reports/pdf_build/verify.py"], repo, timeout=300)
        if rc == 0 and p["expect"] in out:
            return dict(verdict="PASS", observed=f"verify.py 输出『{p['expect']}』")
        tail = [ln for ln in out.splitlines() if "项" in ln][-3:]
        return dict(verdict="FAIL", observed=f"rc={rc}；输出末行: {' / '.join(tail) or '无输出'}")

    if k == "determinism":
        def md5_all():
            h = []
            for sub in ("results", "data/processed", "data/splits"):
                d = repo / sub
                if not d.exists():
                    continue
                for f in sorted(d.rglob("*.csv")):
                    h.append((str(f.relative_to(repo)), hashlib.md5(f.read_bytes()).hexdigest()))
            return h
        py = python_exe()
        if not py:
            return dict(verdict="SKIP", observed="exe 模式未找到本机 Python：深度核验需装 Python（快速核验不受影响）")
        rc, _ = sh(py + ["run_all.py"], repo, timeout=600)
        if rc != 0:
            return dict(verdict="FAIL", observed="第1次 run_all.py 失败")
        h1 = md5_all()
        rc, _ = sh(py + ["run_all.py"], repo, timeout=600)
        if rc != 0:
            return dict(verdict="FAIL", observed="第2次 run_all.py 失败")
        h2 = md5_all()
        if h1 == h2:
            return dict(verdict="PASS", observed=f"{tag}两次运行 {len(h1)} 个CSV md5 全一致")
        diff = [a for a, b in zip(h1, h2) if a != b][:3]
        return dict(verdict="FAIL", observed=f"{tag}不一致文件: {diff}")

    if k == "learning_flow":
        ex = exercises()[p["week"]]
        f = repo / "learning" / CURRENT_MEMBER / ex["file"]
        if not f.exists():
            return dict(verdict="FAIL", observed=f"{tag}练习未创建：learning/{CURRENT_MEMBER}/{ex['file']}（可先 scaffold {p['week']} 生成骨架）")
        if ex.get("md"):
            # 笔记类：文本内找 [FLOW] 行
            m = re.search(r"\[FLOW\]\s*(.+)", read_text(f))
            if not m:
                if ex.get("min_chars"):
                    return dict(verdict="FAIL", observed=f"{tag}笔记无 [FLOW] 闭环行且字数校验另见 C13-01；请在文末手填 [FLOW] 契约行")
                return dict(verdict="FAIL", observed=f"{tag}笔记缺 [FLOW] 契约行（文末手填）")
            ok, why = _pred_ok(ex["preds"], m.group(1))
            return dict(verdict="PASS" if ok else "FAIL", observed=f"{tag}[FLOW] {m.group(1)}" + ("" if ok else f" → {why}"))
        if ex.get("sh"):
            # bash 脚本类（服务器练习）：本机有 bash 就跑，没有则 SKIP 提示 record 补录
            rc, out = sh(["bash", str(f)], cwd=repo, timeout=1800)
            if rc == 127 or "命令不存在" in out:
                return dict(verdict="SKIP", observed=f"{tag}本机无 bash（Windows）：到服务器跑通后 record {p['id']} pass '服务器实测值'")
            m = re.search(r"\[FLOW\]\s*(.+)", out)
            if rc != 0 or not m:
                tail = " | ".join(out.strip().splitlines()[-3:])[:200]
                return dict(verdict="FAIL", observed=f"{tag}练习未完成或未输出契约行（rc={rc}）: {tail}")
            ok, why = _pred_ok(ex["preds"], m.group(1))
            return dict(verdict="PASS" if ok else "FAIL", observed=f"{tag}[FLOW] {m.group(1)}" + ("" if ok else f" → {why}"))
        py = python_exe()
        if not py:
            return dict(verdict="SKIP", observed="exe 模式未找到本机 Python：练习需 Python 运行（快速核验不受影响）")
        rc, out = sh(py + [str(f)], cwd=repo, timeout=900)
        m = re.search(r"\[FLOW\]\s*(.+)", out)
        if "ModuleNotFoundError" in out or "ImportError" in out:
            return dict(verdict="SKIP", observed=f"{tag}本地缺依赖（{ex['needs']}）→ 到服务器跑通后：record {p['id']} pass '服务器实测值'")
        if rc != 0 or not m:
            tail = " | ".join(out.strip().splitlines()[-3:])[:200]
            return dict(verdict="FAIL", observed=f"{tag}练习未完成或未输出契约行（rc={rc}）: {tail}")
        ok, why = _pred_ok(ex["preds"], m.group(1))
        return dict(verdict="PASS" if ok else "FAIL", observed=f"{tag}[FLOW] {m.group(1)}" + ("" if ok else f" → {why}"))

    if k == "dir_files":
        d = repo / p["path"]
        if d.exists() and len(list(d.iterdir())) >= p["min"]:
            return dict(verdict="PASS", observed=f"{tag}{p['path']} 已有 {len(list(d.iterdir()))} 个产物 ≥ {p['min']}")
        n = len(list(d.iterdir())) if d.exists() else 0
        return dict(verdict="FAIL", observed=f"{tag}{p['path']} 产物 {n} < {p['min']}（六模块复算未完成）")

    if k == "glob_min":
        g = list(repo.glob(p["pattern"]))
        if len(g) >= p["min"]:
            return dict(verdict="PASS", observed=f"{tag}{p['pattern']} 命中 {len(g)}")
        return dict(verdict="FAIL", observed=f"{tag}{p['pattern']} 命中 {len(g)} < {p['min']}")

    return dict(verdict="SKIP", observed=f"未知检查类型 {k}")


def flow_id(week):
    return f"C{week}-01"


VERDICT_TAG = {"PASS": "[通过]", "FAIL": "[不符]", "SKIP": "[跳过]"}


def member_check_defs(member):
    """成员模式的检查集：只含各自练习的 [FLOW] 判定（编号与打卡页检查项同前缀）。
    项目任务/文件核验在成员打卡页与 docs/VERIFY_TASKS.md，不在本工具重复。"""
    pfx = MEMBER_PREFIX[member]
    return [dict(id=f"{pfx}-C{w}-01", week=w, kind="learning_flow", target=True,
                 desc=f"W{w} 学习练习 {exercises(member)[w]['file']}",
                 source="成员打卡页·本周自动检查（过关标准与页面一致）",
                 params={"week": w}) for w in sorted(exercises(member))]


def eval_checks(repo, weeks=None, deep=False, state=None):
    out = []
    pool = CHECKS if CURRENT_MEMBER == "王启龙" else member_check_defs(CURRENT_MEMBER)
    for ck in pool:
        if weeks and ck["week"] not in weeks:
            continue
        r = run_check(ck, repo, deep=deep)
        r.update(id=ck["id"], week=ck["week"], desc=ck["desc"], source=ck["source"], target=ck.get("target", False))
        out.append(r)
        if state is not None and r["verdict"] != "SKIP":
            record_verdict(state, ck["id"], r["verdict"], r["observed"])
    return out


def print_check_results(results):
    cur = None
    npass = nfail = nskip = 0
    for r in results:
        if r["week"] != cur:
            cur = r["week"]
            print(f"\n—— 第 {cur} 周 ——")
        print(f"  {VERDICT_TAG[r['verdict']]} {r['id']} {r['desc']}")
        print(f"        实测: {r['observed']}")
        print(f"        依据: {r['source']}")
        npass += r["verdict"] == "PASS"
        nfail += r["verdict"] == "FAIL"
        nskip += r["verdict"] == "SKIP"
    print(f"\n合计: 通过 {npass} / 不符 {nfail} / 跳过 {nskip}")
    if nfail:
        print("口径说明: 标注【目标态】的不符=该周工作未到期/未完成，属预期推进状态，非数据错误。")
    return 1 if nfail else 0

# ---------------------------------------------------------------- 骨架生成

def gen_scaffold(week, repo):
    ex = exercises().get(week)
    if not ex:
        print(f"第 {week} 周无练习骨架（该周为文档/工程类任务）")
        return
    w = WEEKS[week - 1]
    task_txt = ex.get("task") or w["card"]["task"]
    f = repo / "learning" / CURRENT_MEMBER / ex["file"]
    if f.exists():
        print(f"已存在: {f}（如需重新生成请先删除）")
        return
    f.parent.mkdir(parents=True, exist_ok=True)
    member_cmd = "" if CURRENT_MEMBER == "王启龙" else f" --member {CURRENT_MEMBER}"

    if CURRENT_MEMBER == "王启龙" and week == 1:  # W1 骨架即完整可用实现
        code = '''# -*- coding: utf-8 -*-
# W1 学习验证卡 · 环境自检（本骨架开箱即用，本地与服务器各跑一遍）
# 预期: [FLOW] env=ok ... 零 ImportError（来源: docs/00_environment.md §1/§2）
import sys
def v(mod):
    try:
        m = __import__(mod); return getattr(m, "__version__", "ok")
    except Exception:
        return "MISSING"
mods = dict(numpy="numpy", rdkit="rdkit", torch="torch",
            pyg="torch_geometric", vina="vina")
vers = {k: v(m) for k, m in mods.items()}
env_ok = "ok" if vers["numpy"] != "MISSING" else "MISSING"
print("[FLOW] env=" + env_ok + " python=" + sys.version.split()[0] +
      " numpy=" + str(vers["numpy"]) +
      " rdkit=" + ("ok" if vers["rdkit"] != "MISSING" else "MISSING") +
      " torch=" + ("ok" if vers["torch"] != "MISSING" else "MISSING") +
      " pyg=" + ("ok" if vers["pyg"] != "MISSING" else "MISSING") +
      " vina=" + ("ok" if vers["vina"] != "MISSING" else "MISSING"))
'''
        f.write_text(code, encoding="utf-8")
    elif ex.get("sh"):
        code = f'''#!/usr/bin/env bash
# 第 {week} 周 学习练习骨架 · 由 semester_flow.py scaffold {week} 生成（{CURRENT_MEMBER}）
# 任务: {task_txt}
# 预期契约: [FLOW] {ex['flow']}
#           判定: {ex['preds']}
# 依赖: {ex['needs']}（服务器运行；跑通后本机可 check {week} 或 record 补录）
# 完成后核验: python tools/semester_flow.py{member_cmd} check {week}
set -euo pipefail
# TODO 1: 两个蛋白结构处理（去水、加氢、转 pdbqt）——盒子中心用 src/docking/grid_box.py，勿手改
# TODO 2: 抽出 1OSH / 2FLU 各自的原配体（保留原始坐标作参照）
# TODO 3: Vina 重对接（同盒子同种子，exh=16）
# TODO 4: 对接口袋构象 vs 原配体 计算 RMSD（fxr_rmsd / keap1_rmsd）
# TODO 5: both_lt2=两个 RMSD 都 <2 才为 True；≥2 按 WP2 排查清单记录过程
echo "[FLOW] 未完成：先实现上方 TODO（实测值禁止手填）"; exit 1
# 实现后把上一行替换为:
# echo "[FLOW] fxr_rmsd=<实测> keap1_rmsd=<实测> both_lt2=<True|False>"
'''
        f.write_text(code, encoding="utf-8")
    elif ex.get("md"):
        body = f"# 第 {week} 周 · {task_txt}\n\n（成员：{CURRENT_MEMBER}｜生成：scaffold {week}）\n\n"
        if (CURRENT_MEMBER == "王启龙" and week == 2):
            body += ("verify.py 的 45 项检查注释表：每项断言对应哪个文件、对的是什么数字。\n\n"
                     "| # | 断言内容 | 对的文件 | 对的数字 |\n|---|---|---|---|\n" +
                     "| 1 | | | |\n" * 45 +
                     "\n凑满 45 行后本练习即完成（C2-04 核验『week02_notes.md 里有 45 行』）。\n")
        elif (CURRENT_MEMBER == "王启龙" and week == 14):
            body += ("第三方空白环境复现演练报告（W14 学习检查）。\n\n"
                     "- 演练人／时间／机器：\n- 只给手册，能否 30 分钟内复现排名 v3：\n"
                     "- 总耗时（如实）：\n\n## 卡点清单\n\n| # | 卡在哪一步 | 原因 | 当天修了吗 |\n|---|---|---|---|\n| 1 | | | |\n\n"
                     "## 修复状态与结论\n\n（有没修完的卡点就不算过；全程计时记录）\n")
        elif ex["flow"] and "closed=" in (ex["flow"] or ""):
            body += ("| 条目 | 原文关键句 | LLM检索式 | PubMed命中 | 最终PMID/处置 |\n|---|---|---|---|---|\n"
                     "| 1 | | | | |\n" * 10 +
                     "\nLLM命中率/人工修正率（如实记录）: \nLLM幻觉案例（答辩素材）: \n\n"
                     "完成10条闭环后，把下面契约行的 {f} 改为实测值：\n[FLOW] " + ex["flow"] + "\n")
        else:
            body += ("要点（三类模型各一句原理：RNN / VAE / 扩散）：\n\n\n"
                     "对本课题候选扩充的潜在用法：\n\n\n（400–600字）\n")
        f.write_text(body, encoding="utf-8")
    else:
        todos = (SCAFFOLD_TODO_BY_MEMBER.get(CURRENT_MEMBER, {}).get(week)
                 or SCAFFOLD_TODO.get(week, []))
        keys = [p[0] for p in ex["preds"]] or ["done"]
        funcs = "\n".join(
            f"def {name}():\n    \"\"\"TODO {i+1}: {doc}\"\"\"\n    raise NotImplementedError(\"TODO: 按验证卡实现\")\n"
            for i, (name, doc) in enumerate(todos)) or \
            f"def compute():\n    \"\"\"TODO: {task_txt}\"\"\"\n    raise NotImplementedError(\"TODO: 按验证卡实现\")\n"
        code = f'''# -*- coding: utf-8 -*-
# 第 {week} 周 学习练习骨架 · 由 semester_flow.py scaffold {week} 生成（{CURRENT_MEMBER}）
# 任务: {task_txt}
# 预期契约: [FLOW] {ex['flow']}
#           判定: {ex['preds']}   过关标准与打卡页一致
# 依赖: {ex['needs']}（本地缺依赖时到服务器跑，再 record 补录）
# 完成后核验: python tools/semester_flow.py{member_cmd} check {week}
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]  # learning/{CURRENT_MEMBER}/ → 仓库根

{funcs}

def main():
    # TODO: 调用上方函数得到下列键的实测值后打印契约行（禁止手填未实测的值）
    vals = {{}}
    keys = {keys}
    missing = [k for k in keys if k not in vals]
    if missing:
        raise SystemExit(f"未完成: 缺 {{missing}}（先实现 TODO 再输出契约）")
    print("[FLOW] " + " ".join(f"{{k}}={{vals[k]}}" for k in keys))

if __name__ == "__main__":
    main()
'''
        f.write_text(code, encoding="utf-8")
    print(f"已生成: {f}")
    print(f"下一步: 按文件内 TODO 实现 → 运行它 → python tools/semester_flow.py{member_cmd} check {week}")

# ---------------------------------------------------------------- 输出视图

def show_week(w, state, repo):
    print("═" * 66)
    print(f"第 {w['no']} 周（{w['dates']}）· {w['theme']}")
    print(f"学习线: {w['stage']}")
    print("─" * 66)
    print("【AIDD 学习】")
    for t in w["learn"]:
        print("  · " + t)
    print("【学习验证卡】")
    c = w["card"]
    print(f"  任务: {c['task']}")
    print(f"  命令: {c['cmd']}")
    print(f"  预期: {c['expected']}")
    print(f"  依据: {c['source']}")
    print(f"  口径: {c['criteria']}")
    print(f"  核验人: {c['verifier']}")
    print("【项目推进】")
    for tid, text in w["tasks"]:
        mark = "✓" if state["done"].get(tid) else " "
        print(f"  [{mark}] {tid}  {text}")
    for m in MANUALS:
        if m["week"] == w["no"]:
            st = manual_status(state, m["id"])
            mark = "✓" if st == "pass" else " "
            dead = f"（截止 {m['dead']}）" if m["dead"] else ""
            print(f"  [{mark}] {m['id']}  {m['text']}{dead}" + ("" if st != "fail" else "  ⚠已记录不符"))
    print("【负责人统筹】")
    for t in w["coord"]:
        print("  · " + t)
    ex = exercises().get(w["no"])
    if ex:
        f = repo / "learning" / CURRENT_MEMBER / ex["file"] if repo else None
        exists = f.exists() if f else False
        hint = "已存在" if exists else f"未创建（先运行 scaffold {w['no']} 生成）"
        print(f"【练习文件】learning/{CURRENT_MEMBER}/{ex['file']}  {hint}")
    print("═" * 66)


def dashboard(repo, state):
    wn = week_of_today()
    if wn == 0:
        days = (SEMESTER_START - dt.date.today()).days
        print(f"今天 {dt.date.today()} · 距开学（{SEMESTER_START} 周一）还有 {days} 天 → 先看第 1 周卡片预热")
        show_week(WEEKS[0], state, repo)
        return
    if wn > N_WEEKS:
        print(f"学期 16 周已结束（当前第 {wn} 周段=结题/考试周）→ 看第 16 周")
        show_week(WEEKS[-1], state, repo)
        return
    w = WEEKS[wn - 1]
    print(f"今天 {dt.date.today()} → 学期第 {wn} 周")
    show_week(w, state, repo)
    # 本周快速核验
    res = eval_checks(repo, weeks={wn}, deep=False)
    res = [r for r in res if not r["verdict"] == "SKIP" or True]
    print("本周快速核验（深度项加 --deep）:")
    for r in res:
        print(f"  {VERDICT_TAG[r['verdict']]} {r['id']} {r['desc']} → {r['observed'][:90]}")


def cmd_plan(state):
    print("═" * 72)
    print(f"学期推进总览（{SEMESTER_START} 开学 · 16 周 · 负责人 王启龙）")
    print("═" * 72)
    print(pad("周", 4) + pad("日期", 15) + pad("学习线", 22) + pad("主题", 24) + "任务完成")
    for w in WEEKS:
        done = sum(1 for t, _ in w["tasks"] if state["done"].get(t))
        total = len(w["tasks"]) + sum(1 for m in MANUALS if m["week"] == w["no"])
        done += sum(1 for m in MANUALS if m["week"] == w["no"] and manual_status(state, m["id"]) == "pass")
        print(pad(w["no"], 4) + pad(w["dates"], 15) + pad(w["stage"], 22) + pad(w["theme"], 24) + f"{done}/{total}")
    print("─" * 72)
    print("里程碑:")
    for m in MILESTONES:
        print(f"  {m['id']} W{m['week']:>2} {m['name']} → 依赖 {m['checks'] if m['checks'] else '现场/外部'}")


def cmd_milestones(repo, state, deep=False):
    print("里程碑状态（自动项即时核验，手工项看 record 记录）:")
    alldone = True
    for m in MILESTONES:
        parts = []
        ok_all = True
        for cid in m["checks"]:
            if cid.startswith("MAN-"):
                st = manual_status(state, cid)
                v = "pass" if st == "pass" else ("fail" if st == "fail" else "待办")
                if v != "pass":
                    ok_all = False
            else:
                ck = next(c for c in CHECKS if c["id"] == cid)
                r = run_check(ck, repo, deep=deep)
                if r["verdict"] != "PASS":
                    ok_all = False
                v = r["verdict"]
            parts.append(f"{cid}:{v}")
        mark = "✓" if ok_all else "…"
        if not ok_all:
            alldone = False
        print(f"  [{mark}] {m['id']} W{m['week']:>2} {m['name']}")
        if parts:
            print(f"        {'; '.join(parts)}")
    print("全部达成" if alldone else "（…=进行中/待到期，目标态项到期后自然转绿）")


def cmd_next(repo, state):
    wn = max(1, min(N_WEEKS, week_of_today()))
    w = WEEKS[wn - 1]
    for tid, text in w["tasks"]:
        if not state["done"].get(tid):
            print(f"下一步（本周第 {wn} 周）: [{tid}] {text}")
            print(f"  完成后: python tools/semester_flow.py done {tid}")
            return
    for m in MANUALS:
        if m["week"] == wn and manual_status(state, m["id"]) is None:
            print(f"下一步（本周手工项）: [{m['id']}] {m['text']}")
            print(f"  完成后: python tools/semester_flow.py record {m['id']} pass '实测/证据说明'")
            return
    print(f"第 {wn} 周任务全部勾选 ✓ → 运行 check {wn} 核验，然后看第 {min(wn + 1, N_WEEKS)} 周")


def cmd_ledger(repo, state, sync=False):
    print("═" * 88)
    print("学习验证台账（机器核验记录 + 手工补录）")
    print("═" * 88)
    rows = []
    for wk in WEEKS:
        ex = exercises().get(wk["no"])
        if ex:
            f = repo / "learning" / CURRENT_MEMBER / ex["file"] if repo else None
            if f and f.exists():
                t = read_text(f)
                m = re.search(r"\[FLOW\]\s*(.+)", t)
                rows.append((wk["no"], ex["file"], m.group(1) if m else "（无契约行）"))
            else:
                rows.append((wk["no"], ex["file"], "未创建"))
    if rows:
        print(pad("周", 4) + pad("练习", 34) + "最近 [FLOW] 契约输出")
        for r in rows:
            print(pad(r[0], 4) + pad(r[1], 34) + r[2][:60])
    print("─" * 88)
    if state["records"]:
        print(pad("项", 12) + pad("判定", 6) + pad("时间", 20) + "实测")
        for cid, r in sorted(state["records"].items()):
            print(pad(cid, 12) + pad(r["verdict"], 6) + pad(r["ts"][:16], 20) + r["observed"][:70])
    else:
        print("（暂无核验记录，先运行 check）")
    if sync and repo:
        p = repo / ledger_relpath()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(f"\n## 台账同步 {now_str()}\n")
            for cid, r in sorted(state["records"].items()):
                fh.write(f"- {cid} | {r['verdict']} | {r['ts']} | {r['observed']}\n")
        print(f"已追加同步到 {p}")


def cmd_report(week_no, repo, state):
    p = repo / "learning" / CURRENT_MEMBER / f"周报_第{week_no}周_{dt.date.today():%Y%m%d}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    if CURRENT_MEMBER != "王启龙":
        # 成员版周报：练习状态 + 勾选/补录记录（16 周卡片内容以打卡_姓名.html 为准）
        ex = exercises().get(week_no)
        f = repo / "learning" / CURRENT_MEMBER / ex["file"] if ex else None
        flow_now = ""
        if f and f.exists():
            m = re.search(r"\[FLOW\]\s*(.+)", read_text(f))
            flow_now = m.group(1) if m else "（无契约行）"
        with p.open("w", encoding="utf-8") as fh:
            fh.write(f"# 周报 · 第 {week_no} 周 · {CURRENT_MEMBER}（{MEMBER_ROLE[CURRENT_MEMBER]}）\n\n")
            fh.write(f"生成: semester_flow.py v{TOOL_VERSION} --member {CURRENT_MEMBER} · {now_str()}\n\n")
            fh.write("## 本周学习练习\n\n")
            if ex:
                fh.write(f"- 文件: learning/{CURRENT_MEMBER}/{ex['file']}\n- 任务: {ex.get('task', '')}\n")
                fh.write(f"- 过关契约: [FLOW] {ex['flow']}\n- 当前状态: {'已创建' if f and f.exists() else '未创建（scaffold 生成）'}｜{flow_now or '未实现'}\n")
            else:
                fh.write("- 本周无代码练习（按打卡_姓名.html 周卡片执行）\n")
            fh.write("\n## 已勾选任务（done）\n\n")
            for k, v in sorted(state.get("done", {}).items()):
                fh.write(f"- [x] {k}（{v[:16]}）\n")
            fh.write("\n## 核验/补录记录（check/record）\n\n")
            for cid, r in sorted(state.get("records", {}).items()):
                fh.write(f"- {r['verdict']} {cid}｜{r['ts'][:16]}｜{r['observed']}\n")
            fh.write("\n（完整周卡片任务/视频/检查项见本人打卡_姓名.html；数字锚定仓库存档文件）\n")
        print(f"周报已生成: {p}")
        return
    w = WEEKS[week_no - 1]
    res = eval_checks(repo, weeks={week_no}, deep=False, state=state)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        fh.write(f"# 周报 · 第 {week_no} 周（{w['dates']}）· {w['theme']}\n\n")
        fh.write(f"生成: semester_flow.py v{TOOL_VERSION} · {now_str()}\n\n## 任务完成情况\n\n")
        for tid, text in w["tasks"]:
            fh.write(f"- [{'x' if state['done'].get(tid) else ' '}] {tid} {text}\n")
        for m in MANUALS:
            if m["week"] == week_no:
                st = manual_status(state, m["id"]) or "待办"
                fh.write(f"- [{ 'x' if st=='pass' else ' '}] {m['id']} {m['text']} → {st}\n")
        fh.write("\n## 学习验证卡\n\n")
        c = w["card"]
        for k in ("task", "cmd", "expected", "source", "criteria", "verifier"):
            fh.write(f"- **{k}**: {c[k]}\n")
        fh.write("\n## 自动核验结果\n\n")
        for r in res:
            fh.write(f"- {VERDICT_TAG[r['verdict']]} {r['id']} {r['desc']}｜实测: {r['observed']}｜依据: {r['source']}\n")
        fh.write("\n## 下周预告\n\n")
        if week_no < N_WEEKS:
            n = WEEKS[week_no]
            fh.write(f"- 第 {n['no']} 周（{n['dates']}）: {n['theme']}（{n['stage']}）\n")
            for t in n["tasks"][:3]:
                fh.write(f"  - {t[0]} {t[1]}\n")
        fh.write("\n（数字均锚定仓库存档文件，证据路径见上）\n")
    print(f"周报已生成: {p}")

# ---------------------------------------------------------------- main

def member_dashboard(repo, state):
    print("═" * 66)
    print(f"成员模式 · {CURRENT_MEMBER}（{MEMBER_ROLE[CURRENT_MEMBER]}）")
    print(f"状态文件: learning/{CURRENT_MEMBER}/flow_state.json")
    print("─" * 66)
    print("16 周卡片/任务/视频/打卡 → 你的 打卡_姓名.html（克隆仓库后本地浏览器打开）")
    print("本工具管：练习骨架 scaffold N ｜ 练习核验 check N ｜ 勾选 done/undo")
    print("          ｜ 手工补录 record ｜ 台账 ledger ｜ 周报 report N")
    print("═" * 66)
    print(pad("周", 4) + pad("练习文件", 34) + "状态")
    for wk in sorted(exercises()):
        ex = exercises()[wk]
        f = repo / "learning" / CURRENT_MEMBER / ex["file"] if repo else None
        st = "已创建" if (f and f.exists()) else f"未创建（scaffold {wk} 生成）"
        print(pad(wk, 4) + pad(ex["file"], 34) + st)
    print("─" * 66)
    print(f"已勾选 {len(state.get('done', {}))} 项 ｜ 核验/补录 {len(state.get('records', {}))} 条")
    print("本周练习核验: check <周号>（all = 全部练习周；过关标准与打卡页一致）")


def main():
    global CURRENT_MEMBER
    ap = argparse.ArgumentParser(prog="semester_flow.py",
                                 description="学期学习推进流工具（全员版）——负责人三线合一；成员用 --member 姓名")
    ap.add_argument("--repo", default=None, help="仓库路径（默认自动探测）")
    ap.add_argument("--member", default="王启龙", choices=MEMBERS,
                    help="成员名（默认王启龙=负责人完整版；成员版=各自练习契约/状态/周报）")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("plan", help="学期总览+里程碑清单")
    sub.add_parser("milestones", help="里程碑达成状态")
    sub.add_parser("next", help="下一个该做的事")
    sub.add_parser("ledger", help="学习验证台账").add_argument("--sync", action="store_true", help="同步写入 VERIFY_LEDGER.md")

    p_week = sub.add_parser("week", help="查看某周完整卡片")
    p_week.add_argument("n", type=int)

    p_check = sub.add_parser("check", help="自动核验（真实执行命令比对基线）")
    p_check.add_argument("n", nargs="?", default=None, help="周号或 all（默认本周）")
    p_check.add_argument("--deep", action="store_true", help="深度核验（run_all.py/verify.py/确定性重跑）")

    p_scaf = sub.add_parser("scaffold", help="生成某周练习骨架（含[FLOW]契约）")
    p_scaf.add_argument("n", type=int)

    p_done = sub.add_parser("done", help="勾选任务完成")
    p_done.add_argument("id")
    p_undo = sub.add_parser("undo", help="取消勾选")
    p_undo.add_argument("id")

    p_rec = sub.add_parser("record", help="手工补录核验结果（外部平台/服务器实测）")
    p_rec.add_argument("id")
    p_rec.add_argument("verdict", choices=["pass", "fail"])
    p_rec.add_argument("observed", help="实测/证据说明（引号包裹）")

    p_rep = sub.add_parser("report", help="生成周报md")
    p_rep.add_argument("n", nargs="?", type=int, default=None)

    args = ap.parse_args()
    CURRENT_MEMBER = args.member
    repo = find_repo(args.repo)
    state, sfile = load_state(repo)

    is_member = CURRENT_MEMBER != "王启龙"
    if repo is None and args.cmd not in ("plan",):
        print("⚠ 未找到仓库根（run_all.py）。学习卡/台账可用，自动核验将跳过。用 --repo 指定。")
        print(f"⚠ 无仓库时状态将写到本工具旁 semester_flow_state_{CURRENT_MEMBER}.json（不进 git，进度与仓库脱钩）")
    else:
        print(f"仓库: {repo}" + (f" ｜ 成员: {CURRENT_MEMBER}（{MEMBER_ROLE[CURRENT_MEMBER]}）" if is_member else ""))

    cmd = args.cmd or "dashboard"

    if cmd == "dashboard":
        member_dashboard(repo, state) if is_member else dashboard(repo, state)
    elif cmd == "plan":
        member_dashboard(repo, state) if is_member else cmd_plan(state)
    elif cmd == "week":
        if not (1 <= args.n <= N_WEEKS):
            sys.exit(f"周号 1–{N_WEEKS}")
        if is_member:
            ex = exercises().get(args.n)
            if not ex:
                sys.exit(f"第 {args.n} 周无成员练习（16 周完整卡片见你的 打卡_姓名.html）")
            print(f"第 {args.n} 周练习 · learning/{CURRENT_MEMBER}/{ex['file']}")
            print(f"任务: {ex.get('task', '')}")
            print(f"契约: [FLOW] {ex['flow']}")
            print(f"判定: {ex['preds']} ｜ 依赖: {ex['needs']}")
            f = repo / "learning" / CURRENT_MEMBER / ex["file"] if repo else None
            print("状态:", "已创建" if (f and f.exists()) else f"未创建（先 scaffold {args.n} 生成）")
        else:
            show_week(WEEKS[args.n - 1], state, repo)
    elif cmd == "next":
        member_dashboard(repo, state) if is_member else cmd_next(repo, state)
    elif cmd == "milestones":
        member_dashboard(repo, state) if is_member else cmd_milestones(repo, state)
    elif cmd == "check":
        if is_member:
            print("成员模式：只核验你的学习练习 [FLOW] 契约（项目任务/文件核验按打卡_姓名.html 与 VERIFY_TASKS 执行）")
        if args.n is None:
            weeks = {max(1, min(N_WEEKS, week_of_today()))}
        elif args.n == "all":
            weeks = set(range(1, N_WEEKS + 1))
        else:
            try:
                weeks = {int(args.n)}
            except ValueError:
                sys.exit("周号须为 1–16 或 all")
        res = eval_checks(repo, weeks=weeks, deep=args.deep, state=state)
        save_state(state, sfile)
        sys.exit(print_check_results(res))
    elif cmd == "scaffold":
        if not repo:
            sys.exit("需要仓库路径")
        if not (1 <= args.n <= N_WEEKS):
            sys.exit(f"周号 1–{N_WEEKS}")
        gen_scaffold(args.n, repo)
    elif cmd == "done":
        if is_member:
            print("（成员模式：任务号按你打卡页上的编号勾选，如 W2-A1 / N1 / Y3）")
        else:
            valid = {t for w in WEEKS for t, _ in w["tasks"]} | {m["id"] for m in MANUALS}
            if args.id not in valid:
                sys.exit(f"未知任务号。可用示例: {sorted(valid)[:6]} ...")
        state["done"][args.id] = now_str()
        save_state(state, sfile)
        print(f"✓ 已勾选 {args.id}（{CURRENT_MEMBER}）")
    elif cmd == "undo":
        state["done"].pop(args.id, None)
        state["records"].pop(args.id, None)
        save_state(state, sfile)
        print(f"↺ 已取消 {args.id}")
    elif cmd == "record":
        if not is_member:
            valid = {m["id"] for m in MANUALS} | {c["id"] for c in CHECKS}
            if args.id not in valid:
                sys.exit(f"未知编号 {args.id}（手工项 MAN-* / 检查项 C*）")
        record_verdict(state, args.id, args.verdict, args.observed)
        save_state(state, sfile)
        print(f"✓ 已记录 {args.id} = {args.verdict}：{args.observed}")
    elif cmd == "ledger":
        cmd_ledger(repo, state, sync=args.sync)
    elif cmd == "report":
        n = args.n or max(1, min(N_WEEKS, week_of_today()))
        cmd_report(n, repo, state)
        print("（如需附深度核验结果，先运行 check --deep 再 report）")

    if is_frozen() and len(sys.argv) == 1:
        try:
            input("\n（打包版直接运行：看完板后回车退出。日常请用 python tools/semester_flow.py "
                  "[--member 姓名] 子命令；成员用法如：python tools/semester_flow.py --member 宁显泷）")
        except EOFError:
            pass


if __name__ == "__main__":
    main()
