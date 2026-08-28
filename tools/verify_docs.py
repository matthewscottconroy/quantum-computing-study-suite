#!/usr/bin/env python3
"""verify_docs.py — regression checks for the study corpus (docs/ and lesson-plans/).

Checks
------
  structure  docs/<chapter>/*.md: Exercises + Further Reading sections present,
             <details> blocks balanced, every solution wrapped, no empty
             sections, no truncated files.
  lint       docs/ and lesson-plans/: AI self-talk leftovers, TODO/FIXME/XXX,
             stranded "·..." fragments.
  crossrefs  markdown links / backtick paths that look like repo-relative file
             references must resolve to existing files.
  readme     docs/README.md file-map tables and lesson-plans/README.md lesson
             table must agree with the files on disk.
  snippets   run the ```python blocks of selected lesson-plans cumulatively in
             the project venv (see SNIPPET_FILES).  Requires .venv.

Usage
-----
  tools/verify_docs.py                 # all checks (incl. snippets)
  tools/verify_docs.py --no-snippets   # all static checks, skip snippet exec
  tools/verify_docs.py --structure --crossrefs
  tools/verify_docs.py --snippets --timeout 60

Exit status: 0 = all selected checks passed (warnings allowed), 1 = failures.

Stdlib only; the snippet check shells out to .venv/bin/python via subprocess.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LESSONS = ROOT / "lesson-plans"
VENV_PY = ROOT / ".venv" / "bin" / "python"

# Lesson files whose ```python blocks are executed by --snippets.
SNIPPET_FILES = ["06-qiskit.md", "07-qasm.md", "10-transpiling.md"]

# Top-level modules that mark a block as "not runnable offline in this venv".
# Blocks importing these are skipped automatically (they need external
# services or packages deliberately not installed: IBM runtime, pytket).
SKIP_MODULES = {"qiskit_ibm_runtime", "pytket"}

# (regex on block source, required module) — the block is skipped when the
# required module is not importable in the venv, even though the block's own
# import lines would succeed (lazy optional dependencies).
FEATURE_REQUIREMENTS = [
    # qiskit.qasm3.loads() needs the optional qiskit-qasm3-import package.
    (re.compile(r"qasm3\s+import[^\n]*\bloads\b|qiskit\.qasm3\.loads"),
     "qiskit_qasm3_import"),
]

# Explicit skip-list: {filename: {block_index: reason}}.  Prefer the
# automatic rules above; use this only for one-off exceptions.  A block whose
# first line matches "# verify: skip[ — reason]" is also skipped.
MANUAL_SKIPS: dict[str, dict[int, str]] = {}

SKIP_MARKER_RE = re.compile(r"^\s*#\s*verify:\s*skip\b\s*[-—:]?\s*(.*)$", re.I)

# ---------------------------------------------------------------------------
# reporting


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# markdown helpers


FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def fence_mask(lines: list[str]) -> list[bool]:
    """mask[i] is True when line i is inside (or delimits) a fenced code block."""
    mask = [False] * len(lines)
    fence: str | None = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0] * 3
                mask[i] = True
        else:
            mask[i] = True
            if m and m.group(1).startswith(fence):
                fence = None
    return mask


def chapter_files() -> list[Path]:
    """All chapter content files: docs/<chapter_dir>/*.md (READMEs excluded)."""
    out = []
    for d in sorted(DOCS.iterdir()):
        if d.is_dir():
            out.extend(sorted(p for p in d.glob("*.md")
                              if p.name.lower() != "readme.md"))
    return out


def corpus_files() -> list[Path]:
    """Every .md under docs/ and lesson-plans/."""
    out = []
    for base in (DOCS, LESSONS):
        if base.is_dir():
            out.extend(sorted(base.rglob("*.md")))
    return out


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


# ---------------------------------------------------------------------------
# check 1: STRUCTURE


HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
# Matches the item styles used across chapters:
#   **Exercise 1**: ...   |   **Exercise 1.** ...   |   **1.** ...
EXERCISE_ITEM_RE = re.compile(r"^\*\*(?:Exercise\s+\d+[.:]?|\d+[.:])\*\*")


def check_structure(rep: Report) -> None:
    for path in chapter_files():
        name = rel(path)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue  # file vanished mid-run (concurrent edits); skip
        lines = text.splitlines()
        mask = fence_mask(lines)

        def content_lines():
            for i, line in enumerate(lines):
                if not mask[i]:
                    yield i, line

        headings = [(i, len(HEADING_RE.match(l).group(1)), l.strip())
                    for i, l in content_lines() if HEADING_RE.match(l)]

        h2_titles = [t[2:].strip() for _, lvl, t in headings if lvl == 2]
        if "Exercises" not in h2_titles:
            rep.error(f"{name}: missing '## Exercises' section")
        if "Further Reading" not in h2_titles:
            rep.error(f"{name}: missing '## Further Reading' section")

        # <details> balance (counted outside code fences)
        body = "\n".join(l for i, l in enumerate(lines) if not mask[i])
        n_open = body.count("<details>")
        n_close = body.count("</details>")
        if n_open != n_close:
            rep.error(f"{name}: unbalanced <details> tags "
                      f"({n_open} open / {n_close} close)")

        # every <details> block carries a Solution summary
        for bi, chunk in enumerate(body.split("<details>")[1:], start=1):
            block = chunk.split("</details>")[0]
            if "<summary>Solution</summary>" not in block:
                rep.error(f"{name}: <details> block #{bi} lacks "
                          "'<summary>Solution</summary>'")

        # exercise items inside the Exercises section
        n_items = 0
        in_ex = False
        for i, line in content_lines():
            if line.startswith("## "):
                in_ex = line[3:].strip() == "Exercises"
            elif in_ex and EXERCISE_ITEM_RE.match(line):
                n_items += 1
        if "Exercises" in h2_titles and n_items == 0:
            rep.error(f"{name}: '## Exercises' section has no recognizable "
                      "exercise items (**Exercise N**, **Exercise N.**, "
                      "or **N.**)")
        if n_open < n_items:
            rep.error(f"{name}: {n_items} exercise items but only {n_open} "
                      "<details> solution blocks")

        # empty sections: a heading whose next content is a heading of the
        # same or shallower level (a deeper sub-heading is a legal body)
        for k, (i, lvl, title) in enumerate(headings):
            nxt_content = None
            for j, line in content_lines():
                if j <= i or not line.strip():
                    continue
                nxt_content = (j, line)
                break
            if nxt_content is None:
                rep.error(f"{name}:{i + 1}: section '{title}' at end of file "
                          "has no content")
                continue
            m = HEADING_RE.match(nxt_content[1])
            if m and len(m.group(1)) <= lvl:
                rep.error(f"{name}:{i + 1}: empty section '{title}' "
                          "(immediately followed by another heading)")

        # truncation: file must end with a non-empty line
        if not text.strip():
            rep.error(f"{name}: file is empty")
        elif not text.rstrip("\n").splitlines()[-1].strip():
            rep.error(f"{name}: file ends with blank line(s) — possible "
                      "truncation or stray whitespace")


# ---------------------------------------------------------------------------
# check 2: ARTIFACT LINT


SELF_TALK_RE = re.compile(
    r"(wait[,— ]+let|hmm[,— ]|let me recompute|let me be more careful"
    r"|this is getting complicated|let me verify:)",
    re.I,
)
WAIT_FOR_RE = re.compile(r"wait(s|ing|ed)?\s+for", re.I)
TODO_RE = re.compile(r"\b(TODO|FIXME)\b")
# 'XXX ' as a leftover marker; Pauli strings (XXX, XXXX, XXZZ, IXXI …) are
# excluded by requiring no adjacent Pauli letters or backticks.
XXX_RE = re.compile(r"(?<![A-Za-z`])XXX (?![XYZI(])")
STRANDED_RE = re.compile(r"·\.\.\.")


def check_lint(rep: Report) -> None:
    for path in corpus_files():
        name = rel(path)
        try:
            lines = read_lines(path)
        except FileNotFoundError:
            continue
        for i, line in enumerate(lines, start=1):
            m = SELF_TALK_RE.search(line)
            if m and not WAIT_FOR_RE.search(line):
                rep.error(f"{name}:{i}: AI self-talk leftover "
                          f"({m.group(0)!r}): {line.strip()[:80]}")
            m = TODO_RE.search(line)
            if m:
                rep.error(f"{name}:{i}: {m.group(0)} marker: "
                          f"{line.strip()[:80]}")
            if XXX_RE.search(line):
                rep.error(f"{name}:{i}: 'XXX ' marker: {line.strip()[:80]}")
            if STRANDED_RE.search(line):
                rep.error(f"{name}:{i}: stranded '·...' fragment: "
                          f"{line.strip()[:80]}")


# ---------------------------------------------------------------------------
# check 3: CROSS-REFS


MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_MD_RE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./\-]*\.md)`")
SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def _basename_index() -> set[str]:
    return {p.name for p in corpus_files()}


def _resolve(ref: str, src: Path, basenames: set[str]) -> bool:
    ref = ref.split("#", 1)[0]
    if not ref:
        return True
    candidates = [src.parent / ref, ROOT / ref, DOCS / ref, LESSONS / ref]
    for c in candidates:
        try:
            if c.exists():
                return True
        except OSError:
            pass
    # bare filename: accept if it exists anywhere in the corpus (README
    # file-map rows are checked strictly by the readme check)
    if "/" not in ref and ref in basenames:
        return True
    return False


def check_crossrefs(rep: Report) -> None:
    basenames = _basename_index()
    for path in corpus_files():
        name = rel(path)
        try:
            lines = read_lines(path)
        except FileNotFoundError:
            continue
        mask = fence_mask(lines)
        for i, line in enumerate(lines, start=1):
            if mask[i - 1]:
                continue
            for m in MD_LINK_RE.finditer(line):
                target = m.group(1)
                if SCHEME_RE.match(target) or target.startswith("#"):
                    continue
                bare = target.split("#", 1)[0]
                # only path-like targets: .md files or directory links
                if not (bare.endswith(".md") or bare.endswith("/")):
                    continue
                if not _resolve(target, path, basenames):
                    rep.error(f"{name}:{i}: broken link target "
                              f"'{target}'")
            for m in BACKTICK_MD_RE.finditer(line):
                if not _resolve(m.group(1), path, basenames):
                    rep.error(f"{name}:{i}: backtick path `{m.group(1)}` "
                              "does not resolve to an existing file")


# ---------------------------------------------------------------------------
# check 4: README SYNC


FILES_MARKER_RE = re.compile(r"\*\*Files\*\*:\s*`([A-Za-z0-9_\-]+)/`")
MAP_ROW_RE = re.compile(r"^\|\s*`([^`|]+\.md)`\s*\|")


def check_readme(rep: Report) -> None:
    readme = DOCS / "README.md"
    if readme.is_file():
        current_dir: Path | None = None
        mapped: dict[Path, set[str]] = {}
        for i, line in enumerate(read_lines(readme), start=1):
            fm = FILES_MARKER_RE.search(line)
            if fm:
                current_dir = DOCS / fm.group(1)
                if not current_dir.is_dir():
                    rep.error(f"docs/README.md:{i}: chapter directory "
                              f"`{fm.group(1)}/` does not exist")
                    current_dir = None
                continue
            rm = MAP_ROW_RE.match(line)
            if rm:
                fname = rm.group(1).strip()
                if current_dir is None:
                    rep.warn(f"docs/README.md:{i}: file-map row "
                             f"`{fname}` has no preceding **Files** chapter "
                             "marker; cannot verify")
                    continue
                mapped.setdefault(current_dir, set()).add(fname)
                if not (current_dir / fname).is_file():
                    rep.error(f"docs/README.md:{i}: file-map names "
                              f"`{fname}` but "
                              f"{rel(current_dir / fname)} does not exist")
        # chapters that have a map: warn on files missing from it
        for d, names in sorted(mapped.items()):
            for p in sorted(d.glob("*.md")):
                if p.name.lower() == "readme.md":
                    continue
                if p.name not in names:
                    rep.warn(f"docs/README.md: {rel(p)} is not listed in the "
                             f"file map for `{d.name}/`")
    else:
        rep.error("docs/README.md not found")

    lp_readme = LESSONS / "README.md"
    if lp_readme.is_file():
        basenames = _basename_index()
        lines = read_lines(lp_readme)
        mask = fence_mask(lines)
        for i, line in enumerate(lines, start=1):
            if mask[i - 1]:
                continue
            for m in MD_LINK_RE.finditer(line):
                target = m.group(1)
                if SCHEME_RE.match(target) or not target.split("#")[0].endswith(".md"):
                    continue
                if not _resolve(target, lp_readme, basenames):
                    rep.error(f"lesson-plans/README.md:{i}: lesson table link "
                              f"'{target}' does not resolve")
        # warn if a lesson file is never linked from the README
        linked = {m.group(1).split("#")[0]
                  for line in lines for m in MD_LINK_RE.finditer(line)}
        for p in sorted(LESSONS.glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            if p.name not in linked:
                rep.warn(f"lesson-plans/README.md: {p.name} is not linked "
                         "from the lesson table")
    else:
        rep.error("lesson-plans/README.md not found")


# ---------------------------------------------------------------------------
# check 5: SNIPPETS


PY_BLOCK_RE = re.compile(r"^```python[^\n]*\n(.*?)^```\s*$", re.S | re.M)

RUNNER = r'''
import io, json, signal, sys, time, traceback

blocks = json.load(open(sys.argv[1], encoding="utf-8"))
timeout = int(sys.argv[2])
ns = {"__name__": "__main__"}

class Timeout(Exception):
    pass

def alarm(signum, frame):
    raise Timeout()

signal.signal(signal.SIGALRM, alarm)

for blk in blocks:
    idx, src = blk["index"], blk["source"]
    buf = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    t0 = time.monotonic()
    status, detail = "pass", ""
    signal.alarm(timeout)
    try:
        code = compile(src, f"<block {idx}>", "exec")
        exec(code, ns)
    except Timeout:
        status, detail = "fail", f"timed out after {timeout}s"
    except BaseException:
        status = "fail"
        detail = traceback.format_exc(limit=5)
    finally:
        signal.alarm(0)
        sys.stdout, sys.stderr = old_out, old_err
    out = buf.getvalue()
    print("##RESULT## " + json.dumps({
        "index": idx, "status": status, "detail": detail[-2000:],
        "seconds": round(time.monotonic() - t0, 2),
        "output_tail": out[-1500:],
    }), flush=True)
'''


def _block_names(src: str) -> tuple[set[str], set[str], set[str]]:
    """(top-level imported modules, bound names, loaded names) of a block."""
    mods: set[str] = set()
    bound: set[str] = set()
    loaded: set[str] = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return mods, bound, loaded
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mods.add(a.name.split(".")[0])
                bound.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                mods.add(node.module.split(".")[0])
            for a in node.names:
                bound.add(a.asname or a.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                loaded.add(node.id)
            else:
                bound.add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, ast.alias):
            pass
    return mods, bound, loaded


class ModuleProbe:
    """Cached 'is module importable in the venv' checks."""

    def __init__(self) -> None:
        self.cache: dict[str, bool] = {}

    def ok(self, mod: str) -> bool:
        if mod not in self.cache:
            r = subprocess.run(
                [str(VENV_PY), "-c",
                 f"import importlib.util,sys;"
                 f"sys.exit(0 if importlib.util.find_spec({mod!r}) else 1)"],
                capture_output=True, timeout=60)
            self.cache[mod] = r.returncode == 0
        return self.cache[mod]


BUILTIN_NAMES = set(dir(builtins)) | {"__name__", "__file__", "__doc__"}


def check_snippets(rep: Report, timeout: int,
                   extra_skips: dict[str, set[int]], verbose: bool) -> None:
    if not VENV_PY.is_file():
        rep.error(f"snippets: venv python not found at {rel(VENV_PY)} "
                  "(create the venv or use --no-snippets)")
        return
    probe = ModuleProbe()
    for fname in SNIPPET_FILES:
        path = LESSONS / fname
        if not path.is_file():
            rep.warn(f"snippets: {rel(path)} not found; skipping")
            continue
        blocks = PY_BLOCK_RE.findall(path.read_text(encoding="utf-8"))
        if not blocks:
            rep.warn(f"snippets: no ```python blocks in {fname}")
            continue

        to_run: list[dict] = []
        results: dict[int, tuple[str, str]] = {}   # idx -> (status, note)
        available: set[str] = set(BUILTIN_NAMES)   # names defined so far
        skipped_names: set[str] = set()            # names only skipped blocks define

        for idx, src in enumerate(blocks):
            mods, bound, loaded = _block_names(src)
            reason = None
            first = src.lstrip().splitlines()[0] if src.strip() else ""
            mm = SKIP_MARKER_RE.match(first)
            if mm:
                reason = mm.group(1).strip() or "explicit '# verify: skip' marker"
            if reason is None and idx in extra_skips.get(fname, set()):
                reason = "skipped via --skip"
            if reason is None and idx in MANUAL_SKIPS.get(fname, {}):
                reason = MANUAL_SKIPS[fname][idx]
            if reason is None:
                bad = sorted(mods & SKIP_MODULES)
                if bad:
                    reason = f"imports {', '.join(bad)} (needs external service/package)"
            if reason is None:
                for pat, req in FEATURE_REQUIREMENTS:
                    if pat.search(src) and not probe.ok(req):
                        reason = f"requires {req} (not installed in venv)"
                        break
            if reason is None:
                missing = [m for m in sorted(mods) if not probe.ok(m)]
                if missing:
                    reason = (f"imports unavailable module(s): "
                              f"{', '.join(missing)}")
            if reason is None:
                free = loaded - bound - available
                from_skipped = sorted(free & skipped_names)
                undefined = sorted(free - skipped_names)
                if from_skipped:
                    reason = ("uses name(s) defined only in skipped "
                              f"block(s): {', '.join(from_skipped)}")
                elif undefined:
                    reason = ("uses name(s) not defined by any prior "
                              f"block: {', '.join(undefined)}")

            if reason is not None:
                results[idx] = ("skip", reason)
                skipped_names |= (bound - available)
            else:
                to_run.append({"index": idx, "source": src})
                available |= bound

        if to_run:
            with tempfile.TemporaryDirectory(prefix="verify_docs_") as tmp:
                tmpdir = Path(tmp)
                (tmpdir / "blocks.json").write_text(
                    json.dumps(to_run), encoding="utf-8")
                (tmpdir / "runner.py").write_text(RUNNER, encoding="utf-8")
                env = dict(os.environ, MPLBACKEND="Agg",
                           PYTHONUNBUFFERED="1")
                try:
                    proc = subprocess.run(
                        [str(VENV_PY), "runner.py", "blocks.json",
                         str(timeout)],
                        cwd=tmpdir, env=env, capture_output=True, text=True,
                        timeout=timeout * len(to_run) + 120)
                except subprocess.TimeoutExpired:
                    rep.error(f"snippets: {fname}: runner exceeded overall "
                              "timeout")
                    proc = None
                if proc is not None:
                    for line in proc.stdout.splitlines():
                        if line.startswith("##RESULT## "):
                            r = json.loads(line[len("##RESULT## "):])
                            note = r["detail"] or f"{r['seconds']}s"
                            results[r["index"]] = (r["status"], note)
                    if proc.returncode != 0 and not any(
                            s == "fail" for s, _ in results.values()):
                        rep.error(f"snippets: {fname}: runner crashed: "
                                  f"{proc.stderr[-500:]}")
                    for blk in to_run:
                        if blk["index"] not in results:
                            results[blk["index"]] = (
                                "fail", "no result (runner died earlier)")

        n_pass = sum(1 for s, _ in results.values() if s == "pass")
        n_skip = sum(1 for s, _ in results.values() if s == "skip")
        n_fail = sum(1 for s, _ in results.values() if s == "fail")
        rep.info(f"snippets: {fname}: {len(blocks)} blocks — "
                 f"{n_pass} pass, {n_skip} skip, {n_fail} fail")
        for idx in sorted(results):
            status, note = results[idx]
            if status == "fail":
                rep.error(f"snippets: {fname} block {idx} FAILED:\n"
                          + "\n".join("    " + l
                                      for l in note.strip().splitlines()))
            elif status == "skip":
                rep.info(f"snippets:   {fname} block {idx}: skip — {note}")
            elif verbose:
                rep.info(f"snippets:   {fname} block {idx}: pass ({note})")


# ---------------------------------------------------------------------------
# main


def parse_skips(specs: list[str]) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    for spec in specs:
        try:
            fname, idxs = spec.split(":", 1)
            out.setdefault(fname, set()).update(
                int(x) for x in idxs.split(",") if x.strip())
        except ValueError:
            raise SystemExit(f"bad --skip spec: {spec!r} "
                             "(expected file.md:0,2,5)")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Regression checks for the study corpus.")
    ap.add_argument("--structure", action="store_true",
                    help="chapter file structure check")
    ap.add_argument("--lint", action="store_true",
                    help="AI-leftover / marker lint")
    ap.add_argument("--crossrefs", action="store_true",
                    help="file-reference resolution check")
    ap.add_argument("--readme", action="store_true",
                    help="README file-map sync check")
    ap.add_argument("--snippets", action="store_true",
                    help="execute lesson-plan python blocks (needs .venv)")
    ap.add_argument("--all", action="store_true",
                    help="run every check (default when no check flag given)")
    ap.add_argument("--no-snippets", action="store_true",
                    help="with --all/default: skip the snippet execution")
    ap.add_argument("--timeout", type=int, default=120, metavar="SEC",
                    help="per-snippet-block timeout (default 120)")
    ap.add_argument("--skip", action="append", default=[], metavar="F.md:I,J",
                    help="extra snippet blocks to skip, e.g. 06-qiskit.md:3")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="also report passing snippet blocks")
    args = ap.parse_args(argv)

    explicit = args.structure or args.lint or args.crossrefs \
        or args.readme or args.snippets
    run_all = args.all or not explicit
    sel = {
        "structure": run_all or args.structure,
        "lint": run_all or args.lint,
        "crossrefs": run_all or args.crossrefs,
        "readme": run_all or args.readme,
        "snippets": (run_all and not args.no_snippets) or args.snippets,
    }
    if args.no_snippets:
        sel["snippets"] = False

    rep = Report()
    if sel["structure"]:
        check_structure(rep)
    if sel["lint"]:
        check_lint(rep)
    if sel["crossrefs"]:
        check_crossrefs(rep)
    if sel["readme"]:
        check_readme(rep)
    if sel["snippets"]:
        check_snippets(rep, args.timeout, parse_skips(args.skip),
                       args.verbose)

    ran = ", ".join(k for k, v in sel.items() if v)
    print(f"verify_docs: ran checks: {ran}")
    for msg in rep.infos:
        print(f"  [info] {msg}")
    for msg in rep.warnings:
        print(f"  [warn] {msg}")
    for msg in rep.errors:
        print(f"  [FAIL] {msg}")
    n_files = len(corpus_files())
    print(f"verify_docs: {n_files} markdown files scanned — "
          f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    if rep.errors:
        print("verify_docs: FAILED")
        return 1
    print("verify_docs: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
