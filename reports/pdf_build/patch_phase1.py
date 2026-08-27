# -*- coding: utf-8 -*-
import io
p = r'D:\zcode-workspace\hepato-gnn-screening\reports\pdf_build\build_phase1.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    ("本报告是第一阶段的汇总材料，内容取自仓库各总结文件：中期报告（reports/midterm_report.md）、'\n                  '三次组会纪要（docs/minutes/）、数据字典与模型/对接说明（docs/）、文献支撑库（literature/），'\n                  '以及两阶段规划与核验手册。全部数字可通过 docs/VERIFY_MANUAL.md 的步骤独立复算。'",
     "本报告是第一阶段的汇总材料，内容取自仓库各总结文件：中期报告、三次组会纪要、数据字典与模型说明、'\n                  '对接说明、文献支撑库，以及两阶段规划、全文件清单与核验手册，逐文件路径见 docs/MANIFEST.md。'\n                  '全部数字可通过 docs/VERIFY_MANUAL.md 的步骤独立复算。'"),
    ("'骨架级划分；剔除记录零剔除时也落盘留痕'\n                  '（data/processed/rejected.csv）。'",
     "'骨架级划分。剔除记录即使在零剔除时也落盘留痕，留痕文件为 data/processed/rejected.csv。'"),
    ("['W3-4', '全量清洗与骨架划分；MC Dropout方案定型（对比集成）；双基准线出分；新分子池12条交付',",
     "['W3-4', '全量清洗与骨架划分，MC Dropout定型（对比集成后选定），双基准线与新分子池12条交付',"),
    ("story.append(body('双基准线：描述符+高斯朴素贝叶斯、2048bit哈希指纹+逻辑回归（MD5哈希保证跨平台确定性），'\n                  '先于模型出分保证可对比。对接为演示模式：FXR(1OSH)与Keap1(2FLU)双靶点盒子参数已定，'",
     "story.append(body('双基准线：描述符+高斯朴素贝叶斯、2048bit哈希指纹+逻辑回归。指纹采用MD5哈希保证跨平台'\n                  '确定性。两条线先于模型出分保证可对比。对接为演示模式：FXR(1OSH)与Keap1(2FLU)双靶点盒子参数已定，'"),
    ("story.append(Paragraph('—— 第一阶段完，交接下学期 ——',",
     "story.append(Paragraph('第一阶段完 · 交接下学期',"),
]
n = 0
for old, new in pairs:
    if old in s:
        s = s.replace(old, new)
        n += 1
    else:
        print('SKIP(not found):', old[:40].replace('\n', ' '))
io.open(p, 'w', encoding='utf-8').write(s)
print('patched', n, 'of', len(pairs))
