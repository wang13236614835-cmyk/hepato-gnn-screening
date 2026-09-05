# -*- coding: utf-8 -*-
"""同步其余四人打卡页（对照表共用块+各人CSV行+投稿映射+里程碑对齐）。每处替换断言唯一命中。"""
import json, re, sys, os

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

VERIFY = "按指定版本核验来源、规则、完整结果及差异原因；不能为达到旧数字改数据、参数或挑结果。"
SNAP = "旧结果仅在原数据/代码/参数快照中核对；历史核验有价值，差异留痕不默认失败，不把旧45项通过用于新管线放行。"
W16EXP = "保留原写作、逐项复核和问答练习，交付论文方法/结果、图源与复现说明；不以预答辩或湿实验完成为通过条件。"
COORD_NEW = '["论文材料提交导师审阅","按总体目标推进：争取2027年2月达到投稿水准"]'

PAPER = {
    "N01": ("复算V1一组核心结果并量测算力", "代维斯丹", "2026-09-13"),
    "N02": ("冻结比较与校准协议", "衣思淼", "2026-09-27"),
    "N03": ("执行全套基线与GNN比较", "衣思淼", "2026-10-25"),
    "N04": ("完成UQ与拒判验证", "代维斯丹", "2026-11-01"),
    "N05": ("锁定分析环境和复现入口", "代维斯丹", "2026-11-22"),
    "Y01": ("一个FXR assay全记录来源样例", "王散曼", "2026-09-13"),
    "Y02": ("完成主稿FXR数据与成分登记", "王散曼", "2026-09-27"),
    "Y03": ("数据与独立验证最终冻结", "宁显泷", "2026-10-11"),
    "Y04": ("核验CW-BCS数据输入和药材成分数偏倚", "代维斯丹", "2026-11-01"),
    "Y05": ("论文表格和数据共享检查", "王散曼", "2026-11-15"),
    "D01": ("V1一个共晶系统证据链样例", "宁显泷", "2026-09-13"),
    "D02": ("V1 FXR/THRβ/ACC结构与药理审查", "王散曼", "2026-10-11"),
    "D03": ("对接稳健性与必要对照", "宁显泷", "2026-10-25"),
    "D04": ("逐图核验与统一生成", "衣思淼", "2026-11-15"),
    "D05": ("非实现者干净环境独立复现", "王启龙", "2026-11-22"),
    "S01": ("主稿FXR终点和创新原文样例", "衣思淼", "2026-09-13"),
    "S02": ("纳入assay组与天然产物证据复核", "代维斯丹", "2026-09-27"),
    "S03": ("V1 GSE135251与背景主张核对", "宁显泷", "2026-10-18"),
    "S04": ("真人论述与候选证据矩阵", "衣思淼", "2026-11-15"),
    "S05": ("目标期刊最终核查", "王启龙", "2026-11-22"),
}

