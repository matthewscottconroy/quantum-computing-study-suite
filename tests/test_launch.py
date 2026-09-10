"""Tests for launch.py (the suite launcher).

Standalone: run with ``.venv/bin/python -m pytest tests/test_launch.py`` from
any working directory.  The repo root is put on sys.path here, so no
conftest.py or pytest.ini is required.  GUI tests run offscreen and are
skipped when PyQt6 is not importable.

Isolation: an autouse fixture points QUANTUM_STUDY_DATA_DIR and
launch.API_KEY_FILE at a per-test temp dir and unsets ANTHROPIC_API_KEY, so
every test (and every subprocess it starts, which inherits the environment)
sees an empty data directory and no key.  App launches use a stubbed Popen or
a stub main.py under a temp copy of the launcher; coach.py honours
QUANTUM_STUDY_DATA_DIR; dashboard.py does not, so its end-to-end run gets
HOME/USERPROFILE redirected at the temp dir.  Nothing here reads or writes the
real ~/.local/share/quantum-study/ or ~/.config/quantum-study/.
"""
from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import launch  # noqa: E402

CANONICAL = {
    "dojo": "qiskit-dojo",
    "exam": "exam-sim",
    "flash": "flashcard-drill",
    "quiz": "quantum-quiz",
    "math": "math-quiz",
    "circuit": "circuit-trainer",
    "qec": "qec-trainer",
    "vqa": "vqa-trainer",
    "paper": "paper-drill",
    "problem": "problem-trainer",
}

LEARNING_PATH = [
    "flashcard-drill", "math-quiz", "quantum-quiz", "circuit-trainer",
    "qec-trainer", "vqa-trainer", "paper-drill", "qiskit-dojo",
    "problem-trainer", "exam-sim",
]

# Pinned classification (see App.api_key in launch.py).  "required": the core
# loop generates/grades through Claude; "optional": the core loop is offline
# and a key only adds free-form grading / Claude review; "none": no API use.
EXPECTED_API_KEY = {
    "flashcard-drill": "none",
    "exam-sim": "none",
    "qiskit-dojo": "optional",
    "qec-trainer": "optional",
    "vqa-trainer": "optional",
    "circuit-trainer": "optional",
    "problem-trainer": "required",
    "quantum-quiz": "required",
    "math-quiz": "required",
    "paper-drill": "required",
}


class FakePopen:
    """Records the launch call instead of starting a process."""
    calls: list[tuple[list[str], dict]] = []
    pid = 4242

    def __init__(self, argv, **kwargs):
        FakePopen.calls.append((list(argv), dict(kwargs)))


@pytest.fixture
def fake_popen(monkeypatch):
    FakePopen.calls = []
    monkeypatch.setattr(launch.subprocess, "Popen", FakePopen)
    return FakePopen


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch) -> Path:
    """Empty data dir + no API key for every test and its subprocesses."""
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(launch, "API_KEY_FILE", tmp_path / "api_key.txt")
    return data


def _sandbox_env(tmp_path: Path) -> dict:
    """Environment for subprocesses: HOME redirected so Path.home() is sandboxed too."""
    env = dict(os.environ)
    env["HOME"] = env["USERPROFILE"] = str(tmp_path)
    return env


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_registry_matches_directories():
    # Both directions: every registry entry has a main.py, and every <dir>/main.py
    # in the repo is in the registry (a new or renamed app cannot be silently omitted).
    on_disk = {p.parent.name for p in ROOT.glob("*/main.py")}
    assert {a.dir for a in launch.APPS} == on_disk
    assert len(launch.APPS) == 10


def test_registry_is_in_learning_path_order_with_unique_keys():
    assert [a.dir for a in launch.APPS] == LEARNING_PATH
    for field in ("dir", "name", "alias"):
        values = [getattr(a, field) for a in launch.APPS]
        assert len(set(values)) == len(values), f"duplicate {field}"
    assert {a.alias for a in launch.APPS} == set(CANONICAL)
    for app in launch.APPS:
        assert app.api_key in launch.API_KEY_LEVELS
        assert app.description and "\n" not in app.description


def test_api_key_classification_is_pinned():
    assert {a.dir: a.api_key for a in launch.APPS} == EXPECTED_API_KEY
    assert set(EXPECTED_API_KEY.values()) == set(launch.API_KEY_LEVELS)


