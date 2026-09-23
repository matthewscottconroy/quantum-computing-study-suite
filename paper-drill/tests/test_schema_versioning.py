"""Every file paper-drill writes carries a schema version, migrates forward,
refuses a downgrade, and is backed up before the first write of a session.

The suite now holds data you cannot regenerate — the mistake journal,
confidence ratings, session history, the paper library.  Until ``common.schema``
there was no version marker anywhere, no migration path, and one corrupt write
was unrecoverable.  These tests pin the four properties that insurance has to
have, for each of the six files this app touches.

The marker is a **sidecar** (``paper_history.json.schema.json``), not a key
inside the data, because ``coach._load_list``, ``dashboard._load`` and
``dashboard._read_journal`` all require the top level of these files to be a
plain JSON list — a ``{"schema": 1, "rows": [...]}`` wrapper would make every
one of them read the file as empty.  ``test_every_file_is_still_a_bare_json_*``
below is what keeps that true from this side.
"""
from __future__ import annotations

import json

import pytest

import persistence
from common import journal, schema

#: (label, path helper, writer, reader, schema kind)
STORES = [
    ("history", "history_path", "history"),
    ("library", "library_path", persistence.LIBRARY_KIND),
    ("flagged", "flagged_path", "flagged"),
    ("settings", "settings_path", "settings"),
    ("mistakes", "mistakes_path", "mistakes"),
    ("confidence", "confidence_path", "confidence"),
]


def _write_everything() -> None:
    """One write through each of this app's six stores."""
    from core.models import SessionStats

    persistence.save_session(SessionStats(title="P", total=1, scores=[7]))
    persistence.save_paper("P", "body", 3)
    persistence.toggle_flag("paper-0000000000000001", "Q", "P")
    persistence.set_confidence_prompt_enabled(False)
    persistence.log_mistake("paper-a", "P", "Q", "w", "r")
    persistence.log_confidence("paper-a", "P", 3, False)


def _path(name: str):
    return getattr(persistence, name)()


# ---------------------------------------------------------------------------
# The marker
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,helper,kind", STORES,
                         ids=[s[0] for s in STORES])
def test_every_file_gets_a_version_sidecar(data_dir, label, helper, kind):
    _write_everything()
    path = _path(helper)
    assert path.exists(), f"{label} was not written"
    sidecar = schema.sidecar_path(path)
    assert sidecar.exists(), f"{label} has no schema sidecar"
    meta = json.loads(sidecar.read_text())
    assert meta["file"] == path.name
    assert meta["kind"] == kind
    assert meta["schema"] == schema.get(kind).version == 1
    assert meta["written_by"].startswith("common/")
    assert isinstance(meta["updated"], float)


@pytest.mark.parametrize("label,helper,kind", STORES,
                         ids=[s[0] for s in STORES])
def test_the_data_file_itself_is_unchanged_json(data_dir, label, helper, kind):
    """No on-disk format changed: coach.py and dashboard.py open these files by
    name and require a bare list (or, for settings, a bare object)."""
    _write_everything()
    data = json.loads(_path(helper).read_text())
    if label == "settings":
        assert isinstance(data, dict)
    else:
        assert isinstance(data, list)
    assert "schema" not in (data if isinstance(data, dict) else {})


def test_the_registered_kinds_are_the_ones_this_app_uses():
    assert persistence.LIBRARY_KIND == "paper_library"
    for _label, _helper, kind in STORES:
        assert kind in schema.kinds(), kind


def test_registering_the_library_kind_twice_is_not_an_error():
    """persistence is reloaded by some tests; registration must be idempotent."""
    import importlib

    before = schema.get(persistence.LIBRARY_KIND)
    importlib.reload(persistence)
    assert schema.get(persistence.LIBRARY_KIND) is before


# ---------------------------------------------------------------------------
# Reading an older file: migrate forward, in memory
# ---------------------------------------------------------------------------

def test_an_unmarked_file_is_read_as_v1_and_is_not_rewritten(data_dir):
    """Every file already on a learner's disk has no sidecar.  It is a v1 file,
    it reads normally, and merely reading it writes nothing."""
    data_dir.mkdir(parents=True, exist_ok=True)
    path = persistence.history_path()
    path.write_text(json.dumps([{"title": "old", "total": 1,
                                 "average": 5.0, "scores": [5]}]))
    assert not schema.sidecar_path(path).exists()

    assert schema.stored_version(path, "history") == 1
    assert [s["title"] for s in persistence._load_raw()] == ["old"]
    assert not schema.sidecar_path(path).exists()   # a read is never destructive


