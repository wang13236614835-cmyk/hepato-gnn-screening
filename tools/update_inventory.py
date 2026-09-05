"""Snapshot local file bytes; existence is distinct from scientific review."""
from pathlib import Path
import argparse,csv,json,hashlib,subprocess
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path);a=p.parse_args();base=a.root.resolve();out=a.output or base/'docs/file_inventory.csv';out=out.resolve()
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=base).decode('utf-8').split('\0'));tracked.discard('');paths=set(tracked);rows=[]
 for f in base.rglob('*'):
  if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts or f.suffix in ['.pyc','.exe']:continue
  paths.add(f.relative_to(base).as_posix())
 excluded={out.relative_to(base).as_posix(),out.with_suffix('.json').relative_to(base).as_posix()}
 for rel in sorted(paths-excluded):
  f=base/rel;present=f.is_file();h=hashlib.sha256()
  if present:
   with f.open('rb') as stream:
    for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
  rows.append({'path':rel,'bytes':f.stat().st_size if present else '', 'sha256':h.hexdigest() if present else '', 'present':present,'tracked_before_snapshot':rel in tracked,'content_review':'not_implied_by_inventory'})
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8-sig',newline='') as stream:w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 result={'files':len(rows),'missing_tracked':[r['path'] for r in rows if not r['present'] and r['tracked_before_snapshot']],'meaning':'Local filesystem bytes at inventory generation; CRLF/LF checkout conversion can change hashes. Presence does not validate scientific content.','excluded':'Git metadata, pycache, untracked exe, inventory CSV/JSON themselves'}
 out.with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