ROUTE_CARD = '''  <div class="card" style="border-left:4px solid var(--brand)"><h2>🧭 当前研究路线（AIDD 主线 · FXR/GNN/CW-BCS）</h2>
    <div class="kv">本库（GNN）负责暑假核验与学习打卡；AIDD 承载已立项的 FXR/GNN/CW-BCS 论文主线。总体目标：争取 2027 年 2 月达到投稿水准；湿实验为进度按时完成、质量优秀、创意新颖前提下的可选后续（锦上添花）。任务唯一入口：${linkPaths("docs/中文核心投稿任务入口.md")}。</div>
    <table><tr><th>阶段</th><th>已有成果（可引用）</th><th>剩余验收</th></tr>
      <tr><td><b>① 数据审核</b></td><td>结构解析/去重全过；审核模板就位</td><td>身份/活性/终点逐条人工审核（Y线、S线）</td></tr>
      <tr><td><b>② 模型比较</b></td><td>教学管线 RF/LR/GNN 同表对照</td><td>同划分同预算基线比较＋协议冻结（N线）</td></tr>
      <tr><td><b>③ 外推与校准验证</b></td><td>覆盖率 Wilson CI、误差分层、划分选择性已量化</td><td>封存外部集验证＋校准重建（N线）</td></tr>
      <tr><td><b>④ CW-BCS 应用</b></td><td>方差降权融合框架可运行（探索性）</td><td>输入核验＋偏倚审查＋独立证据（Y线、Q线）</td></tr>
      <tr><td><b>⑤ 复现与写作</b></td><td>运行清单/哈希留档流程可用</td><td>净环境独立复现＋逐图核验（D线）＋主稿（Q线）</td></tr>
      <tr><td><b>⑥ 投稿</b></td><td>25 项任务表与个人卡已定</td><td>首投、返修与材料复核（Q05）</td></tr>
    </table>
    <div class="hint">分支说明：THRB/FASN/SCD1 独立扩展、KEAP1 教学对接等探索属分支工作，只在其所属位置标注，不排入本主线必做流程；分支结论不自动进入主稿。</div>
  </div>
'''
LEDGER_LEGEND = '    <div class="hint" style="margin-top:8px">验收四态：<b>机器运行完成 → 本人核验完成 → 交叉复核通过 → 导师审阅</b>。本页勾选只代表本人核验，不自动等于后两态；机器跑通（含 AI 辅助产出）单独记账，不折算为研究完成度。</div>\n'
PAPER_RENDER = '    ${w.paper?`<div class="hint" style="margin-top:8px">📌 本周投稿任务 <b>${w.paper[0]}</b>：${esc(w.paper[1])}（复核：${esc(w.paper[2])}；截止 ${esc(w.paper[3])}）——同一工作只交一次证据，学习打卡不代替投稿验收；任务唯一来源：AIDD 任务总表（入口 ${linkPaths("docs/中文核心投稿任务入口.md")}）。</div>`:\'\'\n}\n'

