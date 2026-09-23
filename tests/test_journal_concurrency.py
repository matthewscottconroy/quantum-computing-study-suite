"""The two shared journals survive several apps writing at once.

``mistakes.json`` and ``confidence.json`` live in one data directory and all
ten apps append to them.  Every app writes by read-modify-write, and the write
alone being atomic is not enough: with two apps open — which ``launch.py``
invites in so many words, "run several at once" — the *read* goes stale and the
second writer replaces the file with a list that never contained the first
writer's new row.  Measured before the fix, three processes appending 60 rows
each kept 103 of 180 rows; 43 % of the journal was lost.

The fix is ``journal_sync`` (a byte-identical copy in every app tree): an
``fcntl.flock`` on a ``<file>.lock`` sidecar held across the whole
read-modify-write, plus ``merge_foreign``, which puts rows owned by another app
back exactly as they were read.

These tests run the real thing: one **process per app**, each importing that
app's own store module from its own tree by path (no two apps can share a
process — several define the same top-level ``config`` and ``core`` modules),
all of them hammering one temp data directory through the public logging
helpers.  Nothing here touches ``~/.local/share/quantum-study``.

Run it standalone for the reproduction in the bug report::

    python tests/test_journal_concurrency.py
"""

from __future__ import annotations

import importlib.util
import json
import multiprocessing
import os
import sys
import traceback
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: app directory -> store module inside it (the names differ per app).
STORES = {
    "flashcard-drill": "persistence/review_store.py",
    "math-quiz":       "persistence.py",
    "quantum-quiz":    "persistence.py",
    "circuit-trainer": "persistence.py",
    "qec-trainer":     "persistence.py",
    "vqa-trainer":     "persistence.py",
    "paper-drill":     "persistence.py",
    "qiskit-dojo":     "persistence.py",
    "exam-sim":        "persistence.py",
    "problem-trainer": "persistence.py",
}

#: A foreign row, seeded before the run, carrying keys no app's schema knows.
#: It must come back byte for byte however many apps rewrite the file.
FOREIGN_ROW = {
    "id": "tutor-42", "app": "quantum-tutor", "category": "Gates",
    "question": "q", "your_answer": "a", "correct_answer": "b",
    "cause": "confused", "note": "n", "timestamp": 1.0, "resolved": False,
    "revision": 7, "tags": ["unknown-key", {"nested": True}],
}
FOREIGN_CONFIDENCE_ROW = {
    "id": "tutor-42", "app": "quantum-tutor", "category": "Gates",
    "confidence": 2, "correct": True, "timestamp": 1.0,
    "source": "tutor-v2", "latency_ms": 940,
}
FOREIGN = {"mistakes.json": FOREIGN_ROW, "confidence.json": FOREIGN_CONFIDENCE_ROW}

ROWS_PER_APP = 20          # 10 apps x 20 = 200 rows in each shared file
SAME_APP_WRITERS = 3       # two (or three) windows of ONE app, the other race
JOIN_TIMEOUT = 120.0       # a wedged child fails the test instead of hanging it


# ---------------------------------------------------------------------------
# The worker: one app, one process
# ---------------------------------------------------------------------------

