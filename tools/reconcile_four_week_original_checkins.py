# -*- coding: utf-8 -*-
"""Revise original five HTML check-in pages W6-W9 (not the external overlay)."""
import argparse, json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"docs/audit/20261012_original_week6_week9_checkins.json"
PEOPLE={
"王启龙":("Q","负责人与汇总",[["冻结五个MCULE评分规范","抽核历史分数/模型来源与反例"],["核老药历史库2973/4225口径","审老药反向靶点/拒判"],["统一中药与老药可比分数","抽核37成分来源与靶点差异"],["汇总5+1+1探索性面板","三库版本对账/导师汇报"]]),
"宁显泷":("N","模型/统计",[["核评分模型/AD/UQ资格","复算五MCULE历史计算与拒判"],["老药多靶点反向预测","核模型域外/不确定性与反例"],["中药反推靶点及OOD警报","与老药同靶点计算结果对比"],["三轨独立复算","提交模型版本/seed/hash/限制"]]),
"衣思淼":("Y","数据/身份",[["核五MCULE结构、手性和来源","评分数据字段及冲突标记"],["核老药版本数量/去重","审批地区/适应证/撤市及结构清洗"],["核37中药成分身份和植物来源","结构/PAINS/缺失/标准品表"],["三路候选身份和去重核查","原始文件hash及数据字典"]]),
"代维斯丹":("D","结构/ADMET",[["核五MCULE旧Docking和ADMET","结构支持与药理活性分开打分"],["复核老药结构/盐型/靶点","对接/PAINS/ADMET假阳性与反例"],["复核中药结构/PAINS/ADMET","对接支持及不能推断药效的情况"],["结构工件/图表独立复查","输出结构限制与失败项"]]),
"王散曼":("S","文献/机制",[["核五MCULE直接药理与MASH文献","证据级别/先例/负结果核验"],["老药靶点/批准用途原始文献","直接药理与MASH机制分开核对"],["中药来源/靶点/肝病文献","中药直接受体与疾病表型分层"],["三路claim-evidence矩阵","导师论文/专利可写边界与反证"]])
}
STAGES=[
("第1周·评分","五MCULE打分、评分标准定版","学习评分分项、AD/UQ、拒判与文献等级","采用统一新评价法对现有五MCULE打分；每项可UNKNOWN或拒判","W1_SCORING_TEMPLATE_20261012.csv及历史MCULE计算/文献原件","5张有来源的评分/拒判卡+冻结规则与跨人复核","不同assay/靶点分数不能假装活性相同",["五对象结构/历史预测出处完整","分项评分、模型/AD与不确定性可复核","原始证据及负例经不同成员复核"]),
("第2周·老药","老药→靶点→MASH反向筛选","学习地区批准/撤市、靶点反推及领域外拒判","从原始老药库反向探索潜在靶点，再对MASH机制分级，争取1个探索候选","REVERSE_SCREENING_TEMPLATE_20261012.csv和老药原始来源","原库版本+清洗前后+靶点证据矩阵+1个探索老药或不足原因","先核2973/4225历史口径差别，模型未达标只能探索",["老药库口径与批准来源、去重可追","靶点/疾病原始文献、AD/OOD及反例","1个候选或无合格药的理由有交叉复核"]),
("第3周·中药","中药成分→靶点→MASH反向筛选","学习植物物种/成分身份/PAINS/ADMET和跨化学域","从37条具名中药成分反向探索靶点与MASH关系，争取1个探索候选","REVERSE_SCREENING_TEMPLATE_20261012.csv及37成分原始来源","37成分结构/来源QC+靶点证据矩阵+1个探索中药或不足原因","植物来源不等于标准品可购，旧FASN域外模型不可硬打分",["37条中药结构/物种来源与缺口","靶点/疾病证据分级、AD与反例","1个候选或无合格成分的理由有复核"]),
("第4周·收尾","MCULE五个＋老药一个＋中药一个证据整合","学习独立复算、负结果、论文主张与两链边界","合并前三周探索研究，形成5+1+1待验证面板或实际不足情况","CURRENT_SPRINT_20261012.md+真实评分/反向筛选/Workbench V4","证据链/独立复算/导师一页报告/未决清单，可为零正式候选","收尾不是H1冻结，没真实Gate不把评分写成药效",["三路候选与负例/拒判可对账","独立复算和输入/输出hash完整","导师材料和Gate状态分开，未签不称通过"])
]
def change_const(text,key,change):
    rx=re.compile(r"(const "+key+r"\s*=\s*)(\[[^\r\n]*\])")
    m=rx.search(text)
    if not m:raise RuntimeError("missing "+key)
    new=change(json.loads(m.group(2)))
    return text[:m.start(2)]+json.dumps(new,ensure_ascii=False,separators=(",",":"))+text[m.end(2):]
