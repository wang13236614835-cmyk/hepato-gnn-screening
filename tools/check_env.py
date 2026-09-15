# -*- coding: utf-8 -*-
"""Portable environment self-check for hepato-gnn-screening.

Exit code 0 means the base environment is usable. Optional packages are reported
without failing the check. This keeps the repository usable on Windows/Linux,
CPU/GPU, and machines that only need the legacy NumPy workflow.
"""
from __future__ import annotations

import importlib
import platform
import sys

BASE = {
    "numpy": "numpy",
    "matplotlib": "matplotlib",
}
OPTIONAL = {
    "pandas": "pandas",
    "scipy": "scipy",
    "scikit-learn": "sklearn",
    "statsmodels": "statsmodels",
    "RDKit": "rdkit",
    "Meeko": "meeko",
    "Gemmi": "gemmi",
    "PyTorch": "torch",
    "PyTorch Geometric": "torch_geometric",
}


def version_of(module_name: str) -> str:
    mod = importlib.import_module(module_name)
    return str(getattr(mod, "__version__", "unknown"))


def main() -> int:
    print("hepato-gnn-screening environment check")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    print(f"OS: {platform.system()} {platform.release()} | {platform.machine()}")

    py = sys.version_info[:2]
    if py < (3, 10):
        print("[FAIL] Python < 3.10 is not supported.")
        return 2
    if py == (3, 11):
        print("[OK] Python 3.11 is the recommended baseline.")
    elif py in {(3, 10), (3, 12)}:
        print("[OK] Python version is in the full-stack compatibility range (3.10-3.12).")
    else:
        print("[WARN] Base workflow may work, but the full scientific/ML stack is not guaranteed outside Python 3.10-3.12.")

    failed = []
    print("\nBase packages:")
    for label, module in BASE.items():
        try:
            print(f"  [OK] {label}: {version_of(module)}")
        except Exception as exc:
            failed.append(label)
            print(f"  [FAIL] {label}: {exc}")

    print("\nOptional packages:")
    optional_present = {}
    for label, module in OPTIONAL.items():
        try:
            ver = version_of(module)
            optional_present[label] = ver
            print(f"  [OK] {label}: {ver}")
        except Exception:
            print(f"  [--] {label}: not installed")

    try:
        import torch

        print(f"\nPyTorch backend: CUDA available={torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA runtime reported by torch: {torch.version.cuda}")
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("CPU mode is available; CUDA is optional.")
    except Exception:
        pass

    if failed:
        print("\nResult: BASE ENVIRONMENT FAILED")
        print("Install with: python -m pip install -r requirements.txt")
        return 1

    print("\nResult: BASE ENVIRONMENT OK")
    print("Science layer: python -m pip install -r requirements-science.txt")
    print("ML layer: install PyTorch for your platform first, then python -m pip install -r requirements-ml.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
