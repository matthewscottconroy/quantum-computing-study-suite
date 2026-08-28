"""Kata registry — auto-discovers one-file-per-kata directory structure."""
from __future__ import annotations
import importlib
import random
from pathlib import Path
from core.models import Kata, DojoConfig

# Canonical curriculum order (the 8 C1000-179 exam areas, then the two
# dojo-specific practice sections).
SECTION_ORDER = [
    "Create circuits",
    "Quantum operations",
    "Run circuits",
    "Sampler",
    "Estimator",
    "Visualization",
    "Results analysis",
    "OpenQASM",
    "Debugging",
    "Modernization",
]


def all_katas() -> list[Kata]:
    katas: list[Kata] = []
    here = Path(__file__).parent
    for section_dir in sorted(here.iterdir()):
        if not section_dir.is_dir() or section_dir.name.startswith('_'):
            continue
        for kata_file in sorted(section_dir.glob('*.py')):
            if kata_file.stem == '__init__':
                continue
            mod_name = f"katas.{section_dir.name}.{kata_file.stem}"
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, 'KATA'):
                    katas.append(mod.KATA)
            except Exception:
                pass
    return katas


def all_sections() -> list[str]:
    present = {k.section for k in all_katas()}
    ordered = [s for s in SECTION_ORDER if s in present]
    ordered += sorted(present - set(SECTION_ORDER))
    return ordered


def build_kata_set(config: DojoConfig) -> list[Kata]:
    pool = [k for k in all_katas() if k.section in config.sections]
    if not pool:
        return []
    try:
        from persistence import kata_weights
        weight_map = kata_weights()
    except Exception:
        weight_map = {}
    weights = [weight_map.get(k.id, 1.25) for k in pool]
    chosen = random.choices(pool, weights=weights, k=config.kata_count)
    seen: set[str] = set()
    result: list[Kata] = []
    for k in chosen:
        if k.id not in seen:
            seen.add(k.id)
            result.append(k)
    remaining = [k for k in pool if k.id not in seen]
    random.shuffle(remaining)
    while len(result) < config.kata_count and remaining:
        result.append(remaining.pop())
    if config.shuffle:
        random.shuffle(result)
    else:
        order = {s: i for i, s in enumerate(SECTION_ORDER)}
        result.sort(key=lambda k: (order.get(k.section, 99), k.id))
    return result
