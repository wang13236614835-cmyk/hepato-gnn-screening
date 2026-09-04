# -*- coding: utf-8 -*-
"""SOP 步骤 2 · 结构-口袋-redock 门控(RMSD < 2 Å 才允许进入批量对接)

受体: PDB 清洗(留蛋白 ATOM 链, 去水/去共晶配体) -> mk_prepare_receptor(gasteiger)
盒子: 共晶配体包络 + 6 Å 外扩(课程 6 章共晶配体法: 配体范围外扩 4-6 Å)
redock: 共晶配体原位坐标 -> meeko pdbqt -> Vina(exh=16, seed=42) -> GetBestRMS
用法: python s2_prep_redock.py [--download]
"""
import json
import os
import re
import subprocess
import sys
import urllib.request

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, rdMolAlign
from meeko import MoleculePreparation, PDBQTWriterLegacy, PDBQTMolecule
from meeko.rdkit_mol_create import RDKitMolCreate

from common import DOCK, RES

RDLogger.DisableLog("rdApp.*")
PDBD = os.path.join(DOCK, "pdb")
RCP = os.path.join(DOCK, "receptors")
LGD = os.path.join(DOCK, "ligands")
OUT = os.path.join(DOCK, "outputs")
MKR = os.path.join(os.environ.get("APPDATA", ""), "Python", "Python312",
                   "Scripts", "mk_prepare_receptor.exe")
VINA = os.path.join(DOCK, "vina.exe")
STRUCTS = {"FXR_LBD": ("1OSH", "FEX"), "KEAP1_KELCH": ("4IQK", "IQK")}
PADDING = 6.0
AFF_RE = re.compile(r"^\s+\d+\s+(-?\d+\.\d+)\s+")
MK = MoleculePreparation()


def download(pdb_id):
    dst = os.path.join(PDBD, f"{pdb_id}.pdb")
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        return dst
    urllib.request.urlretrieve(f"https://files.rcsb.org/download/{pdb_id}.pdb", dst)
    return dst


def split_pdb(path, keep_lig):
    """蛋白链(ATOM/TER, 无水无配体) + 参考配体 HETATM 坐标。"""
    prot, lig = [], []
    for l in open(path):
        if l.startswith(("ATOM", "TER")):
            prot.append(l)
        elif l.startswith("HETATM") and l[17:20].strip() == keep_lig:
            lig.append(l)
    return "".join(prot), "".join(lig)


def ligand_center_size(lig_block, padding):
    c = np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])]
                  for l in lig_block.splitlines()])
    center = c.mean(0).round(2).tolist()
    size = (c.max(0) - c.min(0) + 2 * padding).round(1).tolist()
    return center, size


def run_vina(receptor_pdbqt, lig_pdbqt, out_pdbqt, box, exh=16, cpu=4):
    cmd = [VINA, "--receptor", receptor_pdbqt, "--ligand", lig_pdbqt, "--out", out_pdbqt,
           "--center_x", str(box["center"][0]), "--center_y", str(box["center"][1]),
           "--center_z", str(box["center"][2]),
           "--size_x", str(box["size"][0]), "--size_y", str(box["size"][1]),
           "--size_z", str(box["size"][2]),
           "--exhaustiveness", str(exh), "--seed", "42", "--num_modes", "9",
           "--cpu", str(cpu)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600,
                       errors="ignore")
    affs = [float(AFF_RE.match(l).group(1)) for l in r.stdout.splitlines() if AFF_RE.match(l)]
    return (affs[0] if affs else None), r


def pdbqt_from_mol(m, path):
    setups = MK(m)
    s, ok, _ = PDBQTWriterLegacy.write_string(setups[0])
    if not ok:
        return False
    open(path, "w").write(s)
    return True


def mol_from_pdb_block(block):
    m = Chem.MolFromPDBBlock(block, removeHs=False, proximityBonding=True)
    return Chem.AddHs(m, addCoords=True) if m else None


