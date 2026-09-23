"""``common.journal`` — the code that was wrong ten times.

Three groups:

* **pure helpers** — clipping, cause normalisation, entry building, and the
  three merge/trim functions that decide what a rewrite puts back;
* **store behaviour** — the reconciled decisions (append not merge, trim only
  our own rows, ``note=None`` keeps the note, a bad rating records nothing);
* **concurrency** — real processes hammering one data directory, and the
  *same* test run against a deliberately unlocked variant, which must fail.
  A concurrency test that has never been seen to fail proves nothing.

Run the reproduction standalone::

    python tests/test_common_journal.py
"""

from __future__ import annotations

import contextlib
import json
import multiprocessing
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:                       # also true in a child
    sys.path.insert(0, str(ROOT))

from common import journal, locking, schema         # noqa: E402

ROWS_PER_WRITER = 25
WRITERS = 4
JOIN_TIMEOUT = 120.0

#: A row from a hypothetical eleventh tool, carrying keys no app knows.  It
#: must come back byte for byte however many apps rewrite the file.
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


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """An empty data directory, and a clean backup/refusal state."""
    target = tmp_path / "quantum-study"
    target.mkdir()
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    schema.reset_session()
    journal.clear_write_error()
    yield target
    schema.reset_session()
    journal.clear_write_error()


def entry(item_id: str, app: str = "qec-trainer", **kw) -> dict:
    kw.setdefault("category", "Gates")
    kw.setdefault("question", "q")
    kw.setdefault("your_answer", "a")
    kw.setdefault("correct_answer", "b")
    return journal.make_mistake_entry(item_id, app, **kw)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_clip_text_collapses_whitespace_and_ellipsises():
    assert journal.clip_text("  a \n b\tc ") == "a b c"
    long = "x" * 500
    out = journal.clip_text(long, 10)
    assert len(out) == 10 and out.endswith("…")
    assert journal.clip_text(None) == ""


def test_clip_note_keeps_line_breaks():
    """A note is prose the learner typed; reflowing it destroys structure."""
    note = "line one\nline two\n\n  - a bullet"
    assert journal.clip_note(note) == note
    assert "\n" not in journal.clip_text(note)


def test_clip_note_truncates_without_reflowing():
    out = journal.clip_note("a\nb" * 500, 20)
    assert len(out) == 20 and out.endswith("…") and "\n" in out


@pytest.mark.parametrize("raw,want", [
    ("misread", "misread"),
    ("  Misread ", "misread"),           # vqa's normalisation, kept
    ("MISREAD", "misread"),
    ("not_a_cause", None),
    ("", None),
    (None, None),
    (17, None),
])
def test_normalise_cause_never_raises(raw, want):
    """math-quiz and exam-sim raised ValueError here; that loses the mistake."""
    assert journal.normalise_cause(raw) == want


@pytest.mark.parametrize("raw,want", [
    (1, 1), (4, 4), ("3", 3), (0, None), (5, None), (None, None),
    ("x", None), (True, None), (2.0, 2),
])
def test_coerce_confidence(raw, want):
    assert journal.coerce_confidence(raw) == want


def test_make_mistake_entry_has_exactly_the_contract_keys():
    row = entry("i1")
    assert tuple(row) == journal.MISTAKE_KEYS
    assert row["id"] == "i1" and row["app"] == "qec-trainer"
    assert row["cause"] is None and row["resolved"] is False
    assert isinstance(row["timestamp"], float)


def test_make_mistake_entry_caps_its_text_fields():
    row = entry("i1", question="q" * 5000, note="n" * 5000)
    assert len(row["question"]) == journal.TEXT_MAX
    assert len(row["note"]) == journal.NOTE_MAX


def test_make_confidence_entry_clamps_but_log_rejects(data_dir):
    """The builder clamps so a row is always valid; the *write* rejects, so a
    rating the learner never gave is never invented."""
    assert journal.make_confidence_entry("i", "a", confidence=9)["confidence"] == 4
    assert journal.make_confidence_entry("i", "a", confidence=0)["confidence"] == 1
    assert journal.log_confidence("i", "qec-trainer", confidence=9) is None
    assert journal.log_confidence("i", "qec-trainer", confidence=None) is None
    assert journal.load_confidence() == []


# ---------------------------------------------------------------------------
# merge_foreign / trim_own
# ---------------------------------------------------------------------------

