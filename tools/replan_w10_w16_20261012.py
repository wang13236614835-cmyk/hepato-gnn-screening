# -*- coding: utf-8 -*-
"""Rewrite in-place W10–W16 of the FIVE EXISTING original check-in HTML files.
W1–W9, existing localStorage SKEY, export/import/ledger kept. Old cards archived.
No research Authority or historical completed count is modified.
"""
import argparse, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"docs/audit/20261012_original_week10_week16_checkins.json"

BASE=[
("11/09–11/15","筛选结果交叉验收","复审5MCULE+老药/中药探索候选及拒判",
 "复核三路筛选原始输入、评分口径、复算结果和候选身份证据；形成每个候选的证据缺口，严禁据此放行H1。",
 "三轨原始候选+评分卡、W6–W9周报、模型数据域、异人复核",
 "逐候选身份/靶点/原始来源/得分或拒判/不确定性/反例，输出“保留研究/补证/否决”",
 "不把5+1+1数量当KPI，不沿用旧FASN域外评分",["三轨候选和拒判按原ID可追","独立异人复算和来源复核有记录","关键阻塞和决策理由归档"],
 "独立复算、数据溯源、盲审和负结果"),
("11/16–11/22","原始数据与模型资格","D1/D2原始assay、训练工件与泄漏验收",
 "检查数据来源、assay统一性、训练/测试切分、模型版本和独立基线；若缺少真实工件，形成阻塞及最小补证清单。",
 "Workbench V4 D1/D2 Evidence Contract与原始assay、split、模型日志",
 "原始数据/来源hash/清洗决策/同折基线与模型重算；或形成不能复算的缺口台账",
 "原件不齐不得宣称GNN/Gate通过，负性能如实报告",["assay标签/测量单位/来源一致或标冲突","训练/测试/种子/泄漏和baseline可独立核","有效D1/D2条件与未决有审查记录"],
 "assay provenance、分子数据划分、泄漏和同折baseline"),
("11/23–11/29","AD/UQ与安全结构筛查","D4适用域、不确定性及D5辅助证据复核",
 "对当前尚可研究的候选核AD/OOD、UQ、PAINS/ADMET和已存Docking/结构来源，记录不支持结论及必要重算。",
 "Workbench V4 D4/D5工件、模型版本、候选结构与ADMET来源",
 "明确每个候选的域内外/不确定性/结构警报、参数可重放情况及HOLD/REJECT理由",
 "对接分数不等于亲和力，结构缺口不能被AI自行补造",["AD/OOD和置信限制逐候选标注","结构/ADMET/PAINS/异常与原工件对账","独立复核并记录模型不适用和负结果"],
 "不确定性校准、AD、PAINS与ADMET结果解释"),
("11/30–12/06","D6证据综合与候选资格建议","多目标机制/反证整合与候选继续价值评估",
 "合并直接靶点、MASH细胞场景、药理、毒理和计算证据；给拟继续研究的候选排序和拒判，并验证新颖性。",
 "V4 D6 Evidence Contract、真实原文、三轨AD/UQ/ADMET数据",
 "逐候选claim-evidence ledger含反例及机制方向限制；3–5项仅作为有证据时的建议上限",
 "模型排名不能替代靶点资格和湿实验，D6缺合同仍保持BLOCKED",["靶点直接作用与MASH疾病证据分层","候选正反证和prior-art可独立核","真实D6合同缺口和建议状态有记录"],
 "靶点资格、多靶点反向药理、claim-evidence与prior art"),
("12/07–12/13","H1条件化冻结与EP0设计","候选冻结资格审查和预注册实验方案草案",
 "若D0–D6满足证据要求则准备H1真人候选冻结；否则补关键缺口。并草拟靶点和MASH场景所需最小验证方案。",
 "V4 H1/H2/EP0规则、资格合同、实验条件与原始协议",
 "冻结资格逐条判断、候选身份/批次/受体终点和阳阴性对照的预注册草案，未签标DRAFT",
 "H1不得因日期自动PASS；实验不合格就不进入采购和实际执行",["H1门槛与实际失败点、签字权限分清","EP0草案包含对照/重复/终点/停止规则","冻结/预注册草案与正式签署分离"],
 "预注册、候选冻结、实验对照与偏倚控制"),
("12/14–12/20","执行可行性与转化准备","实验执行方、采购/预算和稿件方法学同步评估",
 "核实实验平台、binding/细胞或靶点匹配的测定、材料可得性、伦理合规与报价；H1/H2/EP0真实授权前不采购。并完成稿件方法与先例清单。",
 "真实执行方反馈、供货商资料、H2/EP0审批、方法学底稿",
 "可行性/费用/样品/lot/CoA需求与许可清单，未放行则HOLD并转方法与文献稿件",
 "禁止自动下单，不假设ADORA2A是所有化合物唯一靶点；无到货不得写湿实验完成",["实验方/目标assay/预算证据与阻塞完整","授权/物料批次/规格分界真实可查","论文方法与先例/新颖性证据审查"],
 "实验设计、采购合规、材料标准品与方法学写作"),
("12/21–12/27","学期复现归档与下一阶段决策","研究数据与算法可重放、导师交付和论文/专利初稿",
 "冻结三库的计划与真实证据索引，交付评分/反筛/资格/负结果/实验待办和Methods初稿；提出下学期试验与研究Gate路线。",
 "三库版本/原始材料/复算环境、导师会议记录、论文专利草稿",
 "交一份完整复现包、一页结论及未决Gate列表；明确何处仅为干实验、哪个湿实验尚未开始",
 "不以软件测试、旧勾选或截止日期伪造科学结果",["三库原件和复现包hash一致可查","导师报告、阴性/反证、假说证据完整","下学期实验/论文/专利路径按资格真实决定"],
 "可复现研究、论文Methods、专利先例与研究边界")
]
PEOPLE={
"王启龙":("Q","负责人／科学与版本统筹",[
["组织三轨复审，登记冲突","抽查独立复算和异人复核"],["统筹D1/D2证据来源补齐","协调是否能进入模型资格评审"],["审核D4/D5实际证据边界","裁决跨候选不一致与异常处理"],["组织D6证据主张审查","召开候选GO/HOLD/REJECT/缺口组会"],["主持H1资格与授权边界核对","协调EP0草案和导师预审核"],["核实验室平台、报价、审批和采购门槛","形成真实实验/论文双路线取舍"],["完成三库最终同步、独立审计与导师汇报","安排下一轮科研工作和稿件目标"]]),
"宁显泷":("N","模型／统计与质量",[
["从冻结输入复算三轨模型分数与拒判","抽检种子/测试集/泄漏和域外样本"],["整理D2训练、seed、split、基线原件","同折RF/Ridge/XGB/GNN重核并保留负例"],["输出AD/UQ/异常的逐候选表","审计校准、区间与不合理外推"],["复算候选多目标评分敏感性","独立验证排序改变/不能比较的情况"],["提出实验终点/重复/对照统计方案","核EP0统计停机条件与效应量边界"],["给执行方提供数据模板与盲法/QC要求","写方法学模型验证、局限与不确定性"],["冻结分析代码/环境与完整复算指令","交付模型图、负性能表和下轮实验统计方案"]]),
"衣思淼":("Y","数据／身份与追溯",[
["逐条核5MCULE/老药/中药ID、结构及来源","核评分原始输入缺失和三轨去重"],["核D1原始assay、标签单位和纳排规则","出结构清洗、来源哈希和split数据字典"],["核全部候选身份/立体化学与来源版本","审药品批准信息、来源物种和ADMET输入"],["整理候选统一compound/target ID和证据键","对照各组的原始DOI与hash冲突"],["形成H1对象身份/供货规格需求草案","核EP0样品编号、材料追溯字段"],["核标准品供应/CAS/盐型/纯度与物料条件","记录采购授权未完成项及材料缺口"],["整理三轨数据字典、版本和原始文件索引","封存结构、来源、哈希及证据复核记录"]]),
"代维斯丹":("D","结构／ADMET与可靠性",[
["复核三路结构计算工件与参数版本","梳理对接假阳性和未核实手性"],["核D2输入分子图、结构/盐型特征","排查化合物域外和结构标签异常"],["复核ADMET/PAINS和Docking原文件","整理结构支持的不确定性和不支持药效"],["比较候选多目标结构解释/冲突","审同系物/已知药化先例与新颖性"],["列H1冻结构和可能的标准品选择问题","给EP0草案写结构控制与干扰风险"],["审核供货商结构exact match及纯度规格","明确实验平台所需结构风险和检测干扰"],["冻结结构输入、姿态、日志、参数与失败例","交付结构图、可复现文件和限制声明"]]),
"王散曼":("S","文献／机制与科研主张",[
["逐候选独立核直接靶点/疾病原文证据","审三轨反证、先例与真实药理方向"],["审assay原文/单位/方法是否可比","汇总训练标签与既有直接药理来源"],["查ADMET和结构警报相关文献","核拟靶点的作用方向/疾病反例"],["构建每一候选正反证与机制断链图","核MASH通路和已发表先例/专利新颖性"],["核实验直接靶点与MASH终点的逻辑","审EP0对照/可证明主张/局限"],["查不同实验平台方法/既有测定和专利风险","起草论文引言和Methods主张限定"],["交付文献库/claim-evidence和负结果叙述","完成论文/专利可写/不可写核查"]])
}
def jconst(text,key,fn):
    match=re.search(r"(const "+re.escape(key)+r"\s*=\s*)(\[[^\r\n]*\])",text)
    if not match:raise ValueError("missing const "+key)
    old=json.loads(match.group(2));new=fn(old)
    return text[:match.start(2)]+json.dumps(new,ensure_ascii=False,separators=(",",":"))+text[match.end(2):]
