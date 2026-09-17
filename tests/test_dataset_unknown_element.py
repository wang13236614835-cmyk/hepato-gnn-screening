# -*- coding: utf-8 -*-
"""src/models/dataset.py 未知元素处理的永久回归测试。

历史 bug：未知元素回退到元素槽位 0，等价于按碳处理（静默化学错误）。
2026-09-17 修复后：
- 默认 raise：未知元素抛 UnsupportedElementError，绝不静默按碳；
- 显式 unk_slot：未知元素使用独立 UNK one-hot 槽位（14 维）；
- 只含已知元素的分子，特征与旧版 13 维布局逐位一致（历史复现不受影响）。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from models.dataset import (  # noqa: E402
    ELEMS,
    KNOWN_FEATURE_DIM,
    UNK_FEATURE_DIM,
    GraphRecord,
    UnsupportedElementError,
    node_features,
)
from chem.smiles_graph import parse_smiles  # noqa: E402


def _features(smiles, unknown_element="raise"):
    g = parse_smiles(smiles)
    assert g is not None, smiles
    g._source_smiles = smiles
    return node_features(g, unknown_element=unknown_element), g


def _legacy_features(g):
    """旧版 node_features 的逐位复刻（未知元素按槽位 0）。仅测试用。"""
    deg = g.degrees()
    nH = g.num_h()
    X = np.zeros((len(g.atoms), 13))
    for a in g.atoms:
        idx = ELEMS.index(a.element) if a.element in ELEMS else 0
        X[a.idx, idx] = 1.0
        X[a.idx, 10] = 1.0 if a.aromatic else 0.0
        X[a.idx, 11] = min(deg[a.idx] / 6.0, 1.5)
        X[a.idx, 12] = min(nH[a.idx] / 4.0, 1.5)
    return X


# ---- 1. 未知元素不再作为 C ----

def test_unknown_element_raises_instead_of_carbon():
    # smiles_graph 对 ELEMS/VALENCE 之外的括号原子（Na/Se/Xe 等）统一输出
    # '*'；'*' 不在 ELEMS 中，必须触发 UnsupportedElementError。
    with pytest.raises(UnsupportedElementError) as exc:
        _features("[Na+].[O-]C(=O)c1ccccc1")
    assert "*" in exc.value.elements
    assert "不会静默按碳处理" in str(exc.value)
    # 错误信息保留原始 SMILES，可追溯到具体坏行。
    assert "Na" in exc.value.smiles


def test_selenium_raises_with_clear_message():
    with pytest.raises(UnsupportedElementError) as exc:
        _features("C[Se]C")
    assert exc.value.elements == ["*"]
    assert "Se" in exc.value.smiles


def test_wildcard_atom_raises():
    # smiles_graph 对无法识别的括号元素会输出 '*'。
    with pytest.raises(UnsupportedElementError) as exc:
        _features("[Xe]")
    assert "*" in exc.value.elements or "Xe" in exc.value.elements


def test_unknown_element_unk_slot_is_independent_feature():
    X, _ = _features("C[Se]C", unknown_element="unk_slot")
    assert X.shape[1] == UNK_FEATURE_DIM
    # C 原子：one-hot 落在 C 槽位（0），UNK 槽位（10）为 0。
    assert X[0, 0] == 1.0 and X[0, 10] == 0.0
    # Se 原子：C 槽位必须为 0（不再按碳处理），UNK 槽位为 1。
    assert X[1, 0] == 0.0
    assert X[1, 10] == 1.0
    # 度/氢数特征仍在末三列（芳香 11、度 12、氢 13）。
    assert X[1, 11] == 0.0
    assert X[1, 12] > 0.0


def test_invalid_unknown_element_mode_rejected():
    with pytest.raises(ValueError, match="unknown_element"):
        _features("CCO", unknown_element="ignore")


# ---- 2. 已知元素历史复现逐位一致 ----

def test_known_elements_features_match_legacy_bitwise():
    for smiles in ("CCO", "c1ccccc1O", "CC(=O)Oc1ccccc1C(=O)O", "CN1C=NC2=C1C(=O)N(C)C(=O)N2C"):
        X, g = _features(smiles)
        assert X.shape[1] == KNOWN_FEATURE_DIM
        legacy = _legacy_features(g)
        assert np.array_equal(X, legacy), smiles


def test_unk_slot_mode_known_elements_match_legacy_prefix():
    # unk_slot 模式下，已知元素的 one-hot(0-9) 与历史一致，只是维度扩到 14。
    X, g = _features("CCO", unknown_element="unk_slot")
    legacy = _legacy_features(g)
    assert X.shape[1] == UNK_FEATURE_DIM
    assert np.array_equal(X[:, :10], legacy[:, :10])
    assert np.array_equal(X[:, 11:], legacy[:, 10:])
    assert not X[:, 10].any()  # 没有 UNK 原子


# ---- 3. GraphRecord / loader 兼容性 ----

def test_graph_record_default_raises_on_unknown_element():
    with pytest.raises(UnsupportedElementError):
        GraphRecord({"compound_id": "X1", "name_cn": "测试", "smiles": "C[Se]C", "label": "1"})


def test_graph_record_known_element_backward_compatible():
    rec = GraphRecord({"compound_id": "X2", "name_cn": "乙醇", "smiles": "CCO", "label": "1"})
    assert rec.label == 1
    assert rec.X.shape == (3, KNOWN_FEATURE_DIM)
    legacy = _legacy_features(rec.g)
    assert np.array_equal(rec.X, legacy)


def test_graph_record_invalid_smiles_now_raises():
    # 旧行为：parse_smiles 失败 → g=None → node_features 内 len(None) 崩溃。
    # 新行为：显式 ValueError，错误信息带 compound_id，便于定位坏行。
    with pytest.raises(ValueError, match="无法解析 SMILES"):
        GraphRecord({"compound_id": "X3", "name_cn": "坏行", "smiles": "not_a_smiles%%%", "label": ""})


def test_graph_record_unk_slot_mode():
    rec = GraphRecord(
        {"compound_id": "X4", "name_cn": "含硒", "smiles": "C[Se]C", "label": "1"},
        unknown_element="unk_slot",
    )
    assert rec.X.shape == (3, UNK_FEATURE_DIM)
    assert rec.X[1, 10] == 1.0
    assert rec.X[1, 0] == 0.0
