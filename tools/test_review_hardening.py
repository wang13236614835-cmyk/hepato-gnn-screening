"""Regression checks for the revised computation; no biological validation."""
from pathlib import Path
import importlib.util
import json
import sys
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "final-aidd-screening/src"))
import s5_fuse_select as fusion


def test_fusion_never_sorts_nonfinite_scores():
    rows = [{"compound_id":"A", "model_term":float("nan"), "dock_term":1, "dl_term":1, "in_ad":True}]
    with pytest.raises(ValueError, match="non-finite"):
        fusion._score_rows(rows, .45, .35, .2)


def test_fusion_ties_are_serialized_by_compound_id():
    rows = [{"compound_id":cid, "model_term":1, "dock_term":1, "dl_term":1, "in_ad":True} for cid in ["B","A"]]
    assert fusion._score_rows(rows, .45, .35, .2) == ["A","B"]


def _module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mock_is_explicit_demo_only(monkeypatch):
    module = _module("src/docking/mock_docking.py", "demo_mock")
    monkeypatch.delenv("HEPATO_DATA_MODE", raising=False)
    with pytest.raises(RuntimeError, match="DEMO"):
        module.score_all()
    assert Path(module.OUT) == ROOT / "results/demo/docking"


def test_legacy_fusion_cannot_publish_mock_candidates():
    module = _module("src/scoring/fuse.py", "legacy_fusion")
    with pytest.raises(RuntimeError, match="Historical"):
        module.run()


def test_public_sources_do_not_mislabel_technology_or_assay():
    catalog = json.loads((ROOT / "data/curation/public_source_catalog.json").read_text())
    assert catalog["sources"]["GSE89632"]["technology"] == "microarray"
    assert catalog["sources"]["GSE135251"]["total_samples"] == 216
    assert catalog["drug_target"]["Resmetirom"]["gene"] == "THRB"
    assert catalog["berberine_fxr"]["direct_binding_ec50_uM"] is None
