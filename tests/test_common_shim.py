"""The import shim — ``common/app_shim.py`` copied to ``<app>/common_path.py``.

The apps are not packages: each is run as ``cd <app> && python main.py``, and
several define the same top-level module names, so the repository root is not
importable from inside one.  The shim is how ``import common`` works anyway,
and the migration agents copy it verbatim into all ten trees — so it is tested
the way they will use it: by building a **simulated app directory** and running
a real interpreter and a real pytest inside it.

Nothing here imports any app.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHIM = ROOT / "common" / "app_shim.py"
PY = sys.executable


@pytest.fixture
def fake_app(tmp_path):
    """A directory shaped like one of the ten apps, one level under a repo root.

    The stand-in root symlinks the **real** ``common/``, so the subprocesses
    below import the real package through the real shim, at the real depth —
    without creating anything inside the repository.  (A probe directory left
    behind by a hard kill would add an eleventh suite to
    ``tools/run_tests.sh`` and fail CI's "Check APPS" step.)
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "common").symlink_to(ROOT / "common", target_is_directory=True)
    # Root-level names an app must never have shadowed by the repo root.
    (repo / "tools").mkdir()
    (repo / "tools" / "__init__.py").write_text("WHO = 'repo tools'\n",
                                                encoding="utf-8")

    app = repo / "sim-trainer"
    app.mkdir()
    (app / "common_path.py").write_text(SHIM.read_text(encoding="utf-8"),
                                        encoding="utf-8")
    # A top-level module name several real apps share.
    (app / "config.py").write_text("WHO = 'the app'\n", encoding="utf-8")
    (app / "tests").mkdir()
    (app / "pytest.ini").write_text("[pytest]\naddopts = -q\n", encoding="utf-8")
    return app


def run(cmd, cwd, **kw):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               QT_QPA_PLATFORM="offscreen")
    env.pop("PYTHONPATH", None)             # the shim must not need it
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True,
                          text=True, timeout=180, **kw)


# ---------------------------------------------------------------------------
# The shim file itself
# ---------------------------------------------------------------------------

def test_the_shim_exists_and_is_small():
    """Mostly documentation: under 35 lines of code, so a reviewer can check
    ten copies of it at a glance."""
    assert SHIM.is_file()
    import ast

    tree = ast.parse(SHIM.read_text(encoding="utf-8"))
    body = [n for n in tree.body
            if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    lines = {ln for node in body
             for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1)}
    assert len(lines) < 35, f"the shim has grown to {len(lines)} lines of code"
    assert not any(isinstance(n, ast.Import) and n.names[0].name
                   not in ("sys",) for n in body if isinstance(n, ast.Import))


def test_the_readme_documents_the_shim_verbatim():
    """The migration agents follow README.md; it must not drift from the file."""
    readme = (ROOT / "common" / "README.md").read_text(encoding="utf-8")
    for line in ("def repo_root() -> Path | None:",
                 "def install() -> Path | None:",
                 "sys.path.append(text)",
                 "ROOT = install()",
                 "import common_path  # noqa: F401"):
        assert line in readme, f"README.md is missing: {line}"
    assert "cp common/app_shim.py <app>/common_path.py" in readme


def test_the_shim_finds_this_repository():
    from common import app_shim
    assert app_shim.repo_root() == ROOT


def test_install_is_idempotent():
    from common import app_shim
    before = list(sys.path)
    app_shim.install()
    app_shim.install()
    assert sys.path.count(str(ROOT)) == before.count(str(ROOT)) or \
        sys.path.count(str(ROOT)) == 1


# ---------------------------------------------------------------------------
# Case 1: cd <app> && python main.py
# ---------------------------------------------------------------------------

def test_running_a_script_from_the_app_directory(fake_app):
    (fake_app / "main.py").write_text(textwrap.dedent("""
        import json
        import sys

        import common_path  # noqa: F401

        import config
        from common import datadir, journal, flags, errata, schema
        from common.ui import theme

        print(json.dumps({
            "config": config.WHO,
            "config_file": config.__file__,
            "common_file": journal.__file__,
            "causes": list(journal.MISTAKE_CAUSES),
            "accent": theme.ACCENT,
            "data_dir": str(datadir.data_dir()),
            "url": errata.issue_url("qec-trainer", "q1", "text", "why"),
            "kinds": list(schema.kinds()),
            "flag_label": flags.make_label("  a  b  "),
            "root_on_path": sys.path[-1],
        }))
    """), encoding="utf-8")

    proc = run([PY, "main.py"], cwd=fake_app)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["config"] == "the app", "the repo root shadowed the app's config"
    assert out["config_file"].startswith(str(fake_app))
    assert Path(out["common_file"]).resolve() == \
        (ROOT / "common" / "journal.py").resolve()
    assert out["causes"][0] == "misread"
    assert out["accent"] == "#58a6ff"
    assert out["url"].startswith("https://github.com/")
    assert "mistakes" in out["kinds"]
    assert out["flag_label"] == "a b"
    assert out["root_on_path"] == str(fake_app.parent), (
        "the root must be appended, not prepended")


