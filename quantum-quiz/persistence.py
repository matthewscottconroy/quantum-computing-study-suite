"""Persist quiz session history, and adapt this app to the shared stores.

Three kinds of data, two owners:

* **This app's own files** — ``quiz_history.json`` (sessions, the SRS input),
  ``quiz_draft.json`` (crash recovery) and ``quiz_settings.json`` (the
  confidence opt-out).  Their schemas are load-bearing: ``coach.py`` and
  ``dashboard.py`` parse the history.  They are written here, but now through
  :mod:`common.schema`, so every write is atomic, version-stamped and backed
  up, and a file written by a newer build of the suite is refused rather than
  silently downgraded.
* **The suite-wide stores** — ``mistakes.json``, ``confidence.json`` and
  ``quiz_flagged.json`` — are owned by :mod:`common.journal` and
  :mod:`common.flags`.  Everything below them is a thin adapter that keeps
  this app's call signatures and return shapes; no store logic is duplicated.

Paths are resolved **at call time** from :mod:`common.datadir`, so
``QUANTUM_STUDY_DATA_DIR`` is honoured by tests and power users without any
module constant to monkeypatch.
"""

from __future__ import annotations

import datetime
import hashlib
import math
import pathlib

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir, flags, journal, schema
from common.jsonio import read_json_dict
from common.locking import lock

from core.models import SessionStats

# ── Identity ──────────────────────────────────────────────────────────────────
#: The app directory name.  This is what coach.py / dashboard.py group by, and
#: what marks our rows in the two shared journals.
APP_ID = "quantum-quiz"

#: Cap on a flag's stored label.  The suite-wide value from common.flags — it
#: was 100 here before the migration; common.flags.toggle_flag applies its own
#: cap on the way to disk, so keeping a local 100 would have been a fiction.
FLAG_LABEL_MAX = flags.LABEL_MAX

# Time-based SRS: 14-day half-life.  A session saved 14 days ago contributes
# half the weight of one saved today; 28 days ago → one quarter, etc.
_HALF_LIFE_DAYS = 14.0

# ── Schema kinds ──────────────────────────────────────────────────────────────
# mistakes / confidence / flagged / history / settings are registered by
# common.schema.  The interrupted-session draft is ours alone, so it registers
# its own kind here (replace=True: a module reload must not raise).
DRAFT_KIND = "quiz-draft"
schema.register(
    schema.FileSchema(DRAFT_KIND,
                      description="quantum-quiz interrupted-session draft "
                                  "(quiz_draft.json)"),
    replace=True,
)


# ── Paths (resolved now, never cached) ────────────────────────────────────────

def data_dir() -> pathlib.Path:
    """The suite data directory (``QUANTUM_STUDY_DATA_DIR`` or the default)."""
    return datadir.data_dir()


def history_file() -> pathlib.Path:
    return datadir.app_file(APP_ID, "history")


def draft_file() -> pathlib.Path:
    return datadir.app_file(APP_ID, "draft")


def flagged_file() -> pathlib.Path:
    return datadir.app_file(APP_ID, "flagged")


def settings_file() -> pathlib.Path:
    return datadir.app_file(APP_ID, "settings")


def mistakes_file() -> pathlib.Path:
    return journal.mistakes_path()


def confidence_file() -> pathlib.Path:
    return journal.confidence_path()


# ── Session history (this app's own schema — unchanged on disk) ───────────────

def save_session(stats: SessionStats) -> None:
    history = _load_raw()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    history.append({
        "date": str(datetime.date.today()),
        "timestamp": timestamp,
        "answered": stats.answered,
        "average_score": round(stats.average_score, 2),
        "records": [
            {
                "question_id": r.question_id,
                "subject": r.question.subject,
                "topic": r.question.topic,
                "score": r.evaluation.score,
                "elapsed_seconds": r.elapsed_seconds,
                "timestamp": timestamp,
            }
            for r in stats.history
        ],
    })
    schema.save_versioned(history_file(), history, "history")
    clear_draft()


def save_draft(stats: SessionStats) -> None:
    """Overwrite the in-progress draft so a crash doesn't lose answered questions."""
    data = {
        "date": str(datetime.date.today()),
        "answered": stats.answered,
        "skipped": stats.skipped,
        "average_score": round(stats.average_score, 2),
        "questions": [
            {
                "subject": r.question.subject,
                "topic": r.question.topic,
                "difficulty": r.question.difficulty,
                "type": r.question.question_type,
                "question": r.question.text,
                "answer": r.user_answer,
                "score": r.evaluation.score,
                "verdict": r.evaluation.verdict,
                "feedback": r.evaluation.feedback,
                "model_answer": r.evaluation.model_answer,
            }
            for r in stats.history
        ],
    }
    schema.save_versioned(draft_file(), data, DRAFT_KIND)


