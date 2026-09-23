"""Question bank: size, section proportions, per-question validity, uniqueness.

Section *weights* live in ``config.SECTIONS`` (20/18/16/13/13/12/11/7 — the
C1000-179 breakdown) and drive exam-set allocation. The bank is several times
larger than those numbers, so the tests below check the bank's *shape* against
the weights (every section present, big enough for a sprint, and its share of
the bank within ``PROPORTION_TOLERANCE`` of its exam weight) rather than pinning
per-section counts. The one exact number is ``BANK_TOTAL`` — bump it when you
add questions.
"""
import importlib
import re
from collections import Counter
from pathlib import Path

import pytest

import bank
from bank import question_by_id, questions_by_section
from config import BANK_SIZE, SECTIONS, SPRINT_QUESTION_COUNT
from core.models import Question

# ---- tunables -------------------------------------------------------------

BANK_TOTAL = 300            # exact size of the bank today - bump when adding questions
MIN_BANK_TOTAL = 300        # floor the suite promises (README, launcher blurb)
PROPORTION_TOLERANCE = 0.02  # |section share of bank - exam weight| allowed (absolute)

# Exam weights (third-party-sourced; see README disclaimer). These are what
# config.SECTIONS must hold - they are NOT bank counts.
EXAM_WEIGHTS = {
    "Create circuits": 20,
    "Quantum operations": 18,
    "Run circuits": 16,
    "Sampler": 13,
    "Estimator": 13,
    "Visualization": 12,
    "Results analysis": 11,
    "OpenQASM": 7,
}
ID_PREFIXES = {
    "Create circuits": "cc",
    "Quantum operations": "qo",
    "Run circuits": "rc",
    "Sampler": "sa",
    "Estimator": "es",
    "Visualization": "vz",
    "Results analysis": "ra",
    "OpenQASM": "oq",
}
DIFFICULTIES = {"easy", "medium", "hard"}

# Files whose id deliberately differs from the file stem. Keep this empty in
# spirit: an entry here is a TODO for the bank owner, not a convention.
# (cc_if_test_control_flow.py predates the file-stem rule; renaming the *file*
# back to cc_if_test.py keeps the id stable for any persisted exam_missed.json.)
KNOWN_ID_FILENAME_MISMATCHES = {
    "create_circuits/cc_if_test_control_flow.py": "cc_if_test",
}

BANK_DIR = Path(bank.__file__).resolve().parent


def _section_dir_name(section: str) -> str:
    return section.lower().replace(" ", "_")


def _question_files() -> list[Path]:
    files: list[Path] = []
    for section_dir in sorted(BANK_DIR.iterdir()):
        if not section_dir.is_dir() or section_dir.name.startswith("_"):
            continue
        files.extend(p for p in sorted(section_dir.glob("*.py")) if p.stem != "__init__")
    return files


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _code_body(text: str) -> str:
    """Fenced code minus import/blank lines - the part that makes a snippet distinct."""
    blocks = re.findall(r"```[A-Za-z0-9]*\n(.*?)```", text, re.S)
    lines = [ln.strip() for blk in blocks for ln in blk.splitlines()]
    return "\n".join(ln for ln in lines if ln and not ln.startswith(("import ", "from ")))


# ---- config / size ------------------------------------------------------------

def test_config_sections_hold_the_exam_weights():
    assert SECTIONS == EXAM_WEIGHTS
    assert BANK_SIZE == sum(EXAM_WEIGHTS.values()) == 110


def test_bank_total_is_exactly_bank_total(questions):
    assert len(questions) == BANK_TOTAL, (
        f"bank has {len(questions)} questions; update BANK_TOTAL in {__file__}")


def test_bank_meets_minimum_size_and_types(questions):
    assert len(questions) >= MIN_BANK_TOTAL
    assert all(isinstance(q, Question) for q in questions)


def test_every_question_file_loads():
    """The loader swallows import errors - make sure it is not hiding any."""
    files = _question_files()
    assert files, "no question files found"
    broken = []
    for path in files:
        mod_name = f"bank.{path.parent.name}.{path.stem}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001 - report every failure
            broken.append(f"{path.relative_to(BANK_DIR)}: {exc!r}")
            continue
        if not isinstance(getattr(mod, "QUESTION", None), Question):
            broken.append(f"{path.relative_to(BANK_DIR)}: no QUESTION")
    assert not broken, "\n".join(broken)
    assert len(bank.all_questions()) == len(files)


# ---- section shape ------------------------------------------------------------

def test_every_section_present_and_big_enough_for_a_sprint(questions):
    counts = Counter(q.section for q in questions)
    assert set(counts) == set(SECTIONS), "unknown or missing section"
    too_small = {s: n for s, n in counts.items() if n < SPRINT_QUESTION_COUNT}
    assert not too_small, f"sections smaller than a {SPRINT_QUESTION_COUNT}-question sprint: {too_small}"


