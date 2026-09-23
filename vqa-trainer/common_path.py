"""THE IMPORT SHIM.  Copy this file verbatim to ``<app>/common_path.py``.

Why an app needs it
===================
The ten apps are not packages.  Each is a self-contained tree run as
``cd <app> && python main.py``, and several define the *same* top-level module
names (``config``, ``core``, ``ui``, ``persistence``), so they can never share
one ``sys.path``.  That is why ``tools/run_tests.sh`` runs each app's suite in
its own pytest process, and why the repository root — where ``common/`` lives —
is **not** importable from inside an app by default.

This file fixes that, and nothing else.  Importing it appends the repository
root to ``sys.path``; ``import common`` then works.

How to use it
=============
1. Copy this file to ``<app>/common_path.py``.  Do not edit it: it locates the
   repository from **its own** ``__file__``, so it works at any depth and
   needs no per-app constant.
2. In **every** module of that app that imports from ``common``, import it
   first::

       import common_path  # noqa: F401  (puts the repo root on sys.path)

       from common import journal
       from common.ui import theme

   Every module, not just ``main.py``: ``persistence.py`` is imported directly
   by ``tests/test_journal_concurrency.py`` with no ``main`` and no
   ``conftest`` in the way, and a screen module is imported directly by that
   app's UI tests.  A module that assumes someone else ran the shim first
   works until the day something imports it first.

Why this works in all three cases
=================================
``cd <app> && python main.py``
    ``sys.path[0]`` is the app directory, so ``import common_path`` resolves;
    the shim then appends ``<repo>`` and ``import common`` resolves.

``cd <app> && python -m pytest``
    pytest puts the rootdir (the app directory, which holds its ``pytest.ini``)
    on ``sys.path`` for the same reason ``import persistence`` already works
    there.  Same two steps follow.

An installed wheel
    ``common`` is an installed package, so ``import common`` would work even
    without the shim.  The shim finds no repository root (there is none),
    appends nothing, and is a no-op.  It never fails on a machine with no
    checkout.

Why **append**, not ``insert(0, …)``
====================================
The repository root holds ``coach.py``, ``dashboard.py``, ``launch.py``,
``tools/`` and ``tests/``.  Putting it *before* the app directory would let a
root module shadow an app module of the same name — ``import tests`` inside an
app suite is the obvious landmine.  Appending guarantees the app's own modules
always win, which is the existing behaviour, unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path | None:
    """The nearest ancestor directory that contains this suite's ``common/``.

    Two files are checked, not one, so a directory called ``common`` that
    belongs to some other project higher up the tree is not mistaken for ours.
    """
    for parent in Path(__file__).resolve().parents:
        pkg = parent / "common"
        if (pkg / "__init__.py").is_file() and (pkg / "journal.py").is_file():
            return parent
    return None


def install() -> Path | None:
    """Append the repository root to ``sys.path`` if it is not already there.

    Returns the root, or None when there is no checkout (an installed wheel,
    or an app copied out of the repository).  Safe to call any number of times.
    """
    root = repo_root()
    if root is None:
        return None
    text = str(root)
    if text not in sys.path:
        sys.path.append(text)      # append: the app's own modules always win
    return root


ROOT = install()
