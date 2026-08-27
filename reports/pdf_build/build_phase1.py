# -*- coding: utf-8 -*-
"""暑假阶段报告汇总 PDF - 正文生成（第一阶段材料，汇总自各总结文件）"""
import hashlib
import os
import sys

PDF_SKILL_DIR = r"C:\Users\user\.zcode\cli\plugins\cache\zcode-plugins-official\document-skills\0.1.0\skills\pdf"
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, "scripts"))

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, HRFlowable, Image, KeepTogether,
                                PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = r"D:\zcode-workspace\hepato-gnn-screening"
OUT = os.path.join(ROOT, "reports", "pdf_build", "body_phase1.pdf")
FIG = os.path.join(ROOT, "results", "figures")

ACCENT = colors.HexColor('#1f7692')
TEXT_PRIMARY = colors.HexColor('#1b1a18')
TEXT_MUTED = colors.HexColor('#7a766f')
BG_SURFACE = colors.HexColor('#e5e3df')
BG_PAGE = colors.HexColor('#edecea')

pdfmetrics.registerFont(TTFont('SimHei', r'C:\Windows\Fonts\simhei.ttf'))
try:
    pdfmetrics.registerFont(TTFont('Microsoft YaHei', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('Microsoft YaHei-Bold', r'C:\Windows\Fonts\msyhbd.ttc', subfontIndex=0))
    registerFontFamily('Microsoft YaHei', normal='Microsoft YaHei', bold='Microsoft YaHei-Bold')
    HEAD_FONT = 'Microsoft YaHei'
except Exception:
    registerFontFamily('Microsoft YaHei', normal='SimHei', bold='SimHei')
    HEAD_FONT = 'SimHei'
pdfmetrics.registerFont(TTFont('Times New Roman', r'C:\Windows\Fonts\times.ttf'))
pdfmetrics.registerFont(TTFont('Times New Roman-Bold', r'C:\Windows\Fonts\timesbd.ttf'))
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman-Bold')

from pdf import install_font_fallback  # noqa: E402
install_font_fallback()

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
AVAIL_W = PAGE_W - 2 * MARGIN
AVAIL_H = PAGE_H - 2 * MARGIN
MAX_KEEP_HEIGHT = PAGE_H * 0.4
H1_ORPHAN = AVAIL_H * 0.15

S_H1 = ParagraphStyle('H1', fontName=HEAD_FONT, fontSize=20, leading=28,
                      textColor=ACCENT, spaceBefore=18, spaceAfter=4, wordWrap='CJK')
S_H2 = ParagraphStyle('H2', fontName=HEAD_FONT, fontSize=14.5, leading=21,
                      textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=6, wordWrap='CJK')
S_BODY = ParagraphStyle('Body', fontName='SimHei', fontSize=10.5, leading=17.5,
                        textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap='CJK',
                        firstLineIndent=21, spaceAfter=6)
S_BODY_NI = ParagraphStyle('BodyNI', parent=S_BODY, firstLineIndent=0)
S_BULLET = ParagraphStyle('Bullet', fontName='SimHei', fontSize=10.5, leading=17,
                          textColor=TEXT_PRIMARY, wordWrap='CJK', leftIndent=16,
                          spaceAfter=3)
S_CAPTION = ParagraphStyle('Caption', fontName='SimHei', fontSize=8.5, leading=12,
                           textColor=TEXT_MUTED, alignment=TA_CENTER,
                           spaceBefore=3, spaceAfter=6, wordWrap='CJK')
S_TH = ParagraphStyle('TH', fontName=HEAD_FONT, fontSize=9.5, leading=13,
                      textColor=colors.white, alignment=TA_CENTER, wordWrap='CJK')
S_TD = ParagraphStyle('TD', fontName='SimHei', fontSize=9, leading=13,
                      textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap='CJK')
S_TDC = ParagraphStyle('TDC', parent=S_TD, alignment=TA_CENTER)
S_QUOTE = ParagraphStyle('Quote', fontName='SimHei', fontSize=10, leading=16.5,
                         textColor=TEXT_PRIMARY, leftIndent=24, wordWrap='CJK',
                         spaceBefore=6, spaceAfter=6)
S_STAT = ParagraphStyle('Stat', fontName=HEAD_FONT, fontSize=20, leading=24,
                        textColor=ACCENT, alignment=TA_CENTER, wordWrap='CJK')
S_STATL = ParagraphStyle('StatL', fontName='SimHei', fontSize=8.5, leading=12,
                         textColor=TEXT_MUTED, alignment=TA_CENTER, wordWrap='CJK')
S_CODE = ParagraphStyle('Code', fontName='SimHei', fontSize=9, leading=14,
                        textColor=TEXT_PRIMARY, wordWrap='CJK', leftIndent=10)
S_TOC0 = ParagraphStyle('TOC0', fontName=HEAD_FONT, fontSize=12, leading=20, leftIndent=6)
S_TOC1 = ParagraphStyle('TOC1', fontName='SimHei', fontSize=10, leading=16, leftIndent=28)
S_TOCTITLE = ParagraphStyle('TocTitle', fontName=HEAD_FONT, fontSize=18, leading=26,
                            textColor=TEXT_PRIMARY, spaceAfter=12)


class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            self.notify('TOCEntry', (getattr(flowable, 'bookmark_level', 0),
                                     getattr(flowable, 'bookmark_text', ''),
                                     self.page, getattr(flowable, 'bookmark_key', '')))


def heading(text, level=0):
    key = 'h_%s' % hashlib.md5(text.encode()).hexdigest()[:8]
    style = S_H1 if level == 0 else (S_H2 if level == 1 else S_BODY)
    p = Paragraph('<a name="%s"/><b>%s</b>' % (key, text), style)
    p.bookmark_name = text
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    return p


def h1_block(text):
    return [CondPageBreak(H1_ORPHAN), heading(text, 0),
            HRFlowable(width='100%', thickness=1.2, color=ACCENT,
                       spaceBefore=0, spaceAfter=10)]


def body(text):
    return Paragraph(text, S_BODY)


def bullet(text):
    return Paragraph('• ' + text, S_BULLET)


def safe_keep(elements):
    total_h = 0
    for el in elements:
        w, h = el.wrap(AVAIL_W, PAGE_H)
        total_h += h
    if total_h <= MAX_KEEP_HEIGHT:
        return [KeepTogether(elements)]
    elif len(elements) >= 2:
        return [KeepTogether(elements[:2])] + list(elements[2:])
    return list(elements)


def make_table(header, rows, ratios, caption=None, center_cols=None):
    center_cols = center_cols or set()
    data = [[Paragraph('<b>%s</b>' % c, S_TH) for c in header]]
    for r in rows:
        data.append([Paragraph(str(c), S_TDC if j in center_cols else S_TD)
                     for j, c in enumerate(r)])
    widths = [x * AVAIL_W for x in ratios]
    t = Table(data, colWidths=widths, hAlign='CENTER', repeatRows=1)
    style = [('BACKGROUND', (0, 0), (-1, 0), ACCENT),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('GRID', (0, 0), (-1, -1), 0.4, TEXT_MUTED),
             ('LEFTPADDING', (0, 0), (-1, -1), 6),
             ('RIGHTPADDING', (0, 0), (-1, -1), 6),
             ('TOPPADDING', (0, 0), (-1, -1), 4),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]
    for i in range(1, len(data)):
        style.append(('BACKGROUND', (0, i), (-1, i),
                      BG_SURFACE if i % 2 == 0 else colors.white))
    t.setStyle(TableStyle(style))
    out = [Spacer(1, 10), t]
    if caption:
        out += [Spacer(1, 4), Paragraph(caption, S_CAPTION)]
    out.append(Spacer(1, 8))
    return out


def callout_row(items):
    cells = []
    for b, l in items:
        ct = Table([[Paragraph('<b>%s</b>' % b, S_STAT)],
                    [Paragraph(l, S_STATL)]], colWidths=[170])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_SURFACE),
            ('BOX', (0, 0), (-1, -1), 1, ACCENT),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('TOPPADDING', (0, -1), (-1, -1), 2)]))
        cells.append(ct)
    t = Table([cells], colWidths=[AVAIL_W / len(items)] * len(items), hAlign='CENTER')
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    return [Spacer(1, 8), t, Spacer(1, 8)]


