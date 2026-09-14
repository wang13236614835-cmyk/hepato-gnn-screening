# -*- coding: utf-8 -*-
"""在负责人 HTML 模板上追加当前研究链和任务分层展示，不改变历史数据。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "王启龙" / "打卡_王启龙.html"

CHAIN = '''/* ---- 当前正式研究链（AIDD 主库只读投影；旧暑假管线见下方折叠区） ---- */
const RESEARCH_CHAIN={
 updated:"2026-09-14", current:4,
 steps:[
  ["① 历史结果核验","旧 Top-10、旧 AUC、旧 docking 和旧双靶结果保留为历史复核，不代表当前科研结论。","docs/PROJECT_STATUS.md","已完成"],
  ["② 数据/结构/终点审核","FASN canonical assay/provenance 已有资格资产；GNN 库结构注册表仍需人工核验。","00-当前研究/qualification_v1/RESEARCH_STATE.md","已完成·人工待核"],
  ["③ 模型公平比较","Ridge/XGB/RF/GNN 已在同折 benchmark；当前 GNN 未证明优于经典 baseline。","00-当前研究/qualification_v1/GNN_clean_benchmark_report.md","已完成"],
  ["④ 化学空间外推与泄漏审计","当前阶段：FASN Gate T1 待完成；外部泛化仍失败或受限。","00-当前研究/advancement_round_20260913/FASN_transferability_report.md","当前·受阻"],
  ["⑤ UQ/校准/适用域/拒判","既有 AD/UQ 结果保留；外部校准不足，不能替代外推资格。","00-当前研究/qualification_v1/FASN_AD_UQ_report.md","待执行"],
  ["⑥ CW-BCS 与天然产物应用","NP54 对 canonical 域外；不生成 FASN 天然产物排名。","00-当前研究/qualification_v1/NP54_FASN_domain_gap_report.md","待执行·受限"],
  ["⑦ 独立复现与图表/数据对账","按 manifest、hash 和人工记录复核，不把软件通过当科学放行。","00-当前研究/qualification_v1/QC_report.md","待执行"],
  ["⑧ 论文/审稿/投稿","投稿准备服从前置资格门；candidate_release=false。","00-当前研究/qualification_v1/RESEARCH_STATE.md","待执行·受门控"]
 ]
};

'''
CTX = {
    "stage": "pipeline revalidation（研究链重新核对）",
    "week": "W2｜2026-09-14–09-20",
    "why": "主库已经冻结研究状态；现在要收齐旧资产的保留/降级和人工核验，不能再用旧榜单推进。",
    "first": "打开 AIDD 主库状态和本库 RESEARCH_STATE，确认 candidate_release=false、GNN gated，再检查资产登记和组员待核记录。",
    "deliver": "提交状态/资产核验汇总：哪些已核、哪些待人工、哪些只是历史；不打新候选榜。",
    "action": "先看主库 qualification_v1 与资产保留轮",
    "action_url": "https://github.com/wang13236614835-cmyk/aidd/tree/main/00-%E5%BD%93%E5%89%8D%E7%A0%94%E7%A9%B6/qualification_v1",
    "source": "AIDD 主库 qualification_v1/RESEARCH_STATE.md + 本库 RESEARCH_STATE.md",
}

WORK = r'''function vPipeline(){
  const stages=RESEARCH_CHAIN.steps.map((x,i)=>{ const status=i+1===RESEARCH_CHAIN.current?'当前阶段':x[3]; const cls=i+1===RESEARCH_CHAIN.current?'tag b':(x[3].includes('受阻')?'tag r':(x[3].includes('完成')?'tag g':'tag y')); return `<tr class="${i+1===RESEARCH_CHAIN.current?'now':''}"><td><b>${esc(x[0])}</b></td><td>${esc(x[1])}</td><td>${linkPaths(x[2])}</td><td><span class="${cls}">${esc(status)}</span></td></tr>`; }).join('');
  const oldSteps=PIPELINE.steps.map(s=>`<tr><td><b>${esc(s[0])}</b></td><td>${esc(s[1])}</td><td><span class="cmd">${esc(s[2])}</span></td><td>${esc(s[3])}</td></tr>`).join('');
  const prog=PIPELINE.progress.map(p=>`<div class="item"><span class="tx"><b>${p[0]} ${esc(p[1])}</b>——${esc(p[2])}</span></div>`).join('');
  return `<div class="card current-task" style="border-left:4px solid var(--brand)"><h2>🧭 当前正式研究链（${RESEARCH_CHAIN.updated}）</h2><div class="kv">AIDD 主库是唯一正式科研状态源；本库负责方法学习、历史模型复核和组员任务。当前阶段突出显示，工具不能反过来决定科研阶段。</div><table><tr><th>阶段</th><th>现在的含义</th><th>状态/证据入口</th><th>状态</th></tr>${stages}</table><div class="hint">当前阻塞：FASN Gate T1（多 assay 对齐）待完成；GNN enable gate=closed；candidate_release=false。先阅读主库状态并按成员当前任务提交人工复核记录。</div></div><details class="card history-fold"><summary>历史暑假教学管线（保留用于复现，不代表当前科研结论）</summary><div class="kv">旧 Top-10、旧 AUC、旧双靶和 docking 排名只可作历史复核，不能直接转为当前候选。</div><table><tr><th>旧步骤</th><th>历史内容</th><th>代码/产物</th><th>状态</th></tr>${oldSteps}</table><div class="hint">历史复现：<span class="cmd">python run_all.py --legacy-demo</span>；默认入口只显示未放行状态。</div></details><details class="card history-fold"><summary>历史进度与核验记录</summary><div class="kv">历史进度保留作错误分析和复现入口，不作为当前研究链完成度。</div>${prog}</details>`;
}

'''
WORK = WORK.replace("\n", "\n")
VWORK = r'''function vMyWork(){
  const M=MYWORK; const C=M.currentContext||{};
  const tasks=M.tasks.map(t=>`<tr><td><span class="id">${t[0]}</span></td><td>${esc(t[1])}</td><td>${linkPaths(t[2])}</td></tr>`).join('');
  const files=M.files.map(g=>`<h3>${esc(g[0])}</h3><table>${g[1].map(r=>`<tr><td>${linkPaths(r[0])}</td><td>${esc(r[1])}</td></tr>`).join('')}</table>`).join('');
  const ops=M.ops.map(o=>`<div class="item"><span class="tx"><b>${esc(o[0])}</b>——${linkPaths(o[1])}</span></div>`).join('');
  const links=M.ghlinks.map(l=>`<div class="logline"><span class="t">${esc(l[0])}</span><a href="${l[1]}" target="_blank" rel="noopener">打开 ↗</a></div>`).join('');
  const team=M.team.map(t=>`<tr><td><b>${t[0]}</b></td><td>${esc(t[1])}</td><td><a class="cmd" href="../${esc(t[2])}">${esc(t[2])}</a></td></tr>`).join('');
  return `<div class="card current-task current-review-banner" style="border-left:4px solid var(--brand)"><h2>现在先做什么</h2><div class="kv"><b>${esc(C.week||'本周')}</b> ｜ 当前阶段：<b>${esc(C.stage||'pipeline revalidation')}</b></div><div class="grid current-task-grid"><div><h3>为什么现在做</h3><div class="lead">${esc(C.why||'')}</div></div><div><h3>第一步</h3><div class="lead">${esc(C.first||'')}</div></div><div><h3>做完交什么</h3><div class="lead">${esc(C.deliver||'')}</div></div></div>${C.action_url?`<div class="hint"><b>直达：</b><a class="pl" href="${C.action_url}" target="_blank" rel="noopener">${esc(C.action||'打开入口')}</a> ｜ 状态来源：${esc(C.source||'AIDD 主库')}</div>`:''}</div><div class="card history-boundary"><h2>先记住这件事</h2><div class="kv">本仓库是 <b>GNN 方法学习＋历史模型复核＋组员工作区</b>；AIDD 主库才是正式科研状态源。<b>candidate_release=false</b>，GNN 当前 gated。旧结果只作历史复核。</div></div><div class="card" style="border-left:4px solid var(--brand2)"><h2>🧭 ${esc(M.fullname)} 的工作台</h2><div class="kv"><b>${esc(M.fullname)}</b> ｜ ${esc(M.roleTag)} ｜ <span class="tag g">${esc(M.lineTag)}</span> ｜ 待核文件 <b>${M.fileCount}</b> 个 ｜ 时限 <b>${esc(M.deadline)}</b></div><div class="exp">职责：${esc(M.duty)}</div></div><details class="card history-fold"><summary>历史复核任务与技术参数（不代表当前科研结论）</summary><div class="kv">以下内容用于复现旧代码、学习和错误分析；旧指标不再是当前任务的通过门槛。</div><table><tr><th>编号</th><th>要做什么</th><th>过关口径</th></tr>${tasks}</table></details><details class="card history-fold"><summary>文件映射与操作细节</summary><h3>我的文件（共 ${M.fileCount} 个）</h3>${files}<h3>怎么操作</h3>${ops}</details><details class="card history-fold"><summary>仓库直链与全队入口</summary>${links}<table><tr><th>成员</th><th>角色·校验线</th><th>打卡页</th></tr>${team}</table></details>`;
}

'''

def replace_function(text: str, name: str, new_body: str, next_marker: str) -> str:
    start = text.index(f"function {name}(){{")
    end = text.index(next_marker, start)
    return text[:start] + new_body + text[end:]


def replace_const(text: str, name: str, new_content: str) -> str:
    import re
    match = re.search(rf"const\s+{re.escape(name)}\s*=\s*([\[{{])", text)
    if not match:
        raise ValueError(name)
    opening = match.group(1); closing = ']' if opening == '[' else '}'
    depth = 0; quote = None; escaped = False; close = None
    for i in range(match.start(1), len(text)):
        c = text[i]
        if quote:
            if escaped: escaped=False
            elif c == '\\': escaped=True
            elif c == quote: quote=None
            continue
        if c in "'\"`": quote=c; continue
        if c == opening: depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0: close=i; break
    if close is None: raise ValueError(f'unclosed {name}')
    return text[:match.start(1)+1] + new_content + text[close:]

s = PATH.read_text(encoding='utf-8')
if 'const RESEARCH_CHAIN=' not in s:
    marker = '/* ---- 全线研究流程与当前进度（final-aidd-screening，2026-09-04） ---- */'
    s = s.replace(marker, CHAIN + marker, 1)
s = replace_function(s, 'vPipeline', WORK, '/* ---- 我的工作台 ---- */')
# Replace vMyWork only in the template; generator will use this for all four member pages.
s = replace_function(s, 'vMyWork', VWORK, '/* ---- 本周看板 ---- */')
if 'currentContext:' not in s[s.index('const MYWORK = {'):s.index('const WEEKS', s.index('const MYWORK = {'))]:
    idx=s.index('const MYWORK = {'); end=s.index('\n};\n\n\nconst WEEKS',idx)
    obj=s[idx:end+3]
    obj=obj[:-3]+',\ncurrentContext:'+json.dumps(CTX,ensure_ascii=False,separators=(',',':'))+'\n};'
    s=s[:idx]+obj+s[end+3:]
PATH.write_text(s,encoding='utf-8')
print(PATH)
