"""Regression for the worker-thread segfault.

qiskit's native extension must be initialised on the GUI thread before the
first ProblemWorker QThread runs; first-importing it inside a worker made the
NEXT generation on a fresh worker thread segfault (Python 3.14 + qiskit 2.5).
The in-process tests check the plumbing; the subprocess test checks the
guarantee from a cold interpreter, where nothing else has imported qiskit."""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import textwrap

from PyQt6.QtCore import QEventLoop, QTimer

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_importing_the_worker_module_imports_qiskit():
    import workers.problem_worker  # noqa: F401

    assert "qiskit" in sys.modules
    assert "qiskit._accelerate" in sys.modules


def _run_worker_once(session, timeout_ms=60000):
    from workers.problem_worker import ProblemWorker

    loop = QEventLoop()
    got: dict = {}
    worker = ProblemWorker(session)
    worker.problem_ready.connect(lambda p: (got.__setitem__("problem", p), loop.quit()))
    worker.error.connect(lambda m: (got.__setitem__("error", m), loop.quit()))
    QTimer.singleShot(timeout_ms, loop.quit)
    worker.start()
    loop.exec()
    worker.wait(5000)
    return got


def test_sequential_workers_each_deliver_a_problem(qapp):
    from core.models import ProblemCategory, TrainerConfig
    from core.session import TrainerSession

    session = TrainerSession(TrainerConfig(
        categories=[ProblemCategory.SINGLE_GATE_OUTPUT, ProblemCategory.GATE_SEQUENCE],
        difficulty="beginner", problem_count=3))
    for _ in range(3):
        got = _run_worker_once(session)
        assert "error" not in got, got
        assert "problem" in got, "worker neither delivered nor errored"
        assert got["problem"].choices


def test_cold_interpreter_survives_three_worker_threads(tmp_path):
    script = textwrap.dedent("""
        import faulthandler, sys
        faulthandler.enable()
        sys.path.insert(0, %r)
        assert "qiskit" not in sys.modules, "test precondition: cold interpreter"
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QEventLoop, QTimer
        app = QApplication([])
        from ui.main_window import MainWindow
        assert "qiskit" in sys.modules, "ui.main_window must import qiskit on the GUI thread"
        win = MainWindow()
        from core.models import ProblemCategory, TrainerConfig
        from core.session import TrainerSession
        from workers.problem_worker import ProblemWorker
        session = TrainerSession(TrainerConfig(
            categories=[ProblemCategory.SINGLE_GATE_OUTPUT], difficulty="beginner", problem_count=3))
        for i in range(3):
            loop = QEventLoop(); got = {}
            w = ProblemWorker(session)
            w.problem_ready.connect(lambda p: (got.__setitem__("p", p), loop.quit()))
            w.error.connect(lambda m: (got.__setitem__("e", m), loop.quit()))
            QTimer.singleShot(60000, loop.quit)
            w.start(); loop.exec(); w.wait(5000)
            assert "p" in got, got
            print("gen", i + 1, "ok", flush=True)
        win.close()
        print("ALL OK", flush=True)
    """ % str(APP_ROOT))
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen",
           "QUANTUM_STUDY_DATA_DIR": str(tmp_path / "quantum-study")}
    env.pop("ANTHROPIC_API_KEY", None)
    proc = subprocess.run([sys.executable, "-c", script], cwd=APP_ROOT, env=env,
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, f"rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr[-3000:]}"
    assert "ALL OK" in proc.stdout
    assert "Segmentation fault" not in proc.stderr
