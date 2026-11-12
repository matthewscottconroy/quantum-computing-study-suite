"""Every app is a package under ``quantum_study`` and starts as a module.

Before the restructure each app was a directory of top-level modules
(``config``, ``core``, ``ui``, ``persistence``) run with ``cd <app> && python
main.py``, so no two of them could be imported into one interpreter.  These
tests hold the properties that restructure bought.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import quantum_study

REPO = Path(__file__).resolve().parent.parent
PACKAGE = REPO / "quantum_study"
APP_PACKAGES = sorted(quantum_study.APPS.values())


def _run(code: str, tmp_path: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    env.update(QT_QPA_PLATFORM="offscreen", MPLBACKEND="Agg",
               QUANTUM_STUDY_DATA_DIR=str(tmp_path / "data"))
    return subprocess.run([sys.executable, "-c", code], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=180)


def test_the_registry_lists_exactly_the_app_packages_on_disk():
    on_disk = sorted(p.parent.name for p in PACKAGE.glob("*/main.py"))
    assert APP_PACKAGES == on_disk
    for app_id, package in quantum_study.APPS.items():
        assert package == app_id.replace("-", "_"), "the package is the id with underscores"


def test_the_launcher_and_the_registry_agree():
    from quantum_study import launch

    assert sorted(a.dir for a in launch.APPS) == sorted(quantum_study.APPS)
    for app in launch.APPS:
        assert app.package == quantum_study.APPS[app.dir]
        assert app.module == f"quantum_study.{app.package}"
        assert (app.path / "main.py").is_file()


@pytest.mark.parametrize("package", APP_PACKAGES)
def test_app_has_a_module_entry_point(package):
    app_dir = PACKAGE / package
    assert (app_dir / "__init__.py").is_file()
    assert "from quantum_study.%s.main import main" % package in (
        app_dir / "__main__.py").read_text(encoding="utf-8")
    assert "\ndef main(" in (app_dir / "main.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("package", APP_PACKAGES)
def test_app_imports_in_a_fresh_interpreter_with_no_api_key(package, tmp_path):
    proc = _run(f"import quantum_study.{package}.main as m; assert callable(m.main)", tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert not (tmp_path / "data").exists(), "importing an app must not write study data"


def test_all_ten_apps_import_into_one_interpreter(tmp_path):
    """The thing the old layout could not do: ten apps, one sys.path, no clash."""
    imports = "; ".join(f"import quantum_study.{p}.main, quantum_study.{p}.config" for p in APP_PACKAGES)
    check = ("names = {m.split('.')[1] for m in __import__('sys').modules "
             "if m.startswith('quantum_study.') and m.count('.') >= 2}; "
             f"assert set({APP_PACKAGES!r}) <= names, names")
    proc = _run(f"{imports}; {check}", tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]


def test_no_app_module_is_importable_by_its_old_bare_name(tmp_path):
    """`import config` / `import persistence` must not resolve to an app."""
    code = (
        "import importlib.util as u\n"
        "import quantum_study.exam_sim.main\n"
        "found = [n for n in ('config', 'persistence', 'core', 'ui', 'common', 'common_path') if u.find_spec(n)]\n"
        "assert not found, found\n")
    proc = _run(code, tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]


def test_the_claude_model_is_named_in_exactly_one_place():
    """It used to be hard-coded in eight config.py files."""
    import re

    from quantum_study.common import llm

    literal = re.compile(r"""["']claude-[a-z0-9.-]+["']""")
    hits = sorted(
        str(p.relative_to(REPO)) for p in PACKAGE.rglob("*.py")
        if "tests" not in p.parts and p.name != "llm.py"
        and literal.search(p.read_text(encoding="utf-8")))
    assert not hits, f"model id written outside quantum_study/common/llm.py: {hits}"
    assert literal.fullmatch(repr(llm.MODEL).replace("'", '"'))