def embed_fig(path, caption, max_h=240):
    max_w = AVAIL_W * 0.82
    pw, ph = PILImage.open(path).size
    ratio = min(max_w / pw, max_h / ph, 1.0)
    img = Image(path, width=pw * ratio, height=ph * ratio)
    img.hAlign = 'CENTER'
    return safe_keep([img, Paragraph(caption, S_CAPTION)])


def quote(text):
    t = Table([[Paragraph(text, S_QUOTE)]], colWidths=[AVAIL_W - 10])
    t.setStyle(TableStyle([
        ('LINEBEFORE', (0, 0), (0, -1), 2, ACCENT),
        ('BACKGROUND', (0, 0), (-1, -1), BG_PAGE),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    return [Spacer(1, 6), t, Spacer(1, 6)]


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('SimHei', 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 14, '保肝中药成分虚拟筛选课题 · 暑假阶段报告汇总（第一阶段）')
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.2)
    canvas.line(MARGIN, PAGE_H - MARGIN + 8, PAGE_W - MARGIN, PAGE_H - MARGIN + 8)
    canvas.setStrokeColor(TEXT_MUTED)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, MARGIN - 16, PAGE_W - MARGIN, MARGIN - 16)
    canvas.setFont('SimHei', 7.5)
    canvas.drawString(MARGIN, MARGIN - 28, '课题组：王启龙 宁显泷 衣思淼 代维斯丹 王散曼')
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 28, '第 %d 页' % doc.page)
    canvas.restoreState()


