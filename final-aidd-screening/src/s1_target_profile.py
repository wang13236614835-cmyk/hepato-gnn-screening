# -*- coding: utf-8 -*-
"""SOP 步骤 1 · 选题与靶点档案(证据四栏: 遗传/功能/表达/安全)

靶点: FXR(胆汁酸核受体, 1OSH+fexaramine) 与 Keap1-Kelch(Nrf2 通路, 4IQK+小分子 IQK)。
说明: 两结构均携带小分子共晶配体, 满足课程要求的 redock 门控(RMSD<2Å)前提;
IQK 为占据 Nrf2 结合口袋的小分子抑制剂, 盒子即落在该口袋。
"""
import json
import os

from common import RES

TARGETS = {
    "FXR_LBD": {
        "pdb_id": "1OSH",
        "cocrystal_ligand": "FEX",
        "gene": "NR1H4",
        "uniprot": "Q96RI1",
        "role": "胆汁酸核受体——保肝/利胆经典靶点, 配体结合口袋为疏水型",
        "evidence": {
            "遗传": "FXR 激活改善胆汁淤积与脂肪变性;Nr1h4-/- 小鼠对胆汁酸损伤敏感",
            "功能": "调控 BSEP/SHP/CYP7A1, 抑制肝内脂肪合成与炎症通路",
            "表达": "肝/肠高表达(核受体组织分布经典数据)",
            "安全": "FXR 激动剂奥贝胆酸已上市(获 FDA 批准用于 PBC), 靶点成药性已被临床验证",
        },
        "pocket_type": "hydrophobic",
    },
    "KEAP1_KELCH": {
        "pdb_id": "4IQK",
        "cocrystal_ligand": "IQK",
        "gene": "KEAP1",
        "uniprot": "Q14145",
        "role": "Nrf2 通路人源负调控因子——氧化应激型肝损伤关键蛋白-蛋白界面",
        "evidence": {
            "遗传": "Keap1 敲低/Nrf2 激活小鼠对对乙酰氨基酚等肝毒物抵抗",
            "功能": "Kelch 区捕获 Nrf2 促其泛素化降解;阻断该界面即稳定 Nrf2、启动抗氧化应答",
            "表达": "全身广泛表达, 肝内含量高",
            "安全": "Nrf2 激动剂 dimethyl fumarate 已上市;直接 Kelch 界面抑制剂处于临床前/早期临床",
        },
        "pocket_type": "polar",
    },
}


def run():
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, "targets.json"), "w", encoding="utf-8") as f:
        json.dump(TARGETS, f, ensure_ascii=False, indent=1)
    print("[s1] 靶点档案:")
    for k, v in TARGETS.items():
        print(f"  {k}: {v['pdb_id']} + 共晶配体 {v['cocrystal_ligand']} | {v['role']}")
        for col, ev in v["evidence"].items():
            print(f"    证据·{col}: {ev}")
    return TARGETS


if __name__ == "__main__":
    run()