def test_a_v1_file_migrates_forward_when_the_format_moves_on(data_dir, monkeypatch):
    """The machinery, exercised with a synthetic v2 of the history schema.

    Every real kind is at v1 with no migrations today (the sidecar was
    introduced *without* changing any format), so this is the only way to prove
    the forward path actually runs.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    path = persistence.history_path()
    path.write_text(json.dumps([{"title": "old", "total": 1,
                                 "average": 5.0, "scores": [5]}]))

    def _v1_to_v2(rows):
        return [{**r, "app": "paper-drill"} for r in rows if isinstance(r, dict)]

    original = schema.get("history")
    schema.register(schema.FileSchema("history", version=2,
                                      migrations={1: _v1_to_v2}), replace=True)
    try:
        rows = persistence._load_raw()
        assert rows == [{"title": "old", "total": 1, "average": 5.0,
                         "scores": [5], "app": "paper-drill"}]
        # …and the migrated shape is what gets written back, stamped v2.
        from core.models import SessionStats
        persistence.save_session(SessionStats(title="new", total=1, scores=[9]))
        assert json.loads(schema.sidecar_path(path).read_text())["schema"] == 2
        assert [r["title"] for r in json.loads(path.read_text())] == ["old", "new"]
    finally:
        schema.register(original, replace=True)


# ---------------------------------------------------------------------------
# Refusing a downgrade
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,helper,kind", STORES,
                         ids=[s[0] for s in STORES])
def test_a_newer_file_is_refused_not_corrupted(data_dir, label, helper, kind):
    """A build that does not understand v9 must not overwrite a v9 file with
    its v1 view of it — that is exactly how the newer build's fields get
    silently deleted."""
    _write_everything()
    path = _path(helper)
    before = path.read_text()
    schema.write_meta(path, kind, version=9)
    persistence.clear_write_error()

    # Each store's own write path, and none of them may raise.
    if label == "history":
        from core.models import SessionStats
        assert persistence.save_session(SessionStats(title="x", total=1,
                                                     scores=[1])) is False
    elif label == "library":
        persistence.save_paper("x", "y", 1)
    elif label == "flagged":
        persistence.toggle_flag("paper-0000000000000002", "Q2", "P")
    elif label == "settings":
        persistence.set_confidence_prompt_enabled(True)
    elif label == "mistakes":
        persistence.log_mistake("paper-b", "P", "Q", "w", "r")
    else:
        persistence.log_confidence("paper-b", "P", 4, False)

    assert path.read_text() == before, f"{label} was overwritten by an older build"
    err = persistence.last_write_error()
    assert isinstance(err, schema.SchemaTooNewError)
    assert err.found == 9 and err.understood == 1
    persistence.clear_write_error()
    assert persistence.last_write_error() is None


def test_a_refused_journal_write_never_reaches_the_drill(data_dir):
    """The refusal is recorded, not raised: a study session must not die
    because the journal is from the future."""
    persistence.log_mistake("paper-a", "P", "Q", "w", "r")
    schema.write_meta(persistence.mistakes_path(), "mistakes", version=7)
    journal.clear_write_error()

    entry = persistence.log_mistake("paper-b", "P", "Q", "w", "r")  # must not raise
    assert entry["id"] == "paper-b"
    rows = json.loads(persistence.mistakes_path().read_text())
    assert [r["id"] for r in rows] == ["paper-a"]                   # unchanged
    assert isinstance(journal.last_write_error(), schema.SchemaTooNewError)
    journal.clear_write_error()


# ---------------------------------------------------------------------------
# Rotating backups
# ---------------------------------------------------------------------------

def test_the_first_write_of_a_session_backs_the_file_up(data_dir):
    from core.models import SessionStats

    path = persistence.history_path()
    persistence.save_session(SessionStats(title="one", total=1, scores=[1]))
    assert not path.with_name(path.name + ".bak").exists()   # nothing existed before

    # A new session: the state it started from is what is worth getting back to.
    schema.reset_session(path)
    persistence.save_session(SessionStats(title="two", total=1, scores=[2]))
    backup = path.with_name(path.name + ".bak")
    assert backup.exists()
    assert [s["title"] for s in json.loads(backup.read_text())] == ["one"]

    # …and one backup per session, however many writes it makes.
    persistence.save_session(SessionStats(title="three", total=1, scores=[3]))
    assert [s["title"] for s in json.loads(backup.read_text())] == ["one"]


def test_three_generations_are_kept_and_can_be_restored(data_dir):
    from core.models import SessionStats

    path = persistence.history_path()
    for n, title in enumerate(("one", "two", "three", "four")):
        schema.reset_session(path)
        persistence.save_session(SessionStats(title=title, total=1, scores=[n]))

    gens = schema.backup_paths(path)
    assert len(gens) == 3
    assert [g.name for g in gens] == ["paper_history.json.bak",
                                      "paper_history.json.bak.1",
                                      "paper_history.json.bak.2"]
    # .bak holds the state before the newest write: one, two, three.
    assert [s["title"] for s in json.loads(gens[0].read_text())] == \
        ["one", "two", "three"]
    assert [s["title"] for s in json.loads(gens[1].read_text())] == ["one", "two"]
    assert [s["title"] for s in json.loads(gens[2].read_text())] == ["one"]

    # And the whole point: a corrupt current file can be rolled back.
    path.write_text("{ truncated by a power cut")
    assert persistence._load_raw() == []
    assert schema.restore_backup(path) is True
    assert [s["title"] for s in persistence._load_raw()] == ["one", "two", "three"]


def test_a_backup_failure_never_stops_the_write(data_dir, monkeypatch):
    from core.models import SessionStats

    path = persistence.history_path()
    persistence.save_session(SessionStats(title="one", total=1, scores=[1]))
    schema.reset_session(path)
    monkeypatch.setattr(schema.shutil, "copy2",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("full disk")))
    persistence.save_session(SessionStats(title="two", total=1, scores=[2]))
    assert [s["title"] for s in persistence._load_raw()] == ["one", "two"]
