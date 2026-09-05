import hashlib
import json
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def cache_key(paths, config):
    data = {"inputs": [digest(p) for p in paths], "config": config}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def read_metadata(path):
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError): return {}

def write_metadata(path, data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(p)