def test_a_module_imported_from_a_subdirectory_also_works(fake_app):
    """A screen at ``ui/screens/x.py`` is three levels down; the shim computes
    from its own location, so depth is irrelevant."""
    (fake_app / "ui" / "screens").mkdir(parents=True)
    (fake_app / "ui" / "__init__.py").write_text("", encoding="utf-8")
    (fake_app / "ui" / "screens" / "__init__.py").write_text("", encoding="utf-8")
    (fake_app / "ui" / "screens" / "ref.py").write_text(textwrap.dedent("""
        import common_path  # noqa: F401
        from common.ui import reference

        DOCS = reference.docs_root()
    """), encoding="utf-8")
    (fake_app / "main.py").write_text(textwrap.dedent("""
        import common_path  # noqa: F401
        from ui.screens.ref import DOCS
        print(DOCS)
    """), encoding="utf-8")

    proc = run([PY, "main.py"], cwd=fake_app)
    assert proc.returncode == 0, proc.stderr
    # The stand-in root has no docs/, so resolution walks on to the real one.
    assert proc.stdout.strip() == str(ROOT / "docs")


def test_the_repo_root_never_shadows_an_app_module(fake_app):
    """``tests`` and ``tools`` exist at the repo root; an app's own must win.

    This is why the shim **appends**: ``sys.path.insert(0, root)`` would make
    ``import tools`` inside an app resolve to the repository's.
    """
    (fake_app / "tests" / "__init__.py").write_text("WHO = 'app tests'\n",
                                                    encoding="utf-8")
    (fake_app / "tools").mkdir()
    (fake_app / "tools" / "__init__.py").write_text("WHO = 'app tools'\n",
                                                    encoding="utf-8")
    (fake_app / "main.py").write_text(textwrap.dedent("""
        import common_path  # noqa: F401
        import tests
        import tools
        from common import journal  # noqa: F401
        print(tests.WHO, "|", tools.WHO)
    """), encoding="utf-8")
    proc = run([PY, "main.py"], cwd=fake_app)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "app tests | app tools"


# ---------------------------------------------------------------------------
# Case 2: cd <app> && python -m pytest
# ---------------------------------------------------------------------------

def test_running_pytest_from_the_app_directory(fake_app):
    (fake_app / "persistence.py").write_text(textwrap.dedent("""
        import common_path  # noqa: F401
        from common import datadir, journal

        APP = "probe-app"

        def log(item_id, question, wrong, right):
            return journal.log_mistake(journal.make_mistake_entry(
                item_id, APP, "Gates", question, wrong, right))

        def path():
            return datadir.mistakes_file()
    """), encoding="utf-8")
    (fake_app / "tests" / "test_probe.py").write_text(textwrap.dedent("""
        import json

        import persistence
        from common import journal


        def test_the_shim_works_under_pytest(tmp_path, monkeypatch):
            monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(tmp_path))
            assert persistence.path() == tmp_path / "mistakes.json"
            persistence.log("i1", "q?", "wrong", "right")
            rows = journal.load_mistakes("probe-app")
            assert [r["id"] for r in rows] == ["i1"]
            assert json.loads((tmp_path / "mistakes.json").read_text())
    """), encoding="utf-8")

    proc = run([PY, "-m", "pytest"], cwd=fake_app)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "1 passed" in proc.stdout


def test_a_store_imported_by_path_with_no_conftest(fake_app):
    """How ``tests/test_journal_concurrency.py`` loads each app's store: by
    file path, in a bare interpreter.  Nothing has run ``main`` or a conftest,
    so the store module's own shim import is what has to carry it."""
    (fake_app / "persistence.py").write_text(textwrap.dedent("""
        import common_path  # noqa: F401
        from common import journal

        CAUSES = journal.MISTAKE_CAUSES
    """), encoding="utf-8")
    probe = textwrap.dedent(f"""
        import importlib.util, sys
        app = {str(fake_app)!r}
        sys.path.insert(0, app)
        spec = importlib.util.spec_from_file_location(
            "store_probe", app + "/persistence.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(mod.CAUSES[0])
    """)
    proc = run([PY, "-c", probe], cwd=Path(os.sep))   # not the app, not the repo
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "misread"


# ---------------------------------------------------------------------------
# Case 3: an installed wheel (no checkout)
# ---------------------------------------------------------------------------

def test_outside_a_checkout_the_shim_is_a_no_op(tmp_path):
    """An app copied out of the repository, or a wheel install: the shim finds
    no root, appends nothing, and must not raise."""
    lonely = tmp_path / "lonely-app"
    lonely.mkdir()
    (lonely / "common_path.py").write_text(SHIM.read_text(encoding="utf-8"),
                                           encoding="utf-8")
    (lonely / "main.py").write_text(textwrap.dedent("""
        import sys
        before = list(sys.path)
        import common_path
        print(repr(common_path.ROOT), sys.path == before)
    """), encoding="utf-8")
    proc = run([PY, "main.py"], cwd=lonely)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "None True"


def test_the_shim_ignores_a_foreign_directory_called_common(tmp_path):
    """Two files are checked, not one, so somebody else's ``common`` package
    higher up the tree is not mistaken for ours."""
    decoy = tmp_path / "other-project"
    (decoy / "common").mkdir(parents=True)
    (decoy / "common" / "__init__.py").write_text("", encoding="utf-8")
    app = decoy / "app"
    app.mkdir()
    (app / "common_path.py").write_text(SHIM.read_text(encoding="utf-8"),
                                        encoding="utf-8")
    (app / "main.py").write_text(
        "import common_path\nprint(repr(common_path.ROOT))\n", encoding="utf-8")
    proc = run([PY, "main.py"], cwd=app)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "None"


def test_an_installed_common_is_importable_without_the_shim(tmp_path):
    """The wheel case proper: ``common`` on sys.path already, no checkout."""
    proc = run([PY, "-c", "from common import journal; print(journal.TEXT_MAX)"],
               cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "200"