def _readme_app_table() -> dict[str, tuple[str, str]]:
    """{app dir: (Offline cell, Needs cell)} from the README 'ten apps' table."""
    rows = {}
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ["):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue                       # other link tables (content packs) have 2 cells
        name = cells[0][1:cells[0].index("]")]
        rows[name] = (cells[2], cells[3])
    return rows


def _level_from_readme(offline: str, needs: str) -> str:
    o, n = offline.lower(), needs.lower()
    if "key" not in n:
        return "optional" if "optional" in o else "none"
    if "fully" in o or re.search(r"\bmc\b", o) or "everything except" in o:
        return "optional"
    return "required"


def test_api_key_classification_matches_readme_table():
    rows = _readme_app_table()
    assert set(rows) == set(EXPECTED_API_KEY), "README app table rows != registry"
    derived = {d: _level_from_readme(*cells) for d, cells in rows.items()}
    assert derived == {a.dir: a.api_key for a in launch.APPS}


def test_tool_paths_exist():
    assert launch.COACH_PY.is_file()
    assert launch.DASHBOARD_PY.is_file()
    assert launch.DOCS_README.is_file()


def test_launcher_is_executable():
    # launch.py carries a shebang, so ./launch.py must work.
    if os.name == "nt":
        pytest.skip("no exec bit on Windows")
    assert os.access(launch.__file__, os.X_OK), "launch.py has a shebang but no exec bit"


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected", sorted(CANONICAL.items()))
def test_resolve_canonical_aliases(query, expected):
    assert launch.resolve_app(query).dir == expected


@pytest.mark.parametrize("query,expected", [
    ("fl", "flashcard-drill"),
    ("pr", "problem-trainer"),
    ("quantum", "quantum-quiz"),
    ("qi", "qiskit-dojo"),
    ("d", "qiskit-dojo"),
    ("e", "exam-sim"),
    ("c", "circuit-trainer"),
    ("math-quiz", "math-quiz"),          # exact directory
    ("EXAM-SIM", "exam-sim"),            # case-insensitive
    ("Qiskit Dojo", "qiskit-dojo"),      # display name with a space
    ("qec_trainer", "qec-trainer"),      # underscore form
    ("  vqa  ", "vqa-trainer"),          # surrounding whitespace
    ("qiskit-dojo/", "qiskit-dojo"),     # shell tab-completion forms ...
    ("./qiskit-dojo", "qiskit-dojo"),
    ("qiskit-dojo/main.py", "qiskit-dojo"),
    (str(ROOT / "exam-sim"), "exam-sim"),
    ("./qiskit-dojo/", "qiskit-dojo"),
])
def test_resolve_prefixes_and_forms(query, expected):
    assert launch.resolve_app(query).dir == expected


@pytest.mark.parametrize("query,expected_dirs", [
    ("q", {"quantum-quiz", "qec-trainer", "qiskit-dojo"}),
    ("p", {"paper-drill", "problem-trainer"}),
])
def test_resolve_ambiguous(query, expected_dirs):
    with pytest.raises(launch.AmbiguousAppError) as info:
        launch.resolve_app(query)
    assert {a.dir for a in info.value.candidates} == expected_dirs
    assert info.value.query == query
    assert isinstance(info.value, launch.LaunchError)
    # Candidates are shown as "alias (dir)" so a match through the directory
    # name (q -> qiskit-dojo) does not read as nonsense.
    for d in expected_dirs:
        assert f"({d})" in str(info.value)


@pytest.mark.parametrize("query", ["", "   ", "nope", "trainer", "quiz-", "qq", "./", "/", "main.py"])
def test_resolve_unknown(query):
    with pytest.raises(launch.UnknownAppError):
        launch.resolve_app(query)


def test_exact_match_beats_prefix(monkeypatch):
    # No real registry entry exercises this branch (every alias is also a unique
    # prefix), so use a synthetic registry where "ab" is both an exact alias and
    # a prefix of another app.
    fake = [
        launch.App("ab-x", "AB X", "", "none", "ab"),
        launch.App("abc-y", "ABC Y", "", "none", "abc"),
    ]
    monkeypatch.setattr(launch, "APPS", fake)
    assert launch.resolve_app("ab").dir == "ab-x"
    assert launch.resolve_app("abc").dir == "abc-y"
    with pytest.raises(launch.AmbiguousAppError):
        launch.resolve_app("a")


# ---------------------------------------------------------------------------
# CLI (in-process)
# ---------------------------------------------------------------------------

def _table_rows(out: str) -> dict[str, str]:
    return {a.dir: next(l for l in out.splitlines() if f"  {a.dir}  " in l) for a in launch.APPS}


def test_list_prints_every_app(capsys):
    assert launch.main(["--list"]) == 0
    out = capsys.readouterr().out
    for app in launch.APPS:
        assert app.name in out
        assert app.dir in out
        assert app.alias in out
        assert app.description in out
    assert "python launch.py" in out
    rows = _table_rows(out)
    cell = {"required": "yes", "optional": "optional", "none": "no"}
    for app in launch.APPS:
        assert f"  {cell[app.api_key]}  " in rows[app.dir], rows[app.dir]


def test_status_prints_environment_line(capsys):
    assert launch.main(["--status"]) == 0
    out = capsys.readouterr().out
    assert "Python" in out and "Qiskit" in out
    assert "API key: not configured" in out and "Study history: none yet" in out


def test_cli_unknown_app_exits_2(capsys, fake_popen):
    assert launch.main(["nope"]) == 2
    err = capsys.readouterr().err
    assert "unknown app 'nope'" in err
    assert "--list" in err
    assert fake_popen.calls == []


def test_cli_ambiguous_app_exits_2_and_lists_candidates(capsys, fake_popen):
    assert launch.main(["p"]) == 2
    err = capsys.readouterr().err
    assert "ambiguous" in err
    assert "paper (paper-drill)" in err and "problem (problem-trainer)" in err
    assert fake_popen.calls == []


def test_cli_launch_uses_detached_popen(capsys, fake_popen, isolated_env):
    assert launch.main(["dojo"]) == 0
    assert len(fake_popen.calls) == 1
    argv, kwargs = fake_popen.calls[0]
    assert argv == [sys.executable, "main.py"]
    assert kwargs["cwd"] == str(ROOT / "qiskit-dojo")
    assert kwargs["stdin"] == subprocess.DEVNULL
    # stdout/stderr go to the per-app log, never to the launcher's own pipes.
    log = isolated_env / "logs" / "qiskit-dojo.log"
    assert kwargs["stdout"].name == str(log)
    assert kwargs["stdout"].closed          # parent released its copy after Popen
    assert kwargs["stderr"] == subprocess.STDOUT
    assert log.is_file() and "launch:" in log.read_text(encoding="utf-8")
    if os.name == "nt":
        assert kwargs["creationflags"]
    else:
        assert kwargs["start_new_session"] is True
    out = capsys.readouterr().out
    assert "Launched Qiskit Dojo" in out and "4242" in out
    assert "qiskit-dojo.log" in out


def test_launch_falls_back_to_devnull_when_log_unavailable(fake_popen, monkeypatch):
    monkeypatch.setattr(launch, "_open_app_log", lambda app, argv, cwd: None)
    launch.launch_app(launch.resolve_app("flash"), popen=fake_popen)
    _, kwargs = fake_popen.calls[0]
    assert kwargs["stdout"] == subprocess.DEVNULL
    assert kwargs["stderr"] == subprocess.DEVNULL
    assert kwargs["stdin"] == subprocess.DEVNULL


def test_detached_popen_kwargs_never_inherit_stdio():
    kw = launch.detached_popen_kwargs()
    assert kw["stdin"] == kw["stdout"] == kw["stderr"] == subprocess.DEVNULL
    with open(os.devnull, "wb") as f:
        kw = launch.detached_popen_kwargs(f)
        assert kw["stdout"] is f and kw["stderr"] == subprocess.STDOUT


def test_app_log_is_truncated_once_oversized(isolated_env, monkeypatch):
    app = launch.resolve_app("exam")
    log = launch.app_log_path(app)
    log.parent.mkdir(parents=True)
    log.write_bytes(b"x" * 100)
    monkeypatch.setattr(launch, "_LOG_MAX_BYTES", 50)
    f = launch._open_app_log(app, ["python", "main.py"], ROOT / app.dir)
    f.close()
    text = log.read_text(encoding="utf-8")
    assert not text.startswith("x") and text.startswith("===")   # truncated, header written
    monkeypatch.setattr(launch, "_LOG_MAX_BYTES", 10_000)
    launch._open_app_log(app, ["python", "main.py"], ROOT / app.dir).close()
    assert log.read_text(encoding="utf-8").count("=== ") == 2           # appended


@pytest.mark.parametrize("alias,expect", [
    ("math", "uses the Claude API"),                 # required
    ("vqa", "free-form grading / Claude review"),    # optional
])
def test_cli_launch_notes_missing_key(capsys, fake_popen, alias, expect):
    assert launch.main([alias]) == 0                 # autouse fixture: no key anywhere
    captured = capsys.readouterr()
    assert "Launched" in captured.out
    assert "no key is configured" in captured.err and expect in captured.err


def test_cli_launch_offline_app_has_no_key_note(capsys, fake_popen):
    assert launch.main(["flash"]) == 0
    assert capsys.readouterr().err == ""


def test_cli_launch_no_note_when_key_present(capsys, fake_popen, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    assert launch.main(["math"]) == 0
    assert capsys.readouterr().err == ""


def test_missing_key_note_levels():
    by = {a.api_key: a for a in launch.APPS}
    assert launch.missing_key_note(by["none"]) is None
    assert "Claude API" in launch.missing_key_note(by["required"])
    assert "offline" in launch.missing_key_note(by["optional"])


def test_launch_app_direct_injection(fake_popen):
    app = launch.resolve_app("exam")
    proc = launch.launch_app(app, popen=fake_popen)
    assert isinstance(proc, fake_popen)
    argv, kwargs = fake_popen.calls[0]
    assert argv[1] == "main.py" and kwargs["cwd"].endswith("exam-sim")


def test_launch_app_missing_main_raises(fake_popen, monkeypatch, tmp_path):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    with pytest.raises(launch.LaunchError):
        launch.launch_app(launch.resolve_app("exam"), popen=fake_popen)
    assert fake_popen.calls == []


def test_cli_paths_work_without_pyqt6_in_process(capsys, monkeypatch):
    """Call-time guard: main() must not import Qt for --list / the GUI fallback.

    The import-time guard (launch.py itself must import without PyQt6) is the
    fresh-interpreter test below; this one cannot see it because `launch` is
    already imported.
    """
    for mod in list(sys.modules):
        if mod == "PyQt6" or mod.startswith("PyQt6."):
            monkeypatch.delitem(sys.modules, mod)
    monkeypatch.setitem(sys.modules, "PyQt6", None)          # makes `import PyQt6...` raise
    monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", None)
    assert launch.main(["--list"]) == 0
    assert "Flashcard Drill" in capsys.readouterr().out
    assert launch.main([]) == 1
    assert "PyQt6 is required" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# CLI (fresh interpreter)
# ---------------------------------------------------------------------------

# Blocks PyQt6 *before* `import launch`, so a module-level Qt import in
# launch.py (which would kill every CLI path) fails this test.
_BLOCK_PYQT6 = textwrap.dedent("""
    import importlib.abc, sys
    class Block(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name == "PyQt6" or name.startswith("PyQt6."):
                raise ImportError(name + " blocked for this test")
    sys.meta_path.insert(0, Block())
    sys.path.insert(0, sys.argv[1])
    exec(sys.argv[2])
""")


def _run_blocked(tmp_path: Path, body: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", _BLOCK_PYQT6, str(ROOT), body, *args],
        capture_output=True, text=True, timeout=120,
        cwd=str(tmp_path), env=_sandbox_env(tmp_path),
    )


def test_pyqt6_block_harness_really_blocks(tmp_path):
    res = _run_blocked(tmp_path, "import PyQt6.QtWidgets")
    assert res.returncode != 0 and "blocked for this test" in res.stderr


@pytest.mark.parametrize("args,rc,stream,needle", [
    (["--list"], 0, "stdout", "Flashcard Drill"),
    (["--status"], 0, "stdout", "API key: not configured"),
    (["nope"], 2, "stderr", "unknown app 'nope'"),
    (["p"], 2, "stderr", "ambiguous"),
    ([], 1, "stderr", "PyQt6 is required"),
])
def test_cli_works_in_fresh_interpreter_without_pyqt6(tmp_path, args, rc, stream, needle):
    res = _run_blocked(tmp_path, "import launch; sys.exit(launch.main(sys.argv[3:]))", *args)
    assert res.returncode == rc, (res.stdout, res.stderr)
    assert needle in getattr(res, stream), (res.stdout, res.stderr)


def _sandbox_launcher(tmp_path: Path, stub_body: str) -> Path:
    """Copy launch.py into tmp_path next to a stub flashcard-drill/main.py."""
    script = tmp_path / "launch.py"
    shutil.copy(launch.__file__, script)
    app_dir = tmp_path / "flashcard-drill"
    app_dir.mkdir()
    (app_dir / "main.py").write_text(stub_body, encoding="utf-8")
    return script


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def test_cli_launch_returns_immediately_when_output_is_captured(tmp_path, isolated_env):
    """`launch.py flash | cat` (or $(launch.py flash)) must not wait for the app."""
    script = _sandbox_launcher(tmp_path, textwrap.dedent("""
        import sys, time
        print("stub app up", flush=True)
        print("stub warning", file=sys.stderr, flush=True)
        time.sleep(60)
    """))
    t0 = time.monotonic()
    res = subprocess.run([sys.executable, str(script), "flash"], capture_output=True,
                         text=True, timeout=30, cwd=str(tmp_path), env=_sandbox_env(tmp_path))
    elapsed = time.monotonic() - t0
    assert res.returncode == 0, res.stderr
    assert elapsed < 15, f"launcher blocked on the app's stdio for {elapsed:.1f}s"
    m = re.search(r"pid (\d+)", res.stdout)
    assert m, res.stdout
    pid = int(m.group(1))
    try:
        if os.name != "nt":
            assert _pid_alive(pid), "app should outlive the launcher"
        # The app's output went to its log, not to our pipe.
        log = isolated_env / "logs" / "flashcard-drill.log"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            text = log.read_text(encoding="utf-8") if log.is_file() else ""
            if "stub warning" in text:
                break
            time.sleep(0.05)
        assert "stub app up" in text and "stub warning" in text, text
        assert text.startswith("=== ")
        assert "stub app up" not in res.stdout and "stub warning" not in res.stderr
        assert "logs/flashcard-drill.log" in res.stdout   # printed with HOME shortened to ~
    finally:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def test_api_key_configured(tmp_path):
    key_file = tmp_path / "api_key.txt"
    assert launch.api_key_configured(env={}, key_file=key_file) is False
    assert launch.api_key_configured(env={"ANTHROPIC_API_KEY": "sk-ant-x"}, key_file=key_file) is True
    assert launch.api_key_configured(env={"ANTHROPIC_API_KEY": "   "}, key_file=key_file) is False
    key_file.write_text("\n")
    assert launch.api_key_configured(env={}, key_file=key_file) is False
    key_file.write_text("sk-ant-file\n")
    assert launch.api_key_configured(env={}, key_file=key_file) is True


def test_api_key_file_default_resolved_at_call_time(monkeypatch, tmp_path):
    key_file = tmp_path / "elsewhere" / "k.txt"
    monkeypatch.setattr(launch, "API_KEY_FILE", key_file)
    assert launch.api_key_configured(env={}) is False
    assert launch.status_info()["api_key"] is False
    key_file.parent.mkdir()
    key_file.write_text("sk-ant-late\n")
    assert launch.api_key_configured(env={}) is True
    assert launch.status_info()["api_key"] is True


def test_history_files(tmp_path, monkeypatch):
    assert launch.history_files(tmp_path / "missing") == []
    (tmp_path / "quiz_history.json").write_text("[]")
    (tmp_path / "dojo_history.json").write_text("[]")
    (tmp_path / "flagged_cards.json").write_text("[]")
    (tmp_path / "coach_state.json").write_text("{}")
    names = [p.name for p in launch.history_files(tmp_path)]
    assert names == ["dojo_history.json", "quiz_history.json"]
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(tmp_path))
    assert launch.data_dir() == tmp_path
    assert launch.status_info()["history"] == 2


def test_format_status():
    line = launch.format_status({"python": "3.14.7", "venv": ".venv", "qiskit": "2.5.2",
                                 "api_key": True, "history": 1})
    assert line == "Python 3.14.7 (.venv) | Qiskit 2.5.2 | API key: configured | Study history: 1 file"
    line = launch.format_status({"python": "3.12.0", "venv": None, "qiskit": None,
                                 "api_key": False, "history": 0}, sep=" / ")
    assert line == ("Python 3.12.0 / Qiskit not installed / API key: not configured"
                    " / Study history: none yet")


def test_qiskit_version_uses_metadata_not_import(monkeypatch):
    for mod in list(sys.modules):
        if mod == "qiskit" or mod.startswith("qiskit."):
            monkeypatch.delitem(sys.modules, mod)
    version = launch.qiskit_version()
    assert version is None or (isinstance(version, str) and version[0].isdigit())
    assert "qiskit" not in sys.modules   # metadata lookup, no (slow) import


def test_key_badge_mapping():
    by = {a.api_key: a for a in launch.APPS}
    html, _ = launch.key_badge(by["none"], key_ok=False)
    assert "offline" in html and launch.SUCCESS in html
    html, _ = launch.key_badge(by["optional"], key_ok=False)
    assert "key optional" in html and launch.WARNING not in html
    html, tip = launch.key_badge(by["required"], key_ok=False)
    assert "API key" in html and launch.WARNING in html and "no key" in tip
    html, tip = launch.key_badge(by["required"], key_ok=True)
    assert launch.WARNING not in html and launch.TEXT_MUTED in html and "no key" not in tip


# ---------------------------------------------------------------------------
# GUI (offscreen)
# ---------------------------------------------------------------------------

QtWidgets = pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not installed")
from PyQt6.QtCore import QCoreApplication, QEvent, QProcess  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    app.setStyleSheet(launch.QSS)
    return app


@pytest.fixture
def window(qapp):
    win = launch.build_window()
    win.show()
    yield win
    win.close()
    qapp.processEvents()


def _wait_for_tool(win, qapp, timeout=30.0):
    deadline = time.monotonic() + timeout
    while win.tool_running() and time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.01)
    assert not win.tool_running(), "tool subprocess did not finish in time"
    qapp.processEvents()


