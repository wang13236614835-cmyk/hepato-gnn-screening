"""Portable checks of published GNN plans and inputs; never grants science approval."""
from pathlib import Path
import csv,hashlib,json,sys
from collections import Counter
from validate_current_sprint import validate_tasks

def verify(root):
 root=Path(root);docs=root/'docs';refs=json.loads((docs/'CURRENT_EXECUTION_20261015.json').read_text(encoding='utf-8'))
 errors=[]
 for name,sha in refs['files'].items():
  p=docs/name
  if Path(name).name!=name or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:errors.append('missing/stale registered input: '+name)
 def rows(name):
  with (docs/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
 tasks=rows('CURRENT_SPRINT_TASKS_20261012.csv');follow=rows('CURRENT_FOLLOWUP_TASKS_20261015.csv')
 errors+=validate_tasks(tasks,base=docs,schedule=refs.get('schedule_revision'))
 errors+=validate_tasks(follow,followup=True,base=docs,schedule=refs.get('schedule_revision'))
 inv=rows('CURRENT_CANDIDATE_INVENTORY_20261015.csv');cards=rows('W1_SCORING_CARDS_20261015.csv');queue=rows('REVERSE_SCREENING_QUEUE_20261015.csv')
 counts=Counter(r['source_track'] for r in inv)
 if counts!=dict(NATURAL_PRODUCTS=37,DRUG_REPURPOSING=5,EXTERNAL_LIBRARY=5):errors.append('candidate source count differs from registered 47-record snapshot')
 if len(cards)!=5 or len(queue)!=42:errors.append('scorecards/reverse queue coverage mismatch')
 if len({r['candidate_id'] for r in inv})!=len(inv):errors.append('duplicate candidate identity')
 for name in ['王启龙','宁显泷','衣思淼','代维斯丹','王散曼']:
  import re
  text=(root/name/f'打卡_{name}.html').read_text(encoding='utf-8');match=re.search(r'const WEEKS\s*=',text)
  weeks=json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]
  if [w['no'] for w in weeks]!=list(range(1,18)):errors.append(name+': native weekly coverage changed')
  if '10/19' not in str(weeks[6]) and '10月19' not in str(weeks[6]):errors.append(name+': research start not shifted')
 return {'file_consistency':'FAIL' if errors else 'PASS','errors':errors,'tasks':len(tasks),'followup_tasks':len(follow),'named_inputs':len(inv),'scorecards':len(cards),'not_screened':len(queue),'scientific_approval':'NOT_EVALUATED_BY_THIS_TOOL','scope':'PUBLISHED_REPO_ONLY_NO_EXTERNAL_ABSOLUTE_PATH_REQUIRED'}

if __name__=='__main__':
 try:result=verify(Path(__file__).resolve().parents[1])
 except Exception as e:result={'file_consistency':'FAIL','errors':[str(e)],'scientific_approval':'NOT_EVALUATED_BY_THIS_TOOL'}
 print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(result['file_consistency']!='PASS')
