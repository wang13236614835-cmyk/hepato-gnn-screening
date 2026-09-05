"""Numerical and governance regression checks. Passing does not validate biology."""
import ast,copy,csv,datetime,hashlib,importlib.util,json,os,subprocess,sys,tempfile,traceback
from pathlib import Path
from types import SimpleNamespace
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'final-aidd-screening/src'))
import common, s3_model
from rdkit import Chem
from rdkit.Chem import AllChem,rdMolAlign,rdMolDescriptors
from provenance import cache_key,digest
checks=[]
def check(name,fn):
 try:detail=fn();checks.append({'name':name,'passed':True,'detail':detail})
 except Exception as e:checks.append({'name':name,'passed':False,'detail':str(e)});traceback.print_exc()
def gradients():
 tree=ast.parse((ROOT/'src/models/gnn.py').read_text(encoding='utf-8-sig'))
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='GCN');ns={'np':np}
 exec(compile(ast.Module(body=[cls],type_ignores=[]),'<legacy GCN class>','exec'),ns)
 rng=np.random.default_rng(11);a=np.array([[1,1,0],[1,1,1],[0,1,1]],float);d=a.sum(1);a=a/np.sqrt(np.outer(d,d))
 rec=SimpleNamespace(A=a,X=rng.normal(size=(3,4)),g=SimpleNamespace(atoms=[1,2,3]))
 errs={}
 for tag,C in [('final',s3_model.GCN),('legacy',ns['GCN'])]:
  maximum=0.;count=0
  for seed in [9,13]:
   net=C(d_in=4,d_hid=5,d_out=3,seed=seed);initial=copy.deepcopy(net.rng.bit_generator.state)
   z,cache=net.forward_graph(rec,True);grads=net.backward_graph(rec,1.,cache)
   for k in net.params:
    arr=getattr(net,k)
    for idx in np.ndindex(arr.shape):
     old=arr[idx];h=1e-5;arr[idx]=old+h;net.rng.bit_generator.state=copy.deepcopy(initial);plus=net.forward_graph(rec,True)[0]
     arr[idx]=old-h;net.rng.bit_generator.state=copy.deepcopy(initial);minus=net.forward_graph(rec,True)[0];arr[idx]=old
     error=abs((plus-minus)/(2*h)-grads[k][idx]);maximum=max(maximum,error);count+=1
  assert maximum<1e-7,(tag,maximum);errs[tag]={'max_abs_error':maximum,'coordinates':count}
 assert not np.allclose(a.sum(1),1),'nonregular symmetric normalization counterexample'
 return errs
def rmsd():
 m=Chem.AddHs(Chem.MolFromSmiles('CCO'));assert AllChem.EmbedMolecule(m,randomSeed=12)==0;m=Chem.RemoveHs(m);p=Chem.Mol(m)
 for i in range(p.GetNumAtoms()):v=p.GetConformer().GetAtomPosition(i);p.GetConformer().SetAtomPosition(i,(v.x+5,v.y,v.z))
 fixed=rdMolAlign.CalcRMS(p,m);aligned=rdMolAlign.GetBestRMS(p,m)
 assert abs(fixed-5)<1e-6 and aligned<1e-6
 return {'translation_angstrom':5,'fixed_RMSD':fixed,'aligned_RMSD':aligned}
def ccd():
 import redock
 data=json.loads((ROOT/'final-aidd-screening/data/ccd_templates.json').read_text(encoding='utf-8'));out={}
 for target,(pdb,lig) in redock.STRUCTS.items():
  _,block=redock.split_pdb(ROOT/'final-aidd-screening/docking/pdb'/f'{pdb}.pdb',lig)
  m=redock.mol_from_pdb_block(block,lig);f=rdMolDescriptors.CalcMolFormula(m)
  assert f==data[lig]['formula'].replace(' ',''),(lig,f,data[lig]);out[lig]=f
 return out
def cache():
 from batch_docking import reusable
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'input';f.write_text('a');key=cache_key([f],{'seed':42});meta={'key':key,'status':'success','score':-1,'pose_hash':digest(f)}
  assert reusable(meta,key,f);assert not reusable(dict(meta,status='failed'),key,f)
  assert not reusable(meta,cache_key([f],{'seed':43}),f)
  f.write_text('b');assert not reusable(meta,key,f);assert key!=cache_key([f],{'seed':42})
 return 'Content/parameter/output changes invalidate success cache; failures never reused.'
def data():
 os.environ.pop('HEPATO_DATA_MODE',None)
 try:common.load_registry()
 except ValueError:pass
 else:raise AssertionError('Unreviewed registry was released')
 os.environ['HEPATO_DATA_MODE']='proposed';rows=common.load_registry();assert len(rows)==100
 assert all(r['identity_status']=='pending_review' for r in rows)
 assert all(r['label_status']=='unresolved' for r in rows)
 assert len({r['compound_id'] for r in rows})==100
 return {'count':len(rows),'default_unreviewed_run':'blocked_as_expected','mode':'diagnostic_only'}