def test_merge_foreign_restores_unknown_keys_verbatim():
    normalised = dict(FOREIGN_ROW)
    normalised.pop("revision")                      # as an app's loader would
    normalised.pop("tags")
    out = journal.merge_foreign([FOREIGN_ROW], [normalised], "qec-trainer")
    assert out == [FOREIGN_ROW]
    assert out[0] is FOREIGN_ROW


def test_merge_foreign_keeps_a_row_that_appeared_since_our_read():
    mine = entry("m1")
    out = journal.merge_foreign([FOREIGN_ROW], [mine], "qec-trainer")
    assert mine in out and FOREIGN_ROW in out and len(out) == 2


def test_merge_foreign_never_duplicates_repeated_ids():
    twin = [dict(FOREIGN_ROW, timestamp=1.0), dict(FOREIGN_ROW, timestamp=2.0)]
    out = journal.merge_foreign(twin, list(twin), "qec-trainer")
    assert len(out) == 2
    assert [r["timestamp"] for r in out] == [1.0, 2.0]


def test_rows_without_an_app_are_not_foreign():
    """The loaders claim them, so treating them as foreign writes them twice."""
    orphan = {"id": "x", "timestamp": 1.0}
    assert journal.is_foreign(orphan, "qec-trainer") is False
    out = journal.merge_foreign([orphan], [orphan], "qec-trainer")
    assert out == [orphan]


def test_trim_own_never_touches_another_apps_rows():
    """Eight of the ten copies trimmed the whole file by timestamp, deleting
    other apps' history during a write to a file they do not own."""
    mine = [entry(f"m{i}", timestamp=float(i)) for i in range(10)]
    theirs = [dict(FOREIGN_ROW, id=f"t{i}", timestamp=0.0) for i in range(5)]
    out = journal.trim_own(theirs + mine, "qec-trainer", cap=8)
    assert len(out) == 8
    assert [r for r in out if r["app"] == "quantum-tutor"] == theirs
    assert [r["id"] for r in out if r["app"] == "qec-trainer"] == \
        [f"m{i}" for i in range(7, 10)]


# ---------------------------------------------------------------------------
# Store behaviour
# ---------------------------------------------------------------------------

def test_log_mistake_appends_rather_than_merging(data_dir):
    """Three slips on one item are three rows: that is the signal coach counts
    and dashboard.load_mistakes documents."""
    for _ in range(3):
        journal.log_mistake(entry("same"))
    rows = journal.load_mistakes()
    assert len(rows) == 3
    assert {r["id"] for r in rows} == {"same"}


def test_a_missing_or_corrupt_file_reads_as_empty(data_dir):
    assert journal.load_mistakes() == []
    (data_dir / "mistakes.json").write_text("{not json")
    assert journal.load_mistakes() == []
    (data_dir / "mistakes.json").write_text('{"schema": 1}')
    assert journal.load_mistakes() == []


def test_load_mistakes_filters_by_app(data_dir):
    journal.log_mistake(entry("a", app="qec-trainer"))
    journal.log_mistake(entry("b", app="exam-sim"))
    assert len(journal.load_mistakes()) == 2
    assert [r["id"] for r in journal.load_mistakes("exam-sim")] == ["b"]


def test_set_mistake_cause_targets_the_newest_open_row(data_dir):
    journal.log_mistake(entry("i", timestamp=1.0))
    journal.log_mistake(entry("i", timestamp=2.0))
    updated = journal.set_mistake_cause("i", "misread", app="qec-trainer")
    assert updated is not None and updated["timestamp"] == 2.0
    rows = journal.load_mistakes()
    assert [r["cause"] for r in rows] == [None, "misread"]


def test_set_mistake_cause_falls_back_to_a_resolved_row(data_dir):
    journal.log_mistake(entry("i"))
    journal.resolve_mistakes("i", "qec-trainer")
    assert journal.set_mistake_cause("i", "confused", app="qec-trainer") is not None
    assert journal.load_mistakes()[0]["cause"] == "confused"


def test_set_mistake_cause_keeps_the_note_unless_asked(data_dir):
    """paper-drill's ``note: str = ""`` wiped a note whenever a cause was
    picked after the note had been typed."""
    journal.log_mistake(entry("i", note="little-endian again"))
    journal.set_mistake_cause("i", "misread", app="qec-trainer")
    assert journal.load_mistakes()[0]["note"] == "little-endian again"
    journal.set_mistake_cause("i", "misread", note="", app="qec-trainer")
    assert journal.load_mistakes()[0]["note"] == ""


def test_set_mistake_cause_on_an_unknown_item_returns_none(data_dir):
    assert journal.set_mistake_cause("nope", "misread", app="qec-trainer") is None


