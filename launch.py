#!/usr/bin/env python3
"""Quantum Study Suite launcher.

GUI (default)          python launch.py
Launch one app         python launch.py <app>       name, directory, or unique prefix
                                                    (dojo, exam, flash, quiz, math,
                                                    circuit, qec, vqa, paper, problem)
List the apps          python launch.py --list
Environment status     python launch.py --status

Single file, stdlib + PyQt6.  PyQt6 is imported lazily so every CLI path
works even when it is not installed.  Each app is started as a detached
subprocess (``sys.executable main.py`` with cwd = the app directory) whose
stdin is /dev/null and whose stdout/stderr go to ``<data dir>/logs/<app>.log``
(never to the launcher's own pipes), so several trainers can run side by
side, outlive the launcher window, and ``python launch.py flash | cat``
returns as soon as the app is up.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple, Optional

ROOT = Path(__file__).resolve().parent
COACH_PY = ROOT / "coach.py"
DASHBOARD_PY = ROOT / "dashboard.py"
DOCS_README = ROOT / "docs" / "README.md"
API_KEY_FILE = Path.home() / ".config" / "quantum-study" / "api_key.txt"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "quantum-study"
LOG_DIR_NAME = "logs"
_LOG_MAX_BYTES = 1_000_000   # a per-app log is truncated once it grows past this


# ---------------------------------------------------------------------------
# App registry — learning-path order (README "Recommended Learning Path")
# ---------------------------------------------------------------------------

API_KEY_LEVELS = ("required", "optional", "none")


class App(NamedTuple):
    dir: str            # directory under the repo root containing main.py
    name: str           # display name
    description: str    # one line
    api_key: str        # one of API_KEY_LEVELS:
                        #   "required" - the core loop (question generation and/or
                        #                answer grading) calls the Claude API; with no
                        #                key only Reference, history and browsing remain
                        #   "optional" - the core loop runs offline (auto-graded MC,
                        #                numeric answers, execution-graded katas); a
                        #                key only adds free-form grading / Claude review
                        #   "none"     - never touches the API
    alias: str          # short CLI name


APPS: list[App] = [
    App("flashcard-drill", "Flashcard Drill",
        "SRS flashcards - 550 cards covering the whole ladder, fully offline",
        "none", "flash"),
    App("math-quiz", "Math Quiz",
        "Mathematical foundations for QC: linear algebra, complex numbers, probability",
        "required", "math"),
    App("quantum-quiz", "Quantum Quiz",
        "Dynamic Q&A across 11 QC subjects, incl. Qiskit and C1000-179 certification",
        "required", "quiz"),
    App("circuit-trainer", "Circuit Trainer",
        "Qiskit-generated circuit problems plus timed prediction sprints",
        "optional", "circuit"),
    App("qec-trainer", "QEC Trainer",
        "Error-correction problem set and the syndrome decoder game",
        "optional", "qec"),
    App("vqa-trainer", "VQA Trainer",
        "Variational algorithms: VQE, QAOA, ansatz design, barren plateaus",
        "optional", "vqa"),
    App("paper-drill", "Paper Drill",
        "Generate and grade questions from any research paper you are reading",
        "required", "paper"),
    App("qiskit-dojo", "Qiskit Dojo",
        "36 write-and-run coding katas, graded by execution (Claude review optional)",
        "optional", "dojo"),
    App("problem-trainer", "Problem Trainer",
        "Textbook problem sets and guided derivations, AI-graded",
        "required", "problem"),
    App("exam-sim", "Exam Simulator",
        "Timed C1000-179 mock exams and section sprints - 110-question bank, offline",
        "none", "exam"),
]

_API_KEY_CELL = {"required": "yes", "optional": "optional", "none": "no"}   # --list column


# ---------------------------------------------------------------------------
# Name resolution
# ---------------------------------------------------------------------------

class LaunchError(Exception):
    """Base class for launcher errors."""


class UnknownAppError(LaunchError):
    def __init__(self, query: str):
        super().__init__(f"unknown app '{query}'")
        self.query = query


class AmbiguousAppError(LaunchError):
    def __init__(self, query: str, candidates: list[App]):
        # Show the directory too: a prefix can match through the directory name
        # (e.g. 'q' -> qiskit-dojo), which the alias alone would not explain.
        names = ", ".join(f"{a.alias} ({a.dir})" for a in candidates)
        super().__init__(f"'{query}' is ambiguous - did you mean: {names}?")
        self.query = query
        self.candidates = candidates


def _normalize(text: str) -> str:
    """Canonical lookup key: lower-case, '-' for spaces/underscores.

    Shell path forms produced by tab completion resolve to the directory name:
    ``qiskit-dojo/``, ``./qiskit-dojo``, ``qiskit-dojo/main.py`` and an absolute
    path all become ``qiskit-dojo``.
    """
    text = text.strip()
    if "/" in text or os.sep in text:
        parts = [p for p in text.replace(os.sep, "/").split("/") if p and p != "."]
        if parts and parts[-1] == "main.py":
            parts.pop()
        text = parts[-1] if parts else ""
    return text.lower().replace(" ", "-").replace("_", "-")


def _match_names(app: App) -> tuple[str, str, str]:
    return app.dir, app.alias, _normalize(app.name)


def resolve_app(query: str) -> App:
    """Return the App for *query*: exact dir/alias/name first, then unique prefix.

    Raises UnknownAppError when nothing matches and AmbiguousAppError when a
    prefix matches more than one app.
    """
    q = _normalize(query or "")
    if not q:
        raise UnknownAppError(query)
    exact = [a for a in APPS if q in _match_names(a)]
    if len(exact) == 1:
        return exact[0]
    prefixed = [a for a in APPS if any(n.startswith(q) for n in _match_names(a))]
    if len(prefixed) == 1:
        return prefixed[0]
    if not prefixed:
        raise UnknownAppError(query)
    raise AmbiguousAppError(query, prefixed)


# ---------------------------------------------------------------------------
# Launching
# ---------------------------------------------------------------------------

def data_dir() -> Path:
    return Path(os.environ.get("QUANTUM_STUDY_DATA_DIR") or DEFAULT_DATA_DIR)


def app_log_path(app: App) -> Path:
    """Where a launched app's stdout/stderr goes: ``<data dir>/logs/<app dir>.log``."""
    return data_dir() / LOG_DIR_NAME / f"{app.dir}.log"