def clear_draft() -> None:
    path = draft_file()
    for target in (path, schema.sidecar_path(path)):
        try:
            target.unlink()
        except OSError:
            pass


def has_draft() -> bool:
    return draft_file().exists()


def avg_scores_by_subject() -> dict[str, float]:
    """Time-decayed average score per subject across all saved sessions."""
    return _weighted_averages(key_fn=lambda r: r.get("subject", ""))


def avg_scores_by_topic() -> dict[str, float]:
    """Time-decayed average score per subject::topic key."""
    return _weighted_averages(
        key_fn=lambda r: f"{r.get('subject','')}::{r.get('topic','')}"
    )


def question_score_weights() -> dict[str, float]:
    """Return per-question SRS sampling weights keyed by question_id.

    Weight formula (14-day half-life):
        weight    = exp(-days * log(2) / 14.0)
        avg_score = weighted_sum / weighted_count
        result[qid] = max(0.5, 2.0 - avg_score * 0.15)

    Unseen questions receive weight 1.25.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    buckets: dict[str, list[tuple[float, int]]] = {}

    for session in _load_raw():
        for r in session.get("records", []):
            qid = r.get("question_id")
            if not qid:
                continue
            w = _record_weight(r, session, now)
            buckets.setdefault(qid, []).append((w, r.get("score", 0)))

    result: dict[str, float] = {}
    for qid, pairs in buckets.items():
        total_w = sum(w for w, _ in pairs)
        avg_score = sum(w * s for w, s in pairs) / total_w if total_w else 0.0
        result[qid] = max(0.5, 2.0 - avg_score * 0.15)
    return result


# ── Flag for review (common.flags) ────────────────────────────────────────────
#
# quiz_flagged.json = [ {id, label, category, app, timestamp}, … ], the shared
# contract coach.py reads.  The store itself — locking, the atomic rewrite, the
# legacy bare-id upgrade, the schema stamp — is common.flags; the wrappers here
# only bind this app's file and app id so callers keep their one-argument form.

def question_flag_id(subject: str, topic: str, text: str) -> str:
    """Stable, question-specific flag id: ``subject::topic::<sha1(text)[:10]>``.

    Questions are generated on demand, so two questions on the same topic must
    not share one flag entry (flagging the second would silently drop the
    first).  The hash is over whitespace-normalised question text so the same
    question always maps to the same id.
    """
    compact = " ".join((text or "").split())
    digest = hashlib.sha1(compact.encode("utf-8")).hexdigest()[:10]
    return f"{subject}::{topic}::{digest}"


def make_flag_label(text, limit: int = FLAG_LABEL_MAX) -> str:
    """Collapse whitespace and truncate to ``limit`` chars with an ellipsis."""
    return flags.make_label(text, limit)


def load_flagged() -> list[dict]:
    """Flagged entries in the shared contract shape, oldest first."""
    return flags.load_flagged(flagged_file(), APP_ID)


def flagged_ids() -> set[str]:
    return flags.flagged_ids(flagged_file(), APP_ID)


def is_flagged(flag_id: str) -> bool:
    return flags.is_flagged(flagged_file(), flag_id, APP_ID)


def toggle_flag(flag_id: str, label: str, category: str) -> bool:
    """Flag ``flag_id`` if it is not flagged, otherwise unflag it.

    Returns the new state (True = now flagged).  ``flag_id`` is normally
    :func:`question_flag_id`, ``label`` the question text (stored collapsed and
    truncated) and ``category`` the subject.
    """
    return flags.toggle_flag(flagged_file(), flag_id, label, category,
                             app=APP_ID)


def unflag(flag_id: str) -> None:
    flags.unflag(flagged_file(), flag_id, app=APP_ID)


# ── Mistake journal & confidence calibration (common.journal) ─────────────────
#
# Both files are shared with the other nine apps and several apps can be open
# at once.  common.journal owns the locking, the read-inside-the-lock, the
# foreign-row preservation and the per-app growth cap; the wrappers below only
# adapt argument order and return shape to this app's existing callers.

MISTAKE_CAUSES = journal.MISTAKE_CAUSES
CAUSE_LABELS = journal.CAUSE_LABELS
CONFIDENCE_LABELS = journal.CONFIDENCE_LABELS
UNCATEGORISED = journal.UNCATEGORISED
TEXT_MAX = journal.TEXT_MAX
NOTE_MAX = journal.NOTE_MAX
MISTAKES_MAX = journal.MISTAKES_MAX
CONFIDENCE_MAX = journal.CONFIDENCE_MAX

clip_text = journal.clip_text
normalise_cause = journal.normalise_cause

# App setting keys (quiz_settings.json — this app's own file, not a shared one).
CONFIDENCE_PROMPT_SETTING = "confidence_prompt_enabled"


def mistake_item_id(subject: str, question_text: str) -> str:
    """Stable item id: 16 hex digits of sha1(subject + whitespace-normalised text).

    Questions are generated on demand, so the id has to come from content: the
    same question asked again in a later session maps to the same journal item
    (which is what makes ``resolved`` meaningful).
    """
    compact = " ".join((question_text or "").split())
    payload = f"{subject or ''}\x1f{compact}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def make_mistake_entry(item_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str, cause=None,
                       note: str = "", timestamp: float | None = None,
                       resolved: bool = False, app: str = APP_ID) -> dict:
    """Build one journal entry — pure, no I/O.  This app's argument order."""
    return journal.make_mistake_entry(
        item_id, app, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=note, timestamp=timestamp, resolved=resolved,
    )


