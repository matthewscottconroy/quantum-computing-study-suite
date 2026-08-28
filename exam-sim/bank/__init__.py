"""Question bank — auto-discovers one-file-per-question directory structure."""
from __future__ import annotations
import importlib
import random
from pathlib import Path
from core.models import Question
from config import SECTIONS


def all_questions() -> list[Question]:
    qs: list[Question] = []
    here = Path(__file__).parent
    for section_dir in sorted(here.iterdir()):
        if not section_dir.is_dir() or section_dir.name.startswith('_'):
            continue
        for q_file in sorted(section_dir.glob('*.py')):
            if q_file.stem == '__init__':
                continue
            mod_name = f"bank.{section_dir.name}.{q_file.stem}"
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, 'QUESTION'):
                    qs.append(mod.QUESTION)
            except Exception:
                pass
    return qs


def questions_by_section() -> dict[str, list[Question]]:
    out: dict[str, list[Question]] = {s: [] for s in SECTIONS}
    for q in all_questions():
        out.setdefault(q.section, []).append(q)
    return out


def question_by_id(qid: str) -> Question | None:
    for q in all_questions():
        if q.id == qid:
            return q
    return None


def _proportional_allocation(count: int) -> dict[str, int]:
    """Largest-remainder allocation of `count` draws across exam-weighted sections."""
    total_weight = sum(SECTIONS.values())
    exact = {s: count * w / total_weight for s, w in SECTIONS.items()}
    alloc = {s: int(v) for s, v in exact.items()}
    leftover = count - sum(alloc.values())
    by_remainder = sorted(SECTIONS, key=lambda s: exact[s] - alloc[s], reverse=True)
    for s in by_remainder[:leftover]:
        alloc[s] += 1
    return alloc


def build_exam_set(count: int) -> list[Question]:
    """Draw `count` questions proportional to section weights, shuffled."""
    pools = questions_by_section()
    alloc = _proportional_allocation(count)
    chosen: list[Question] = []
    short = 0
    for section, n in alloc.items():
        pool = list(pools.get(section, []))
        random.shuffle(pool)
        take = pool[:n]
        short += n - len(take)
        chosen.extend(take)
    if short:  # top up from remaining questions if any section pool ran dry
        used = {q.id for q in chosen}
        rest = [q for q in all_questions() if q.id not in used]
        random.shuffle(rest)
        chosen.extend(rest[:short])
    random.shuffle(chosen)
    return chosen


def build_sprint_set(section: str, count: int) -> list[Question]:
    pool = [q for q in all_questions() if q.section == section]
    random.shuffle(pool)
    return pool[:count]
