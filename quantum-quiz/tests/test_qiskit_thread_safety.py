"""Regression: Qiskit must be initialised on the MAIN thread.

With Python 3.14 + qiskit 2.x, first-initialising the Rust extension
(``qiskit._accelerate``) inside a worker thread makes every *subsequent* fresh
thread's Qiskit call segfault.  build_context() runs in a fresh QuestionWorker
QThread per question, so lazy imports inside it killed the app at question 2
of every session.  core.qiskit_bridge therefore imports the context modules
eagerly (it is pulled in by ui.main_window on the main thread).

The end-to-end check runs in a subprocess: a regression here is a SIGSEGV,
which would otherwise take the whole pytest process down with it.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import textwrap

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent

_SCRIPT = textwrap.dedent("""
    import sys, threading
    sys.path.insert(0, %r)
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    import ui.main_window                       # exactly what main.py imports first
    assert "qiskit" in sys.modules, "ui.main_window must pull Qiskit in on the main thread"

    from PyQt6.QtCore import QThread
    from core.qiskit_bridge import build_context
    from core.topics import SUBJECT_CONTEXT_MODE, TOPICS

    results = []
    def job(subject, topic):
        results.append((subject, topic, build_context(subject, topic).has_content()))

    for mode in ("hamiltonian", "statevector", "circuit"):
        subject = next(s for s, m in SUBJECT_CONTEXT_MODE.items() if m == mode)
        topics = TOPICS[subject]
        for i in range(2):                      # a FRESH thread per question, like the app
            t = threading.Thread(target=job, args=(subject, topics[i %% len(topics)]))
            t.start(); t.join()
        class Worker(QThread):
            def run(self_):
                job(subject, topics[2 %% len(topics)])
        w = Worker(); w.start(); w.wait()

    bad = [r for r in results if not r[2]]
    assert not bad, bad
    print("THREAD_SAFE", len(results))
""") % str(APP_ROOT)


def test_build_context_survives_sequential_worker_threads(tmp_path):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", MPLBACKEND="Agg",
               QUANTUM_STUDY_DATA_DIR=str(tmp_path))
    env.pop("ANTHROPIC_API_KEY", None)
    proc = subprocess.run(
        [sys.executable, "-X", "faulthandler", "-c", _SCRIPT],
        cwd=APP_ROOT, env=env, capture_output=True, text=True, timeout=240,
    )
    assert proc.returncode == 0, (
        f"exit {proc.returncode} (139/-11 = segfault)\n--- stdout ---\n{proc.stdout}"
        f"\n--- stderr (tail) ---\n{proc.stderr[-4000:]}"
    )
    assert "THREAD_SAFE 9" in proc.stdout, proc.stdout


def test_qiskit_bridge_imports_every_context_module_eagerly():
    import core.qiskit_bridge as bridge

    assert set(bridge._CONTEXT_MODULES) == {"circuit", "hamiltonian", "statevector"}
    for module_name in bridge._CONTEXT_MODULES.values():
        assert module_name in sys.modules, f"{module_name} must be imported at bridge import time"
    assert set(bridge._BUILDERS) == set(bridge._CONTEXT_MODULES)
    assert "qiskit" in sys.modules