def _load_store(app: str):
    """Import *app*'s store module from its own tree, by path.

    The app directory goes on ``sys.path`` first so the module's own
    ``import config`` / ``import journal_sync`` resolve inside that tree.  Only
    ever one app per process: ten trees define ten different ``config``
    modules under the same name.
    """
    app_dir = ROOT / app
    sys.path.insert(0, str(app_dir))
    path = app_dir / STORES[app]
    spec = importlib.util.spec_from_file_location(
        f"store_{app.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _log_mistake(app: str, store, item_id: str) -> None:
    """Append one mistake through *app*'s own public helper."""
    if app == "math-quiz":                       # takes a Question, not an id
        from core.models import Question         # noqa: PLC0415 (per-process)
        store.log_mistake(
            Question(subject="Linear Algebra", topic="spectral theorem",
                     difficulty="beginner", question_type="conceptual",
                     text=f"Question {item_id}?", hints=["h"]),
            "wrong", "right")
    elif app in ("circuit-trainer", "qec-trainer", "qiskit-dojo", "exam-sim"):
        entry = {                                # these take a prepared row
            "id": item_id, "app": app, "category": "Gates",
            "question": "q", "your_answer": "a", "correct_answer": "b",
            "cause": None, "note": "", "timestamp": 1000.0, "resolved": False,
        }
        appender = getattr(store, "append_mistake", None) or store.log_mistake
        appender(entry)
    else:
        store.log_mistake(item_id, "Gates", "q", "a", "b")


def _log_confidence(app: str, store, item_id: str) -> None:
    """Append one calibration row through *app*'s own public helper."""
    if app == "math-quiz":
        from core.models import Question         # noqa: PLC0415 (per-process)
        store.log_confidence(
            Question(subject="Linear Algebra", topic="spectral theorem",
                     difficulty="beginner", question_type="conceptual",
                     text=f"Question {item_id}?", hints=["h"]),
            3, False)
    else:
        store.log_confidence(item_id, "Gates", 3, False)


def writer(app: str, data_dir: str, tag: str, rows: int, barrier) -> None:
    """Child-process entry point: append *rows* mistakes and *rows* ratings.

    Must stay importable at module level — ``forkserver`` (the default start
    method on Linux from Python 3.14) re-imports this module in the child and
    looks the target up by name.
    """
    try:
        os.environ["QUANTUM_STUDY_DATA_DIR"] = data_dir   # before the import
        store = _load_store(app)
        if barrier is not None:
            barrier.wait(timeout=JOIN_TIMEOUT)            # all start together
        for i in range(rows):
            _log_mistake(app, store, f"{tag}-{i}")
            _log_confidence(app, store, f"{tag}-{i}")
    except BaseException:                                 # pragma: no cover
        traceback.print_exc()
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(jobs: list[tuple[str, str]], data_dir: Path, rows: int) -> None:
    """Run one (app, tag) pair per process and wait for all of them."""
    ctx = multiprocessing.get_context()
    barrier = ctx.Barrier(len(jobs))
    procs = [ctx.Process(target=writer,
                         args=(app, str(data_dir), tag, rows, barrier),
                         name=f"writer-{tag}")
             for app, tag in jobs]
    for p in procs:
        p.start()
    try:
        for p in procs:
            p.join(JOIN_TIMEOUT)
    finally:
        for p in procs:
            if p.is_alive():                              # pragma: no cover
                p.terminate()
                p.join(5)
    stuck = [p.name for p in procs if p.exitcode is None]
    assert not stuck, f"writer(s) never finished (deadlock?): {stuck}"
    failed = {p.name: p.exitcode for p in procs if p.exitcode != 0}
    assert not failed, f"writer(s) exited non-zero: {failed}"


def _rows(path: Path) -> list:
    """Parse a journal file, failing loudly if a concurrent write corrupted it."""
    text = path.read_text()
    try:
        data = json.loads(text)
    except ValueError as exc:                             # pragma: no cover
        pytest.fail(f"{path.name} is not valid JSON after the run: {exc}\n"
                    f"{text[:400]}")
    assert isinstance(data, list), f"{path.name} is not a JSON list"
    return data


def _seed(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, row in FOREIGN.items():
        (data_dir / name).write_text(json.dumps([row]))


def _ids(rows: list, app: str) -> list[str]:
    return [str(r.get("id")) for r in rows if r.get("app") == app]


# ---------------------------------------------------------------------------
# The tests
# ---------------------------------------------------------------------------

def test_ten_apps_writing_at_once_lose_no_rows(tmp_path):
    """One process per app, all appending at once: nothing may be dropped."""
    data_dir = tmp_path / "quantum-study"
    _seed(data_dir)
    apps = sorted(STORES)
    _run([(app, app) for app in apps], data_dir, ROWS_PER_APP)

    for name, foreign in FOREIGN.items():
        rows = _rows(data_dir / name)
        assert rows.count(foreign) == 1, (
            f"{name}: the seeded foreign row was rewritten, dropped or "
            f"duplicated by one of the ten apps")
        expected = len(apps) * ROWS_PER_APP
        assert len(rows) == expected + 1, (
            f"{name}: expected {expected} rows + the foreign one, "
            f"found {len(rows)} — {expected + 1 - len(rows)} lost")
        for app in apps:
            ids = _ids(rows, app)
            assert len(ids) == ROWS_PER_APP, (
                f"{name}: {app} wrote {ROWS_PER_APP} rows but {len(ids)} "
                f"survived the other nine apps writing alongside it")
            assert len(set(ids)) == len(ids), f"{name}: {app} duplicated rows"
            if app != "math-quiz":       # math-quiz hashes its own item ids
                assert sorted(ids) == sorted(f"{app}-{i}"
                                             for i in range(ROWS_PER_APP))


def test_two_windows_of_one_app_lose_no_rows(tmp_path):
    """The same app open several times over — every window appends its own rows.

    This is the case the lock alone has to carry: the rows all claim the same
    ``app``, so preserving *foreign* rows cannot help.  It works because every
    helper re-reads the file inside the lock rather than before it.
    """
    data_dir = tmp_path / "quantum-study"
    _seed(data_dir)
    app = "flashcard-drill"
    tags = [f"window{n}" for n in range(SAME_APP_WRITERS)]
    _run([(app, tag) for tag in tags], data_dir, ROWS_PER_APP)

    rows = _rows(data_dir / "mistakes.json")
    assert rows.count(FOREIGN_ROW) == 1
    got = sorted(_ids(rows, app))
    want = sorted(f"{tag}-{i}" for tag in tags for i in range(ROWS_PER_APP))
    assert got == want, (
        f"{len(want) - len(got)} of {len(want)} rows lost across "
        f"{SAME_APP_WRITERS} windows of {app}")


def test_the_lock_is_really_taken_and_is_released_on_a_hard_exit(tmp_path):
    """flock, not hope: the sidecar exists, and a killed holder frees it."""
    sys.path.insert(0, str(ROOT / "flashcard-drill"))
    spec = importlib.util.spec_from_file_location(
        "journal_sync_probe", ROOT / "flashcard-drill" / "journal_sync.py")
    journal_sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(journal_sync)

    data_dir = tmp_path / "quantum-study"
    data_dir.mkdir(parents=True)
    target = data_dir / "mistakes.json"

    with journal_sync.lock(target, create=True) as held:
        assert held, "flock is not available here — the suite would be a no-op"
    assert (data_dir / "mistakes.json.lock").exists()

    ctx = multiprocessing.get_context()
    proc = ctx.Process(target=_die_holding_the_lock, args=(str(target),))
    proc.start()
    proc.join(JOIN_TIMEOUT)
    assert proc.exitcode == 0

    with journal_sync.lock(target, timeout=5.0) as held:
        assert held, "the lock was not released when its holder died"


def _die_holding_the_lock(target: str) -> None:
    """Child: take the lock, then die without unwinding (kernel must free it)."""
    sys.path.insert(0, str(ROOT / "flashcard-drill"))
    spec = importlib.util.spec_from_file_location(
        "journal_sync_probe", ROOT / "flashcard-drill" / "journal_sync.py")
    journal_sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(journal_sync)
    with journal_sync.lock(target, create=True):
        os._exit(0)


def test_every_app_ships_the_same_journal_sync():
    """Ten copies, one implementation: a fix here must reach every app."""
    copies = {app: (ROOT / app / "journal_sync.py") for app in STORES}
    missing = [app for app, path in copies.items() if not path.exists()]
    assert not missing, f"journal_sync.py is missing from: {missing}"
    texts = {app: path.read_text() for app, path in copies.items()}
    reference = texts["flashcard-drill"]
    drifted = [app for app, text in texts.items() if text != reference]
    assert not drifted, f"journal_sync.py has drifted in: {drifted}"


if __name__ == "__main__":          # forkserver/spawn need this guard
    import tempfile
    with tempfile.TemporaryDirectory(prefix="journal-race-") as tmp:
        d = Path(tmp) / "quantum-study"
        _seed(d)
        names = sorted(STORES)
        _run([(a, a) for a in names], d, ROWS_PER_APP)
        for fname in ("mistakes.json", "confidence.json"):
            all_rows = _rows(d / fname)
            want = len(names) * ROWS_PER_APP
            have = len(all_rows) - 1        # minus the seeded foreign row
            print(f"  {fname}: expected {want} rows, found {have} "
                  f"-> LOST {want - have}")
            print("  per app:", {a: len(_ids(all_rows, a)) for a in names})