def _badges(win) -> dict[str, str]:
    return {app.dir: label.text() for label, app in win._key_badges}


def test_window_constructs_offscreen(window):
    assert window.windowTitle() == "Quantum Study Suite"
    buttons = window.findChildren(QtWidgets.QPushButton)
    launch_buttons = [b for b in buttons if b.property("app_dir")]
    assert [b.property("app_dir") for b in launch_buttons] == LEARNING_PATH
    assert set(window.launch_buttons) == set(LEARNING_PATH)
    labels = {b.text() for b in buttons}
    assert {"Today's plan", "Review queue", "Dashboard", "Open docs"} <= labels
    assert window.output.isReadOnly()
    # The pane must resolve to a fixed-pitch font despite the global QSS font-family.
    from PyQt6.QtGui import QFontInfo
    font = window.output.font()
    resolved = QFontInfo(font)
    assert resolved.fixedPitch() or any(
        m in font.family() for m in ("Mono", "Menlo", "Consolas", "Courier")
    ), f"output pane font is {font.family()!r} (resolved {resolved.family()!r})"
    status = window.status_label.text()
    assert "Python" in status and "Qiskit" in status
    assert "API key:" in status and "Study history: none yet" in status
    assert "not configured" in status


def test_window_badges_follow_key_state(window, qapp):
    html = _badges(window)
    assert set(html) == set(LEARNING_PATH)
    for app in launch.APPS:                      # no key: required apps are amber
        if app.api_key == "required":
            assert launch.WARNING in html[app.dir] and "API key" in html[app.dir]
        elif app.api_key == "optional":
            assert "key optional" in html[app.dir] and launch.WARNING not in html[app.dir]
        else:
            assert "offline" in html[app.dir]
    # Key configured after construction -> refresh_status() re-renders every badge.
    launch.API_KEY_FILE.write_text("sk-ant-test\n", encoding="utf-8")
    window.refresh_status()
    assert all(launch.WARNING not in h for h in _badges(window).values())
    assert "not configured" not in window.status_label.text()
    assert "configured" in window.status_label.text()
    # Regaining focus also refreshes (key removed while the launcher was open).
    launch.API_KEY_FILE.unlink()
    QCoreApplication.sendEvent(window, QEvent(QEvent.Type.WindowActivate))
    html = _badges(window)
    assert all(launch.WARNING in html[a.dir] for a in launch.APPS if a.api_key == "required")
    assert "not configured" in window.status_label.text()