def load_mistakes(app: str | None = None) -> list[dict]:
    """Well-formed journal entries, oldest first.

    Rows with no ``id`` are skipped: they cannot be matched, resolved or
    displayed.  They are **not** removed from the file.
    """
    return [e for e in journal.load_mistakes(app) if e.get("id")]


def get_mistake(item_id: str, app: str = APP_ID) -> dict | None:
    """The newest entry for this app+id, or None."""
    rows = [e for e in journal.mistakes_for(item_id, app) if e.get("id")]
    return dict(rows[-1]) if rows else None


def log_mistake(item_id: str, category: str, question: str, your_answer: str,
                correct_answer: str, cause=None, note: str = "",
                app: str = APP_ID) -> dict:
    """Record a wrong answer; returns the stored entry.

    A repeat miss of the same item is a **new row**, not an update of the old
    one: repetition is the signal ``coach --mistakes`` and the dashboard count,
    and merging destroys it (see ``common/README.md``, "Divergences
    reconciled").
    """
    entry = make_mistake_entry(item_id, category, question, your_answer,
                               correct_answer, cause=cause, note=note, app=app)
    return journal.log_mistake(entry)


def set_mistake_cause(item_id: str, cause, note=None, app: str = APP_ID) -> bool:
    """Categorise this app's newest open entry for *item_id*.

    ``note=None`` leaves the stored note alone; ``note=""`` clears it.
    Returns False when there is nothing to update.
    """
    return journal.set_mistake_cause(item_id, cause, note, app=app) is not None


def resolve_mistake(item_id: str, app: str = APP_ID, resolved: bool = True) -> bool:
    """Mark every entry for this app+id resolved (or re-open them).

    Returns True if anything changed.
    """
    if resolved:
        return journal.resolve_mistakes(item_id, app) > 0
    with journal.lock(journal.mistakes_path()):
        rows = journal.load_mistakes()
        changed = 0
        for row in rows:
            if (row.get("app") == app and str(row.get("id")) == str(item_id)
                    and row.get("resolved")):
                row["resolved"] = False
                changed += 1
        if changed:
            journal.save_mistakes(rows, app)
        return changed > 0


def mistake_cause_counts(app: str | None = None,
                         include_resolved: bool = False) -> dict[str, int]:
    """How many mistakes fall under each cause — the point of the journal.

    The key ``"uncategorised"`` counts entries still carrying ``cause=None``.
    """
    return journal.cause_counts(app, include_resolved=include_resolved,
                                entries=load_mistakes(app))


def unresolved_mistakes(app: str | None = None) -> list[dict]:
    """Open entries, oldest first (file order)."""
    return [e for e in load_mistakes(app) if not e.get("resolved")]


def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp: float | None = None,
                          app: str = APP_ID) -> dict:
    """Build one calibration row — pure, no I/O.  Confidence is clamped to 1–4."""
    return journal.make_confidence_entry(item_id, app, category=category,
                                         confidence=confidence,
                                         correct=correct, timestamp=timestamp)