story = []
story.append(Paragraph('<b>目 录</b>', S_TOCTITLE))
toc = TableOfContents()
toc.levelStyles = [S_TOC0, S_TOC1]
story.append(toc)
story.append(PageBreak())

# ── 1 概述 ──
story.extend(h1_block('1 第一阶段概述'))
story.append(body('课题总目标是构建"中药成分 → 图神经网络活性预测（含不确定性）→ 分子对接验证 → 协同评分"的'
                  '虚拟筛选流水线。按两阶段规划（见 docs/PHASE_PLAN.md），暑假为第一阶段：用六周时间在本地'
                  '零依赖环境完成流程搭建与小样本全链路跑通，产出可复核的阶段结果；数据上量、真实对接与实验衔接'
                  '安排在下学期五个工作包中执行。'))
story.append(body('本报告是第一阶段的汇总材料，内容取自仓库各总结文件：中期报告、三次组会纪要、数据字典与模型说明、'
                  '对接说明、文献支撑库，以及两阶段规划、全文件清单与核验手册，逐文件路径见 docs/MANIFEST.md。'
                  '全部数字可通过 docs/VERIFY_MANUAL.md 的步骤独立复算。'))
story.extend(callout_row([('6 周', '三段式执行周期'),
                          ('100 条', '数据体系（88带标签+12筛选池）'),
                          ('60 个', '候选分子协同排名'),
                          ('45 项', '独立数字校验全通过')]))
story.append(heading('1.1 阶段目标达成情况', 1))
story.extend(make_table(
    ['节点', '计划目标', '达成', '证据'],
    [['W2末', '环境统一，小样本端到端跑通', '达成', 'docs/minutes/week1-2.md'],
     ['W4末', '模型输出均值+方差，基准线可并表', '达成', 'docs/minutes/week3-4.md'],
     ['W6末', '排名总表+机制溯源+中期材料', '达成', 'docs/minutes/week5-6.md'],
     ['W6末', '结果可独立复算', '达成', 'verify.py 45项全过']],
    [0.12, 0.42, 0.12, 0.34], center_cols={2}, caption='表 1-1 第一阶段节点对照'))