COMMON = [
    ('页眉', '距开学 ${Math.ceil((START-new Date())/864e5)} 天（预习第1周）', '距9月7日开学 ${Math.ceil((START-new Date())/864e5)} 天（开学前预习）'),
    ('学期后', '"学期结束段（结题/考试周）"', '"学期结束后（论文投稿/返修窗口）"'),
    ('路线卡插入', '  <div class="card"><h2>🔬 全线研究流程（8 步 SOP · final-aidd-screening）</h2>', ROUTE_CARD + '  <div class="card"><h2>🔬 暑假教学管线：8步流程与当前核验状态</h2>'),
    ('kv快照句', '下表数字均为仓库实测（${PIPELINE.updated}）。全文解读：', '下表数字均为仓库实测（${PIPELINE.updated}）。本表为暑假教学管线快照，数字仅在该运行ID/输入版本内有效；论文主线证据见上方研究路线卡。全文解读：'),
    ('门控行', '"✅ FXR 0.74Å / Keap1 1.10Å"', '"历史门控；修正版：FXR五种子5/5通过，KEAP1 2/5仍阻断"'),
    ('建模行③', '"88条标签（48正/40负）+12条NV池；骨架划分 58/13/17；基线 ECFP+RF 0.983、Desc+LR 0.983；GNN+MC Dropout AUC 0.95（方差-误差ρ=0.676）；适用域 h*=0.362（NV池 7/12 域外）"', '"【历史快照·教学诊断模式】88条标签（48正/40负）+12条NV池；骨架划分 58/13/17；基线 ECFP+RF 0.983、Desc+LR 0.983；GNN+MC Dropout AUC 0.95（方差-误差ρ=0.676）；适用域 h*=0.362（NV池 7/12 域外）——数字仅在源表运行ID/输入版本内有效"'),
    ('建模状态③', '"s3_model.py → results/metrics/model_summary.json","✅ 完成"', '"s3_model.py → results/metrics/model_summary.json","✅ 快照核验"'),
    ('共识行', '"✅ 59候选，黄芩苷 0.9601 居首"', '"旧榜留档；当前为FXR单靶探索排序（三榜：已知回顾/独立测试/未标注）"'),
    ('骨架行', '"⑥ 骨架多样性Top-10","ECFP4 Tanimoto Butina 聚类 37 簇，每簇总分最高为代表"', '"⑥ 指纹相似性多样性Top-10","ECFP4 Tanimoto Butina 指纹相似性聚类（≠Murcko骨架），每簇总分最高为代表"'),
    ('可得性行', '天然产物以药材来源（source_herb）标注可得性', '天然产物以药材来源（source_herb）标注——药材来源不等于可购标准品'),
    ('进度双靶', '"✅","全链路真实计算完成","双靶 redock 门控 + 118 次真实对接 + 三源共识排名 + 多样性 Top-10，全部产物入库 final-aidd-screening/"', '"✅","暑假管线计算完成（历史快照）","双靶门控为旧口径；当前FXR单靶探索排序、KEAP1阻断。产物入库 final-aidd-screening/"'),
    ('进度45', '"✅","45 项数字自洽检查","verify.py 45/45 通过，既有核验锚点全部有效"', '"✅","45 项数字自洽检查（暑假教学快照）","verify.py 45/45 通过仅覆盖旧管线锚点，不用于新管线放行"'),
    ('进度1000', '"⏳","数据扩充 ≥1000 条","WP3：ChEMBL 来源、带可信范围（衣思淼线）"', '"🔄","数据审核与质量验收","来源/标签可追溯优先，不以条数为目标（Y线：衣思淼）"'),
    ('进度模型', '"⏳","模型迁移 PyG＋校准","WP4：AUC 不降、ECE＜0.10（宁显泷线）"', '"🔄","模型比较与校准验证","如实比较新旧模型，不设旧数字门槛（N线：宁显泷）"'),
    ('进度文献', '"⏳","文献证据专查","按多样性 Top-10 名单推进（王散曼线）"', '"🔄","文献证据专查","按未标注候选榜推进（S线：王散曼）；历史阳性不重复算新发现"'),
    ('任务节附注', '    <h3>✅ 项目任务（做完就点一下打勾）</h3>${tasks}\n', '    <h3>✅ 项目任务（做完就点一下打勾）</h3>${tasks}\n' + PAPER_RENDER),
    ('台账图例', '  <div class="kv">累计打卡 <b>${d}/${t}</b> ｜ 里程碑 <b>${MILESTONES.filter(msDone).length}/${MILESTONES.length}</b> ｜ 记录 <b>${S.log.length}</b> 条</div>\n', '  <div class="kv">累计打卡 <b>${d}/${t}</b> ｜ 里程碑 <b>${MILESTONES.filter(msDone).length}/${MILESTONES.length}</b> ｜ 记录 <b>${S.log.length}</b> 条</div>\n' + LEDGER_LEGEND),
    ('28天hint', '寒假突击、或者新同学进组，都可以直接照着来。</div></div>`;', '寒假突击、或者新同学进组，都可以直接照着来。<b>定位：辅助学习路线，非另一份项目截止安排；唯一正式周次从 9 月 7 日起算。</b></div></div>`;'),
    ('100天hint', '"产出"列就是检验学没学会的标准。</div></div>`;', '"产出"列就是检验学没学会的标准。<b>定位：辅助学习路线，非另一份项目截止安排；唯一正式周次从 9 月 7 日起算。</b></div></div>`;'),
    ('证据链行', '保肝（MASH）问题 → FXR、Keap1-Nrf2 双靶点', '保肝（MASH）问题 → FXR 主线（Keap1 分支：门控阻断中）'),
]

