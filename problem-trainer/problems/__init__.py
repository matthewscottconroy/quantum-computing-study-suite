"""Problem registry — auto-discovers one-file-per-problem directory structure.

Each problem module defines a module-level PROBLEM (core.models.Problem).
"""
from __future__ import annotations
import importlib
from pathlib import Path
from core.models import Problem


def all_problems() -> list[Problem]:
    probs: list[Problem] = []
    here = Path(__file__).parent
    for topic_dir in sorted(here.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith('_'):
            continue
        for prob_file in sorted(topic_dir.glob('*.py')):
            if prob_file.stem == '__init__':
                continue
            mod_name = f"problems.{topic_dir.name}.{prob_file.stem}"
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, 'PROBLEM'):
                    probs.append(mod.PROBLEM)
            except Exception:
                pass
    return probs


def all_topics() -> list[str]:
    seen: list[str] = []
    for p in all_problems():
        if p.topic not in seen:
            seen.append(p.topic)
    return seen


def problems_by_topic(topics: list[str]) -> list[Problem]:
    return [p for p in all_problems() if p.topic in topics]