# ── 2 组织与分工 ──
story.extend(h1_block('2 组织分工与协作机制'))
story.append(heading('2.1 成员人设与职责', 1))
story.extend(make_table(
    ['成员', '人设', '第一阶段主责模块', '第二阶段去向'],
    [['王启龙', '工程支撑', '仓库/环境/一键运行、适用域预警集成、结果自动化、报告汇编', 'WP1 复现核验工程化'],
     ['宁显泷', '算法', 'SMILES转图解析器、GNN+MC Dropout、损失权重选择', 'WP4 模型升级与校准'],
     ['衣思淼', '数据', '清洗/骨架划分/描述符、适用域边界、协同评分融合规则', 'WP3 数据扩充'],
     ['代维斯丹', '验证', '双基准线、双靶点对接（演示模式）、可靠性评估', 'WP2 真实对接'],
     ['王散曼', '化学信息与文献', '种子候选池与证据标注、新分子池、机制溯源与药效团', 'WP5 文献深化与实验衔接']],
    [0.11, 0.15, 0.50, 0.24], caption='表 2-1 成员×人设×模块（与 CONTRIBUTORS.md、文件头署名一致）'))
story.append(heading('2.2 版本与过程管理', 1))
story.append(body('git 仓库共12次提交、5位作者署名，提交归属与分工矩阵一一对应；联合任务按"主责+协作"双署名'
                  '（如适用域=衣思淼定边界+王启龙写预警代码）。三次组会纪要留档了各节点验收结论与关键决议，'
                  '包括不确定性方案二选一、损失权重选择规则、阳性参照药排名偏低的原因分析等。'))

# ── 3 过程纪要 ──
story.extend(h1_block('3 六周执行纪要'))
story.extend(make_table(
    ['时段', '关键动作', '关键决议/问题'],
    [['W1-2', '零依赖环境定案；解析器完成；48+40种子池交付；首版22条三萜SMILES环号错误修复', '稠环SMILES逐原子核对环号后入库；CSV统一UTF-8'],
     ['W3-4', '全量清洗与骨架划分，MC Dropout定型（对比集成后选定），双基准线与新分子池12条交付', 'ECE偏高如实记录待校准；奥贝胆酸排名低确认为适用域机制而非错误'],
     ['W5-6', '模型冻结批量推理；协同评分矩阵；4张结果图；药效团归纳；中期材料闭环', '排名自动化定稿；演示对接明确标注待服务器复算']],
    [0.10, 0.48, 0.42], caption='表 3-1 三次组会要点（详见 docs/minutes/）'))

# ── 4 数据体系 ──
story.extend(h1_block('4 数据体系成果'))
story.append(heading('4.1 数据构成与标签口径', 1))
story.extend(make_table(
    ['子集', '数量', '构成与用途'],
    [['保肝活性分子（HP）', '48', '黄酮/三萜/木脂素/蒽醌/环烯醚萜苷/生物碱/香豆素等；证据分级A(3)/B/C'],
     ['负参照（DC）', '40', '惰性小分子+无证据西药+经典肝毒性药物（对乙酰氨基酚、异烟肼等难负样本）'],
     ['新分子筛选池（NV）', '12', '三萜6+二萜1+木脂素4+甾体酸阳性参照1（奥贝胆酸）'],
     ['骨架级划分', '53组', 'train 58（正28）/ val 13（正8）/ test 17（正12），同骨架不跨集合']],
    [0.24, 0.10, 0.66], center_cols={1}, caption='表 4-1 数据体系（清洗后88条带标签+12条筛选池）'))
