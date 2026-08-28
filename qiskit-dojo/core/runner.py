"""Execution harness — runs user code + kata tests in a subprocess.

The user's code is exec'd into a fresh namespace; the kata's test_code
(plain asserts) then runs against that namespace.  Everything happens in
a throwaway subprocess with a hard timeout, so buggy or hostile-to-the-UI
code (infinite loops, sys.exit, matplotlib windows) cannot take down the
app.  Fully offline — no network needed.
"""
from __future__ import annotations
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from core.models import RunResult
from config import RUN_TIMEOUT_SECS

_SENTINEL = "DOJO_ALL_TESTS_PASSED"

_HARNESS = '''\
"""Auto-generated dojo harness: exec user code, then run kata tests."""
import sys
import traceback

SENTINEL = "DOJO_ALL_TESTS_PASSED"


def main() -> None:
    with open("user_code.py", encoding="utf-8") as f:
        user_src = f.read()
    with open("test_code.py", encoding="utf-8") as f:
        test_src = f.read()

    ns = {"__name__": "__main__", "__builtins__": __builtins__}
    try:
        exec(compile(user_src, "your_code.py", "exec"), ns)
    except Exception:
        print("=== Error while running your code ===")
        traceback.print_exc(file=sys.stdout)
        sys.exit(2)

    try:
        exec(compile(test_src, "kata_tests.py", "exec"), ns)
    except AssertionError as e:
        print("=== Test failed ===")
        if e.args:
            print(f"FAILED: {e.args[0]}")
        tb = traceback.format_exc().splitlines()
        for line in tb:
            if "kata_tests.py" in line:
                print(line)
        sys.exit(3)
    except Exception:
        print("=== Error while running tests ===")
        traceback.print_exc(file=sys.stdout)
        sys.exit(3)

    print(SENTINEL)


main()
'''


def find_python() -> str:
    """Locate the shared study venv's Python interpreter.

    Order: sys.executable if we are already inside a venv, then
    ../.venv/bin/python relative to the app directory, then sys.executable.
    """
    if sys.prefix != sys.base_prefix:
        return sys.executable
    app_dir = Path(__file__).resolve().parent.parent   # qiskit-dojo/
    for candidate in (
        app_dir.parent / ".venv" / "bin" / "python",
        app_dir / ".venv" / "bin" / "python",
    ):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_kata(user_code: str, test_code: str,
             timeout: int = RUN_TIMEOUT_SECS) -> RunResult:
    """Execute user_code then test_code in an isolated subprocess."""
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="qiskit-dojo-") as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "user_code.py").write_text(user_code, encoding="utf-8")
        (tmp_path / "test_code.py").write_text(test_code, encoding="utf-8")
        (tmp_path / "harness.py").write_text(_HARNESS, encoding="utf-8")

        env = dict(os.environ)
        env["MPLBACKEND"] = "Agg"            # never open GUI windows
        env["PYTHONUNBUFFERED"] = "1"

        try:
            proc = subprocess.run(
                [find_python(), "harness.py"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") + (e.stderr or "")
            if isinstance(out, bytes):
                out = out.decode(errors="replace")
            return RunResult(
                passed=False,
                output=out + f"\n=== Timed out after {timeout}s "
                             "(infinite loop?) ===",
                phase="timeout",
                duration_secs=time.monotonic() - start,
            )
        except OSError as e:
            return RunResult(
                passed=False,
                output=f"Could not launch Python subprocess: {e}",
                phase="crash",
                duration_secs=time.monotonic() - start,
            )

    output = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    passed = proc.returncode == 0 and _SENTINEL in proc.stdout
    if passed:
        # Hide the internal sentinel from the user-facing output.
        output = output.replace(_SENTINEL, "").rstrip() or "(no output)"
        phase = "pass"
    elif proc.returncode == 2:
        phase = "user_error"
    elif proc.returncode == 3:
        phase = "test_failed"
    else:
        phase = "crash"
    return RunResult(
        passed=passed,
        output=output.strip() or "(no output)",
        phase=phase,
        duration_secs=time.monotonic() - start,
    )