def _open_app_log(app: App, argv: list[str], cwd: Path):
    """Open *app*'s log (binary, append; truncated past _LOG_MAX_BYTES) and stamp
    a header.  Returns None when it cannot be opened - the launch then falls
    back to /dev/null rather than failing because of logging."""
    path = app_log_path(app)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if path.is_file() and path.stat().st_size > _LOG_MAX_BYTES else "ab"
        log = open(path, mode)
    except OSError:
        return None
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"=== {stamp} launch: {shlex.join(argv)}  (cwd {cwd})\n".encode("utf-8"))
        log.flush()
    except OSError:
        pass
    return log


def detached_popen_kwargs(log=None) -> dict:
    """Popen keyword arguments that let the child outlive the launcher.

    stdin is /dev/null and stdout/stderr go to *log* (a writable binary file
    object, stderr merged) or to /dev/null - never to the launcher's own
    stdio, so a caller capturing the launcher's output is not held open until
    the app exits.
    """
    kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL if log is None else log,
        "stderr": subprocess.DEVNULL if log is None else subprocess.STDOUT,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        )
    else:
        kwargs["start_new_session"] = True
    return kwargs


def launch_command(app: App) -> tuple[list[str], Path]:
    """(argv, cwd) used to start *app*."""
    return [sys.executable, "main.py"], ROOT / app.dir


def launch_app(app: App, popen=None):
    """Start *app* detached and return the Popen object.

    *popen* may be injected for testing; it defaults to subprocess.Popen.
    The parent's copy of the log file is closed once the child holds it.
    """
    popen = popen or subprocess.Popen
    argv, cwd = launch_command(app)
    if not (cwd / "main.py").is_file():
        raise LaunchError(f"{app.name}: {cwd / 'main.py'} not found")
    log = _open_app_log(app, argv, cwd)
    try:
        return popen(argv, cwd=str(cwd), **detached_popen_kwargs(log))
    finally:
        if log is not None:
            log.close()