story.append(body('标签口径为"是否存在保肝活性的公开证据"（二分类），非活性强度。清洗管线五步：解析校验→'
                  '规范化去重→Murcko骨架签名→描述符计算→骨架级划分。剔除记录即使在零剔除时也落盘留痕，留痕文件为 data/processed/rejected.csv。'))
story.append(heading('4.2 描述符与适用域', 1))
story.append(body('7维二维描述符（MW/logP_est/TPSA_est/nHBD/nHBA/nRot/nAromSystems）为演示口径，'
                  '槲皮素MW实测302.24与真实值一致；适用域采用训练集描述符杠杆值法，阈值h*=3p/n=0.362，'
                  '域外分子在排名中打标并乘0.9预警降权。'))

# ── 5 方法成果 ──
story.extend(h1_block('5 方法成果'))
story.append(heading('5.1 分子图表征与GNN', 1))
story.append(body('自研纯Python SMILES解析器（无RDKit依赖）把分子转为图，节点特征13维；'
                  '两层GCN（对称归一化邻接）接均值池化与Dropout，sigmoid输出保肝概率。'
                  '不确定性采用MC Dropout：推理保持Dropout前向30次，取概率均值为预测、方差为不确定性度量'
                  '（组会对比模型集成后选定，零额外训练成本）。'))
story.extend(make_table(
    ['w_pos', '1.0', '1.25（选用）', '1.5'],
    [['验证集F1', '0.625', '0.667', '0.667']],
    [0.31, 0.23, 0.23, 0.23], center_cols={1, 2, 3}, caption='表 5-1 加权BCE正类权重实验'))
story.append(heading('5.2 基准线与对接演示', 1))
story.append(body('双基准线：描述符+高斯朴素贝叶斯、2048bit哈希指纹+逻辑回归。指纹采用MD5哈希保证跨平台'
                  '确定性。两条线先于模型出分保证可对比。对接为演示模式：FXR(1OSH)与Keap1(2FLU)双靶点盒子参数已定，'
                  '本地以物理启发打分占位（自检区分度：活性-5.46 对 负参照-5.05 kcal/mol），'
                  '服务器端run_vina.sh复算后直接覆盖，下游无需改动。'))
story.append(heading('5.3 协同评分融合', 1))
story.append(Paragraph('final = 0.45×模型分×(0.5+0.5×置信) + 0.35×对接名次分 + 0.20×类药性分，'
                        '域外分子再乘0.9；置信度=1-min(1, √方差/0.25)。', S_BODY_NI))

# ── 6 阶段结果 ──
story.extend(h1_block('6 阶段结果'))
story.append(heading('6.1 模型对比', 1))
story.extend(make_table(
    ['模型', 'AUC', 'ACC', 'BACC', 'F1'],
    [['高斯朴素贝叶斯（描述符）', '0.850', '0.706', '0.733', '0.762'],
     ['逻辑回归（2048bit指纹）', '0.967', '0.706', '0.792', '0.737'],
     ['GNN + MC Dropout（本课题）', '0.967', '0.824', '0.875', '0.857']],
    [0.40, 0.15, 0.15, 0.15, 0.15], center_cols={1, 2, 3, 4},
    caption='表 6-1 测试集指标（n=17，正12；骨架级划分）'))
story.append(body('不确定性质量：方差与误差的Spearman相关ρ=0.718；校准偏差ECE=0.210（模型偏过自信），'
                  '已列入WP4温度校准任务。两个方法论发现：其一，阳性参照药奥贝胆酸模型分仅0.26且域外——'
                  '训练集是中药化学空间，甾体骨架不在其中，说明模型分只在域内可解释、三源融合必要；其二，'
                  '全场最高模型分与最低方差（大黄素/苦参碱）都不在Top-10内，对接与类药性约束了总评。'))
story.extend(embed_fig(os.path.join(FIG, 'reliability_diagram.png'),
                       '图 6-1 可靠性图（ECE=0.210，过自信可见）'))
