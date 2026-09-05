"""Current evidence workflow; old flow_state.json remains read-only history."""
from pathlib import Path
import argparse,json,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--member',required=True);p.add_argument('action',choices=['dashboard','plan','next','check','record']);p.add_argument('--week',type=int,default=1);p.add_argument('--artifact');p.add_argument('--note');a=p.parse_args()
 plan=json.loads((ROOT/'docs/project_plan.json').read_text(encoding='utf-8'))
 if a.member not in {m['name'] for m in plan['members']}:p.error('成员不存在')
 if not 1<=a.week<=16:p.error('周次须为1–16')
 tasks=[t for t in plan['tasks'] if t['member']==a.member and (a.action=='plan' or t['week']==a.week)]
 state_path=ROOT/'learning'/a.member/'review_state_v2.json'
 if a.action=='check':return subprocess.call([sys.executable,str(ROOT/'tools/verify_research.py')])
 if a.action=='record':
  if not a.artifact or not a.note:p.error('提交需 --artifact 实际证据文件 与 --note 实测结果/限制')
  evidence=(ROOT/a.artifact).resolve()
  if not evidence.is_relative_to(ROOT) or not evidence.is_file():p.error('证据须为本库内已存在文件')
  body=evidence.read_text(encoding='utf-8',errors='replace') if evidence.suffix=='.md' else ''
  if '状态：未开始（模板）' in body:p.error('不能把未填写模板提交为证据')
  state=json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {'member':a.member,'schema_version':2,'tasks':{}}
  state['tasks'][tasks[0]['id']]={'artifact':a.artifact,'note':a.note,'status':'submitted_pending_review','at':datetime.datetime.now().isoformat()}
  state_path.parent.mkdir(parents=True,exist_ok=True);state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');print('已记录证据，待交叉复核；不自动放行研究。');return 0
 print(plan['verdict']);print('队长王启龙；MASH干实验在AIDD主线，GNN为暑假核验/学习。')
 for t in tasks:print(f"{t['id']} | {t['due']} | {t['title']}\n  证据: {t['artifact']} | 复核: {t['reviewer']}")
 print('本命令不读取旧flow_state.json作验收，不将模板或日期计为完成。');return 0
if __name__=='__main__':sys.exit(main())
