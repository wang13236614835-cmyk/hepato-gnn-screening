# -*- coding: utf-8 -*-
"""通用 Markdown -> PDF 批量转换器（覆盖本仓库 md 子集：
标题/表格/列表/引用/代码块/粗体/复选框）。内部工作文档版式：
无大封面，首页为紧凑标题区 + 分隔线，页脚页码。"""
import os
import re
import sys

PDF_SKILL_DIR = r"C:\Users\user\.zcode\cli\plugins\cache\zcode-plugins-official\document-skills\0.1.0\skills\pdf"
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, "scripts"))

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

ROOT = r"D:\zcode-workspace\hepato-gnn-screening"
OUTROOT = os.path.join(ROOT, "reports", "pdf_all")

ACCENT = colors.HexColor('#1f7692')
TEXT_PRIMARY = colors.HexColor('#1b1a18')
TEXT_MUTED = colors.HexColor('#7a766f')
BG_SURFACE = colors.HexColor('#e5e3df')

pdfmetrics.registerFont(TTFont('SimHei', r'C:\Windows\Fonts\simhei.ttf'))
try:
    pdfmetrics.registerFont(TTFont('Microsoft YaHei', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('Microsoft YaHei-Bold', r'C:\Windows\Fonts\msyhbd.ttc', subfontIndex=0))
    registerFontFamily('Microsoft YaHei', normal='Microsoft YaHei', bold='Microsoft YaHei-Bold')
    HEAD = 'Microsoft YaHei'
except Exception:
    registerFontFamily('Microsoft YaHei', normal='SimHei', bold='SimHei')
    HEAD = 'SimHei'
pdfmetrics.registerFont(TTFont('Times New Roman', r'C:\Windows\Fonts\times.ttf'))
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')

from pdf import install_font_fallback  # noqa: E402
install_font_fallback()

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
AVAIL_W = PAGE_W - 2 * MARGIN

S_TITLE = ParagraphStyle('T', fontName=HEAD, fontSize=19, leading=27,
                         textColor=ACCENT, spaceAfter=4, wordWrap='CJK')
S_META = ParagraphStyle('M', fontName='SimHei', fontSize=9, leading=13,
                        textColor=TEXT_MUTED, spaceAfter=2, wordWrap='CJK')
S_H2 = ParagraphStyle('H2', fontName=HEAD, fontSize=13.5, leading=19,
                      textColor=TEXT_PRIMARY, spaceBefore=13, spaceAfter=5, wordWrap='CJK')
S_H3 = ParagraphStyle('H3', fontName=HEAD, fontSize=11, leading=16,
                      textColor=TEXT_PRIMARY, spaceBefore=9, spaceAfter=3, wordWrap='CJK')
S_BODY = ParagraphStyle('B', fontName='SimHei', fontSize=10, leading=16.5,
                        textColor=TEXT_PRIMARY, wordWrap='CJK', spaceAfter=5)
S_BULLET = ParagraphStyle('BU', fontName='SimHei', fontSize=10, leading=16,
                          textColor=TEXT_PRIMARY, wordWrap='CJK', leftIndent=14,
                          spaceAfter=2.5)
S_QUOTE = ParagraphStyle('Q', fontName='SimHei', fontSize=9.5, leading=15.5,
                         textColor=TEXT_PRIMARY, wordWrap='CJK', leftIndent=12)
S_CODE = ParagraphStyle('C', fontName='SimHei', fontSize=8.8, leading=13.2,
                        textColor=TEXT_PRIMARY, wordWrap='CJK')
S_TH = ParagraphStyle('TH', fontName=HEAD, fontSize=8.8, leading=12.5,
                      textColor=colors.white, alignment=TA_LEFT, wordWrap='CJK')
S_TD = ParagraphStyle('TD', fontName='SimHei', fontSize=8.6, leading=12.5,
                      textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap='CJK')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'<font color="#1f7692">\1</font>', s)
    return s


def code_block(lines):
    inner = [Paragraph(inline(l) if l.strip() else '&nbsp;', S_CODE) for l in lines]
    t = Table([[inner]], colWidths=[AVAIL_W - 6])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_SURFACE),
        ('LINEBEFORE', (0, 0), (0, -1), 2, ACCENT),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    return [Spacer(1, 4), t, Spacer(1, 4)]