def test_set_mistake_cause_only_touches_its_own_app(data_dir):
    journal.log_mistake(entry("i", app="exam-sim"))
    assert journal.set_mistake_cause("i", "misread", app="qec-trainer") is None
    assert journal.load_mistakes()[0]["cause"] is None


def test_resolve_mistakes_counts_and_is_idempotent(data_dir):
    journal.log_mistake(entry("i"))
    journal.log_mistake(entry("i"))
    assert journal.resolve_mistakes("i", "qec-trainer") == 2
    assert journal.resolve_mistakes("i", "qec-trainer") == 0
    assert all(r["resolved"] for r in journal.load_mistakes())
    assert journal.open_mistakes("qec-trainer") == []


def test_open_mistakes_is_newest_first(data_dir):
    for i, ts in enumerate([3.0, 1.0, 2.0]):
        journal.log_mistake(entry(f"i{i}", timestamp=ts))
    assert [r["timestamp"] for r in journal.open_mistakes()] == [3.0, 2.0, 1.0]


def test_cause_counts(data_dir):
    journal.log_mistake(entry("a", cause="misread"))
    journal.log_mistake(entry("b", cause="misread"))
    journal.log_mistake(entry("c", cause="confused"))
    journal.log_mistake(entry("d"))                     # uncategorised
    assert journal.cause_counts("qec-trainer") == {
        "misread": 2, "confused": 1, journal.UNCATEGORISED: 1}
    assert journal.cause_counts("qec-trainer",
                                include_uncategorised=False) == {
        "misread": 2, "confused": 1}
    journal.resolve_mistakes("a", "qec-trainer")
    assert journal.cause_counts("qec-trainer", include_resolved=False,
                                include_uncategorised=False) == {
        "misread": 1, "confused": 1}


def test_calibration_summary_and_confidently_wrong(data_dir):
    journal.log_confidence("a", "qec-trainer", "Gates", 4, True)
    journal.log_confidence("b", "qec-trainer", "Gates", 4, False)
    journal.log_confidence("c", "qec-trainer", "Codes", 3, False)
    journal.log_confidence("d", "qec-trainer", "Codes", 1, False)
    assert journal.calibration_summary("qec-trainer") == {
        1: {"total": 1, "correct": 0},
        3: {"total": 1, "correct": 0},
        4: {"total": 2, "correct": 1},
    }
    wrong = journal.confidently_wrong("qec-trainer")
    assert sorted(r["id"] for r in wrong) == ["b", "c"]
    assert journal.confidently_wrong_by_category("qec-trainer") == {
        "Gates": 1, "Codes": 1}
    assert [r["id"] for r in
            journal.confidently_wrong("qec-trainer", min_confidence=4)] == ["b"]


def test_growth_cap_drops_our_oldest_and_keeps_theirs(data_dir, monkeypatch):
    monkeypatch.setattr(journal, "MISTAKES_MAX", 5)
    (data_dir / "mistakes.json").write_text(json.dumps([FOREIGN_ROW]))
    for i in range(10):
        journal.log_mistake(entry(f"i{i}", timestamp=float(i)))
    rows = journal.load_mistakes()
    assert rows.count(FOREIGN_ROW) == 1
    mine = [r["id"] for r in rows if r["app"] == "qec-trainer"]
    assert mine == ["i6", "i7", "i8", "i9"]             # 4 + the foreign row = 5


def test_every_write_is_atomic_and_stamps_a_sidecar(data_dir):
    journal.log_mistake(entry("i"))
    assert json.loads((data_dir / "mistakes.json").read_text())
    meta = json.loads((data_dir / "mistakes.json.schema.json").read_text())
    assert meta["kind"] == "mistakes" and meta["schema"] == 1
    assert not list(data_dir.glob("*.tmp"))


def test_a_refused_write_is_reported_not_raised(data_dir):
    """A journal written by a newer build must not be overwritten — and must
    not crash the drill either."""
    journal.log_mistake(entry("before"))
    meta = data_dir / "mistakes.json.schema.json"
    meta.write_text(json.dumps({"file": "mistakes.json", "kind": "mistakes",
                                "schema": 99}))
    journal.clear_write_error()
    journal.log_mistake(entry("after"))
    assert isinstance(journal.last_write_error(), schema.SchemaTooNewError)
    on_disk = json.loads((data_dir / "mistakes.json").read_text())
    assert [r["id"] for r in on_disk] == ["before"], "the newer file was clobbered"


