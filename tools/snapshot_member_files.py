"""Historical snapshots are deliberately preserved; current files are linked."""
from gen_member_pages import ROOT
import json
if __name__=='__main__':
    plan=json.loads((ROOT/'docs/project_plan.json').read_text(encoding='utf-8'))
    for member in plan['members']:
        print(member['name']+': '+str(ROOT/member['name']/'工作台.md'))
    print('旧待核文件未覆盖。当前任务以工作台和 project_plan.json 为准。')
