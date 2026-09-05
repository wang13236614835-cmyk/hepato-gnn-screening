"""Retry failures; reuse only content- and parameter-matched successful poses."""
import json
from pathlib import Path
import meeko
from rdkit import __version__ as rdkit_version
from common import DOCK,RES,VINA,load_candidates,write_csv
from provenance import cache_key,digest,read_metadata,write_metadata
from redock import run_vina

def reusable(meta,key,output):
    return (meta.get("key")==key and meta.get("status")=="success" and
            meta.get("score") is not None and Path(output).exists() and
            meta.get("pose_hash")==digest(output))

def run():
    from s4_dock import prefilter,embed_and_prep
    boxes=read_metadata(Path(DOCK)/"boxes.json");gate=read_metadata(Path(DOCK)/"redock_gate.json")
    if not boxes:raise ValueError("缺少当前运行的对接盒子")
    for target,box in boxes.items():
        receptor=Path(DOCK)/"receptors"/f"{target}_{box['pdb']}.pdbqt";g=gate.get(target,{})
        if not(g.get("pass_gate") and g.get("rmsd_method")=="CalcRMS_no_alignment" and g.get("independent_start") and g.get("box")==box and g.get("receptor_hash")==digest(receptor)):
            raise ValueError(f"{target}缺少与当前输入匹配的有效门控")
    prefilter();rows=[];state=Path(RES)/"tables/docking_real_scores.csv"
    for r in load_candidates():
        cid=r["compound_id"];lq=Path(DOCK)/"ligands"/f"{cid}.pdbqt";lq.parent.mkdir(parents=True,exist_ok=True)
        lp=Path(str(lq)+".cache.json");meta=read_metadata(lp)
        lk=cache_key([],{"smiles":r["smiles"],"rdkit":rdkit_version,"meeko":meeko.__version__,"seed":42,"method":"ETKDGv3-MMFF94s","source":digest(Path(__file__).with_name("s4_dock.py"))})
        try:
            if not(lq.exists() and meta.get("key")==lk and meta.get("output_hash")==digest(lq)):
                embed_and_prep(r["smiles"],lq)
                write_metadata(lp,{"key":lk,"output_hash":digest(lq)})
        except Exception as e:
            for target in boxes:rows.append({"compound_id":cid,"name_cn":r["name_cn"],"target":target,"affinity_kcal_mol":"","note":f"PREP_FAIL:{type(e).__name__}:{e}"})
            write_csv(state,rows);continue
        for target,box in boxes.items():
            receptor=Path(DOCK)/"receptors"/f"{target}_{box['pdb']}.pdbqt";op=Path(DOCK)/"outputs"/f"{cid}_{target}_out.pdbqt";op.parent.mkdir(parents=True,exist_ok=True)
            cp=Path(str(op)+".cache.json");meta=read_metadata(cp)
            key=cache_key([receptor,lq,VINA,Path(__file__).with_name("redock.py")],{"box":box,"exhaustiveness":8,"seed":42,"cpu":4,"num_modes":9})
            try:
                if reusable(meta,key,op):score=meta["score"];note="cached_verified"
                else:
                    score,_=run_vina(receptor,lq,op,box,exh=8);note="computed"
                    write_metadata(cp,{"key":key,"status":"success","score":score,"pose_hash":digest(op)})
            except Exception as e:
                score="";note=f"DOCK_FAIL:{type(e).__name__}:{e}"
                write_metadata(cp,{"key":key,"status":"failed","error":note})
            rows.append({"compound_id":cid,"name_cn":r["name_cn"],"target":target,"affinity_kcal_mol":score,"note":note})
            write_csv(state,rows)
    if not any(r["affinity_kcal_mol"]!="" for r in rows):raise RuntimeError("本轮无成功对接，不能生成排名")
    return rows
