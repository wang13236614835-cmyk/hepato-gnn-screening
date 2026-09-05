"""Generate five offline pages from the single reviewed project plan."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    plan=json.loads((ROOT/'docs/project_plan.json').read_text(encoding='utf-8'))
    template=(ROOT/'tools/templates/checkin.html').read_text(encoding='utf-8')
    payload=json.dumps(plan,ensure_ascii=False).replace('<','\\u003c')
    for member in plan['members']:
        name=member['name']
        html=template.replace('__NAME_JSON__',json.dumps(name,ensure_ascii=False)).replace('__NAME__',name).replace('__PLAN_JSON__',payload)
        (ROOT/name/f'打卡_{name}.html').write_text(html,encoding='utf-8')
    print('Generated 5 member pages; existing browser storage is unchanged.')
if __name__=='__main__':main()
