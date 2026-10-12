# -*- coding: utf-8 -*-
"""把 research_chain_v2_20260921 计划数据同步进五份打卡页与工作台（2026-09-22，按负责人五点要求修订版）。

负责人要求：
1. 不出现"周五组会"——周验收一律改为"周日进度汇总"。
2. 全中文。
3. 不出现"导师"字样——涉及审批处只写"负责人"。
4. 专注本周（W3）进度，任务落到具体文件。
5. 每点写清：目标、注意事项、推荐工具、操作流程，描述简洁。

原则不变：界面结构、DOM id、localStorage 键、W1/W2 历史卡与已有勾选数据全部不动；
W3–W16 任务取自 v2 计划数据.json；自报打卡不构成可信人审，不改变任何 Gate。
历史重放必须显式运行：python tools/sync_v2_to_pages.py --legacy-v2
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = Path(r"D:\zcode-workspace\aidd-repo-work\00-当前研究\research_chain_v2_20260921\计划数据.json")

D = ["09/07–09/13","09/14–09/20","09/21–09/27","09/28–10/04","10/05–10/11","10/12–10/18",
     "10/19–10/25","10/26–11/01","11/02–11/08","11/09–11/15","11/16–11/22","11/23–11/29",
     "11/30–12/06","12/07–12/13","12/14–12/20","12/21–12/27"]

HOURS_MEMBER = "每周约 4 小时（任务约 2.5h＋学习约 1.5h）；按真实可用工时如实记录，不足写原因"
HOURS_MEMBER_LIGHT = "轻量周约 2–3 小时（任务 1.5h＋学习 1h）；延期写明理由，不倒填"
HOURS_LEADER = "每周约 6–8 小时（本线任务 4–5h＋辅助组员 1–2h＋学习约 1h）；辅助记入台账"
HOURS_LEADER_LIGHT = "轻量周约 3–4 小时（本线任务 2h＋辅助组员 1h）；延期写明理由，不倒填"

ROLE_TAG = {
    "王启龙": ("负责人 · 统筹/工程", "v2 线：统筹/工程 ＋ 辅助组员（W3 起）"),
    "衣思淼": ("数据 · 身份/活性数据", "v2 线A：G2 数据资格（Phase 2B P0 主做）"),
    "宁显泷": ("模型 · 统计验证", "v2 线A：G3 模型资格（W7 起跑基线，本周不启动）"),
    "代维斯丹": ("结构 · 独立复现", "v2 线A：结构核验（THRB 两项 P0 主做）"),
    "王散曼": ("文献 · 机制证据", "v2 线A：证据链（两项 P1 组学重复主做＋数据项复核）"),
}

REVIEWER_OF = {"王启龙": "王散曼", "衣思淼": "宁显泷", "宁显泷": "代维斯丹",
               "代维斯丹": "衣思淼", "王散曼": "王启龙"}

def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))

def load_plan():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    tasks = {}
    for t in plan["tasks"]:
        tasks.setdefault(t["member"], {})[t["week"]] = t
    return plan, tasks

# ============ W3 本周焦点：Phase 2B 第一批 11 项（每人的主做/复核，来自 FIRST_BATCH_PILOT_TASKS.md） ============
# 条目: [任务ID, 靶点, 问题标签, 角色是主做还是复核, 一句话目标, 注意事项, 工具, 流程]
W3_FOCUS = {
 "王启龙": [
  ["cr_b0108177640570e3","FASN","direct_screening_eligibility","主做",
   "判定该记录能否直接进筛选池",
   "FASN 当前为仅机制线（T1 裁决失败），不要因本条核验放行任何筛选",
   "任务总表.csv ＋ ChEMBL activity 接口",
   "查任务总表找到该条 → 看 ChEMBL 原始 activity 上下文 → 填回填表（判定/理由/来源）"],
  ["全部 11 项","五个靶点","汇总跟做","跟做＋汇总",
   "收齐五人回填、汇总成批文件并试跑严格导入",
   "回填零条时不预填、不代签；工程测试件不算真人完成",
   "pandas ＋ 回填表格式.json",
   "收各人回填 → 核对字段（判定/人工值/理由/来源编号/时间）→ 汇总为 pilot_batch_001_decisions.json → 试跑严格导入并记录输出"],
 ],
 "衣思淼": [
  ["cr_b2e66c3f80331987","NR1H4","endpoint_unknown＋数值缺失＋单位未识别","主做",
   "确认该活性记录的真实终点（是 EC50 还是别的）",
   "有效浓度（EFFECTIVECONCENTRATION）不等于 EC50，必须回到测定描述判定；数值缺失就写缺失，不猜",
   "ChEMBL activity 接口（activity/438711.json）",
   "任务总表定位 → 打开 ChEMBL 原始条目 → 读测定描述与单位 → 填回填表"],
  ["cr_4ce1a9b511da44f2","ACACA","endpoint_unknown＋单位未识别","主做",
   "分清抑制率（INHIBITION %）与 IC50 不能混用",
   "两条样本值是百分比；百分比不是浓度，禁止折算成 pIC50",
   "ChEMBL activity 接口",
   "读原始测定描述 → 判定终点类型 → 填回填表并写清理由"],
  ["cr_11f2d61b67f82362","NR1H4","endpoint_unknown（26 条受影响）","主做",
   "核对大量重复的 EFFICACY % 是否同一测定口径",
   "影响面最大的一条（26 条）；重复值先查是否同一测定，不确定就写待定",
   "ChEMBL assay 描述 ＋ 表格工具",
   "逐条看受影响记录 → 比对测定描述 → 填回填表"],
 ],
 "宁显泷": [
  ["cr_f505080a747c2290","NR1H4","endpoint_unknown（11 条受影响）","主做",
   "核对 7 个样本值分布，区分 EFFICACY 与有效浓度",
   "终点分层直接影响模型输入；本周只核验，不启动任何模型训练",
   "ChEMBL activity 接口 ＋ 表格工具",
   "看样本值分布 → 读测定描述 → 填回填表"],
  ["cr_db629e920219a104","NR1H4","endpoint_unknown（6 条受影响）","主做",
   "确认同一测定内 EFFICACY % 是否可作为模型输入字段",
   "为后续划分与输入一致性做准备，只记录事实，不替 G3 做决定",
   "ChEMBL assay 描述",
   "读测定描述 → 填回填表"],
 ],
 "代维斯丹": [
  ["cr_e9d2dc6f22913ddd","THRB","target_subtype_selectivity","主做",
   "确认该测定到底是 THR-α 还是 THR-β，选择性口径是什么",
   "蛋白构建体与亚型必须从测定描述确认；这条结论给后续结构复核用",
   "ChEMBL assay 描述 ＋ UniProt",
   "读测定描述 → 查亚型与构建体 → 填回填表"],
  ["cr_f32dff51aa2113e4","THRB","direct_screening_eligibility","主做",
   "判定该记录可否直接用于筛选资格",
   "与 THR-β 条件通过状态及结构门控失败的关联要写进理由，不因核验通过而重开排序用途",
   "ChEMBL activity 接口",
   "读原始条目 → 对照资格条件 → 填回填表"],
 ],
 "王散曼": [
  ["cr_b89a67298bdff12e","NR1H4","omics_replication（组学重复）","主做",
   "查该单队列组学结论有无第二个独立队列或文献复现",
   "单一队列只能算一个方向；找不到复现就如实降级，检索式和日期要留档",
   "PubMed／欧洲文献库检索",
   "记录检索式与日期 → 找第二队列/复现文献 → 填回填表（附文献编号）"],
  ["cr_0e2972744373686c","THRB","omics_replication（组学重复）","主做",
   "同上，针对 THR-β",
   "同上；样本/病例/对照口径一并记录",
   "PubMed／欧洲文献库检索",
   "同上流程，对象换 THR-β"],
 ],
}

COMMON_FILES = "human_review/phase2b_20260915/任务总表.csv、回填表格式.json、核验填写说明.md、FIRST_BATCH_PILOT_TASKS.md"
COMMON_FLOW = "① 打开 human_review/phase2b_20260915/，按任务编号在任务总表.csv 定位 → ② 读原始来源（ChEMBL 接口或文献库）→ ③ 复制 review_return.template.json 填：判定（通过/更正/驳回）、人工值（仅更正时填）、全名、时间、理由（引原文）、来源编号 → ④ 存为回填文件交负责人汇总"
COMMON_NOTICE = "回填只动允许字段（判定/人工值/理由/来源编号/时间/姓名）；AI 原值等只读字段一律不改；判定必须引用原始测定描述或文献；查不到就写查不到，不编"

def v2_learn(week):
    base = [
        None, None,
        ["复习研究链路 v2 方案第 1–2 节：三库分工、四种状态（任务/证据/产物/门控）分离",
         "看 ChEMBL 数据结构入门 1 集：活性记录长什么样、单位与关系符号在哪"],
        ["看 PubMed／欧洲文献库检索入门 1 集：怎么保存检索式和检索日期"],
        ["看 RDKit 复习 1 集：标准化、互变异构、盐剥离为什么不能无脑做"],
        ["看 scikit-learn Pipeline 1 集：插补/标准化为什么只能拟合训练折"],
        ["看交叉验证与数据泄漏 1 集：骨架划分与随机划分差在哪"],
        ["看共形预测入门 1 集：覆盖率含义与交换性前提"],
        ["看模型校准 1 集：可靠性图怎么读；温度校准适用分类、不适用 pIC50 回归"],
        ["看适用域 1 集：最近邻 Tanimoto／杠杆值各自的局限"],
        ["看置换检验 1 集：为什么整条流程都要重跑"],
        ["看置换检验 1 集：为什么整条流程都要重跑"],
        ["看富集因子 EF／BEDROC 1 集：筛选指标怎么预注册"],
        ["看 AutoDock Vina 可复现性文档：多种子、搜索强度与失败报告"],
        ["看 OECD QSAR 验证原则 1 集：适用域、可复现、局限性表述"],
        ["看论文图表规范 1 集：每个数字要能回到原始记录"],
        ["看预注册与偏倚 1 集：探索后改终点要新版本，不算预注册"],
    ]
    return base[week - 1] if week <= len(base) else []

def build_week(no, task, member):
    hours = (HOURS_LEADER if member == "王启龙" else HOURS_MEMBER)
    if no == 4:
        hours = (HOURS_LEADER_LIGHT if member == "王启龙" else HOURS_MEMBER_LIGHT)
    gate = task.get("gate") or "—"
    theme = f'W{no} {task["theme"]}（{gate}）'
    if no == 3:
        # 本周卡：聚焦 Phase 2B 第一批
        focus = W3_FOCUS[member]
        main = [f for f in focus if f[3] != "复核"]
        parts = []
        for f in main:
            parts.append(f'{f[3]}【{f[1]}｜{f[2]}】目标：{f[4]}；注意：{f[5]}')
        task_txt = "本周主做（研究链路 v2·第三周）：\n" + "\n".join(parts)
        card = dict(
            task=task_txt,
            cmd=COMMON_FLOW,
            expected=task["acceptance"] + "；每条判定都引用原始来源，零条完成也如实记录",
            source=f'文件：{COMMON_FILES}；输入：{task["inputs"]}',
            criteria=COMMON_NOTICE,
            verifier=f'{task["reviewer"]}（复核）',
        )
        tasks_arr = [[f"V2-03-1", f'主做：{"；".join(f[0] for f in main)}']]
        tasks_arr.append(["V2-03-2", "回填：每条填判定/理由/来源编号，交负责人汇总（周日）"])
        if member == "王启龙":
            tasks_arr.append(["V2-03-3", "辅助一位组员完成其本周任务（记谁/什么/多久，入台账）"])
            tasks_arr.append(["V2-03-4", "汇总五人回填 → 试跑严格导入 → 周日发进度汇总"])
    else:
        card = dict(
            task=task["action"],
            cmd=f'交付：{task["deliverable"]}',
            expected=task["acceptance"],
            source=f'输入：{task["inputs"]}｜工具：{task["tools"]}',
            criteria=task["review_rule"],
            verifier=f'{task["reviewer"]}（复核）',
        )
        tasks_arr = [
            [f"V2-{no:02d}-1", task["action"]],
            [f"V2-{no:02d}-2", f'周报：工时（{hours}）＋阻塞与下一步；证据路径'],
        ]
        if member == "王启龙":
            tasks_arr.append([f"V2-{no:02d}-3", "辅助一位组员完成其本周任务（记录谁/什么/多久）"])
    checks = [dict(id=f"V2-C{no:02d}", desc=f'W{no} 交付验收', exp=task["acceptance"][:80], src=task["deliverable"])]
    learn = v2_learn(no)
    coord = [f'周日：{task["theme"]} 进度汇总（做了什么/证据/阻塞/下周）',
             f'失败分支：{task["fallback"]}']
    return dict(no=no, dates=D[no-1], stage=task["theme"], theme=theme,
                learn=learn, card=card, tasks=tasks_arr, checks=checks, coord=coord)

def swap_block(text, const_name, new_body):
    declaration = re.search(rf"const\s+{re.escape(const_name)}\s*=\s*([\[{{])", text)
    if not declaration:
        raise ValueError(f"模板缺少声明：{const_name}")
    opening = declaration.group(1)
    closing = "]" if opening == "[" else "}"
    open_index = declaration.start(1)
    depth = 0; quote = None; escaped = False; close_index = None
    for index in range(open_index, len(text)):
        char = text[index]
        if quote is not None:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char; continue
        if char == opening: depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0: close_index = index; break
    if close_index is None:
        raise ValueError(f"括号未闭合：{const_name}")
    return text[:open_index + 1] + new_body + text[close_index:]

def new_manuals():
    return [
        dict(id="V2-M05", week=5, text="W5 周日：G2 是否具备冻结条件的审查结论（可判不具备）", dead=None),
        dict(id="V2-M06", week=6, text="W6 周日：数据冻结＋主线选定裁决（数据不足走方法/负结果路径）", dead=None),
        dict(id="V2-M10", week=10, text="W10 周日：G3 模型资格正式裁决（未过转负结果/方法链，不强行给榜）", dead=None),
        dict(id="V2-M11", week=11, text="W11 周日：是否进入分轨筛选（合格命中可为零）", dead=None),
        dict(id="V2-M14", week=14, text="12/15 早投检查：关键复核全过＋负责人批准，否则走 1 月修订路线", dead=None),
        dict(id="V2-M16", week=16, text="W16：审阅包交付；2026-12-28—2027-01-31 修订窗口；2027-02-01 内部目标", dead=None),
    ]

def new_milestones():
    return [
        dict(id="V2-MS1", week=5, name="Phase 2B P0 高风险单元收敛＋G2 冻结条件审查", need=["V2-C05"]),
        dict(id="V2-MS2", week=6, name="数据冻结＋主线选定（或方法/负结果路径裁决）", need=["V2-C06"]),
        dict(id="V2-MS3", week=10, name="G3 模型资格正式裁决", need=["V2-C10"]),
        dict(id="V2-MS4", week=13, name="证据卡＋G6 人工审计 → 候选发布或保留/负结果包", need=["V2-C13"]),
        dict(id="V2-MS5", week=16, name="审阅包＋归档交付", need=["V2-C16"]),
    ]

def new_research_chain():
    return ("updated:\"2026-09-22\", current:3,\n steps:[\n"
        '  ["① 研究问题冻结（G0）","治疗方向、靶点亚型、终点、用途、主指标、预算先冻结成协议；模糊就只算探索。","00-当前研究/research_chain_v2_20260921/完整研究链路_v2.md §3","本周已定"],\n'
        '  ["② 靶点资格（G1）","临床/机制/组学/可建模性分开审查；疾病相关不等于可筛。","00-当前研究/research_chain_v2_20260921/Gate验收矩阵.csv","待执行"],\n'
        '  ["③ 活性数据资格（G2）——现在做的","Phase 2B P0 共 49 条真人核验＋结构/单位/关系符号/重复冲突审计；关键 P0 未解决则保持阻塞。当前真人完成 0 条。","human_review/phase2b_20260915/FIRST_BATCH_PILOT_TASKS.md","进行中·待真人核验"],\n'
        '  ["④ 模型资格（G3）","同数据同划分同预算；简单基线优先；图网络只做同折比较不堆架构；无外推证据则限探索用途。","00-当前研究/research_chain_v2_20260921/决策与验收补充.md §一","W7–W10"],\n'
        '  ["⑤ 输出资格（G4）","分轨合格命中表：域外/高不确定进探索池不混正式榜；允许零命中。","00-当前研究/research_chain_v2_20260921/Gate验收矩阵.csv","W11·条件启动"],\n'
        '  ["⑥ 结构支持（G5 支路）","姿态恢复/协议稳健性/用途验证三层；野生型 THRβ 排序用途维持关闭；分子动力学只做有判别价值的问题。","00-当前研究/research_chain_v2_20260921/完整研究链路_v2.md §8-9","W12·可选"],\n'
        '  ["⑦ 候选发布（G6）","人工逐条审计＋可信签核＋上游全部现行才放行；合格数可为零。","00-当前研究/qualification_v1/RESEARCH_STATE.md","W13·受门控"],\n'
        '  ["⑧ 实验/最终决策（G7）","莫拉克辛 N 沿既有预注册包推进（线C）；实验结果不填不编。","00-当前研究/qualification_v1/OPEN_ISSUES.md","线C·待物料"\n ]\n ]')

def build_mywork(member, weeks_tasks, plan):
    tag, line = ROLE_TAG[member]
    w3 = weeks_tasks[3]
    hrs = HOURS_LEADER if member == "王启龙" else HOURS_MEMBER
    focus = W3_FOCUS[member]
    main_ids = "、".join(f[0] for f in focus if f[3] != "复核")
    if member == "王启龙":
        duty = ("统筹三库状态同步与研究链路 v2 执行；辅助组员完成任务（每周 1–2h，记台账）；"
                "工程修复、版本账本、每周备份；关键节点裁决记录（G2 冻结、G3 裁决、12/15 检查）")
    else:
        duty = f"研究链路 v2 {line}；每周约 4h（任务 2.5h＋学习 1.5h）；交付附证据路径，复核人 {REVIEWER_OF[member]}"
    tasks = []
    for wk in range(3, 17):
        t = weeks_tasks.get(wk)
        if not t: continue
        tasks.append([f"V2-W{wk:02d}", f'W{wk}：{t["action"]}', t["acceptance"]])
    ops = [
        ["① 先看当前状态", "打开本库 研究状态.md 与主库 qualification_v1/RESEARCH_STATE.md；确认候选未放行、图网络门关闭、FASN T1 失败、G2 待人审"],
        ["② 本周任务（W3）", f"主做：{main_ids}；文件在 human_review/phase2b_20260915/（任务总表.csv 定位 → 读原始来源 → 填回填表）"],
        ["③ 遇到阻塞", "登记到工作台「阻塞与求助登记」表，群里找负责人；查不到原始来源就如实写查不到，不编值"],
        ["④ 记录结果", "交付物注明来源、日期、证据路径与是否人工核验；自报打卡不是可信人审，不改变门控"],
        ["⑤ 每周节奏", f"{hrs}；周日进度汇总（做了什么/证据/阻塞/下周）；负责人做每周备份"],
    ]
    ghlinks = [
        ["① 核验首页（先开这个：11 项任务卡＋每个任务的原始数据直达链接）", "../human_review/phase2b_20260915/index.html"],
        ["② 任务总表 CSV（按任务编号定位我的条目）", "../human_review/phase2b_20260915/任务总表.csv"],
        ["③ 回填表模板（复制一份照格式填）", "../human_review/phase2b_20260915/review_return.template.json"],
        ["④ 核验填写说明（每个字段怎么填）", "../human_review/phase2b_20260915/核验填写说明.md"],
        ["⑤ 第一批任务书（11 项谁主做谁复核）", "../human_review/phase2b_20260915/FIRST_BATCH_PILOT_TASKS.md"],
        ["研究状态.md（本库当前状态）", "https://github.com/wang13236614835-cmyk/hepato-gnn-screening/blob/main/研究状态.md"],
        ["v2 完整方案（任务总源）", "https://github.com/wang13236614835-cmyk/aidd/blob/main/00-%E5%BD%93%E5%89%8D%E7%A0%94%E7%A9%B6/research_chain_v2_20260921/%E5%AE%8C%E6%95%B4%E7%A0%94%E7%A9%B6%E9%93%BE%E8%B7%AF_v2.md"],
    ]
    team = [
        ["王启龙", "负责人·统筹/工程＋辅助组员（6–8h/周）", "王启龙/打卡_王启龙.html"],
        ["宁显泷", "模型·统计验证（4h/周）", "宁显泷/打卡_宁显泷.html"],
        ["衣思淼", "数据·身份/活性数据（4h/周）", "衣思淼/打卡_衣思淼.html"],
        ["代维斯丹", "结构·独立复现（4h/周）", "代维斯丹/打卡_代维斯丹.html"],
        ["王散曼", "文献·机制证据（4h/周）", "王散曼/打卡_王散曼.html"],
    ]
    w3t = weeks_tasks[3]
    ctx = dict(
        stage="research_chain_v2（数据—验证—可复现主线）",
        week="W3｜2026-09-21–09-27（本周）",
        why=f'G2 待人审（真人完成 0 条）是全局卡点；本周任务：{w3t["theme"]}。主做：{main_ids}。',
        first=f'打开 human_review/phase2b_20260915/：任务总表.csv 按编号定位 → 读 ChEMBL/文献原始来源 → 按回填表格式.json 填判定。注意：{COMMON_NOTICE[:60]}…',
        deliver=f'回填文件（每条判定/理由/来源编号）；{w3t["deliverable"]}',
        action="打开核验首页（任务卡＋原始数据直达）",
        action_path="../human_review/phase2b_20260915/index.html",
        action_url="https://github.com/wang13236614835-cmyk/hepato-gnn-screening/blob/main/human_review/phase2b_20260915/index.html",
        source="AIDD 主库 qualification_v1/RESEARCH_STATE.md ＋ research_chain_v2_20260921/完整研究链路_v2.md",
    )
    return dict(fullname=member, roleTag=tag, lineTag=line, fileCount=0,
                deadline="W3–W16 每周日进度汇总；里程碑见下方", duty=duty,
                tasks=tasks, files=[], currentContext=ctx, ops=ops,
                ghlinks=ghlinks, team=team)

def sanitize(text):
    """文案净化：不提导师（改负责人）、周五组会改周日进度汇总、去预算字样（计算量表述改中性）。仅文案层面，不动数据语义。"""
    rep = [
        ("发导师", "发负责人"),
        ("发给导师", "发给负责人"),
        ("导师审阅", "负责人审阅"),
        ("导师意见真实记录", "审阅意见真实记录"),
        ("导师批准", "负责人批准"),
        ("导师确认优先", "负责人确认优先"),
        ("导师审定", "负责人审定"),
        ("导师签字", "负责人签字"),
        ("导师终审", "负责人终审"),
        ("报给导师", "报给负责人"),
        ("给导师", "给负责人"),
        ("导师", "负责人"),
        ("周五组会", "周日进度汇总"),
        ("开组会", "周日进度汇总"),
        ("周一组会", "周日进度汇总"),
        ("选择一个可行计算主线并锁定预算", "选定一条可行计算主线"),
        ("锁定预算", "定好计算方案"),
        ("审超参预算和对照公平性", "审超参设置与对照公平性"),
        ("记录放行、限定或不放行与后续预算", "记录放行、限定或不放行及后续安排"),
        ("结构预算决定与实验就绪清单", "结构必要性决定与实验就绪清单"),
        ("同折、同预算协议", "同折同条件协议"),
        ("同折同预算", "同折同条件"),
        ("终点、用途、主指标、预算先冻结成协议", "终点、用途、主指标先冻结成协议"),
        ("时间算力预算", "时间与算力安排"),
        ("算力预算", "算力安排"),
        ("计算预算", "计算安排"),
        ("同数据同划分同预算", "同数据同划分同条件"),
        ("主指标、预算及测试开封规则", "主指标与测试开封规则"),
    ]
    for a, b in rep:
        text = text.replace(a, b)
    return text

def sync_page(member, weeks_tasks, plan, hist_weeks):
    src = ROOT / member / f"打卡_{member}.html"
    text = src.read_text(encoding="utf-8")
    dest = ROOT / "historical_v2_pages" / member / f"打卡_{member}_v2历史.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    hist = [w for w in hist_weeks if w["no"] <= 2]
    # 历史卡的 coord 属日程文案，一并净化（卡内容保留为历史复核）
    for w in hist:
        w["coord"] = [sanitize(c) for c in w.get("coord", [])]
    new_weeks = hist + [build_week(w, weeks_tasks[w], member) for w in range(3, 17)]
    # 任务文本净化（v2 数据源中个别任务含"导师"）
    for w in new_weeks:
        if w["no"] >= 3:
            w["card"] = {k: sanitize(v) if isinstance(v, str) else v for k, v in w["card"].items()}
    text = swap_block(text, "WEEKS", js(new_weeks)[1:-1])
    text = swap_block(text, "MANUALS", js(new_manuals())[1:-1])
    text = swap_block(text, "MILESTONES", js(new_milestones())[1:-1])
    text = swap_block(text, "RESEARCH_CHAIN", new_research_chain())
    text = swap_block(text, "MYWORK", js(build_mywork(member, weeks_tasks, plan))[1:-1])
    # 模板静态文案净化（周报按钮、页脚提示、验收四态等界面文本）
    text = sanitize(text)
    dest.write_text(text, encoding="utf-8")
    return len(new_weeks)

def main():
    if "--legacy-v2" not in sys.argv:
        raise SystemExit(
            "research_chain_v2 已降为 HISTORICAL_BASELINE；默认禁止覆盖当前 v3 成员工作台。"
            "如确需历史重放，请显式添加 --legacy-v2。"
        )
    plan, tasks = load_plan()
    leader = ROOT / "王启龙" / "打卡_王启龙.html"
    t = leader.read_text(encoding="utf-8")
    dec = json.JSONDecoder()
    m = re.search(r"const WEEKS =", t)
    hist_weeks, _ = dec.raw_decode(t, m.end())
    for member in ["王启龙", "宁显泷", "衣思淼", "代维斯丹", "王散曼"]:
        wt = tasks[member]
        n = sync_page(member, wt, plan, hist_weeks)
        print(f"已同步 {member}：W3 聚焦本周＋W4–W16 计划卡（{n} 周）")

if __name__ == "__main__":
    main()