def rmsd_first_pose(out_pdbqt, crystal_sdf):
    txt = open(out_pdbqt).read()
    first = "MODEL" + txt.split("MODEL")[1].split("ENDMDL")[0] + "ENDMDL\n"
    pmol = PDBQTMolecule(first, skip_typing=True)
    mol = RDKitMolCreate.from_pdbqt_mol(pmol)[0]
    pose = Chem.RemoveHs(mol)
    ref = Chem.RemoveHs(next(iter(Chem.SDMolSupplier(crystal_sdf, removeHs=False))))
    return float(rdMolAlign.GetBestRMS(pose, ref))


def run(download_structures=True):
    for d in (RCP, LGD, OUT):
        os.makedirs(d, exist_ok=True)
    boxes, gate = {}, {}
    for name, (pdb_id, ligname) in STRUCTS.items():
        if download_structures:
            download(pdb_id)
        raw = os.path.join(PDBD, f"{pdb_id}.pdb")
        prot, lig_block = split_pdb(raw, ligname)
        assert lig_block, f"{pdb_id} 未找到共晶配体 {ligname}"
        clean = os.path.join(RCP, f"{name}_{pdb_id}_clean.pdb")
        open(clean, "w").write(prot + "END\n")
        lig_pdb = os.path.join(RCP, f"{name}_{pdb_id}_{ligname}_lig.pdb")
        open(lig_pdb, "w").write(lig_block + "END\n")

        center, size = ligand_center_size(lig_block, PADDING)
        boxes[name] = {"pdb": pdb_id, "ligand": ligname, "center": center, "size": size}
        print(f"[s2] {name}({pdb_id}): 盒子 center={center} size={size} (配体包络+{PADDING}Å)")

        receptor_pdbqt = os.path.join(RCP, f"{name}_{pdb_id}.pdbqt")
        if not os.path.exists(receptor_pdbqt):
            r = subprocess.run([MKR, "--read_pdb", clean, "-o",
                                os.path.join(RCP, f"{name}_{pdb_id}"), "-p",
                                "--charge_model", "gasteiger"],
                               capture_output=True, text=True, timeout=600)
            if not os.path.exists(receptor_pdbqt):
                sys.exit(f"[s2] 受体制备失败 {name}: {r.stderr[-300:]}")

        # 共晶配体 -> 3D 分子 -> redock 输入 + 晶体参照(SDF)
        m = mol_from_pdb_block(lig_block)
        crystal_sdf = os.path.join(RCP, f"{name}_{pdb_id}_{ligname}_crystal.sdf")
        w = Chem.SDWriter(crystal_sdf); w.write(m); w.close()
        lq = os.path.join(LGD, f"{name}_{ligname}_redock.pdbqt")
        assert pdbqt_from_mol(m, lq), f"{name} redock 配体制备失败"

        out_pdbqt = os.path.join(OUT, f"{name}_{ligname}_redock_out.pdbqt")
        aff, _ = run_vina(receptor_pdbqt, lq, out_pdbqt, boxes[name], exh=16)
        rms = rmsd_first_pose(out_pdbqt, crystal_sdf)
        gate[name] = {"ligand": ligname, "affinity": aff, "rmsd": round(rms, 3),
                      "pass_gate": bool(rms < 2.0)}
        print(f"[s2] redock 门控 {name}/{ligname}: aff={aff} RMSD={rms:.2f}Å "
              f"-> {'PASS' if rms < 2.0 else 'FAIL'}")

    json.dump(boxes, open(os.path.join(DOCK, "boxes.json"), "w"), indent=1)
    with open(os.path.join(DOCK, "redock_gate.json"), "w", encoding="utf-8") as f:
        json.dump(gate, f, ensure_ascii=False, indent=1)
    n_pass = sum(g["pass_gate"] for g in gate.values())
    print(f"[s2] 门控通过 {n_pass}/{len(gate)};盒子存至 docking/boxes.json")
    if n_pass < len(gate):
        print("[s2] 警告: 存在未过门控靶点, 后续对接结果仅作参考")
    return boxes, gate


if __name__ == "__main__":
    run("--nodownload" not in sys.argv)
