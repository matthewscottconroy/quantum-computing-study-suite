"""Cross-process safety for the two *shared* journal files.

``mistakes.json`` and ``confidence.json`` live in the suite data directory and
every app in the suite appends to the same two files.  Each app writes them by
read-modify-write: load the list, append or amend its own rows, write the whole
list back.  The write itself is atomic (temp file + ``os.replace``), but that is
not enough — **the read is stale**.  Two apps open at once (which ``launch.py``
explicitly invites: "run several at once") interleave like this:

    app A: read [r1]            app B: read [r1]
    app A: write [r1, a1]
                                app B: write [r1, b1]      <-- a1 is gone

Measured, not theoretical: three processes appending 60 rows each in that
pattern kept 103 of 180 rows.  The lost rows are exactly the data these two
features exist to collect.

This module is the fix, and it is a **verbatim copy in all ten app trees** (the
apps cannot import one another: each is a self-contained tree with its own
top-level ``config.py``/``core/``/``ui/``, see pyproject.toml).  Keep the copies
identical — ``tests/test_journal_concurrency.py`` asserts that they are.

Two pieces:

:func:`lock`
    An exclusive advisory lock (``fcntl.flock``) on a sidecar lock file —
    ``mistakes.json.lock`` beside ``mistakes.json`` — held for the *whole*
    read-modify-write, so the read is never stale.  The sidecar is locked
    rather than the journal itself because ``os.replace`` swaps the journal's
    inode: a lock taken on the old inode would not exclude a writer that opened
    the new one.

    Properties that matter for a GUI:

    * **bounded** — the wait is ``timeout`` seconds (5 by default), never
      indefinite; a drill can stall for a moment, never hang;
    * **always released** — it is a context manager with ``try/finally``, and
      the lock is tied to an open file descriptor, so an exception, ``os._exit``
      or a hard crash releases it too (the kernel closes the fd);
    * **degrades, never fails** — no ``fcntl`` (Windows), a read-only or
      lock-hostile filesystem (NFS without lockd, some FUSE mounts), or a
      timeout falls back to today's unsynchronised behaviour instead of raising
      or blocking.  ``lock()`` yields True when the lock is really held and
      False when it degraded, which is what the test suite asserts on.
    * **creates nothing it does not have to** — the sidecar needs the data
      directory to exist.  Callers that are certain to write pass
      ``create=True`` (they would create the directory anyway); callers that
      may find nothing to do pass nothing, so a no-op stays a no-op and leaves
      an empty disk empty.
    * **re-entrant** — ``log_mistake()`` takes the lock and calls
      ``save_mistakes()``, which takes it again.  A second ``flock`` on a second
      file descriptor in the same process would *not* be granted, so the
      re-entry is tracked per path with a thread lock plus a depth counter.

    Readers stay lock-free on purpose: every write is still a single atomic
    ``os.replace``, so a reader sees either the old file or the new one, never a
    half-written one.  ``coach.py`` and ``dashboard.py`` therefore need no
    changes, and the on-disk format is unchanged — still one JSON list.

:func:`merge_foreign`
    The second half of the contract: a rewrite must put back every row this app
    does not own **exactly as it was read**, unknown keys included.  Apps
    normalise rows through their own schema on load, which would otherwise
    silently drop a key another app added and rewrite a foreign row in this
    app's shape.
"""
from __future__ import annotations

import errno
import threading
import time
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl                       # POSIX only; absent on Windows
except ImportError:                    # pragma: no cover - not POSIX
    fcntl = None                       # type: ignore[assignment]

#: Sidecar suffix: ``mistakes.json`` is guarded by ``mistakes.json.lock``.
LOCK_SUFFIX = ".lock"

#: Longest wait for the lock before giving up and writing anyway.  Journal
#: writes are a few kB, so a contended wait is milliseconds; 5 s is a ceiling
#: for a wedged peer, not an expected delay.
LOCK_TIMEOUT = 5.0

_POLL_START = 0.0005                   # first retry delay, doubling to _POLL_MAX
_POLL_MAX = 0.02

# flock(2) reports "another holder has it" as EWOULDBLOCK/EAGAIN (EACCES on
# some systems).  Anything else means this filesystem will not lock at all —
# retrying it would burn the whole timeout for nothing.
_CONTENDED = frozenset(
    e for e in (getattr(errno, name, None)
                for name in ("EAGAIN", "EWOULDBLOCK", "EACCES", "EINTR"))
    if e is not None
)


class _Guard:
    """Per-path re-entrancy state (see the ``lock`` docstring)."""

    __slots__ = ("rlock", "depth", "handle")

    def __init__(self) -> None:
        self.rlock = threading.RLock()
        self.depth = 0
        self.handle = None


_REGISTRY: dict[str, _Guard] = {}
_REGISTRY_LOCK = threading.Lock()


def lock_path_for(path) -> Path:
    """The sidecar lock file guarding *path* (``<path>.lock``)."""
    target = Path(path)
    return target.with_name(target.name + LOCK_SUFFIX)


