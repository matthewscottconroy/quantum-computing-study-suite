"""``common.errata`` — prefilled GitHub issue URLs.  Pure, offline.

The URL is only useful if it lands in the right *form fields*, so these tests
check the field ids against the repository's real issue template rather than
against a copy of them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import errata                           # noqa: E402

TEMPLATE_FILE = ROOT / ".github" / "ISSUE_TEMPLATE" / "content_error.yml"


def fields(url: str) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


# ---------------------------------------------------------------------------
# Shape
# ---------------------------------------------------------------------------

def test_the_url_points_at_the_repositorys_new_issue_endpoint():
    url = errata.issue_url("exam-sim", "ex_017", "Q?", "wrong")
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"
    assert errata.REPO == "matthewscottconroy/quantum-computing-study-suite"


def test_nothing_is_opened_or_sent():
    """Purity, asserted from the parse tree rather than the prose.

    The module builds a string; opening it is ``common.ui.errata_dialog``'s
    job.  Nothing here may reach the network, the browser or a subprocess, so
    that a report can never stall a drill or leak what the learner typed.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(errata))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "urllib"}, f"unexpected imports: {imported}"

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for forbidden in ("requests", "urlopen", "socket", "webbrowser",
                      "QDesktopServices", "subprocess", "open", "Path"):
        assert forbidden not in names, f"errata.py uses {forbidden}"


def test_the_field_ids_match_the_real_issue_template():
    """A renamed id in the template silently stops prefilling the box."""
    assert TEMPLATE_FILE.is_file()
    text = TEMPLATE_FILE.read_text(encoding="utf-8")
    ids = set(re.findall(r"^\s{4}id:\s*(\S+)\s*$", text, re.M))
    url = errata.issue_url("exam-sim", "ex_017", "Q?", "why",
                           correction="the fix")
    used = set(fields(url)) - {"template", "title"}
    assert used <= ids, f"fields not in the template: {sorted(used - ids)}"
    assert {"file", "quote", "why_wrong", "correction", "severity"} <= used


def test_the_template_name_is_a_real_file():
    assert (ROOT / ".github" / "ISSUE_TEMPLATE" / errata.TEMPLATE).is_file()


def test_the_severity_options_match_the_dropdown():
    text = TEMPLATE_FILE.read_text(encoding="utf-8")
    for label in errata.SEVERITIES.values():
        assert label in text, f"severity option not in the template: {label!r}"


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

def test_every_argument_reaches_the_url():
    url = errata.issue_url("qiskit-dojo", "kata_07",
                           "Build a Bell state with two gates.",
                           "The expected answer uses three gates.",
                           severity="misleading",
                           correction="Accept h+cx as well.")
    f = fields(url)
    assert f["template"] == "content_error.yml"
    assert f["title"] == "[content] qiskit-dojo: kata_07"
    assert "qiskit-dojo/katas/" in f["file"] and "kata_07" in f["file"]
    assert f["quote"] == "Build a Bell state with two gates."
    assert f["why_wrong"] == "The expected answer uses three gates."
    assert f["correction"] == "Accept h+cx as well."
    assert f["severity"] == errata.SEVERITIES["misleading"]


def test_empty_optional_fields_are_left_out():
    f = fields(errata.issue_url("exam-sim", "ex_017"))
    assert "correction" not in f
    assert "quote" not in f and "why_wrong" not in f
    assert f["title"] and f["file"] and f["severity"]


def test_an_unknown_severity_falls_back_to_the_default():
    f = fields(errata.issue_url("exam-sim", "x", severity="catastrophic"))
    assert f["severity"] == errata.SEVERITIES[errata.DEFAULT_SEVERITY]


def test_special_characters_survive_the_round_trip():
    text = "What is ⟨ψ|H|ψ⟩ for |+⟩? a & b = c #hash +plus/slash?query"
    f = fields(errata.issue_url("math-quiz", "m 1", text, "100% wrong"))
    assert f["quote"] == text
    assert f["why_wrong"] == "100% wrong"
    assert " " not in urlparse(errata.issue_url("math-quiz", "m 1", text)).query


def test_a_generated_item_says_so_instead_of_naming_a_file():
    for app in ("math-quiz", "quantum-quiz", "paper-drill"):
        assert "generated" in errata.item_location(app, "id").lower()
    assert errata.item_location("exam-sim", "ex_017") == \
        "exam-sim/bank/ — item id `ex_017`"


def test_an_unknown_app_still_produces_something_usable():
    assert errata.item_location("brand-new-app") == "brand-new-app/"
    assert errata.issue_url("brand-new-app", "x").startswith("https://")


def test_the_title_carries_the_templates_prefix():
    assert errata.issue_title("exam-sim", "ex_017") == "[content] exam-sim: ex_017"
    assert errata.issue_title("exam-sim") == "[content] exam-sim"


# ---------------------------------------------------------------------------
# Size
# ---------------------------------------------------------------------------

def test_a_huge_item_is_truncated_but_the_url_stays_usable():
    url = errata.issue_url("paper-drill", "p1", "q" * 40_000, "w" * 40_000)
    assert len(url) <= errata.MAX_URL
    f = fields(url)
    assert f["title"] and f["severity"], "the structural fields were trimmed"
    assert "truncated" in (f.get("quote", "") + f.get("why_wrong", ""))


def test_a_normal_report_is_not_truncated():
    url = errata.issue_url("exam-sim", "ex_017",
                           "Which primitive returns expectation values?",
                           "Both Estimator and Sampler are defensible here.")
    assert "truncated" not in url
    assert len(url) < 1000


@pytest.mark.parametrize("limit", [400, 800, 2000, 6000])
def test_the_cap_is_respected_at_any_size(limit):
    url = errata.issue_url("exam-sim", "ex_017", "q" * 5000, "w" * 5000,
                           max_url=limit)
    assert len(url) <= limit


# ---------------------------------------------------------------------------
# The plain-body fallback
# ---------------------------------------------------------------------------

def test_without_a_template_a_plain_body_is_built():
    url = errata.issue_url("exam-sim", "ex_017", "Q?", "why", template=None)
    f = fields(url)
    assert "template" not in f
    assert f["labels"] == "content"
    body = f["body"]
    assert "**File**" in body and "ex_017" in body
    assert "```text" in body and "Q?" in body
    assert "why" in body


def test_issue_body_is_usable_on_its_own():
    body = errata.issue_body("qec-trainer", "q1", "the text", "the defect",
                             correction="the fix")
    assert body.startswith("**File**")
    assert "the text" in body and "the defect" in body and "the fix" in body
    assert "reported from qec-trainer" in body.lower()


def test_issue_body_says_so_when_nothing_was_captured():
    body = errata.issue_body("qec-trainer")
    assert "(not captured)" in body and "(not given)" in body


def test_a_custom_repo_is_honoured():
    url = errata.issue_url("exam-sim", "x", repo="someone/else")
    assert urlparse(url).path == "/someone/else/issues/new"