def patch(name,src):
    code,role,task=PEOPLE[name]
    def weeks(items):
        assert len(items)==16
        for idx in range(7):
            n=10+idx; old=items[n-1]
            if not old["theme"].startswith(f"W{n} "):raise ValueError(name+" old W"+str(n)+" mismatch")
            date,stage,title,instruction,source,accept,stop,checks,learn=BASE[idx]
            if old["dates"]!=date:raise ValueError("unexpected original date")
            old.update(stage="新后续科研 · "+stage,theme=title,learn=[learn],
                card=dict(task=instruction,cmd="参照："+source,expected=accept,source=source,
                          criteria=stop,verifier=name+"主核 + 不同成员交叉复核"),
                tasks=[[f"R26-W{n:02d}-{code}-1",task[idx][0]],[f"R26-W{n:02d}-{code}-2",task[idx][1]],
                       [f"R26-W{n:02d}-{code}-LOG","当周真实完成/原件路径/hash/反例/异人复核与阻塞"]],
                checks=[dict(id=f"R26-C{n:02d}-{code}-{i+1}",desc=v,
                             exp="提供真实原件/版本/个人判断和交叉复核；阻塞照实留档",
                             src=source) for i,v in enumerate(checks)],
                coord=["周五交来源、模型/数据版本、失败项与阶段判断","周日不同成员复核与组会，无合同不得冒充正式Gate"])
        return items
    src=jconst(src,"WEEKS",weeks)
    def manuals(items):
        out=[x for x in items if x["week"]<=9]
        out.extend(dict(id=f"R26-M{n:02d}-{code}",week=n,
                        text="本周本人原件核验+不同成员交叉复核+失败/待证留痕；不自动升级Gate",dead=None) for n in range(10,17))
        return sorted(out,key=lambda x:x["week"])
    src=jconst(src,"MANUALS",manuals)
    def milestones(items):
        out=[x for x in items if x["week"]<=9]
        out.extend(dict(id=f"R26-MS{n}",week=n,name=BASE[n-10][2],
                        need=[f"R26-C{n:02d}-{code}-3"]) for n in range(10,17))
        return out
    src=jconst(src,"MILESTONES",milestones)
    def res(items):
        out=[x for x in items if x.get("wk",0)<=9]
        words=["evidence provenance screening audit","assay quality molecule machine learning data leakage",
          "applicability domain uncertainty ADMET PAINS","target qualification MASH mechanism negative evidence",
          "preregistration study design negative control","compound sourcing assay feasibility budget research method",
          "reproducible computational drug discovery manuscript"]
        out.extend(dict(id=f"R26-RES{n}",wk=n,name=BASE[n-10][1],
                        what=BASE[n-10][8],kw=words[n-10]) for n in range(10,17))
        return out
    src=jconst(src,"RES",res)
    # Preserve 2026-09 old W10–W16 notes in S.notes; new task notes go to sprintNotes.
    src=src.replace("[6,7,8,9].includes(Number(n))","(Number(n)>=6&&Number(n)<=16)")
    src=src.replace("[6,7,8,9].includes(n)","(n>=6&&n<=16)")
    if "S.sprintNotes[n]=ta.value" not in src:raise ValueError(name+" no original note logic")
    return src
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--apply",action="store_true");args=parser.parse_args()
    if not ARCHIVE.exists():raise SystemExit("missing preserved original cards")
    original=json.loads(ARCHIVE.read_text(encoding="utf-8"))
    if set(original["people"])!=set(PEOPLE):raise SystemExit("incomplete archive")
    changed=[]
    for name in PEOPLE:
        path=ROOT/name/("打卡_"+name+".html");src=path.read_text(encoding="utf-8")
        key=re.search(r'const SKEY = "([^"]+)"',src)
        assert key and key.group(1)==original["people"][name]["storage_key"]
        revised=patch(name,src)
        changed.append((path,revised))
    if args.apply:
        for path,txt in changed:path.write_text(txt,encoding="utf-8")
        print("APPLIED five W10-W16 cards, learn/verification/milestone/resources; other weeks and storage keys retained")
    else:print("DRY RUN OK five W10-W16 pages and archive checks")
if __name__=="__main__":main()
