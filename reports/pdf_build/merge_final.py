# -*- coding: utf-8 -*-
"""合并 cover.pdf + body.pdf -> 最终交付 PDF（统一A4尺寸）"""
from pypdf import PdfReader, PdfWriter, Transformation

BUILD = r"D:\zcode-workspace\hepato-gnn-screening\reports\pdf_build"
FINAL = r"D:\zcode-workspace\hepato-gnn-screening\reports\课题详解与阶段结果说明.pdf"
A4_W, A4_H = 595.28, 841.89


def normalize_page_to_a4(page):
    box = page.mediabox
    w, h = float(box.width), float(box.height)
    if abs(w - A4_W) > 0.5 or abs(h - A4_H) > 0.5:
        sx, sy = A4_W / w, A4_H / h
        page.add_transformation(Transformation().scale(sx=sx, sy=sy))
        page.mediabox.lower_left = (0, 0)
        page.mediabox.upper_right = (A4_W, A4_H)
    return page


writer = PdfWriter()
cover = PdfReader(BUILD + r"\cover.pdf").pages[0]
writer.add_page(normalize_page_to_a4(cover))
for page in PdfReader(BUILD + r"\body.pdf").pages:
    writer.add_page(normalize_page_to_a4(page))
writer.add_metadata({
    '/Title': '保肝中药成分虚拟筛选课题·详解与阶段结果说明',
    '/Author': 'Z.ai', '/Creator': 'Z.ai',
    '/Subject': 'GNN+MC Dropout保肝中药成分虚拟筛选：方法详解与中期阶段结果',
})
with open(FINAL, 'wb') as f:
    writer.write(f)
print('merged ->', FINAL, '| pages =', len(writer.pages))