def test_lock_is_re_exported_for_migrating_apps():
    from common.locking import lock
    assert journal.lock is lock


# ---------------------------------------------------------------------------
# Concurrency — real processes
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _no_lock(path, timeout=5.0, create=False):
    """The unlocked variant: what the journal did before the lock existed."""
    yield False


def journal_writer(data_dir: str, app: str, tag: str, rows: int,
                   locked: bool, barrier) -> None:
    """Child-process entry point.

    Must stay importable at module level — ``forkserver`` (the default start
    method on Linux from Python 3.14) re-imports this module in the child and
    looks the target up by name.
    """
    try:
        os.environ["QUANTUM_STUDY_DATA_DIR"] = data_dir     # before the import
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from common import journal as jrn
        if not locked:
            jrn.lock = _no_lock                             # the control group
        if barrier is not None:
            barrier.wait(timeout=JOIN_TIMEOUT)              # all start together
        for i in range(rows):
            jrn.log_mistake(jrn.make_mistake_entry(
                f"{tag}-{i}", app, "Gates", "q", "a", "b"))
            jrn.log_confidence(f"{tag}-{i}", app, "Gates", 3, False)
    except BaseException:                                   # pragma: no cover
        import traceback
        traceback.print_exc()
        raise SystemExit(1)


def _run(jobs, data_dir: Path, rows: int, locked: bool) -> None:
    ctx = multiprocessing.get_context()
    barrier = ctx.Barrier(len(jobs))
    procs = [ctx.Process(target=journal_writer,
                         args=(str(data_dir), app, tag, rows, locked, barrier),
                         name=f"writer-{tag}")
             for app, tag in jobs]
    for p in procs:
        p.start()
    try:
        for p in procs:
            p.join(JOIN_TIMEOUT)
    finally:
        for p in procs:
            if p.is_alive():                                # pragma: no cover
                p.terminate()
                p.join(5)
    stuck = [p.name for p in procs if p.exitcode is None]
    assert not stuck, f"writer(s) never finished (deadlock?): {stuck}"
    failed = {p.name: p.exitcode for p in procs if p.exitcode != 0}
    assert not failed, f"writer(s) exited non-zero: {failed}"


def _rows_on_disk(path: Path) -> list:
    text = path.read_text()
    try:
        data = json.loads(text)
    except ValueError as exc:                               # pragma: no cover
        pytest.fail(f"{path.name} is not valid JSON after the run: {exc}\n"
                    f"{text[:400]}")
    assert isinstance(data, list), f"{path.name} is not a JSON list"
    return data


def _seed(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "mistakes.json").write_text(json.dumps([FOREIGN_ROW]))
    (data_dir / "confidence.json").write_text(json.dumps([FOREIGN_CONFIDENCE_ROW]))


def _survivors(data_dir: Path, tags) -> tuple[int, int]:
    """(mistake rows kept, confidence rows kept) out of what was written."""
    want = {f"{tag}-{i}" for tag in tags for i in range(ROWS_PER_WRITER)}
    kept = []
    for name in ("mistakes.json", "confidence.json"):
        rows = _rows_on_disk(data_dir / name)
        kept.append(len({str(r.get("id")) for r in rows
                         if r.get("app") != "quantum-tutor"} & want))
    return kept[0], kept[1]


@pytest.mark.timeout(300)
def test_ten_apps_writing_at_once_lose_no_rows(tmp_path):
    """One process per app, all appending to one data directory at once."""
    from common import datadir
    data_dir = tmp_path / "quantum-study"
    _seed(data_dir)
    apps = list(datadir.APPS)
    _run([(app, app) for app in apps], data_dir, ROWS_PER_WRITER, locked=True)

    for name, foreign in (("mistakes.json", FOREIGN_ROW),
                          ("confidence.json", FOREIGN_CONFIDENCE_ROW)):
        rows = _rows_on_disk(data_dir / name)
        assert rows.count(foreign) == 1, (
            f"{name}: the seeded foreign row was rewritten, dropped or "
            f"duplicated — unknown keys must survive verbatim")
        expected = len(apps) * ROWS_PER_WRITER
        assert len(rows) == expected + 1, (
            f"{name}: expected {expected} rows + the foreign one, found "
            f"{len(rows)} — {expected + 1 - len(rows)} lost")
        for app in apps:
            ids = sorted(str(r["id"]) for r in rows if r.get("app") == app)
            assert ids == sorted(f"{app}-{i}" for i in range(ROWS_PER_WRITER)), (
                f"{name}: {app} lost or duplicated rows")