def test_window_launch_buttons_start_detached_apps(window, fake_popen, isolated_env):
    for i, app in enumerate(launch.APPS):
        window.launch_buttons[app.dir].click()
        assert len(fake_popen.calls) == i + 1
        argv, kwargs = fake_popen.calls[-1]
        assert argv == [sys.executable, "main.py"]
        assert kwargs["cwd"] == str(ROOT / app.dir)
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["stdout"].name == str(isolated_env / "logs" / f"{app.dir}.log")
        assert kwargs["stderr"] == subprocess.STDOUT
        if os.name != "nt":
            assert kwargs["start_new_session"] is True
        msg = window.statusBar().currentMessage()
        assert f"Launched {app.name}" in msg
        assert ("no key" in msg) == (app.api_key != "none")
    text = window.output.toPlainText()
    assert all(f"[launch] {a.name} started" in text for a in launch.APPS)


def test_window_launch_failure_is_reported_not_raised(window, fake_popen, monkeypatch, tmp_path):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    window.launch_buttons["exam-sim"].click()
    assert fake_popen.calls == []
    assert "Could not start Exam Simulator" in window.statusBar().currentMessage()


def test_window_tool_pane_streams_output(window, qapp):
    started = window.run_tool([sys.executable, "-c", "print('hello from tool')"], "test")
    assert started is True
    assert window.run_tool([sys.executable, "-c", "pass"], "second") is False  # busy
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 0
    text = window.output.toPlainText()
    assert text.startswith("$ ")
    assert "hello from tool" in text
    assert all(b.isEnabled() for b in window._tool_buttons)
    assert window.statusBar().currentMessage() == "test finished"


