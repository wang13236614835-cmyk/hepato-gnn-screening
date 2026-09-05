"""科学运行需结构/标签复核。诊断独立输出，不构成湿实验放行。"""
import argparse,datetime,os,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diagnostic",action="store_true",help="建议结构+旧标签，仅调试")
    p.add_argument("--model",action="store_true",help="只建模，不对接、不融合")
    p.add_argument("--redock-only",action="store_true",help="仅共晶方法验证")
    p.add_argument("--output",type=Path,help="全新运行目录")
    a=p.parse_args()
    if a.model and a.redock_only:p.error("--model与--redock-only不可同时使用")
    here=Path(__file__).resolve().parent
    out=(a.output or here/"results/runs"/datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")).resolve()
    if out.exists() and any(out.iterdir()):p.error("输出目录非空，请使用新目录")
    os.environ["HEPATO_RUN_ROOT"]=str(out);os.environ["HEPATO_DATA_MODE"]="proposed" if a.diagnostic else "reviewed"
    sys.path.insert(0,str(here/"src"))
    from common import load_registry,REGISTRY
    from provenance import digest,write_metadata
    if not a.redock_only:
        try:load_registry()
        except ValueError as e:p.exit(2,str(e)+"\n")
    out.mkdir(parents=True,exist_ok=True)
    record={"mode":"redock_method_diagnostic" if a.redock_only else "proposed_structure_legacy_label_diagnostic" if a.diagnostic else "reviewed_data_computation","scientific_validation":"not_granted_by_this_run","wetlab_ready":False,"registry_sha256":digest(REGISTRY),"argv":sys.argv[1:],"status":"running"}
    record['source_sha256']={f.relative_to(here).as_posix():digest(f) for f in sorted((here/'src').glob('*.py'))}
    record['source_sha256']['run_revised.py']=digest(__file__)
    record['python']=sys.version
    write_metadata(out/"run_manifest.json",record)
    try:
        if a.redock_only:
            from s2_prep_redock import run
            run(independent_start=True)
        else:
            from s3_model import run as model
            model()
            if not a.model:
                from s1_target_profile import run as target
                from s2_prep_redock import run as redock
                from s4_dock import run as docking
                from s5_fuse_select import run as fuse
                from s6_report import run as report
                target();redock(independent_start=True);docking();fuse();report()
        record["status"]="completed"
    except BaseException as e:
        record.update(status="failed",error=f"{type(e).__name__}: {e}");raise
    finally:write_metadata(out/"run_manifest.json",record)
    print(f"计算记录：{out}。计算完成不等于研究有效性或湿实验放行。")

if __name__=="__main__":main()
