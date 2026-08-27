# -*- coding: utf-8 -*-
"""受体网格盒子(grid box)参数配置

负责人: 代维斯丹（验证组）
靶点选择依据:
  FXR (胆汁酸核受体)  —— 保肝/利胆经典靶点，配体结合口袋为疏水型
  Keap1-Kelch (Nrf2通路负调控) —— 氧化应激型肝损伤的关键蛋白-蛋白界面
说明: 盒子中心坐标为文献/结构经验初值，服务器端以口袋配体重采样校准为准。
"""

GRID_BOXES = {
    "FXR_LBD": {
        "pdb_id": "1OSH",
        "description": "人FXR配体结合域(与fexaramine复合物)",
        "center": [15.2, 3.8, 24.5],
        "size": [22.0, 22.0, 24.0],
        "pocket_type": "hydrophobic",
        "ref_ligand": "fexaramine",
    },
    "KEAP1_KELCH": {
        "pdb_id": "2FLU",
        "description": "人Keap1 Kelch区(与Nrf2 ETGE肽复合物)",
        "center": [-11.5, 20.4, -6.2],
        "size": [20.0, 20.0, 20.0],
        "pocket_type": "polar_basic",
        "ref_ligand": "Nrf2-ETGE peptide (P1-P4口袋)",
    },
}


def summarize():
    for k, v in GRID_BOXES.items():
        print(f"[grid] {k} ({v['pdb_id']}): center={v['center']} size={v['size']} "
              f"口袋类型={v['pocket_type']}")
    return GRID_BOXES


if __name__ == "__main__":
    summarize()