def test_window_tool_nonzero_exit_is_reported(window, qapp):
    window.run_tool([sys.executable, "-c", "import sys; sys.exit(3)"], "exit3")
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 3
    assert window.statusBar().currentMessage() == "exit3 finished (exit 3)"


def test_window_tool_start_failure_is_closed_out(window, qapp, tmp_path):
    assert window.run_tool([str(tmp_path / "no-such-binary")], "bogus") is True
    deadline = time.monotonic() + 15
    while window.last_tool_exit is None and time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.01)
    assert window.last_tool_exit == -1
    assert not window.tool_running()
    msg = window.statusBar().currentMessage()
    assert not msg.startswith("Running"), msg
    assert "bogus failed to start" in msg
    assert all(b.isEnabled() for b in window._tool_buttons)
    assert "process error" in window.output.toPlainText()
    # ... and the pane accepts a new run.
    assert window.run_tool([sys.executable, "-c", "print('again')"], "again") is True
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 0 and "again" in window.output.toPlainText()


def test_window_finished_tool_processes_are_released(window, qapp):
    for i in range(3):
        assert window.run_tool([sys.executable, "-c", "pass"], f"run{i}") is True
        _wait_for_tool(window, qapp)
        assert window.last_tool_exit == 0
    assert window._proc is None
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert window.findChildren(QProcess) == []


