"""core/runner.py subprocess harness: pass / fail / user error / timeout."""
from pathlib import Path

from core.runner import _SENTINEL, find_python, run_kata


def test_find_python_points_at_an_interpreter():
    assert Path(find_python()).exists()


def test_trivially_passing_kata_passes():
    result = run_kata("x = 41 + 1\n", "assert x == 42, 'math'\nprint('ok')\n")
    assert result.passed is True
    assert result.phase == "pass"
    assert "ok" in result.output
    assert _SENTINEL not in result.output
    assert result.duration_secs >= 0


def test_pass_with_no_output_uses_placeholder():
    result = run_kata("x = 1\n", "assert x == 1\n")
    assert result.passed
    assert result.output == "(no output)"


def test_failing_assertion_surfaces_failed_message():
    result = run_kata("x = 1\n", "assert x == 2, 'x should be 2'\n")
    assert result.passed is False
    assert result.phase == "test_failed"
    assert "FAILED: x should be 2" in result.output
    assert "kata_tests.py" in result.output


def test_exception_inside_tests_is_test_failed():
    result = run_kata("x = 1\n", "y = undefined_name\n")
    assert result.phase == "test_failed"
    assert "NameError" in result.output


def test_syntax_error_is_user_error():
    result = run_kata("def (:\n", "assert True\n")
    assert result.passed is False
    assert result.phase == "user_error"
    assert "SyntaxError" in result.output
    assert "your_code.py" in result.output


def test_runtime_exception_is_user_error():
    result = run_kata("raise ValueError('boom')\n", "assert True\n")
    assert result.phase == "user_error"
    assert "boom" in result.output


def test_infinite_loop_times_out():
    result = run_kata("while True:\n    pass\n", "assert True\n", timeout=2)
    assert result.passed is False
    assert result.phase == "timeout"
    assert "Timed out after 2s" in result.output
    assert result.duration_secs >= 1.5


def test_sys_exit_zero_without_sentinel_is_not_a_pass():
    result = run_kata("import sys\nsys.exit(0)\n", "assert True\n")
    assert result.passed is False
    assert result.phase == "crash"


def test_real_kata_solution_passes_and_starter_fails(katas):
    kata = next(k for k in katas if k.id == "cc_bell_state")
    assert run_kata(kata.solution_code, kata.test_code).passed
    starter = run_kata(kata.starter_code, kata.test_code)
    assert starter.passed is False
    assert starter.phase == "test_failed"


def test_harness_frames_never_leak_into_feedback():
    cases = [
        ("x = 1\n", "y = qc.depth()\n"),                        # NameError in tests
        ("x = 1\n", "from qiskit_nonexistent import thing\n"),  # ImportError in tests
        ("def (:\n", "assert True\n"),                          # SyntaxError in user code
        ("raise ValueError('boom')\n", "assert True\n"),        # runtime error in user code
        ("x = 1\n", "assert x == 2, 'x should be 2'\n"),        # plain assert
    ]
    for user, test in cases:
        out = run_kata(user, test).output
        assert "harness.py" not in out, (user, test, out)
        assert "exec(compile" not in out, (user, test, out)


def test_error_feedback_starts_with_a_one_line_summary():
    result = run_kata("x = 1\n", "y = qc.depth()\n")
    lines = result.output.splitlines()
    assert lines[0] == "=== Error while running tests ==="
    assert lines[1] == "ERROR: NameError: name 'qc' is not defined"
    assert lines[2] == "Traceback (most recent call last):"
    assert lines[3].strip() == 'File "kata_tests.py", line 1, in <module>'
    assert lines[4].strip() == "y = qc.depth()"          # source line is quoted

    result = run_kata("def f():\n    raise ValueError('boom')\n\nf()\n", "assert True\n")
    lines = result.output.splitlines()
    assert lines[0] == "=== Error while running your code ==="
    assert lines[1] == "ERROR: ValueError: boom"
    assert "raise ValueError('boom')" in result.output
    assert 'File "your_code.py", line 2, in f' in result.output


def test_assertion_feedback_quotes_the_failing_assert():
    result = run_kata("x = 1\n", "y = 2\nassert x == y, 'x should equal y'\n")
    lines = result.output.splitlines()
    assert lines[0] == "=== Test failed ==="
    assert lines[1] == "FAILED: x should equal y"
    assert lines[2].strip() == 'File "kata_tests.py", line 2, in <module>'
    assert lines[3].strip() == "assert x == y, 'x should equal y'"