def md_table(rows):
    header = [c.strip() for c in rows[0].strip().strip('|').split('|')]
    body = []
    for r in rows[1:]:
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
            continue
        while len(cells) < len(header):
            cells.append('')
        body.append(cells[:len(header)])
    data = [[Paragraph('<b>%s</b>' % inline(h), S_TH) for h in header]]
    for r in body:
        data.append([Paragraph(inline(c), S_TD) for c in r])
    widths = [AVAIL_W / len(header)] * len(header)
    t = Table(data, colWidths=widths, hAlign='CENTER', repeatRows=1)
    st = [('BACKGROUND', (0, 0), (-1, 0), ACCENT),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('GRID', (0, 0), (-1, -1), 0.4, TEXT_MUTED),
          ('LEFTPADDING', (0, 0), (-1, -1), 5),
          ('RIGHTPADDING', (0, 0), (-1, -1), 5),
          ('TOPPADDING', (0, 0), (-1, -1), 3.5),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]
    for i in range(1, len(data)):
        st.append(('BACKGROUND', (0, i), (-1, i), BG_SURFACE if i % 2 == 0 else colors.white))
    t.setStyle(TableStyle(st))
    return [Spacer(1, 8), t, Spacer(1, 8)]


def convert(md_path, pdf_path, meta_line):
    lines = open(md_path, encoding='utf-8').read().split('\n')
    story = []
    title = None
    i = 0
    first_h1_done = False
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith('```'):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i].replace('\t', '    '))
                i += 1
            story.extend(code_block(block))
        elif ln.startswith('|') and i + 1 < len(lines) and lines[i + 1].startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].startswith('|'):
                tbl.append(lines[i])
                i += 1
            story.extend(md_table(tbl))
            continue
        elif ln.startswith('# ') and not first_h1_done:
            title = ln[2:].strip()
            story.append(Paragraph('<b>%s</b>' % inline(title), S_TITLE))
            story.append(HRFlowable(width='100%', thickness=1.2, color=ACCENT,
                                    spaceBefore=2, spaceAfter=6))
            story.append(Paragraph(inline(meta_line), S_META))
            story.append(Spacer(1, 6))
            first_h1_done = True
        elif ln.startswith('### '):
            story.append(Paragraph('<b>%s</b>' % inline(ln[4:]), S_H3))
        elif ln.startswith('## '):
            story.append(Paragraph('<b>%s</b>' % inline(ln[3:]), S_H2))
        elif ln.startswith('# '):
            story.append(Paragraph('<b>%s</b>' % inline(ln[2:]), S_H2))
        elif ln.startswith('> '):
            q = Paragraph(inline(ln[2:]), S_QUOTE)
            qt = Table([[q]], colWidths=[AVAIL_W - 6])
            qt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#edecea')),
                ('LINEBEFORE', (0, 0), (0, -1), 2, TEXT_MUTED),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
            story.extend([Spacer(1, 4), qt, Spacer(1, 4)])
        elif re.match(r'^\s*[-*] \[[ xX]\] ', ln):
            txt = re.sub(r'^\s*[-*] \[[ xX]\] ', '', ln)
            mark = '☑' if re.search(r'\[[xX]\]', ln) else '□'
            story.append(Paragraph('%s %s' % (mark, inline(txt)), S_BULLET))
        elif re.match(r'^\s*[-*] ', ln):
            story.append(Paragraph('• ' + inline(re.sub(r'^\s*[-*] ', '', ln)), S_BULLET))
        elif re.match(r'^\s*\d+\. ', ln):
            story.append(Paragraph(inline(ln.strip()), S_BULLET))
        elif ln.strip():
            story.append(Paragraph(inline(ln.strip()), S_BODY))
        i += 1

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('SimHei', 7.5)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawString(MARGIN, PAGE_H - MARGIN + 14,
                          (title or os.path.basename(md_path))[:60])
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(1.2)
        canvas.line(MARGIN, PAGE_H - MARGIN + 8, PAGE_W - MARGIN, PAGE_H - MARGIN + 8)
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 24, '第 %d 页' % doc.page)
        canvas.restoreState()

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN + 6, bottomMargin=MARGIN + 8,
        title=(title or os.path.basename(md_path)) + '（PDF版）',
        author='Z.ai', creator='Z.ai', subject=meta_line)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


