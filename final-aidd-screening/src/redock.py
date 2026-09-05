"""CCD化学、独立初始构象、固定受体坐标RMSD；门控用多种子稳定判据。

门控政策（预注册口径，防单种子侥幸/误伤）：5个独立起始种子(42,7,123,2026,555)，
每个种子独立ETKDG构象+Vina(exh=16)；过门需 ≥3/5 种子 RMSD<2A 且中位数<2A。
全部种子RMSD无论过否都写入 redock_gate.json；不过门即中止，不降低门槛重试。
"""
import json,os,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
import numpy as np
from rdkit import Chem,__version__ as rdkit_version
from rdkit.Chem import AllChem,rdMolAlign
from meeko import MoleculePreparation,PDBQTWriterLegacy,PDBQTMolecule
from meeko.rdkit_mol_create import RDKitMolCreate
from common import DOCK,SOURCE_DOCK,DATA,VINA
from provenance import cache_key,digest,read_metadata,write_metadata
PDBD=Path(DOCK)/"pdb";RCP=Path(DOCK)/"receptors";LGD=Path(DOCK)/"ligands";OUT=Path(DOCK)/"outputs"
STRUCTS={"FXR_LBD":("1OSH","FEX"),"KEAP1_KELCH":("4IQK","IQK")}
_active=os.environ.get("HEPATO_TARGETS")  # 仅诊断用途：单靶子集跑下游；正式研究须双靶全过门
if _active:STRUCTS={k:v for k,v in STRUCTS.items() if k in _active.split(",")}
GATE_SEEDS=[42,7,123,2026,555]
GATE_POLICY="pass if >=3/5 seeds RMSD<2A and median RMSD<2A; all seeds recorded"

def download(pdb_id):
    PDBD.mkdir(parents=True,exist_ok=True);dst=PDBD/f"{pdb_id}.pdb";source=Path(SOURCE_DOCK)/"pdb"/dst.name
    if not dst.exists():
        if source.exists():shutil.copy2(source,dst)
        else:urllib.request.urlretrieve(f"https://files.rcsb.org/download/{pdb_id}.pdb",dst)
    return dst

def split_pdb(path,keep_lig):
    lines=Path(path).read_text().splitlines(True)
    lig=[l for l in lines if l.startswith("HETATM") and l[17:20].strip()==keep_lig]
    instances={(l[21:22],l[22:27]) for l in lig}
    if len(instances)!=1:raise ValueError(f"{keep_lig}需要唯一共晶实例，当前{instances}")
    serials={int(l[6:11]) for l in lig}
    conn=[l for l in lines if l.startswith("CONECT") and int(l[6:11]) in serials]
    return "".join(l for l in lines if l.startswith(("ATOM","TER"))),"".join(lig+conn)

def ligand_center_size(block,padding=6.):
    xyz=np.array([[float(l[30:38]),float(l[38:46]),float(l[46:54])] for l in block.splitlines() if l.startswith("HETATM")])
    return xyz.mean(0).round(2).tolist(),(xyz.max(0)-xyz.min(0)+2*padding).round(1).tolist()

def mol_from_pdb_block(block,ligand):
    cc=json.loads((Path(DATA)/"ccd_templates.json").read_text(encoding="utf-8"))[ligand]
    ref=Chem.MolFromSmiles(cc["smiles"]);m=Chem.MolFromPDBBlock(block+"END\n",removeHs=False,proximityBonding=False)
    if m is None:raise ValueError("共晶读取失败")
    m=AllChem.AssignBondOrdersFromTemplate(ref,m);Chem.RemoveStereochemistry(m)
    if Chem.MolToSmiles(m,isomericSmiles=False)!=Chem.MolToSmiles(ref,isomericSmiles=False):raise ValueError("共晶与CCD不一致")
    return Chem.AddHs(m,addCoords=True)

def pdbqt_from_mol(m,path):
    setup=MoleculePreparation()(m)[0];text,ok,error=PDBQTWriterLegacy.write_string(setup)
    if not ok:raise ValueError(error)
    Path(path).write_text(text);return True

def run_vina(receptor,ligand,out,box,exh=16,cpu=4,seed=42):
    cmd=[VINA,"--receptor",str(receptor),"--ligand",str(ligand),"--out",str(out)]
    for key in ("center","size"):
        for axis,value in zip("xyz",box[key]):cmd += [f"--{key}_{axis}",str(value)]
    cmd += ["--exhaustiveness",str(exh),"--seed",str(seed),"--num_modes","9","--cpu",str(cpu)]
    result=subprocess.run(cmd,capture_output=True,text=True,errors="replace",timeout=1200)
    Path(str(out)+".log").write_text(result.stdout+"\n"+result.stderr,encoding="utf-8")
    match=re.search(r"^\s+1\s+(-?[\d.]+)\s+",result.stdout,re.M)
    if result.returncode or not match or not Path(out).exists():raise RuntimeError(f"Vina失败rc={result.returncode}，见{out}.log")
    write_metadata(str(out)+".run.json",{"command":cmd,"returncode":result.returncode})
    return float(match[1]),result

