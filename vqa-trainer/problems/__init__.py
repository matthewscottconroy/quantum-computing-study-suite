"""Problem registry — auto-discovers one-file-per-problem directory structure."""
from __future__ import annotations
import importlib
import random
from pathlib import Path
from core.models import Problem, TrainerConfig


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


def all_categories() -> list[str]:
    seen: list[str] = []
    for p in all_problems():
        if p.category not in seen:
            seen.append(p.category)
    return seen


def build_problem_set(config: TrainerConfig) -> list[Problem]:
    if config.flagged_only:
        try:
            from persistence import load_flagged
            flagged_ids = load_flagged()
        except Exception:
            flagged_ids = set()
        pool = [p for p in all_problems() if p.id in flagged_ids]
    else:
        pool = [p for p in all_problems() if p.category in config.categories]
    if config.difficulty:
        pool = [p for p in pool if p.difficulty == config.difficulty]
    if not pool:
        return []
    try:
        from persistence import problem_score_weights
        prob_weights = problem_score_weights()
    except Exception:
        prob_weights = {}
    weights = [prob_weights.get(p.id, 1.25) for p in pool]
    chosen = random.choices(pool, weights=weights, k=config.problem_count)
    seen: set[str] = set()
    result: list[Problem] = []
    for p in chosen:
        if p.id not in seen:
            seen.add(p.id)
            result.append(p)
    remaining = [p for p in pool if p.id not in seen]
    random.shuffle(remaining)
    while len(result) < config.problem_count and remaining:
        result.append(remaining.pop())
    random.shuffle(result)
    return result
