"""Derivation registry — auto-discovers one-file-per-derivation modules.

Each derivation module defines a module-level DERIVATION (core.models.Derivation).
"""
from __future__ import annotations
import importlib
from pathlib import Path
from core.models import Derivation


def all_derivations() -> list[Derivation]:
    derivs: list[Derivation] = []
    here = Path(__file__).parent
    for deriv_file in sorted(here.glob('*.py')):
        if deriv_file.stem == '__init__':
            continue
        mod_name = f"derivations.{deriv_file.stem}"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, 'DERIVATION'):
                derivs.append(mod.DERIVATION)
        except Exception:
            pass
    return derivs