def test_window_todays_plan_runs_coach_against_temp_dir(window, qapp, isolated_env):
    window.run_todays_plan()
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 0
    text = window.output.toPlainText()
    assert "coach.py" in text.splitlines()[0]
    assert len(text.splitlines()) > 3
    assert (isolated_env / "coach_state.json").is_file()   # coach wrote to the temp dir, not ~


def test_window_review_queue_runs_coach_review(window, qapp):
    window.run_review_queue()
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 0
    assert "--review" in window.output.toPlainText().splitlines()[0]


def test_window_dashboard_argv(window, monkeypatch):
    seen = []
    monkeypatch.setattr(window, "run_tool", lambda argv, label, **kw: seen.append((argv, label)) or True)
    window.run_dashboard()
    assert seen == [([sys.executable, str(launch.DASHBOARD_PY)], "Dashboard")]


def test_window_dashboard_runs_end_to_end_sandboxed(window, qapp, monkeypatch, tmp_path):
    # dashboard.py ignores QUANTUM_STUDY_DATA_DIR and reads Path.home()/.local/share/
    # quantum-study, so redirect HOME (Path.home() honours it) to keep the run
    # independent of whatever JSON sits in the developer's real data dir.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    window.run_dashboard()
    _wait_for_tool(window, qapp)
    assert window.last_tool_exit == 0, window.output.toPlainText()
    assert "dashboard.py" in window.output.toPlainText().splitlines()[0]