SPECIFIC = {
    "宁显泷": [
        ("W1过关", '"expected":"5 条测试全过；参数和 docs/02_model_notes.md 记的一个不差。【对照数据 ✅】final-aidd-screening 三组模型数：ECFP+RF 0.983／Desc+LR 0.983／GNN+MC Dropout 0.95（ρ_方差-误差 0.676）——基线不弱于深度模型，正是课程\\"基线先行\\"的实证；复跑 final-aidd-screening/run_all.py --model 核对这三组数"', '"expected":"' + SNAP + '"'),
        ("W2没过", '"criteria":"差得多就是手算错了，逐个位置找，不许放宽标准糊弄"', '"criteria":"核对手算、自动微分实现、输入、精度和比较方式，定位差异后复核；不预断手算一定错误，也不随意放宽容差。"'),
        ("W7主题", '"theme":"正式迁移——新模型不能比旧的差"', '"theme":"正式迁移——如实比较新旧模型"'),
        ("W7过关", '"expected":"新模型考试分不低于 0.967；别的代码一行不用改就能切换（这条也要验）"', '"expected":"' + VERIFY + '"'),
        ("W8过关", '"expected":"排序相关 ρ 不低于 0.57（暑假版 0.718 的八成；实测如实记）"', '"expected":"' + VERIFY + '"'),
        ("W14主题", '"theme":"写结题报告的模型章节"', '"theme":"写论文的模型章节"'),
        ("W16主题", '"stage":"收尾与答辩","theme":"答辩技术问答准备"', '"stage":"论文写作与投稿准备","theme":"审稿技术问答准备"'),
        ("W16过关", '"expected":"预答辩技术环节不卡壳；问答进结题附录"', '"expected":"' + W16EXP + '"'),
        ("W16统筹", '"coord":["结题材料提交"]', '"coord":' + COORD_NEW),
        ("M5", '"name":"模型线收工：不降分＋校准双过＋参数表"', '"name":"模型线收工：如实比较＋校准与不确定性证据（不设固定阈值）"'),
        ("M9", '{"id":"M9","week":17,"name":"结题答辩（技术环节）"', '{"id":"M9","week":16,"name":"W16后投稿、返修与归档（技术问答线；不新增学习周）"'),
        ("工作台", '<div class="exp">职责一句话：${esc(M.duty)}</div>', '<div class="exp">职责一句话：${esc(M.duty)}</div>\n    <div class="kv" style="margin-top:8px">论文主线职责：模型/UQ（<b>N01–N05</b>，各任务复核人见 AIDD 任务总表）；教学核验职责照上方校验任务执行——<b>两类职责分开记账，不混计完成度</b>。</div>'),
    ],
    "衣思淼": [
        ("W7主题", '"theme":"数据破千＋给分数配\\"可信范围\\""', '"theme":"数据质量验收＋给分数配\\"可信范围\\""'),
        ("W7过关", '"expected":"数据≥1000 条；考试集≥150 条；可信范围比暑假版窄；抽 30 条标签对文献（王散曼做）"', '"expected":"' + VERIFY + '"'),
        ("W14主题", '"theme":"写结题报告的数据章节"', '"theme":"写论文的数据章节"'),
        ("W16主题", '"stage":"收尾与答辩","theme":"答辩数据问答准备"', '"stage":"论文写作与投稿准备","theme":"审稿数据问答准备"'),
        ("W16过关", '"expected":"预答辩数据环节不卡壳"', '"expected":"' + W16EXP + '"'),
        ("W16统筹", '"coord":["结题材料提交"]', '"coord":' + COORD_NEW),
        ("M4", '"name":"数据破千＋可信范围＋验收 4 条"', '"name":"数据质量验收＋可信范围＋验收 4 条"'),
        ("M9", '{"id":"M9","week":17,"name":"结题答辩（数据环节）"', '{"id":"M9","week":16,"name":"W16后投稿、返修与归档（数据问答线；不新增学习周）"'),
        ("工作台", '<div class="exp">职责一句话：${esc(M.duty)}</div>', '<div class="exp">职责一句话：${esc(M.duty)}</div>\n    <div class="kv" style="margin-top:8px">论文主线职责：数据/划分（<b>Y01–Y05</b>，各任务复核人见 AIDD 任务总表）；教学核验职责照上方校验任务执行——<b>两类职责分开记账，不混计完成度</b>。</div>'),
    ],
    "代维斯丹": [
        ("W14主题", '"theme":"写结题报告的验证章节"', '"theme":"写论文的验证章节"'),
        ("W16主题", '"stage":"收尾与答辩","theme":"答辩验证问答＋现场演示保障"', '"stage":"论文写作与投稿准备","theme":"审稿验证问答＋复现演示"'),
        ("W16过关", '"expected":"预答辩验证环节不卡壳；演示有备份方案"', '"expected":"' + W16EXP + '"'),
        ("W16统筹", '"coord":["结题材料提交"]', '"coord":' + COORD_NEW),
        ("M9", '{"id":"M9","week":17,"name":"结题答辩（验证＋演示保障）"', '{"id":"M9","week":16,"name":"W16后投稿、返修与归档（验证问答线；不新增学习周）"'),
        ("工作台", '<div class="exp">职责一句话：${esc(M.duty)}</div>', '<div class="exp">职责一句话：${esc(M.duty)}</div>\n    <div class="kv" style="margin-top:8px">论文主线职责：V1对接/图/复现（<b>D01–D05</b>，各任务复核人见 AIDD 任务总表）；教学核验职责照上方校验任务执行——<b>两类职责分开记账，不混计完成度</b>。</div>'),
    ],
    "王散曼": [
        ("W14主题", '"theme":"写结题报告的文献章节"', '"theme":"写论文的文献章节"'),
        ("W16主题", '"stage":"收尾与答辩","theme":"答辩机制问答＋实验衔接展示"', '"stage":"论文写作与投稿准备","theme":"审稿机制问答＋可选实验评估"'),
        ("W16过关", '"expected":"预答辩文献机制环节不卡壳"', '"expected":"' + W16EXP + '"'),
        ("W16统筹", '"coord":["结题材料提交"]', '"coord":' + COORD_NEW),
        ("M6", '"name":"实验方案获导师确认"', '"name":"可选湿实验评估一页纸（导师确认）"'),
        ("M9", '{"id":"M9","week":17,"name":"结题答辩（文献机制环节）"', '{"id":"M9","week":16,"name":"W16后投稿、返修与归档（文献机制问答线；不新增学习周）"'),
        ("工作台", '<div class="exp">职责一句话：${esc(M.duty)}</div>', '<div class="exp">职责一句话：${esc(M.duty)}</div>\n    <div class="kv" style="margin-top:8px">论文主线职责：文献/药理（<b>S01–S05</b>，各任务复核人见 AIDD 任务总表）；教学核验职责照上方校验任务执行——<b>两类职责分开记账，不混计完成度</b>。</div>'),
    ],
}