def rmsd_first_pose(out,crystal_sdf):
    txt=Path(out).read_text();first="MODEL"+txt.split("MODEL")[1].split("ENDMDL")[0]+"ENDMDL\n"
    pose=Chem.RemoveHs(RDKitMolCreate.from_pdbqt_mol(PDBQTMolecule(first,skip_typing=True))[0])
    ref=Chem.RemoveHs(next(iter(Chem.SDMolSupplier(str(crystal_sdf),removeHs=False))))
    return float(rdMolAlign.CalcRMS(pose,ref))

def run(download_structures=True,independent_start=True,seeds=GATE_SEEDS):
    for d in (PDBD,RCP,LGD,OUT):d.mkdir(parents=True,exist_ok=True)
    boxes={};gate={}
    for target,(pdb,lig) in STRUCTS.items():
        raw=download(pdb);prot,block=split_pdb(raw,lig)
        clean=RCP/f"{target}_{pdb}_clean.pdb";clean.write_text(prot+"END\n")
        receptor=RCP/f"{target}_{pdb}.pdbqt";meta=Path(str(receptor)+".cache.json")
        import meeko
        key=cache_key([clean],{"charge":"gasteiger","meeko":meeko.__version__});prior=read_metadata(meta)
        if not (receptor.exists() and prior.get("key")==key and prior.get("output_hash")==digest(receptor)):
            mkr=os.environ.get("MEEKO_RECEPTOR_BIN") or shutil.which("mk_prepare_receptor.py") or shutil.which("mk_prepare_receptor.exe")
            cmd=([mkr] if mkr else [sys.executable,"-m","meeko.cli.mk_prepare_receptor"])+["--read_pdb",str(clean),"-o",str(receptor.with_suffix("")),"-p","--charge_model","gasteiger"]
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=600)
            Path(str(receptor)+".log").write_text(result.stdout+"\n"+result.stderr,encoding="utf-8")
            if result.returncode or not receptor.exists():raise RuntimeError(f"受体制备失败{target}；见{receptor}.log")
            write_metadata(meta,{"key":key,"output_hash":digest(receptor)})
        center,size=ligand_center_size(block);box={"pdb":pdb,"ligand":lig,"center":center,"size":size};boxes[target]=box
        mol=mol_from_pdb_block(block,lig);ref=RCP/f"{target}_{pdb}_{lig}_crystal.sdf"
        w=Chem.SDWriter(str(ref));w.write(mol);w.close()
        seed_rmsd={};seed_aff={}
        for s in seeds:
            initial=Chem.Mol(mol)
            if independent_start:
                initial.RemoveAllConformers();params=AllChem.ETKDGv3();params.randomSeed=s
                if AllChem.EmbedMolecule(initial,params)!=0:raise ValueError(f"{lig}独立构象失败(seed={s})")
                AllChem.MMFFOptimizeMolecule(initial,maxIters=500)
            lq=LGD/f"{target}_{lig}_redock_s{s}.pdbqt";pdbqt_from_mol(initial,lq)
            op=OUT/f"{target}_{lig}_redock_s{s}_out.pdbqt";aff,_=run_vina(receptor,lq,op,box,seed=s)
            seed_rmsd[s]=rmsd_first_pose(op,ref);seed_aff[s]=aff
            print(f"{target} seed={s}: RMSD={seed_rmsd[s]:.4f} angstrom, score={aff}",flush=True)
        rmsds=sorted(seed_rmsd.values());median=float(np.median(rmsds));n_pass=sum(1 for r in rmsds if r<2)
        best_seed=min(seed_rmsd,key=seed_rmsd.get)
        context=cache_key([receptor,ref,Path(DATA)/"ccd_templates.json",VINA],{"box":box,"seeds":list(seeds),"exh":16,"rdkit":rdkit_version})
        gate[target]={"ligand":lig,"rmsd":median,"rmsd_method":"CalcRMS_no_alignment",
            "rmsd_by_seed":{str(k):v for k,v in seed_rmsd.items()},"affinity_by_seed":{str(k):v for k,v in seed_aff.items()},
            "n_pass_seeds":n_pass,"n_seeds":len(seeds),"policy":GATE_POLICY,
            "affinity":seed_aff[best_seed],"pass_gate":bool(n_pass>=3 and median<2),
            "independent_start":independent_start,"seed":list(seeds),"context":context,
            "receptor_hash":digest(receptor),"pose_hash":digest(OUT/f"{target}_{lig}_redock_s{best_seed}_out.pdbqt"),"box":box}
        print(f"{target}: 中位RMSD={median:.4f}, 过门种子 {n_pass}/{len(seeds)}, gate={'PASS' if gate[target]['pass_gate'] else 'FAIL'}",flush=True)
    write_metadata(Path(DOCK)/"boxes.json",boxes);write_metadata(Path(DOCK)/"redock_gate.json",gate)
    if not all(x["pass_gate"] for x in gate.values()):raise RuntimeError("至少一个靶点未过多种子门控，不执行生产筛选；全部种子RMSD见redock_gate.json")
    return boxes,gate

if __name__=="__main__":run()