def _tilde(path: Path) -> str:
    """str(path) with the home directory shortened to '~' (display only)."""
    try:
        return "~/" + path.relative_to(Path.home()).as_posix()
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Environment status
# ---------------------------------------------------------------------------

def venv_name() -> Optional[str]:
    """Name of the active virtual environment directory, or None."""
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return Path(sys.prefix).name
    return None


def qiskit_version() -> Optional[str]:
    try:
        return importlib.metadata.version("qiskit")
    except importlib.metadata.PackageNotFoundError:
        return None


def api_key_configured(env: Optional[dict] = None, key_file: Optional[Path] = None) -> bool:
    """True when ANTHROPIC_API_KEY is set or the key file has content.

    *key_file* defaults to API_KEY_FILE, resolved at call time so the module
    constant can be redirected.
    """
    env = os.environ if env is None else env
    key_file = API_KEY_FILE if key_file is None else key_file
    if (env.get("ANTHROPIC_API_KEY") or "").strip():
        return True
    try:
        return key_file.is_file() and bool(key_file.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def history_files(directory: Optional[Path] = None) -> list[Path]:
    """Study-history files (``*_history.json``) present in the data directory."""
    directory = data_dir() if directory is None else directory
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*_history.json"))


def status_info() -> dict:
    return {
        "python": platform.python_version(),
        "venv": venv_name(),
        "qiskit": qiskit_version(),
        "api_key": api_key_configured(),
        "history": len(history_files()),
        "data_dir": str(data_dir()),
    }


def format_status(info: dict, sep: str = " | ") -> str:
    py = f"Python {info['python']}"
    if info.get("venv"):
        py += f" ({info['venv']})"
    qk = f"Qiskit {info['qiskit']}" if info.get("qiskit") else "Qiskit not installed"
    key = "API key: configured" if info.get("api_key") else "API key: not configured"
    n = info.get("history", 0)
    hist = "Study history: none yet" if not n else f"Study history: {n} file{'s' if n != 1 else ''}"
    return sep.join([py, qk, key, hist])


def missing_key_note(app: App) -> Optional[str]:
    """What the user loses in *app* without a key (None for offline apps)."""
    if app.api_key == "required":
        return ("this app uses the Claude API for generation/grading and no key is "
                "configured (ANTHROPIC_API_KEY or ~/.config/quantum-study/api_key.txt)")
    if app.api_key == "optional":
        return ("no key is configured - free-form grading / Claude review will be "
                "unavailable; the core problem set works offline")
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_app_table() -> str:
    header = ("#", "App", "Alias", "Directory", "API key", "Description")
    rows = [
        (str(i), a.name, a.alias, a.dir, _API_KEY_CELL[a.api_key], a.description)
        for i, a in enumerate(APPS, 1)
    ]
    widths = [max(len(r[c]) for r in rows + [header]) for c in range(5)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths) + "  {}"
    lines = [fmt.format(*header), fmt.format(*("-" * w for w in widths), "-" * len(header[5]))]
    lines += [fmt.format(*r) for r in rows]
    lines += ["", "API key: yes = generation/grading needs a key; optional = core loop is "
                  "offline, a key adds free-form grading / Claude review; no = never used",
              "Launch:  python launch.py <alias | directory | unique prefix>"
              "    e.g.  python launch.py dojo"]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="launch.py",
        description="Quantum Study Suite launcher. With no arguments, opens the GUI.",
    )
    parser.add_argument("app", nargs="?", metavar="APP",
                        help="app to launch: alias, directory, or unique prefix")
    parser.add_argument("--list", action="store_true", help="print the app table and exit")
    parser.add_argument("--status", action="store_true",
                        help="print the environment status line and exit")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        print(format_app_table())
        return 0
    if args.status:
        print(format_status(status_info()))
        return 0
    if args.app:
        try:
            app = resolve_app(args.app)
        except LaunchError as exc:
            print(f"launch.py: {exc}", file=sys.stderr)
            print("Run `python launch.py --list` to see the apps.", file=sys.stderr)
            return 2
        try:
            proc = launch_app(app)
        except (LaunchError, OSError) as exc:
            print(f"launch.py: could not start {app.name}: {exc}", file=sys.stderr)
            return 1
        log = app_log_path(app)
        where = f"; output in {_tilde(log)}" if log.is_file() else ""
        # flush so this line lands before the stderr note when stdout is a pipe
        print(f"Launched {app.name} ({app.dir}/main.py, pid {proc.pid}{where})", flush=True)
        note = missing_key_note(app)
        if note and not api_key_configured():
            print(f"note: {note}", file=sys.stderr)
        return 0
    return run_gui()