def load_confidence(app: str | None = None) -> list[dict]:
    """Calibration rows that carry both an id and a usable 1–4 rating."""
    return [
        e for e in journal.load_confidence(app)
        if e.get("id") and journal.coerce_confidence(e.get("confidence")) is not None
    ]


def log_confidence(item_id: str, category: str, confidence: int, correct: bool,
                   app: str = APP_ID) -> dict | None:
    """Append one confidence/outcome pairing; returns the stored row.

    A rating outside 1–4 records nothing and returns None — a rating the
    learner never gave must not end up in their calibration curve.
    """
    return journal.log_confidence(item_id, app, category=category,
                                  confidence=confidence, correct=correct)


def confidence_calibration(app: str | None = None) -> dict[int, dict]:
    """Per confidence level: ``{"n": int, "correct": int, "accuracy": float}``."""
    summary = journal.calibration_summary(app, entries=load_confidence(app))
    out: dict[int, dict] = {}
    for level, bucket in summary.items():
        total = bucket["total"]
        out[level] = {
            "n": total,
            "correct": bucket["correct"],
            "accuracy": bucket["correct"] / total if total else 0.0,
        }
    return out


def confidently_wrong(app: str | None = None, min_confidence: int = 3) -> dict[str, int]:
    """Count of 'sure but wrong' answers per category — the unknown unknowns."""
    counts: dict[str, int] = {}
    for row in journal.confidently_wrong(app, min_confidence=min_confidence,
                                         entries=load_confidence(app)):
        key = str(row.get("category") or "—")
        counts[key] = counts.get(key, 0) + 1
    return counts


def journal_write_error():
    """The last write common.journal refused (a newer-schema file), or None."""
    return journal.last_write_error()


# ── App settings (this app's own file) ────────────────────────────────────────

def load_settings() -> dict:
    """quiz_settings.json as a dict; {} when missing, corrupt or not an object."""
    return schema.load_versioned(settings_file(), "settings",
                                 reader=read_json_dict)


def save_settings(settings: dict) -> None:
    schema.save_versioned(settings_file(), settings, "settings")


def get_setting(key: str, default=None):
    return load_settings().get(key, default)


def set_setting(key: str, value) -> None:
    # Locked: two windows of this app must not each read the file, flip one
    # key and write back, losing the other's change.
    with lock(settings_file(), create=True):
        settings = load_settings()
        settings[key] = value
        save_settings(settings)


def confidence_prompt_enabled() -> bool:
    """True unless the user has opted out of the confidence strip."""
    return bool(get_setting(CONFIDENCE_PROMPT_SETTING, True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    set_setting(CONFIDENCE_PROMPT_SETTING, bool(enabled))


# ── Internals ─────────────────────────────────────────────────────────────────

def _record_weight(r: dict, session: dict,
                   now: datetime.datetime) -> float:
    """Compute time-based weight for a single record using 14-day half-life."""
    ts_str = r.get("timestamp") or session.get("timestamp")
    if ts_str:
        try:
            ts = datetime.datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=datetime.timezone.utc)
            days = (now - ts).total_seconds() / 86400.0
        except Exception:
            days = 0.0
    else:
        try:
            d = datetime.date.fromisoformat(session.get("date", ""))
            days = (now.date() - d).days
        except Exception:
            days = 0.0
    return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)


def _weighted_averages(key_fn) -> dict[str, float]:
    """Build a time-decayed weighted average score per key."""
    now = datetime.datetime.now(datetime.timezone.utc)
    buckets: dict[str, list[tuple[float, int]]] = {}

    for session in _load_raw():
        for r in session.get("records", []):
            key = key_fn(r)
            if not key or key.startswith("::"):
                continue
            score = r.get("score", 0)
            weight = _record_weight(r, session, now)
            buckets.setdefault(key, []).append((weight, score))

    return {
        k: sum(w * s for w, s in pairs) / sum(w for w, _ in pairs)
        for k, pairs in buckets.items()
    }


def _load_raw() -> list[dict]:
    """Saved sessions, migrated forward in memory; [] when missing or corrupt."""
    return [s for s in schema.load_versioned(history_file(), "history")
            if isinstance(s, dict)]


#: Public alias — ``_load_raw`` predates it and is still used by the history screen.
load_history = _load_raw