META = {
    'README.md': '项目总览 | 负责人：王启龙 | 阶段：第一阶段（暑假）',
    'CONTRIBUTORS.md': '贡献与分工映射 | 负责人：王启龙 | 阶段：总纲',
    'docs/00_environment.md': '环境配置 | 负责人：王启龙 | 阶段：第一阶段（暑假）',
    'docs/01_data_dictionary.md': '数据字典 | 负责人：衣思淼 | 阶段：第一阶段（暑假）',
    'docs/02_model_notes.md': '模型说明 | 负责人：宁显泷 | 阶段：第一阶段（暑假）',
    'docs/03_docking_protocol.md': '对接流程 | 负责人：代维斯丹 | 阶段：第一阶段（暑假）',
    'docs/PHASE_PLAN.md': '两阶段总规划 | 负责人：王启龙 | 阶段：总纲',
    'docs/MANIFEST.md': '全文件清单 | 负责人：王启龙 | 阶段：总纲',
    'docs/VERIFY_MANUAL.md': '人工核验手册 | 负责人：王启龙 | 阶段：总纲',
    'docs/VERIFY_TASKS.md': '人工校验任务分派表 | 负责人：王启龙 | 阶段：总纲（宁代码·龙辅助·衣+代数据·曼文献）',
    'docs/MEMBER_WORKBENCH.md': '全员工作台·按人导航 | 负责人：王启龙 | 阶段：总纲（五人全名分节）',
    'docs/minutes/week1-2.md': '组会纪要 | 记录：王启龙 | 阶段：第一阶段（W1-2）',
    'docs/minutes/week3-4.md': '组会纪要 | 记录：王启龙 | 阶段：第一阶段（W3-4）',
    'docs/minutes/week5-6.md': '组会纪要 | 记录：王启龙 | 阶段：第一阶段（W5-6）',
    'literature/01_classic_evidence.md': '经典证据库 | 负责人：王散曼 | 阶段：第一阶段（暑假）',
    'literature/02_novel_terpenes_lignans.md': '新分子调研 | 负责人：王散曼 | 阶段：第一阶段（暑假）',
    'literature/03_top_candidate_mechanisms.md': '机制溯源 | 负责人：王散曼 | 阶段：第一阶段（暑假）',
    'phase2_semester/WP1_verify_baseline.md': '工作包 | 主责：王启龙 | 阶段：第二阶段（第1-2周）',
    'phase2_semester/WP2_real_docking.md': '工作包 | 主责：代维斯丹 | 阶段：第二阶段（第3-6周）',
    'phase2_semester/WP3_data_expansion.md': '工作包 | 主责：衣思淼 | 阶段：第二阶段（第3-8周）',
    'phase2_semester/WP4_model_upgrade.md': '工作包 | 主责：宁显泷 | 阶段：第二阶段（第7-10周）',
    'phase2_semester/WP5_experiment_bridge.md': '工作包 | 主责：王散曼 | 阶段：第二阶段（第9-16周）',
    'phase2_semester/推进程序_负责人_王启龙.md': '负责人16周推进程序 | 主责：王启龙 | 阶段：第二学期',
    'tools/使用说明_学期推进流exe.md': 'exe 使用说明 | 主责：王启龙 | 阶段：工具层',
    'reports/midterm_report.md': '中期考核报告 | 汇编：王启龙 | 阶段：第一阶段（暑假）',
    'docs/personal/00_工作量与成果总表.md': '工作量与成果总表 | 负责人：王启龙 | 阶段：两阶段',
    'docs/personal/P1_王启龙.md': '个人工作档案 | 王启龙 | 阶段：两阶段',
    'docs/personal/P2_宁显泷.md': '个人工作档案 | 宁显泷 | 阶段：两阶段',
    'docs/personal/P3_衣思淼.md': '个人工作档案 | 衣思淼 | 阶段：两阶段',
    'docs/personal/P4_代维斯丹.md': '个人工作档案 | 代维斯丹 | 阶段：两阶段',
    'docs/personal/P5_王散曼.md': '个人工作档案 | 王散曼 | 阶段：两阶段',
}

if __name__ == '__main__':
    targets = sys.argv[1:] or list(META.keys())
    for rel in targets:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(OUTROOT, rel.replace('/', os.sep).replace('.md', '.pdf'))
        convert(src, dst, META[rel])
        print('OK', rel, '->', os.path.relpath(dst, ROOT))