def patch(name,text):
    code,role,items=PEOPLE[name]
    if text.count('aidd_current_sprint_20261012.js')!=1:raise RuntimeError("unexpected overlay state "+name)
    def wedit(weeks):
        if len(weeks)!=16 or any(weeks[i]["no"]!=i+1 for i in range(16)):raise RuntimeError("unexpected week list")
        for i in range(4):
            w=weeks[i+5];n=i+6;st,title,learn,task,src,expected,criteria,checks=STAGES[i]
            if not w["theme"].startswith("W"+str(n)+" "):raise RuntimeError("unexpected old week "+str(n))
            w.update(stage="当前科研"+st,theme=title,learn=[learn],
                card=dict(task=task,cmd="填写AIDD主库模板 "+src,expected=expected,source=src,
                          criteria=criteria,verifier=name+"主审＋不同成员复核"),
                tasks=[[f"R26-W{n:02d}-{code}-1",items[i][0]],
                       [f"R26-W{n:02d}-{code}-2",items[i][1]],
                       [f"R26-W{n:02d}-{code}-LOG","周报：原始证据/负例/差异/本人与异人复核/下一步"]],
                checks=[dict(id=f"R26-C{n:02d}-{code}-{j+1}",desc=t,
                             exp="原始来源、模型版本、本人判断与交叉复核均可查",
                             src="AIDD当前四周计划与原始证据") for j,t in enumerate(checks)],
                coord=["周五上传可追溯来源与阻塞","周日组员交叉核验，打勾不自动改变Gate"])
        return weeks
    text=change_const(text,"WEEKS",wedit)
    def medit(data):
        data=[x for x in data if not 6<=x["week"]<=9]
        data.extend(dict(id=f"R26-M{n:02d}-{code}",week=n,
                         text="本人原件核查与不同组员交叉复核留痕；本地勾选≠科研资格通过",
                         dead=None) for n in range(6,10))
        return sorted(data,key=lambda x:x["week"])
    text=change_const(text,"MANUALS",medit)
    text=change_const(text,"MILESTONES",lambda d:
        [x for x in d if x["week"]<6]+
        [dict(id=f"R26-MS{i+1}",week=i+6,name=STAGES[i][1],
              need=[f"R26-C{i+6:02d}-{code}-3"]) for i in range(4)])
    m=re.search(r"const MYWORK\s*=\s*(\{[^\r\n]*\});",text)
    if not m:raise RuntimeError("missing MYWORK")
    my=json.loads(m.group(1))
    my.update(roleTag=role,lineTag="W6评分→W7老药→W8中药→W9收尾",
              deadline="10/12—11/08（原16周的第6–9周）",
              duty="计算与反向筛选由AI辅助，成员核原始来源、解释失效理由并异人复核")
    my["currentContext"]=dict(stage="V4支持：评分与双库反向筛选",
         week="W6打分→W7老药→W8中药→W9收尾",
         why="保留现有五MCULE，先改评价标准，再从老药和37条中药成分反向筛选各1个探索候选",
         first=items[0][0],deliver="5+1+1探索假说或缺口；有原始来源、负例、复算与导师汇报",
         action="查看新四周计划",action_path="../docs/CURRENT_SPRINT_20261012.md",
         action_url="../docs/CURRENT_SPRINT_20261012.md",
         source="AIDD主库当前四周计划与Workbench V4科学事实")
    my["ops"]=[[f"W{i+6}",'；'.join(items[i])] for i in range(4)]
    my["ghlinks"]=[["当前科研计划","../docs/CURRENT_SPRINT_20261012.md"]]+my.get("ghlinks",[])
    text=text[:m.start(1)]+json.dumps(my,ensure_ascii=False,separators=(",",":"))+text[m.end(1):]
    text=text.replace('<script src="../tools/aidd_current_sprint_20261012.js"></script>\n',"")
    text=text.replace("本周自动检查（先跑命令，看到[通过]再勾）","本周检查（W6–W9人工来源核验，其余历史教学检查）")
    text=text.replace("打勾前先跑 <span class=\"cmd\">python tools/semester_flow.py check 周号 --deep</span>（成员加 --member 姓名），看到[通过]再勾。","W6–W9请核对原件/证据卡及异人复核，再打勾；旧教学周可用semester_flow检查。")
    return text
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");args=ap.parse_args()
    a=json.loads(ARCHIVE.read_text(encoding="utf-8"))
    assert set(a["people"])==set(PEOPLE)
    results=[]
    for n in PEOPLE:
        p=ROOT/n/("打卡_"+n+".html")
        t=p.read_text(encoding="utf-8")
        key=re.search(r'const SKEY = "([^"]+)"',t)
        assert key and key.group(1)==a["people"][n]["storage_key"]
        results.append((p,patch(n,t)))
    if args.apply:
        for p,t in results:p.write_text(t,encoding="utf-8")
        print("APPLY OK five original HTML, only W6–W9 data and current banner; original storage keys retained")
    else:print("DRY-RUN OK five original HTML; no writes")
if __name__=="__main__":main()