def _guard_for(key: str) -> _Guard:
    with _REGISTRY_LOCK:
        guard = _REGISTRY.get(key)
        if guard is None:
            guard = _REGISTRY[key] = _Guard()
        return guard


def _flock(handle, timeout: float) -> bool:
    """Take an exclusive flock on *handle*, waiting at most *timeout* seconds."""
    deadline = time.monotonic() + max(0.0, timeout)
    delay = _POLL_START
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError as exc:
            if exc.errno not in _CONTENDED:
                return False                      # this filesystem cannot lock
            if time.monotonic() >= deadline:
                return False                      # bounded: never hang the GUI
            time.sleep(min(delay, _POLL_MAX))
            delay *= 2


def _acquire(path, timeout: float, create: bool):
    """Open and lock the sidecar for *path*; None when locking is unavailable."""
    if fcntl is None:
        return None
    sidecar = lock_path_for(path)
    try:
        if create:
            sidecar.parent.mkdir(parents=True, exist_ok=True)
        handle = open(sidecar, "a+b")             # never truncates, never reads
    except OSError:
        # No data directory (with create=False: then there is no journal file
        # either, so there is nothing to protect), or it is read-only.
        return None
    if _flock(handle, timeout):
        return handle
    _release(handle)
    return None


def _release(handle) -> None:
    """Drop the lock and close the descriptor (closing alone would suffice)."""
    try:
        if fcntl is not None:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        try:
            handle.close()
        except OSError:
            pass


@contextmanager
def lock(path, timeout: float = LOCK_TIMEOUT, create: bool = False):
    """Hold the write lock for the journal at *path* for the whole ``with`` body.

    Wrap the *entire* read-modify-write, and re-read the file inside the body —
    a read taken before the lock is exactly the stale read this exists to stop.

    Pass ``create=True`` when the body always writes: the sidecar then brings
    the data directory into being with it, so even the first write ever made
    into a fresh data directory is serialised.  Leave it alone when the body
    may decide it has nothing to do — a no-op must not create a directory.

    Yields True when the lock is genuinely held, False when it degraded to
    unsynchronised behaviour (no ``fcntl``, unlockable filesystem, no data
    directory, or the timeout expired).  Never raises, never blocks longer than
    *timeout* in total (the two stages — other threads here, then other
    processes — share one deadline), and always releases on the way out.
    """
    deadline = time.monotonic() + max(0.0, timeout)
    guard = _guard_for(str(lock_path_for(path)))
    if not guard.rlock.acquire(timeout=max(0.0, timeout)):
        yield False                               # a wedged thread: write anyway
        return
    try:
        if guard.depth == 0:
            guard.handle = _acquire(
                path, max(0.0, deadline - time.monotonic()), create)
        guard.depth += 1
        try:
            yield guard.handle is not None
        finally:
            guard.depth -= 1
            if guard.depth == 0 and guard.handle is not None:
                _release(guard.handle)
                guard.handle = None
    finally:
        guard.rlock.release()


def row_app(row) -> str | None:
    """The ``app`` field of *row*, or None when it has no usable one."""
    if not isinstance(row, dict):
        return None
    app = row.get("app")
    if isinstance(app, str) and app.strip():
        return app.strip()
    return None


def is_foreign(row, app: str) -> bool:
    """True when *row* was written by a different app in the suite.

    A row with no ``app`` field is *not* foreign: the loaders claim it for
    themselves, so treating it as foreign would write it twice.
    """
    owner = row_app(row)
    return owner is not None and owner != app


def merge_foreign(disk_rows, entries, app: str) -> list:
    """The rows to write: *entries*, with foreign rows taken from *disk_rows*.

    ``entries`` is this app's view of the file, which may be stale and whose
    foreign rows may have been normalised through this app's schema on load.
    Every row in it that belongs to another app is swapped for the copy that is
    on disk right now — same keys, same values, unknown keys intact — and any
    foreign row that has appeared since (a row this app has never seen) is kept
    as well.  Rows this app owns are written exactly as given: they are the
    caller's to normalise, trim or drop.

    Matching is by ``(app, id)``, consuming disk rows in order, so repeated ids
    map one-to-one and nothing is ever duplicated.  A foreign row that is not on
    disk at all (a test seeding one, say) is written as given.
    """
    pool: dict[tuple, list] = {}
    on_disk: list = []
    for row in disk_rows:
        if is_foreign(row, app):
            pool.setdefault((row_app(row), str(row.get("id"))), []).append(row)
            on_disk.append(row)

    out: list = []
    taken: set[int] = set()
    for row in entries:
        if not is_foreign(row, app):
            out.append(row)                       # ours, or unowned: as given
            continue
        bucket = pool.get((row_app(row), str(row.get("id"))))
        if bucket:
            current = bucket.pop(0)
            taken.add(id(current))
            out.append(current)                   # verbatim from disk
        else:
            out.append(row)                       # not on disk: keep the caller's
    out.extend(row for row in on_disk if id(row) not in taken)
    return out