PAPER_WEEKS = {
    "宁显泷": {1: "N01", 3: "N02", 7: "N03", 8: "N04", 11: "N05"},
    "衣思淼": {1: "Y01", 3: "Y02", 5: "Y03", 8: "Y04", 10: "Y05"},
    "代维斯丹": {1: "D01", 5: "D02", 7: "D03", 10: "D04", 11: "D05"},
    "王散曼": {1: "S01", 3: "S02", 6: "S03", 10: "S04", 11: "S05"},
}


def rep1(s, name, old, new, report):
    n = s.count(old)
    if n != 1:
        report.append("    [%s] %s (count=%d)" % ("SKIP" if n == 0 else "MULTI", name, n))
        return s, True
    report.append("    [OK] " + name)
    return s.replace(old, new), False


def main():
    for m in ["宁显泷", "衣思淼", "代维斯丹", "王散曼"]:
        p = "%s/打卡_%s.html" % (m, m)
        s = open(p, encoding="utf-8").read()
        report = []
        bad = False
        for name, old, new in COMMON:
            s, b = rep1(s, name, old, new, report); bad |= b
        for name, old, new in SPECIFIC[m]:
            s, b = rep1(s, name, old, new, report); bad |= b
        for wk, tid in sorted(PAPER_WEEKS[m].items()):
            title, rev, due = PAPER[tid]
            anchor = '"no":%d,"dates"' % wk
            i = s.find(anchor)
            if i < 0:
                report.append("    [SKIP] W%d锚点缺失" % wk); bad = True; continue
            j = s.find(',"learn"', i)
            k = s.find('"no":', i + 10)
            if j < 0 or (0 < k < j):
                report.append("    [SKIP] W%d learn定位失败" % wk); bad = True; continue
            ins = ',"paper":["%s","%s","%s","%s"]' % (tid, title, rev, due)
            s = s[:j] + ins + s[j:]
            report.append("    [OK] W%d+%s" % (wk, tid))
        if bad:
            print("== %s: 存在未命中项，未写回" % m)
            for x in report:
                if "SKIP" in x or "MULTI" in x:
                    print(x)
            sys.exit(1)
        open(p, "w", encoding="utf-8", newline="").write(s)
        print("== %s: %d项替换+5个paper字段，全部命中并写回" % (m, len(COMMON) + len(SPECIFIC[m])))


if __name__ == "__main__":
    main()