# ---------------------------------------------------------------------------
# GUI (PyQt6 imported lazily)
# ---------------------------------------------------------------------------

# Palette copied from vqa-trainer/ui/theme.py (kept in sync by hand; apps are
# deliberately not imported across package boundaries).
BG         = "#0d1117"
SURFACE    = "#161b22"
SURFACE2   = "#21262d"
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#388bfd"
TEXT       = "#e6edf3"
TEXT_MUTED = "#8b949e"
SUCCESS    = "#3fb950"
WARNING    = "#d29922"
ERROR      = "#f85149"

QSS = f"""
QWidget {{
    background-color: {BG}; color: {TEXT};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 14px;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {BG}; border: none; }}
QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QPushButton {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 16px; font-size: 13px;
}}
QPushButton:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton:pressed {{ background-color: {ACCENT2}; color: white; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; border-color: {SURFACE2}; }}
QPushButton#accent {{
    background-color: {ACCENT}; color: {BG};
    border: none; font-weight: bold; padding: 6px 18px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; }}
QPushButton#accent:disabled {{ background-color: {SURFACE2}; color: {TEXT_MUTED}; }}
QPlainTextEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px; selection-background-color: {ACCENT2};
}}
QPlainTextEdit#output {{
    font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Liberation Mono",
                 "Menlo", "Consolas", "Courier New", monospace;
    font-size: 13px;
}}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT}; }}
QLabel#subheading {{ font-size: 14px; color: {TEXT_MUTED}; }}
QLabel#section {{ font-size: 16px; font-weight: bold; color: {TEXT}; }}
QLabel#muted {{ color: {TEXT_MUTED}; font-size: 13px; }}
QLabel#appname {{ font-size: 15px; font-weight: bold; color: {TEXT}; }}
QLabel#step {{ color: {ACCENT}; font-weight: bold; font-size: 15px; }}
QLabel#status {{ color: {TEXT_MUTED}; font-size: 13px; padding: 4px 0; }}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#card QWidget {{ background-color: {SURFACE}; }}
QFrame#card QPushButton {{ background-color: {SURFACE2}; }}
QFrame#card QPushButton#accent {{ background-color: {ACCENT}; }}
QFrame#card QPushButton#accent:disabled {{ background-color: {SURFACE2}; }}
QFrame#card QPlainTextEdit {{ background-color: {BG}; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QStatusBar {{ color: {TEXT_MUTED}; }}
"""


def key_badge(app: App, key_ok: bool) -> tuple[str, str]:
    """(rich text, tooltip) for the API-key badge shown next to *app*.

    Pure function so the GUI can re-render badges whenever the key state
    changes and tests can check the mapping without a window.
    """
    if app.api_key == "none":
        return f'<span style="color:{SUCCESS}">offline</span>', "Works with no API key"
    if app.api_key == "optional":
        return (f'<span style="color:{TEXT_MUTED}">key optional</span>',
                "Core loop works offline; an API key adds free-form grading / Claude review")
    colour = TEXT_MUTED if key_ok else WARNING
    tip = "Uses the Claude API for generation/grading"
    if not key_ok:
        tip += " - no key configured, so those features will be unavailable"
    return f'<span style="color:{colour}">API key</span>', tip


