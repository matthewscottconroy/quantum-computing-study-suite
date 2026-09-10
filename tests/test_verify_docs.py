"""Tests for tools/verify_docs.py — corpus regression checker.

Two layers: the static checks against the *real* docs/ + lesson-plans/
(expected clean: 0 errors, warnings allowed), and unit tests of the artifact
regexes / crossref resolver / structure checker on a throwaway corpus tree.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import verify_docs as vd

ROOT = Path(__file__).resolve().parent.parent

STATIC_CHECKS = ["check_structure", "check_lint", "check_crossrefs", "check_readme"]


# ---------------------------------------------------------------------------
# Real corpus
# ---------------------------------------------------------------------------

class TestRealCorpus:
    def test_module_targets_this_repo(self):
        assert vd.ROOT == ROOT
        assert vd.DOCS == ROOT / "docs" and vd.DOCS.is_dir()
        assert vd.LESSONS == ROOT / "lesson-plans" and vd.LESSONS.is_dir()
        chapters = vd.chapter_files()
        assert len(chapters) >= 40
        assert all(p.parent.parent == vd.DOCS and p.name.lower() != "readme.md"
                   for p in chapters)
        corpus = vd.corpus_files()
        assert set(chapters) <= set(corpus)
        assert vd.DOCS / "README.md" in corpus and vd.LESSONS / "README.md" in corpus

    @pytest.mark.parametrize("check", STATIC_CHECKS)
    def test_static_check_reports_no_errors(self, check):
        rep = vd.Report()
        getattr(vd, check)(rep)
        assert rep.errors == [], "\n".join(rep.errors)

    def test_main_static_checks_exit_zero(self, capsys):
        assert vd.main(["--no-snippets"]) == 0
        out = capsys.readouterr().out
        first = out.splitlines()[0]
        assert first == "verify_docs: ran checks: structure, lint, crossrefs, readme"
        assert "verify_docs: OK" in out

    def test_single_check_selection(self, capsys):
        assert vd.main(["--lint"]) == 0
        assert capsys.readouterr().out.splitlines()[0] == "verify_docs: ran checks: lint"

    @pytest.mark.slow
    @pytest.mark.timeout(1800)      # runs every lesson snippet (120 s each max)
    def test_lesson_snippets_execute(self):
        if not vd.VENV_PY.is_file():
            pytest.skip("project venv not present")
        assert vd.main(["--snippets", "--timeout", "120"]) == 0


# ---------------------------------------------------------------------------
# Artifact regexes
# ---------------------------------------------------------------------------

class TestArtifactRegexes:
    @pytest.mark.parametrize("line", [
        "Wait, let me recompute that.", "wait — let me check", "Hmm, that seems off",
        "hmm— no", "Let me recompute the norm", "let me be more careful here",
        "this is getting complicated", "Let me verify: the trace is 1",
    ])
    def test_self_talk_positive(self, line):
        assert vd.SELF_TALK_RE.search(line)

    @pytest.mark.parametrize("line", [
        "We wait for the job to finish.", "The circuit waits for measurement.",
        "Let me verify the claim later.", "Compute the expectation value.",
        "Recompute after each step.", "Hmmm is not a word here",
    ])
    def test_self_talk_negative(self, line):
        assert not vd.SELF_TALK_RE.search(line)

    def test_wait_for_exclusion(self):
        assert vd.WAIT_FOR_RE.search("wait for it")
        assert vd.WAIT_FOR_RE.search("Waiting for the job")
        assert vd.WAIT_FOR_RE.search("waited for results")
        assert not vd.WAIT_FOR_RE.search("Wait, let me")

    @pytest.mark.parametrize("line,hit", [
        ("TODO: tighten bound", True), ("a FIXME here", True), ("(TODO)", True),
        ("TODOS are tracked elsewhere", False), ("autodo", False), ("fixme", False),
    ])
    def test_todo(self, line, hit):
        assert bool(vd.TODO_RE.search(line)) is hit

    @pytest.mark.parametrize("line,hit", [
        ("XXX fix this later", True), ("see XXX note", True),
        ("the XXXX stabilizer", False), ("XXX X stabilizer", False),
        ("`XXX `", False), ("IXXX Z", False), ("XXXI acts", False),
        ("XXX (see)", False), ("ZZ XXX Y", False),
    ])
    def test_xxx_marker_vs_pauli_strings(self, line, hit):
        assert bool(vd.XXX_RE.search(line)) is hit

    @pytest.mark.parametrize("line,hit", [
        ("continues ·... here", True), ("a ... b", False), ("x · y", False),
    ])
    def test_stranded_fragment(self, line, hit):
        assert bool(vd.STRANDED_RE.search(line)) is hit

    def test_exercise_item_regex(self):
        for s in ("**Exercise 1**: compute", "**Exercise 12.** show",
                  "**Exercise 3** do", "**4.** prove", "**5:** show"):
            assert vd.EXERCISE_ITEM_RE.match(s), s
        for s in ("Exercise 1: compute", "**Solution**", "1. plain list",
                  "**Exercises**", "  **Exercise 1**", "**Exercise** one"):
            assert not vd.EXERCISE_ITEM_RE.match(s), s

    def test_fence_mask(self):
        lines = ["# T", "```python", "x = 1", "```", "after",
                 "~~~", "in tilde", "~~~", "end"]
        assert vd.fence_mask(lines) == [False, True, True, True, False,
                                        True, True, True, False]
        assert vd.fence_mask([]) == []
        assert vd.fence_mask(["```", "never closed"]) == [True, True]

    def test_link_and_backtick_regexes(self):
        found = vd.MD_LINK_RE.findall(
            "see [A](../a.md#s1) and [B](https://x.y/z.md) and [C](#anchor)")
        assert found == ["../a.md#s1", "https://x.y/z.md", "#anchor"]
        assert vd.BACKTICK_MD_RE.findall(
            "read `docs/01_x/02_y.md` not `foo.py` nor `../rel.md`") == ["docs/01_x/02_y.md"]
        assert vd.SCHEME_RE.match("https://example.com")
        assert vd.SCHEME_RE.match("mailto:x@y.z")
        assert not vd.SCHEME_RE.match("docs/a.md")

    def test_skip_marker_regex(self):
        m = vd.SKIP_MARKER_RE.match("# verify: skip — needs hardware")
        assert m and m.group(1) == "needs hardware"
        assert vd.SKIP_MARKER_RE.match("# verify: skip").group(1) == ""
        assert not vd.SKIP_MARKER_RE.match("# verify skip")


# ---------------------------------------------------------------------------
# Throwaway corpus tree
# ---------------------------------------------------------------------------

GOOD_CHAPTER = textwrap.dedent("""\
    # Title

    ## Key Formulas

    - `<0|1> = 0`

    ## Worked Example

    Text.

    ## Summary

    Text.

    ## Exercises

    **Exercise 1**: Compute.

    <details><summary>Solution</summary>

    0

    </details>

    **2.** Prove.

    <details>
    <summary>Solution</summary>
    Done.
    </details>

    ## Further Reading

    - Nielsen & Chuang.
    """)


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    lessons = tmp_path / "lesson-plans"
    (docs / "ch1").mkdir(parents=True)
    (docs / "ch2").mkdir()
    lessons.mkdir()
    (docs / "ch1" / "a.md").write_text(GOOD_CHAPTER)
    (docs / "ch2" / "b.md").write_text(GOOD_CHAPTER)
    (lessons / "l1.md").write_text("# L1\n")
    (docs / "README.md").write_text("# Docs\n")
    (lessons / "README.md").write_text("# Lessons\n\n[L1](l1.md)\n")
    monkeypatch.setattr(vd, "ROOT", tmp_path)
    monkeypatch.setattr(vd, "DOCS", docs)
    monkeypatch.setattr(vd, "LESSONS", lessons)
    return tmp_path


def run_check(name: str) -> vd.Report:
    rep = vd.Report()
    getattr(vd, name)(rep)
    return rep


class TestCrossrefResolver:
    def test_resolve_candidates(self, corpus):
        names = vd._basename_index()
        assert names == {"a.md", "b.md", "l1.md", "README.md"}
        src = corpus / "docs" / "ch1" / "a.md"
        assert vd._resolve("a.md", src, names)                # sibling
        assert vd._resolve("../ch2/b.md", src, names)         # relative
        assert vd._resolve("docs/ch2/b.md", src, names)       # repo-relative
        assert vd._resolve("ch2/b.md", src, names)            # docs-relative
        assert vd._resolve("l1.md", src, names)               # lesson-plans / basename
        assert vd._resolve("b.md#section", src, names)        # anchor stripped
        assert vd._resolve("#only-anchor", src, names)
        assert vd._resolve("ch2/", src, names)                # directory link
        assert not vd._resolve("missing.md", src, names)
        assert not vd._resolve("ch9/b.md", src, names)
        assert not vd._resolve("../../outside.md", src, names)

    def test_check_crossrefs_flags_only_broken_refs(self, corpus):
        (corpus / "docs" / "ch1" / "a.md").write_text(textwrap.dedent("""\
            # A
            Good: [b](../ch2/b.md), [l](../../lesson-plans/l1.md#top),
            [web](https://example.com/x.md), [anchor](#here), [code](script.py),
            [dir](../ch2/), `docs/ch2/b.md`, `b.md`, [img](pic.png).
            Bad: [gone](../ch2/gone.md) and `docs/ch2/nope.md`.
            ```
            [ignored](inside/fence.md) `fence/only.md`
            ```
            """))
        rep = run_check("check_crossrefs")
        assert len(rep.errors) == 2, rep.errors
        assert any("gone.md" in e and "docs/ch1/a.md:5" in e for e in rep.errors)
        assert any("nope.md" in e for e in rep.errors)
        assert not any("fence" in e for e in rep.errors)
        assert rep.warnings == []

    def test_clean_tree_has_no_crossref_errors(self, corpus):
        assert run_check("check_crossrefs").errors == []


class TestStructureCheck:
    def _errors(self, corpus, text):
        (corpus / "docs" / "ch1" / "a.md").write_text(text)
        return [e for e in run_check("check_structure").errors if "ch1/a.md" in e]

    def test_good_chapter_passes(self, corpus):
        assert self._errors(corpus, GOOD_CHAPTER) == []

    def test_missing_required_sections(self, corpus):
        errs = self._errors(corpus, GOOD_CHAPTER.replace("## Further Reading", "## Reading"))
        assert any("Further Reading" in e for e in errs)
        errs = self._errors(corpus, GOOD_CHAPTER.replace("## Exercises", "## Problems"))
        assert any("Exercises" in e for e in errs)

    def test_heading_inside_code_fence_does_not_count(self, corpus):
        text = GOOD_CHAPTER.replace("## Exercises", "## Problems")
        text = text.replace("## Further Reading", "```\n## Exercises\n```\n\n## Further Reading")
        assert any("Exercises" in e for e in self._errors(corpus, text))

    def test_unbalanced_details(self, corpus):
        text = GOOD_CHAPTER.replace("</details>\n\n**2.**", "\n**2.**", 1)
        assert any("unbalanced <details>" in e for e in self._errors(corpus, text))

    def test_solution_summary_required(self, corpus):
        text = GOOD_CHAPTER.replace("<summary>Solution</summary>", "<summary>Answer</summary>", 1)
        assert any("lacks" in e for e in self._errors(corpus, text))

    def test_more_exercises_than_solution_blocks(self, corpus):
        text = GOOD_CHAPTER.replace("## Further Reading", "**3.** Extra.\n\n## Further Reading")
        assert any("3 exercise items but only 2" in e for e in self._errors(corpus, text))

    def test_exercises_without_recognizable_items(self, corpus):
        text = GOOD_CHAPTER.replace("**Exercise 1**: Compute.", "1. Compute.")
        text = text.replace("**2.** Prove.", "2. Prove.")
        assert any("no recognizable exercise items" in e for e in self._errors(corpus, text))

    def test_empty_section(self, corpus):
        text = GOOD_CHAPTER.replace("## Summary\n\nText.\n", "## Summary\n")
        errs = self._errors(corpus, text)
        assert any("empty section" in e and "Summary" in e for e in errs), errs

    def test_trailing_whitespace_line_is_truncation(self, corpus):
        assert any("truncation" in e for e in self._errors(corpus, GOOD_CHAPTER + "   \n"))
        assert any("file is empty" in e for e in self._errors(corpus, "\n\n"))

    def test_chapter_readme_is_not_a_chapter(self, corpus):
        (corpus / "docs" / "ch1" / "README.md").write_text("# index only\n")
        assert run_check("check_structure").errors == []


class TestLintAndReadmeChecks:
    def test_lint_on_temp_corpus(self, corpus):
        (corpus / "docs" / "ch1" / "a.md").write_text(
            "Wait, let me recompute.\n"                       # 1: self-talk
            "Wait, let the job wait for completion.\n"        # 2: excluded (wait for)
            "TODO later\n"                                    # 3
            "XXX marker\n"                                    # 4
            "the XXXX stabilizer\n"                           # 5: Pauli string, ok
            "fragment ·... here\n"                            # 6
            "clean line\n")
        rep = run_check("check_lint")
        lines = sorted(int(e.split(":")[1]) for e in rep.errors if "ch1/a.md" in e)
        assert lines == [1, 3, 4, 6]
        assert all(e.startswith("docs/ch1/a.md:") for e in rep.errors)

    def test_readme_file_map_sync(self, corpus):
        (corpus / "docs" / "README.md").write_text(textwrap.dedent("""\
            # Docs

            **Files**: `ch1/`

            | File | Topic |
            |---|---|
            | `a.md` | A |
            | `zz.md` | missing |

            **Files**: `ch2/`

            | `b.md` | B |

            **Files**: `ch9/`
            """))
        (corpus / "docs" / "ch2" / "extra.md").write_text(GOOD_CHAPTER)
        (corpus / "lesson-plans" / "README.md").write_text(
            "# Lessons\n\n| [L1](l1.md) | [gone](missing.md) | [web](https://x/y.md) |\n")
        (corpus / "lesson-plans" / "l2.md").write_text("# L2\n")
        rep = run_check("check_readme")
        errors, warnings = "\n".join(rep.errors), "\n".join(rep.warnings)
        assert "zz.md" in errors and "ch9/" in errors and "missing.md" in errors
        assert len(rep.errors) == 3, rep.errors
        assert "extra.md" in warnings and "l2.md" in warnings
        assert "a.md" not in errors and "b.md" not in errors

    def test_readme_missing_is_an_error(self, corpus):
        (corpus / "docs" / "README.md").unlink()
        (corpus / "lesson-plans" / "README.md").unlink()
        rep = run_check("check_readme")
        assert any("docs/README.md not found" in e for e in rep.errors)
        assert any("lesson-plans/README.md not found" in e for e in rep.errors)


# ---------------------------------------------------------------------------
# Snippet-runner helpers (no execution)
# ---------------------------------------------------------------------------

def test_parse_skips():
    assert vd.parse_skips(["06-qiskit.md:1,3", "07-qasm.md:2", "06-qiskit.md:5,"]) == {
        "06-qiskit.md": {1, 3, 5}, "07-qasm.md": {2}}
    assert vd.parse_skips([]) == {}
    with pytest.raises(SystemExit):
        vd.parse_skips(["nocolon"])
    with pytest.raises(SystemExit):
        vd.parse_skips(["a.md:x"])


def test_block_names():
    src = ("import numpy as np\nfrom qiskit import QuantumCircuit\n"
           "qc = QuantumCircuit(2)\nprint(qc, undefined_name)\n"
           "def f(a):\n    return a\n")
    mods, bound, loaded = vd._block_names(src)
    assert mods == {"numpy", "qiskit"}
    assert {"np", "QuantumCircuit", "qc", "f", "a"} <= bound
    assert {"QuantumCircuit", "print", "undefined_name"} <= loaded
    assert vd._block_names("def (broken") == (set(), set(), set())


def test_python_block_regex():
    text = "intro\n```python\nx = 1\n```\n```bash\nls\n```\n```python title\ny = 2\n```\n"
    assert vd.PY_BLOCK_RE.findall(text) == ["x = 1\n", "y = 2\n"]
    assert vd.SNIPPET_FILES and all(f.endswith(".md") for f in vd.SNIPPET_FILES)