@pytest.mark.timeout(300)
def test_several_windows_of_one_app_lose_no_rows(tmp_path):
    """The case the lock alone has to carry.

    Every row claims the same ``app``, so preserving *foreign* rows cannot
    help: it works only because each helper re-reads the file inside the lock
    rather than before it.
    """
    data_dir = tmp_path / "quantum-study"
    _seed(data_dir)
    tags = [f"window{n}" for n in range(WRITERS)]
    _run([("qec-trainer", tag) for tag in tags], data_dir, ROWS_PER_WRITER,
         locked=True)

    mistakes, confidence = _survivors(data_dir, tags)
    want = WRITERS * ROWS_PER_WRITER
    assert mistakes == want, f"{want - mistakes} of {want} mistake rows lost"
    assert confidence == want, f"{want - confidence} of {want} rating rows lost"


@pytest.mark.timeout(300)
def test_the_same_race_without_the_lock_does_lose_rows(tmp_path):
    """The control group.  A concurrency test that has never been seen to fail
    proves nothing, so this runs the identical workload with ``lock`` replaced
    by a no-op and asserts that rows *are* lost.

    If this ever passes, either the machine is too slow to interleave the
    writers or the lock is no longer what is doing the work — investigate
    rather than deleting the test.
    """
    data_dir = tmp_path / "quantum-study"
    _seed(data_dir)
    tags = [f"window{n}" for n in range(WRITERS)]
    _run([("qec-trainer", tag) for tag in tags], data_dir, ROWS_PER_WRITER,
         locked=False)

    mistakes, confidence = _survivors(data_dir, tags)
    want = WRITERS * ROWS_PER_WRITER
    assert mistakes < want or confidence < want, (
        f"the unlocked variant kept every row ({mistakes}/{want} mistakes, "
        f"{confidence}/{want} ratings) — the writers did not interleave, so "
        f"the locked test above proved nothing on this run")


def test_the_lock_is_really_taken_and_is_released_on_a_hard_exit(tmp_path):
    """flock, not hope: the sidecar exists, and a killed holder frees it."""
    data_dir = tmp_path / "quantum-study"
    data_dir.mkdir(parents=True)
    target = data_dir / "mistakes.json"

    with locking.lock(target, create=True) as held:
        assert held, "flock is not available here — the suite would be a no-op"
    assert (data_dir / "mistakes.json.lock").exists()

    ctx = multiprocessing.get_context()
    proc = ctx.Process(target=_die_holding_the_lock, args=(str(target),))
    proc.start()
    proc.join(JOIN_TIMEOUT)
    assert proc.exitcode == 0

    with locking.lock(target, timeout=5.0) as held:
        assert held, "the lock was not released when its holder died"


def _die_holding_the_lock(target: str) -> None:
    """Child: take the lock, then die without unwinding (kernel must free it)."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from common import locking
    with locking.lock(target, create=True):
        os._exit(0)


def test_the_lock_is_re_entrant(tmp_path):
    """``log_mistake`` takes the lock and calls ``save_mistakes``, which takes
    it again: a second flock on a second fd would not be granted."""
    target = tmp_path / "mistakes.json"
    with locking.lock(target, create=True) as outer:
        assert outer
        with locking.lock(target) as inner:
            assert inner


def test_the_lock_creates_nothing_when_it_need_not(tmp_path):
    """A caller that may find nothing to do must leave an empty disk empty."""
    absent = tmp_path / "gone" / "mistakes.json"
    with locking.lock(absent) as held:
        assert held is False
    assert not absent.parent.exists()


if __name__ == "__main__":          # forkserver/spawn need this guard
    import tempfile
    with tempfile.TemporaryDirectory(prefix="common-journal-race-") as tmp:
        d = Path(tmp) / "quantum-study"
        _seed(d)
        tag_list = [f"window{n}" for n in range(WRITERS)]
        for locked_flag in (False, True):
            for f in ("mistakes.json", "confidence.json"):
                (d / f).write_text(json.dumps(
                    [FOREIGN_ROW if f == "mistakes.json"
                     else FOREIGN_CONFIDENCE_ROW]))
            _run([("qec-trainer", t) for t in tag_list], d, ROWS_PER_WRITER,
                 locked_flag)
            m, c = _survivors(d, tag_list)
            total = WRITERS * ROWS_PER_WRITER
            label = "locked  " if locked_flag else "unlocked"
            print(f"  {label}: mistakes {m}/{total} kept (lost {total - m}), "
                  f"confidence {c}/{total} kept (lost {total - c})")