story.extend(embed_fig(os.path.join(FIG, 'uncertainty_vs_error.png'),
                       '图 6-2 方差与误差正相关（ρ=0.718）'))
story.append(heading('6.2 协同排名（60候选）', 1))
story.extend(make_table(
    ['排名', '候选', '类别', '模型分', '方差', '置信', '对接', '总评'],
    [['1', '黄芩苷', '黄酮苷', '0.9612', '0.0012', '0.863', '-6.86', '0.9291'],
     ['2', '二氢杨梅素', '黄酮醇', '0.9653', '0.0017', '0.837', '-7.14', '0.8990'],
     ['3', '葛根素', '异黄酮苷', '0.9614', '0.0018', '0.832', '-7.03', '0.8903'],
     ['4', '姜黄素', '多酚', '0.8898', '0.0050', '0.718', '-6.94', '0.8821'],
     ['5', '柚皮素', '黄烷酮', '0.9413', '0.0021', '0.815', '-6.54', '0.8811'],
     ['6', '木犀草素', '黄酮', '0.9783', '0.0008', '0.887', '-6.43', '0.8704'],
     ['7', '水飞蓟宾', '黄酮木脂素', '0.9666', '0.0011', '0.869', '-6.39', '0.8497'],
     ['8', '松脂素（新）', '呋喃木脂素', '0.8814', '0.0068', '0.670', '-6.64', '0.8397'],
     ['9', '槲皮素', '黄酮醇', '0.9718', '0.0031', '0.776', '-6.37', '0.8198'],
     ['10', '落叶松脂素（新）', '开环木脂素', '0.7912', '0.0097', '0.606', '-6.89', '0.8181']],
    [0.09, 0.19, 0.14, 0.12, 0.11, 0.11, 0.11, 0.13],
    center_cols={0, 3, 4, 5, 6, 7}, caption='表 6-2 协同评分Top-10（单位：对接为kcal/mol）'))
story.extend(embed_fig(os.path.join(FIG, 'top_candidates.png'),
                       '图 6-3 Top-15候选总评条形图', max_h=250))
story.extend(embed_fig(os.path.join(FIG, 'model_dock_scatter.png'),
                       '图 6-4 模型分与对接分一致性（叉号=域外）', max_h=220))
story.append(heading('6.3 药效团归纳', 1))
story.extend(make_table(
    ['药效团要素', '命中', '对应机制'],
    [['多酚羟基特征（每分子至少2个酚羟基）', '10/10（6/10含间/邻二酚）', '抗氧化；Keap1口袋氢键网络'],
     ['双芳香环体系', '10/10', 'FXR疏水口袋π堆积'],
     ['C6-C3-C6或木脂素二聚骨架', '9/10（姜黄素例外）', '刚性疏水核心+极性锚点'],
     ['三萜酸C-28羧基+3β-OH', '独立支线', 'FXR胆酸口袋等排（奥贝胆酸路径）']],
    [0.36, 0.22, 0.42], center_cols={1}, caption='表 6-3 Top-10药效团要素（详见literature/03）'))

# ── 7 质量保证 ──
story.extend(h1_block('7 质量保证与复核机制'))
story.append(body('三条证据链支撑结果可信度：（1）确定性——全流程随机种子固定，连续两次运行的14个结果文件'
                  'md5完全一致；（2）独立可复算——verify.py不导入项目代码，从CSV独立重算45项被引用数字全部'
                  '一致（含AUC 0.967、ρ 0.718、Top-10全部单元格）；（3）诚实性分级——演示对接分、教学版SMILES、'
                  '整理稿文献均已显式标注，列入下学期复核任务。'))