def test_section_shares_track_exam_weights(questions):
    counts = Counter(q.section for q in questions)
    total = len(questions)
    off = {}
    for section, weight in SECTIONS.items():
        share, target = counts[section] / total, weight / BANK_SIZE
        if abs(share - target) > PROPORTION_TOLERANCE:
            off[section] = (round(share, 3), round(target, 3))
    assert not off, f"section share vs exam weight beyond {PROPORTION_TOLERANCE}: {off}"


def test_questions_by_section_matches_flat_bank(questions):
    grouped = questions_by_section()
    assert list(grouped) == list(SECTIONS)          # config order, for the UI
    assert sum(len(v) for v in grouped.values()) == len(questions)
    assert {s: len(v) for s, v in grouped.items()} == Counter(q.section for q in questions)


# ---- ids / files --------------------------------------------------------------

def test_ids_globally_unique(questions):
    dupes = [qid for qid, n in Counter(q.id for q in questions).items() if n > 1]
    assert not dupes, f"duplicate ids: {dupes}"


def test_ids_are_slugs_with_section_prefix(questions):
    for q in questions:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", q.id), q.id
        assert q.id.split("_")[0] == ID_PREFIXES[q.section], (q.id, q.section)


def test_filename_matches_id_and_directory_matches_section():
    mismatched_ids, wrong_dirs = {}, []
    for path in _question_files():
        q = importlib.import_module(f"bank.{path.parent.name}.{path.stem}").QUESTION
        rel = path.relative_to(BANK_DIR).as_posix()
        if q.id != path.stem:
            mismatched_ids[rel] = q.id
        if _section_dir_name(q.section) != path.parent.name:
            wrong_dirs.append((rel, q.section))
    assert not wrong_dirs, f"question in the wrong section directory: {wrong_dirs}"
    unexpected = {k: v for k, v in mismatched_ids.items()
                  if KNOWN_ID_FILENAME_MISMATCHES.get(k) != v}
    assert not unexpected, f"id != file stem: {unexpected}"


# ---- per-question validity ------------------------------------------------------

def test_every_question_has_exactly_four_distinct_options(questions):
    for q in questions:
        assert len(q.options) == 4, q.id
        assert all(isinstance(o, str) and o.strip() for o in q.options), q.id
        assert len({_norm(o) for o in q.options}) == 4, (q.id, q.options)


def test_correct_index_in_range(questions):
    for q in questions:
        assert type(q.correct_index) is int, q.id
        assert 0 <= q.correct_index < len(q.options), q.id


def test_required_text_fields_and_difficulty(questions):
    for q in questions:
        assert isinstance(q.question, str) and q.question.strip(), q.id
        assert isinstance(q.explanation, str) and q.explanation.strip(), q.id
        assert len(q.explanation.strip()) >= 40, (q.id, q.explanation)
        assert q.difficulty in DIFFICULTIES, (q.id, q.difficulty)


def test_fenced_code_blocks_are_closed(questions):
    for q in questions:
        assert q.question.count("```") % 2 == 0, f"unbalanced ``` in {q.id}"


# ---- duplicates -----------------------------------------------------------------

def test_no_two_questions_have_identical_text(questions):
    seen: dict[str, str] = {}
    dupes = []
    for q in questions:
        key = _norm(q.question)
        if key in seen:
            dupes.append((seen[key], q.id))
        seen.setdefault(key, q.id)
    assert not dupes, f"identical question text: {dupes}"


def test_no_two_questions_share_code_and_answer(questions):
    """Same snippet (ignoring imports) with the same correct answer is a duplicate."""
    seen: dict[tuple[str, str], str] = {}
    dupes = []
    for q in questions:
        body = _code_body(q.question)
        if not body:
            continue
        key = (_norm(body), _norm(q.options[q.correct_index]))
        if key in seen:
            dupes.append((seen[key], q.id))
        seen.setdefault(key, q.id)
    assert not dupes, f"same code and answer: {dupes}"


# ---- answer-position balance -----------------------------------------------------

@pytest.mark.xfail(
    strict=False,
    reason="Known: 261/300 questions store the correct answer at index 0 and the UI "
           "shows options in stored order, so 'A' is right ~87% of the time. Either "
           "rebalance correct_index across the bank or shuffle options per attempt. "
           "Remove this marker once fixed.",
)
def test_correct_answer_position_is_not_predictable(questions):
    overall = Counter(q.correct_index for q in questions)
    assert max(overall.values()) / len(questions) <= 0.5, dict(overall)
    per_section = {s: Counter() for s in SECTIONS}
    for q in questions:
        per_section[q.section][q.correct_index] += 1
    skewed = {s: dict(c) for s, c in per_section.items()
              if max(c.values()) / sum(c.values()) > 0.6}
    assert not skewed, skewed


# ---- lookup ---------------------------------------------------------------------

def test_question_by_id_round_trip(questions):
    for sample in (questions[0], questions[-1]):
        found = question_by_id(sample.id)
        assert found is not None
        assert (found.id, found.section, found.question) == (sample.id, sample.section, sample.question)
    assert question_by_id("definitely_not_a_question") is None