_WINDOW_CLS = None


def _window_class():
    """Define (once) and return the LauncherWindow class; imports PyQt6."""
    global _WINDOW_CLS
    if _WINDOW_CLS is not None:
        return _WINDOW_CLS

    from PyQt6.QtCore import QEvent, QProcess, QProcessEnvironment, Qt, QUrl
    from PyQt6.QtGui import QDesktopServices
    from PyQt6.QtWidgets import (
        QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
        QPushButton, QSizePolicy, QVBoxLayout, QWidget,
    )

    class LauncherWindow(QMainWindow):
        """Suite launcher: app list, coach/dashboard tools, environment status."""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("Quantum Study Suite")
            self.resize(900, 760)
            self._proc: Optional[QProcess] = None
            self._tool_buttons: list[QPushButton] = []
            self._key_badges: list[tuple[QLabel, App]] = []
            self.launch_buttons: dict[str, QPushButton] = {}
            self.last_tool_exit: Optional[int] = None
            self._key_ok = api_key_configured()

            central = QWidget()
            self.setCentralWidget(central)
            root = QVBoxLayout(central)
            root.setContentsMargins(24, 20, 24, 12)
            root.setSpacing(12)

            heading = QLabel("Quantum Study Suite")
            heading.setObjectName("heading")
            sub = QLabel("Ten desktop trainers in learning-path order. Each Launch opens an "
                         "independent window - run several at once.")
            sub.setObjectName("subheading")
            sub.setWordWrap(True)
            root.addWidget(heading)
            root.addWidget(sub)

            root.addWidget(self._build_apps_card())
            root.addWidget(self._build_tools_card(), stretch=1)

            self.status_label = QLabel()
            self.status_label.setObjectName("status")
            self.status_label.setTextFormat(Qt.TextFormat.RichText)
            self.refresh_status()
            root.addWidget(self.status_label)

        # -- construction ---------------------------------------------------

        def _build_apps_card(self) -> QWidget:
            card = QFrame()
            card.setObjectName("card")
            grid = QGridLayout(card)
            grid.setContentsMargins(16, 12, 16, 12)
            grid.setHorizontalSpacing(14)
            grid.setVerticalSpacing(6)

            for row, app in enumerate(APPS):
                step = QLabel(f"{row + 1}")
                step.setObjectName("step")
                step.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                text = QWidget()
                tl = QVBoxLayout(text)
                tl.setContentsMargins(0, 0, 0, 0)
                tl.setSpacing(0)
                name = QLabel(app.name)
                name.setObjectName("appname")
                desc = QLabel(app.description)
                desc.setObjectName("muted")
                desc.setWordWrap(True)
                tl.addWidget(name)
                tl.addWidget(desc)
                text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

                badge = QLabel()
                badge.setObjectName("muted")
                html, tip = key_badge(app, self._key_ok)
                badge.setText(html)
                badge.setToolTip(tip)
                self._key_badges.append((badge, app))

                btn = QPushButton("Launch")
                btn.setObjectName("accent")
                btn.setProperty("app_dir", app.dir)
                btn.setToolTip(f"python {app.dir}/main.py   (alias: {app.alias})\n"
                               f"output: {_tilde(app_log_path(app))}")
                btn.clicked.connect(lambda _=False, a=app: self.launch(a))
                self.launch_buttons[app.dir] = btn

                grid.addWidget(step, row, 0)
                grid.addWidget(text, row, 1)
                grid.addWidget(badge, row, 2)
                grid.addWidget(btn, row, 3)
            grid.setColumnStretch(1, 1)
            return card

        def _build_tools_card(self) -> QWidget:
            card = QFrame()
            card.setObjectName("card")
            lay = QVBoxLayout(card)
            lay.setContentsMargins(16, 12, 16, 12)
            lay.setSpacing(8)

            title = QLabel("Study tools")
            title.setObjectName("section")
            lay.addWidget(title)

            row = QHBoxLayout()
            row.setSpacing(8)
            for label, slot, tip in (
                ("Today's plan", self.run_todays_plan, "python coach.py"),
                ("Review queue", self.run_review_queue, "python coach.py --review"),
                ("Dashboard", self.run_dashboard, "python dashboard.py"),
            ):
                b = QPushButton(label)
                b.setToolTip(tip)
                b.clicked.connect(slot)
                self._tool_buttons.append(b)
                row.addWidget(b)
            docs = QPushButton("Open docs")
            docs.setToolTip(str(DOCS_README))
            docs.clicked.connect(self.open_docs)
            row.addWidget(docs)
            row.addStretch(1)
            lay.addLayout(row)

            self.output = QPlainTextEdit()
            self.output.setObjectName("output")   # monospace via QSS (stylesheet fonts win over setFont)
            self.output.setReadOnly(True)
            self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            self.output.setPlaceholderText(
                "Output from coach.py / dashboard.py appears here.")
            self.output.setMinimumHeight(180)
            lay.addWidget(self.output, stretch=1)
            return card

        # -- apps -------------------------------------------------------------

        def launch(self, app: App) -> None:
            try:
                proc = launch_app(app)
            except (LaunchError, OSError) as exc:
                self.statusBar().showMessage(f"Could not start {app.name}: {exc}", 8000)
                self.output.appendPlainText(f"[launch] {app.name}: {exc}")
                return
            msg = f"Launched {app.name} (pid {proc.pid})"
            note = missing_key_note(app)
            if note and not self._key_ok:
                msg += " - " + note.split(" (")[0]
            self.statusBar().showMessage(msg, 6000)
            self.output.appendPlainText(
                f"[launch] {app.name} started (pid {proc.pid}); output in {_tilde(app_log_path(app))}")

        # -- tools ------------------------------------------------------------

        def run_todays_plan(self) -> None:
            self.run_tool([sys.executable, str(COACH_PY)], "Today's plan")

        def run_review_queue(self) -> None:
            self.run_tool([sys.executable, str(COACH_PY), "--review"], "Review queue")

        def run_dashboard(self) -> None:
            self.run_tool([sys.executable, str(DASHBOARD_PY)], "Dashboard")

        def open_docs(self) -> None:
            if not DOCS_README.is_file():
                self.statusBar().showMessage(f"Not found: {DOCS_README}", 6000)
                return
            ok = QDesktopServices.openUrl(QUrl.fromLocalFile(str(DOCS_README)))
            self.statusBar().showMessage(
                "Opened docs/README.md" if ok else "No handler for docs/README.md", 4000)

        def tool_running(self) -> bool:
            return (self._proc is not None
                    and self._proc.state() != QProcess.ProcessState.NotRunning)

        def run_tool(self, argv: list[str], label: str, cwd: Path = ROOT) -> bool:
            """Run *argv* (cwd = repo root) and stream its output into the pane."""
            if self.tool_running():
                self.statusBar().showMessage("A tool is still running - wait for it to finish", 4000)
                return False
            self.output.setPlainText("$ " + " ".join(shlex.quote(a) for a in argv) + "\n")
            proc = QProcess(self)
            proc.setWorkingDirectory(str(cwd))
            proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            env = QProcessEnvironment.systemEnvironment()
            env.insert("PYTHONUNBUFFERED", "1")
            env.insert("PYTHONIOENCODING", "utf-8")
            proc.setProcessEnvironment(env)
            # Each handler is bound to *its* QProcess so a late signal from a
            # finished run can never be read against a newer one.
            proc.readyReadStandardOutput.connect(lambda p=proc: self._on_tool_output(p))
            proc.finished.connect(
                lambda code, _st, p=proc, lbl=label: self._on_tool_finished(lbl, code, p))
            proc.errorOccurred.connect(
                lambda err, p=proc, lbl=label: self._on_tool_error(lbl, err, p))
            self._proc = proc
            self.last_tool_exit = None
            self._set_tools_enabled(False)
            self.statusBar().showMessage(f"Running {label}...")
            proc.start(argv[0], argv[1:])
            return True

        def _on_tool_output(self, proc=None) -> None:
            proc = self._proc if proc is None else proc
            if proc is None:
                return
            data = bytes(proc.readAllStandardOutput()).decode("utf-8", "replace")
            if data:
                self.output.moveCursor(self.output.textCursor().MoveOperation.End)
                self.output.insertPlainText(data)
                self.output.moveCursor(self.output.textCursor().MoveOperation.End)

        def _on_tool_finished(self, label: str, code: int, proc=None) -> None:
            proc = self._proc if proc is None else proc
            self._on_tool_output(proc)
            self.last_tool_exit = code
            self._end_run(proc, f"{label} finished" + ("" if code == 0 else f" (exit {code})"), 5000)

        def _on_tool_error(self, label: str, err, proc=None) -> None:
            proc = self._proc if proc is None else proc
            name = getattr(err, "name", str(err))
            self.output.appendPlainText(f"[{label}] process error: {name}")
            if err == QProcess.ProcessError.FailedToStart:
                # No `finished` follows a start failure, so close the run out here
                # (a crash does emit `finished`, which reports the real exit code).
                self.last_tool_exit = -1
                self._end_run(proc, f"{label} failed to start ({name})", 8000)
            elif not self.tool_running():
                self._set_tools_enabled(True)

        def _end_run(self, proc, message: str, msecs: int) -> None:
            """Common tail of a tool run: buttons back, report, refresh, drop the QProcess."""
            self._set_tools_enabled(True)
            self.statusBar().showMessage(message, msecs)
            self.refresh_status()
            if proc is not None:
                if self._proc is proc:
                    self._proc = None
                proc.deleteLater()

        def _set_tools_enabled(self, enabled: bool) -> None:
            for b in self._tool_buttons:
                b.setEnabled(enabled)

        # -- status -----------------------------------------------------------

        def refresh_status(self) -> None:
            info = status_info()
            self._key_ok = bool(info["api_key"])
            for badge, app in self._key_badges:
                html, tip = key_badge(app, self._key_ok)
                badge.setText(html)
                badge.setToolTip(tip)
            key_colour = SUCCESS if info["api_key"] else WARNING
            key = ("configured" if info["api_key"] else "not configured")
            py = f"Python {info['python']}" + (f" ({info['venv']})" if info.get("venv") else "")
            qk = f"Qiskit {info['qiskit']}" if info.get("qiskit") else \
                 f'<span style="color:{WARNING}">Qiskit not installed</span>'
            n = info["history"]
            hist = ("Study history: none yet" if not n
                    else f"Study history: {n} file{'s' if n != 1 else ''}")
            self.status_label.setText(
                f"{py} &nbsp;·&nbsp; {qk} &nbsp;·&nbsp; API key: "
                f'<span style="color:{key_colour}">{key}</span> &nbsp;·&nbsp; {hist}')
            self.status_label.setToolTip(f"Data directory: {info['data_dir']}")

        def event(self, ev) -> bool:  # noqa: N802 (Qt naming)
            # A key written while the launcher is open (or history from an app
            # closed meanwhile) is picked up when the window regains focus.
            if (ev.type() == QEvent.Type.WindowActivate
                    and getattr(self, "status_label", None) is not None):
                self.refresh_status()
            return super().event(ev)

        def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
            if self.tool_running():
                self._proc.kill()
                self._proc.waitForFinished(1000)
            super().closeEvent(event)

    _WINDOW_CLS = LauncherWindow
    return LauncherWindow


def build_window():
    """Construct the launcher window (a QApplication must already exist)."""
    return _window_class()()


def run_gui() -> int:
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        print(f"launch.py: PyQt6 is required for the GUI ({exc}).", file=sys.stderr)
        print("Use `python launch.py --list` or `python launch.py <app>` instead.",
              file=sys.stderr)
        return 1
    qapp = QApplication.instance() or QApplication(sys.argv[:1])
    qapp.setApplicationName("Quantum Study Suite")
    qapp.setStyleSheet(QSS)
    window = build_window()
    window.show()
    return qapp.exec()


if __name__ == "__main__":
    sys.exit(main())