story.extend(make_table(
    ['事项', '状态', '复核方式'],
    [['模型指标/不确定性/适用域/评分', '本地真实计算', 'run_all.py 复现 + verify.py 45项核验'],
     ['对接评分', '演示模式占位', 'WP2 服务器Vina复算覆盖'],
     ['种子集SMILES', '教学复现版（三萜有简化）', 'WP3 数据库正式导出替换'],
     ['文献引用', '调研整理稿', 'WP5 逐条核对原文附PMID']],
    [0.34, 0.28, 0.38], caption='表 7-1 结果诚实性分级（复核责任已排入工作包）'))

# ── 8 交付物与文件地图 ──
story.extend(h1_block('8 交付物与文件地图'))
story.extend(make_table(
    ['目录', '内容', '负责人', '核验入口'],
    [['data/', '原始/清洗/划分数据（8个CSV）', '王散曼/衣思淼', 'VERIFY_MANUAL §3.4'],
     ['src/', '五人模块代码（13个py）', '五人各自', 'VERIFY_MANUAL §3.1-3.3'],
     ['results/', '指标/预测/对接/AD/排名/图', '各自模块', 'verify.py'],
     ['docs/', '数据字典/模型/对接说明+纪要+规划/清单/手册', '王启龙汇编', 'MANIFEST.md'],
     ['literature/', '证据库/新分子调研/机制溯源', '王散曼', 'lit/01逐条溯源'],
     ['reports/', '中期报告+详解PDF+本报告', '王启龙', '抽查数字与CSV一致'],
     ['phase2_semester/', '下学期五个工作包', '各自主责', 'WP内验收标准']],
    [0.18, 0.36, 0.16, 0.30], caption='表 8-1 交付物地图（逐文件核验方法见 docs/MANIFEST.md）'))

# ── 9 下学期衔接 ──
story.extend(h1_block('9 下学期工作衔接'))
story.extend(make_table(
    ['工作包', '内容', '周次', '主责', '核验人'],
    [['WP1', '复现核验与基线固化（v1.0标签）', '1-2', '王启龙', '全员'],
     ['WP2', '真实分子对接（Vina替换演示分）', '3-6', '代维斯丹', '宁显泷'],
     ['WP3', '数据扩充与正式库导出（≥1000条）', '3-8', '衣思淼', '王散曼'],
     ['WP4', '模型升级与校准（PyG/温度校准ECE小于0.10）', '7-10', '宁显泷', '衣思淼'],
     ['WP5', '文献深化与实验衔接（松脂素/落叶松脂素优先）', '9-16', '王散曼', '代维斯丹']],
    [0.10, 0.44, 0.10, 0.16, 0.20], center_cols={0, 2}, caption='表 9-1 第二阶段工作包（详见 phase2_semester/）'))
story.append(body('执行原则：每个工作包完成后由核验人按包内验收标准逐条打勾签字；WP1是全员入口——'
                  '先证明暑假结果可复现再动新东西；新文件必须在 MANIFEST.md 登记后才算交付。'))

# ── 附录 ──
story.extend(h1_block('附录 人工核验十分钟路径'))
story.append(Paragraph('cd hepato-gnn-screening && python run_all.py', S_CODE))
story.append(Paragraph('python reports/pdf_build/verify.py', S_CODE))
story.append(body('前者约6秒跑完全流程，控制台关键数字见 docs/VERIFY_MANUAL.md §2.1（逐字对照）；'
                  '后者输出"通过45项；不符0项"。两步通过即完成暑假结果的机器核验，'
                  '人工逐模块核验按手册§3执行（约40分钟）。'))
story.append(Spacer(1, 14))
story.append(Paragraph('第一阶段完 · 交接下学期',
                       ParagraphStyle('End', parent=S_CAPTION, fontSize=10)))

doc = TocDocTemplate(
    OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN + 6, bottomMargin=MARGIN + 10,
    title='保肝中药成分虚拟筛选课题·暑假阶段报告汇总',
    author='Z.ai', creator='Z.ai',
    subject='第一阶段（暑假）报告材料汇总：分工、过程、结果、复核与下学期衔接')
doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
print('body_phase1.pdf built:', OUT)