def split():
 with tempfile.TemporaryDirectory() as td:
  old=s3_model.SPLITS;s3_model.SPLITS=td
  try:s3_model.make_splits()
  finally:s3_model.SPLITS=old
  files=list(Path(td).glob('*.csv'));assert len(files)==3
  groups=[];allids=[]
  for f in files:
   rows=common.read_csv(f);groups.append({common.scaffold_smiles(common.mol_of(r['smiles'])) for r in rows});allids.extend(r['compound_id'] for r in rows)
  assert len(allids)==88==len(set(allids))
  assert all(not(groups[i]&groups[j]) for i in range(3) for j in range(i))
 return '88 historical labels, canonical Murcko groups disjoint; not MASH labels.'
def plan():
 p=json.loads((ROOT/'docs/project_plan.json').read_text(encoding='utf-8'));assert len(p['tasks'])==10 and len({t['id'] for t in p['tasks']})==10
 assert p['semester_start']=='2026-08-24' and len(p['weeks'])==2
 for t in p['tasks']:
  assert datetime.date.fromisoformat(t['due']).weekday()==4
  assert t['reviewer']!=t['member'] and (ROOT/t['artifact']).exists()
 assert {t['week'] for t in p['tasks']}=={1,2}
 assert max(c['week'] for c in p['course'])==2 and len(p['course'])==8
 for m in p['members']:
  page=(ROOT/m['name']/f"打卡_{m['name']}.html").read_text(encoding='utf-8')
  assert '__PLAN_JSON__' not in page and '__NAME_JSON__' not in page
 return '10 two-week evidence tasks, Friday deadlines, 8 course modules by W2, 5 pages.'
def syntax():
 paths=list((ROOT/'final-aidd-screening/src').glob('*.py'))+[ROOT/'final-aidd-screening/run_revised.py',ROOT/'tools/semester_flow.py',ROOT/'tools/gen_member_pages.py']
 for f in paths:ast.parse(f.read_text(encoding='utf-8-sig'))
 return len(paths)
def fusion_contract():
 import s5_fuse_select as s
 with tempfile.TemporaryDirectory() as td:
  base=Path(td);res=base/'results';dock=base/'docking';(res/'metrics').mkdir(parents=True);dock.mkdir()
  (dock/'boxes.json').write_text(json.dumps({'T1':{},'T2':{}}))
  candidates=[{'compound_id':cid,'name_cn':cid,'category':'fixture','smiles':smiles,'role':'positive_control' if cid=='CTRL' else 'candidate'} for cid,smiles in [('A','CCO'),('B','CCN'),('MISSING','c1ccccc1'),('CTRL','CCCC')]]
  common.write_csv(str(res/'predictions/fullpool_predictions.csv'),[{'compound_id':r['compound_id'],'pred_mean':.8,'pred_var':.01,'in_domain':1} for r in candidates])
  common.write_csv(str(res/'tables/prefilter_report.csv'),[{'compound_id':r['compound_id'],'lipinski_violations':0,'pains_alert':''} for r in candidates])
  common.write_csv(str(res/'tables/docking_real_scores.csv'),[{'compound_id':r['compound_id'],'target':t,'affinity_kcal_mol':-8} for r in candidates for t in (['T1'] if r['compound_id']=='MISSING' else ['T1','T2'])])
  previous=(s.RES,s.DOCK,s.load_candidates);s.RES=str(res);s.DOCK=str(dock);s.load_candidates=lambda:candidates
  try:rows,picked=s.run()
  finally:s.RES,s.DOCK,s.load_candidates=previous
  assert {r['compound_id'] for r in rows}=={'A','B'}
  assert rows[0]['final_score']==rows[1]['final_score']
 return 'Incomplete dual-target candidates and controls excluded; ties get identical scores; output generated.'
def main():
 for name,fn in [('fixed_mask_gradients',gradients),('no_alignment_RMSD',rmsd),('CCD_chemical_identity',ccd),('cache_invalidation',cache),('unreviewed_data_block',data),('canonical_scaffold_isolation',split),('plan_and_pages',plan),('python_syntax',syntax),('fusion_eligibility_and_ties',fusion_contract)]:check(name,fn)
 result={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'software_passed':all(c['passed'] for c in checks),'scientific_validation':'not_granted','wetlab_ready':False,'checks':checks}
 out=ROOT/'results/validation/software_checks.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['software_passed'] else 1
if __name__=='__main__':sys.exit(main())
