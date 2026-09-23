#!/usr/bin/env python3
"""Generate cloze (fill-in-the-blank) flashcards from the docs corpus.

Every chapter under ``docs/`` ends with a **Key Formulas** section: a list of
named identities that the chapter has already derived and verified.  This tool
turns each of those into a retrieval-practice card by blanking the right-hand
side of the identity, and writes the result as ordinary one-card-per-file
modules under ``flashcard-drill/cards/cloze/`` (category ``Cloze``).

Design: conservative by construction
------------------------------------
A bad cloze is worse than no cloze, so every stage *rejects* rather than
guesses:

* **Parsing** understands exactly three shapes of Key-Formulas entry — a bold
  label followed by a ``$$…$$`` display-math block, a bold label followed by
  inline ``` `code` ``` spans, and a bullet of either kind.  Anything else is
  skipped.
* **LaTeX → Unicode** is a whitelist.  Every command the corpus uses is mapped
  explicitly; an unknown command, a matrix/cases environment, an alignment
  ``&`` or a stray backslash raises and the whole formula is dropped.  A
  garbled card can therefore never be emitted — only a missing one.
* **Cloze selection** only fires on a clause with a single kind of top-level
  relation.  The prompt keeps the left-hand side and the relation; the answer
  is everything after it.  Chains of ``=`` are allowed (the whole chain is the
  answer); a clause mixing ``=`` with ``≤`` is dropped, as is anything with an
  ellipsis, prose on the left-hand side, or an answer long enough to be an
  essay.
* **Dedupe** removes cards that ask the same question twice — identical
  left-hand side and answer, or the same left-hand side under the same label
  keywords in two chapters.

Idempotence
-----------
A card's id is ``cz_<chapter>_<file>_<label slug>_<hash>`` where the hash is
over *source path + label + left-hand side*.  Re-running writes a file only
when its bytes change and deletes generated files that no longer correspond to
a formula, so ``--write`` twice in a row leaves the tree untouched.

Usage
-----
    python3 tools/gen_cloze.py                    # same as --dry-run
    python3 tools/gen_cloze.py --dry-run          # report, write nothing
    python3 tools/gen_cloze.py --write            # (re)generate the cards
    python3 tools/gen_cloze.py --clean            # remove every generated card
    python3 tools/gen_cloze.py --write --limit 50 # cap the card count
    python3 tools/gen_cloze.py --sample 20 --seed 7   # print a review sample

``--limit`` keeps the first N cards in corpus order (chapter, then position in
the chapter), so the cap is deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CARD_DIR = REPO_ROOT / "flashcard-drill" / "cards" / "cloze"
CATEGORY = "Cloze"
ID_PREFIX = "cz_"

# Sentinels used while converting; none of them can occur in the corpus.
LB, RB = "\x01", "\x06"          # literal (escaped) braces  \{  \}
TXT_O, TXT_C = "\x02", "\x03"    # \text{...} boundaries
QUAD = "\x04"                    # \quad / \qquad — a clause separator
COMMA = "\x05"                   # a comma protected inside a bra/ket

BLANK = "______"


class ConvError(Exception):
    """The formula uses something the whitelist does not cover."""


# --------------------------------------------------------------------------
# LaTeX -> Unicode  (whitelist; anything unknown raises ConvError)
# --------------------------------------------------------------------------

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "Gamma": "Γ", "delta": "δ",
    "Delta": "Δ", "epsilon": "ϵ", "varepsilon": "ε", "zeta": "ζ", "eta": "η",
    "theta": "θ", "Theta": "Θ", "vartheta": "ϑ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "Lambda": "Λ", "mu": "μ", "nu": "ν", "xi": "ξ", "Xi": "Ξ",
    "pi": "π", "Pi": "Π", "rho": "ρ", "varrho": "ϱ", "sigma": "σ",
    "Sigma": "Σ", "tau": "τ", "upsilon": "υ", "phi": "ϕ", "varphi": "φ",
    "Phi": "Φ", "chi": "χ", "psi": "ψ", "Psi": "Ψ", "omega": "ω",
    "Omega": "Ω",
}

SYMBOLS = {
    "langle": "⟨", "rangle": "⟩", "otimes": "⊗", "oplus": "⊕",
    "bigotimes": "⨂", "bigoplus": "⨁", "dagger": "†", "cdot": "·",
    "cdots": "⋯", "ldots": "…", "dots": "…", "vdots": "⋮",
    "pm": "±", "mp": "∓", "times": "×", "div": "÷",
    "leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "neq": "≠", "ne": "≠",
    "approx": "≈", "equiv": "≡", "sim": "∼", "simeq": "≃", "cong": "≅",
    "propto": "∝", "ll": "≪", "gg": "≫",
    "in": "∈", "notin": "∉", "ni": "∋", "subseteq": "⊆", "subset": "⊂",
    "supseteq": "⊇", "supset": "⊃", "cap": "∩", "cup": "∪",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "mapsto": "↦",
    "leftrightarrow": "↔", "Leftrightarrow": "⟺", "iff": "⟺",
    "Rightarrow": "⇒", "implies": "⟹", "Leftarrow": "⇐", "longrightarrow": "⟶",
    "hbar": "ℏ", "infty": "∞", "partial": "∂", "nabla": "∇",
    "forall": "∀", "exists": "∃", "neg": "¬", "wedge": "∧", "vee": "∨",
    "lfloor": "⌊", "rfloor": "⌋", "lceil": "⌈", "rceil": "⌉",
    "sum": "Σ", "prod": "∏", "int": "∫", "oint": "∮",
    "circ": "∘", "star": "⋆", "ast": "*", "bullet": "•",
    "ell": "ℓ", "emptyset": "∅", "perp": "⊥", "angle": "∠",
    "prime": "′", "degree": "°", "colon": ":",
}

# Bare function/operator names: emitted verbatim, no following space eaten.
FUNCS = {
    "log", "ln", "lg", "exp", "sin", "cos", "tan", "cot", "sec", "csc",
    "sinh", "cosh", "tanh", "arcsin", "arccos", "arctan", "det", "dim",
    "gcd", "lcm", "max", "min", "sup", "inf", "lim", "deg", "ker", "arg",
    "Tr", "tr", "Re", "Im", "Pr", "mod",
}

BLACKBOARD = {"C": "ℂ", "R": "ℝ", "Z": "ℤ", "N": "ℕ", "Q": "ℚ",
              "F": "𝔽", "E": "𝔼", "P": "ℙ", "H": "ℍ"}

ACCENTS = {"hat": "̂", "tilde": "̃", "bar": "̄",
           "overline": "̄", "vec": "⃗", "dot": "̇",
           "check": "̌", "acute": "́", "grave": "̀"}

# Styling commands whose argument is kept and whose styling is dropped.
PLAIN_STYLE = {"mathcal", "mathscr", "mathbf", "mathsf", "mathfrak",
               "boldsymbol", "bm", "mathtt", "mathnormal", "operatorname"}

TEXTY = {"text", "textrm", "textit", "textbf", "mathrm", "mbox", "textsf"}

SIZERS = {"left", "right", "big", "Big", "bigg", "Bigg",
          "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "Biggl", "Biggr"}

NOT_MAP = {"subseteq": "⊄", "subset": "⊄", "equiv": "≢", "in": "∉",
           "=": "≠", "leq": "≰", "geq": "≱"}

_CMD_RE = re.compile(r"\\([a-zA-Z]+)")

# Only these behave like letters, so only these swallow the space LaTeX uses as a
# command terminator (``\pi i`` is "πi", but ``\theta \approx`` stays "θ ≈").
LETTERLIKE = set(GREEK) | {"hbar", "ell", "infty", "partial", "nabla"}


def _read_group(s: str, i: int) -> tuple[str, int]:
    """``s[i]`` is ``{``; return (contents, index just past the matching ``}``)."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\" and j + 1 < len(s):
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ConvError("unbalanced brace")


def _read_arg(s: str, i: int) -> tuple[str, int]:
    """Read one LaTeX argument: a ``{group}``, a ``\\command`` or one char."""
    while i < len(s) and s[i] in " \t":
        i += 1
    if i >= len(s):
        raise ConvError("missing argument")
    if s[i] == "{":
        return _read_group(s, i)
    if s[i] == "\\":
        m = _CMD_RE.match(s, i)
        if m:
            return m.group(0), m.end()
        return s[i:i + 2], i + 2
    return s[i], i + 1


def _strip_marks(s: str) -> str:
    """Base characters only — ``Ĥ`` (precomposed or combining) becomes ``H``."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))


_BASE_ATOM = re.compile(r"^[A-Za-z0-9Ͱ-Ͽℏℓ∞]$")
_SIMPLE_DEN = re.compile(
    r"^(?:√?[A-Za-z0-9Ͱ-Ͽℏℓ](?:[_^]\{?[A-Za-z0-9+\-,]+\}?)?"
    r"|[0-9]+|[A-Za-z]{1,3}|√\(.*\))$"
)


def _top_level(s: str):
    """Yield (index, char) for every character at bracket depth zero."""
    depth = 0
    for idx, ch in enumerate(s):
        if ch in "([" or ch == LB:
            depth += 1
            continue
        if ch in ")]" or ch == RB:
            depth = max(0, depth - 1)
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth = max(0, depth - 1)
            continue
        if depth == 0:
            yield idx, ch


def _needs_parens(s: str) -> bool:
    for _, ch in _top_level(s):
        if ch in "+- =<>≤≥≈∓±":
            return True
    return False


def _sqrt_atom(inner: str) -> str:
    if _BASE_ATOM.match(_strip_marks(inner)):
        return "√" + inner
    return "√(" + inner + ")"


def _frac(num: str, den: str) -> str:
    n = "(" + num + ")" if _needs_parens(num) else num
    d = den if _SIMPLE_DEN.match(_strip_marks(den)) else "(" + den + ")"
    return n + "/" + d


def convert(src: str) -> str:
    """LaTeX (or already-Unicode text) -> flat Unicode.  Raises ConvError."""
    out: list[str] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "&":
            raise ConvError("alignment tab (matrix/cases environment)")
        if c == "$":
            i += 1
            continue
        if c != "\\":
            out.append(c)
            i += 1
            continue

        m = _CMD_RE.match(src, i)
        if not m:
            nxt = src[i + 1] if i + 1 < n else ""
            if nxt == "{":
                out.append(LB)
            elif nxt == "}":
                out.append(RB)
            elif nxt == "|":
                out.append("‖")
            elif nxt in ",;: ":
                out.append(" ")
            elif nxt == "!":
                pass
            elif nxt in "%_&#$":
                out.append(nxt)
            else:
                raise ConvError(f"unknown escape {nxt!r}")
            i += 2
            continue

        cmd, i = m.group(1), m.end()

        if cmd in ("frac", "tfrac", "dfrac", "nicefrac"):
            a, i = _read_arg(src, i)
            b, i = _read_arg(src, i)
            frac = _frac(convert(a), convert(b))
            tail = "".join(out)
            if any(tail.endswith(f) for f in FUNCS):
                frac = "(" + frac + ")"
            out.append(frac)
        elif cmd == "sqrt":
            a, i = _read_arg(src, i)
            out.append(_sqrt_atom(convert(a)))
        elif cmd in TEXTY:
            a, i = _read_arg(src, i)
            if "\\" in a or "{" in a:
                raise ConvError("markup inside \\text")
            out.append(TXT_O + a.strip() + TXT_C)
        elif cmd == "mathbb":
            a, i = _read_arg(src, i)
            if a not in BLACKBOARD:
                raise ConvError(f"\\mathbb{{{a}}}")
            out.append(BLACKBOARD[a])
        elif cmd in PLAIN_STYLE:
            a, i = _read_arg(src, i)
            out.append(convert(a))
        elif cmd in ACCENTS:
            a, i = _read_arg(src, i)
            base = convert(a)
            if len(_strip_marks(base)) != 1:
                raise ConvError(f"\\{cmd} over {base!r}")
            out.append(base + ACCENTS[cmd])
        elif cmd in SIZERS:
            if cmd == "right" and i < n and src[i] == ".":
                i += 1
        elif cmd == "not":
            m2 = _CMD_RE.match(src, i)
            if m2 and m2.group(1) in NOT_MAP:
                out.append(NOT_MAP[m2.group(1)])
                i = m2.end()
            elif i < n and src[i] in NOT_MAP:
                out.append(NOT_MAP[src[i]])
                i += 1
            else:
                raise ConvError("\\not on an unmapped relation")
        elif cmd == "pmod":
            a, i = _read_arg(src, i)
            out.append(" (mod " + convert(a) + ")")
        elif cmd == "bmod":
            out.append(" mod ")
        elif cmd in ("quad", "qquad"):
            out.append(QUAD)
        elif cmd in GREEK or cmd in SYMBOLS:
            out.append(GREEK[cmd] if cmd in GREEK else SYMBOLS[cmd])
            if cmd in LETTERLIKE and i < n and src[i] == " ":
                j = i + 1
                nxt = src[j:j + 1]
                if nxt.isalnum():
                    i = j
                elif nxt == "\\":
                    m2 = _CMD_RE.match(src, j)
                    if m2 and (m2.group(1) in LETTERLIKE or m2.group(1) in FUNCS):
                        i = j
        elif cmd in FUNCS:
            if out and (out[-1][-1:].isalnum() or out[-1][-1:] in ")]"):
                out.append(" ")
            out.append(cmd)
        else:
            raise ConvError(f"\\{cmd}")

    return "".join(out)


_SUPSUB_SINGLE = re.compile(r"([_^])\{([^{}\x01\x06])\}")


def _drop_grouping_braces(s: str) -> str:
    """Delete LaTeX grouping braces that are not a sub/superscript group.

    Real set braces reach here as :data:`LB` / :data:`RB` sentinels (they are
    written ``\\{ … \\}`` in the corpus), so anything left is pure grouping.
    """
    keep = [True] * len(s)
    stack: list[int] = []
    for idx, ch in enumerate(s):
        if ch == "{":
            stack.append(idx)
        elif ch == "}":
            if not stack:
                raise ConvError("unbalanced brace after conversion")
            open_idx = stack.pop()
            if not (open_idx > 0 and s[open_idx - 1] in "_^"):
                keep[open_idx] = keep[idx] = False
    if stack:
        raise ConvError("unbalanced brace after conversion")
    return "".join(ch for ch, k in zip(s, keep) if k)


_SPACE_BEFORE = re.compile(r"(?<=[A-Za-z0-9)\]⟩|])(?=[Σ∏∫∮⨂⨁])")


def tidy(s: str, latex: bool = True) -> str:
    """Whitespace / bracket cosmetics after conversion.

    ``latex`` is False for a formula that was already written in Unicode inside
    a ``` `code` ``` span.  There every brace is meant literally (``C_n = {U :
    U P U† = P}``), so the LaTeX grouping-brace pass must not touch it.
    """
    if latex:
        s = _drop_grouping_braces(s)
        for _ in range(3):
            s2 = _SUPSUB_SINGLE.sub(r"\1\2", s)
            if s2 == s:
                break
            s = s2
    s = _SPACE_BEFORE.sub(" ", s)
    s = s.replace("^†", "†").replace("^{†}", "†")
    s = re.sub(r"[ \t]+", " ", s)
    s = s.replace("⟨ ", "⟨").replace(" ⟩", "⟩")
    # collapse the padding inside a bra-ket:  ⟨u | v⟩ -> ⟨u|v⟩.  The pattern is
    # deliberately narrow — a loose ⟨…⟩ match would span from one ket's ⟨ to a
    # later ket's ⟩ and eat the operators in between.
    s = re.sub(r"⟨\s*([^⟨⟩|]{1,25}?)\s*\|\s*([^⟨⟩|]{1,25}?)\s*⟩", r"⟨\1|\2⟩", s)
    s = re.sub(r"⟨\s*([^⟨⟩|]{1,25}?)\s*⟩", r"⟨\1⟩", s)
    s = re.sub(r"\|\s+([A-Za-z0-9Ͱ-Ͽ+\-])\s*⟩", r"|\1⟩", s)
    s = s.replace("^{⊗ ", "^{⊗").replace("_{⊗ ", "_{⊗")
    # "X⊗ Y" -> "X⊗Y"; a tight operator stays tight on both sides.
    s = re.sub(r"(?<=\S)([⊗⊕⨂⨁·×]) +", r"\1", s)
    return s.strip()


def to_unicode(src: str, latex: bool = True) -> str:
    """Full pipeline; raises :class:`ConvError` on anything unsupported."""
    s = tidy(convert(src), latex=latex)
    if "\\" in s:
        raise ConvError("backslash survived conversion")
    if latex and ("{" in s or "}" in s):
        # only sub/superscript groups may keep braces
        for mm in re.finditer(r"[{}]", s):
            j = mm.start()
            if s[j] == "{" and j > 0 and s[j - 1] in "_^":
                continue
            if s[j] == "}":
                continue
            raise ConvError("stray brace")
    return s


def render(s: str) -> str:
    """Strip the internal sentinels for display."""
    s = (s.replace(TXT_O, "").replace(TXT_C, "")
          .replace(LB, "{").replace(RB, "}")
          .replace(QUAD, "  ").replace(COMMA, ","))
    return re.sub(r" {3,}", "  ", s).strip()


# --------------------------------------------------------------------------
# Markdown: the Key Formulas section
# --------------------------------------------------------------------------

_HEAD = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_KEYF = re.compile(r"^key formulas\b", re.I)
_RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")

_ENTRY_BOLD = re.compile(r"^\*\*(?P<label>.+?)\*\*(?P<qual>[^:]*?):\s*(?P<rest>.*)$")
_BULLET_BOLD = re.compile(r"^[-*]\s+\*\*(?P<label>.+?)\*\*(?P<qual>[^:]*?):\s*(?P<rest>.*)$")
_BULLET_PLAIN = re.compile(r"^[-*]\s+(?P<label>[A-Z][^:`*]{1,60}?):\s+(?P<rest>\S.*)$")


@dataclass
class Entry:
    label: str
    body: str
    order: int


def chapter_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        m = _HEAD.match(line)
        if m and len(m.group(1)) == 1:
            return m.group(2).strip()
    return fallback


def key_formula_lines(text: str) -> list[str]:
    out: list[str] = []
    level: int | None = None
    for line in text.splitlines():
        m = _HEAD.match(line)
        if m:
            if level is None:
                if _KEYF.match(m.group(2).strip()):
                    level = len(m.group(1))
                continue
            if len(m.group(1)) <= level:
                break
            continue
        if level is None:
            continue
        if _RULE.match(line):
            break
        out.append(line)
    return out


def _clean_label(label: str, qual: str) -> str:
    label = label.replace("`", "").strip()
    qual = qual.replace("`", "").strip()
    if qual and len(qual) <= 40 and qual.startswith("(") and qual.endswith(")"):
        label = f"{label} {qual}"
    return re.sub(r"\s+", " ", label).strip()


# A label that names no concept cannot carry a prompt on its own ("Problem:
# |x⟩ ∝ ______" is unanswerable without the chapter in front of you).
GENERIC_LABELS = {
    "problem", "solution", "notation", "note", "notes", "example", "examples",
    "summary", "result", "results", "setup", "definition", "definitions",
    "overview", "recap", "remark", "remarks", "caveat", "aside", "key",
    "general", "special case", "in general", "idea", "intuition", "warning",
    # too many chapters state "a Hamiltonian" for the bare word to be a prompt
    "hamiltonian",
}


def parse_entries(lines: list[str]) -> list[Entry]:
    entries: list[Entry] = []
    cur: Entry | None = None
    order = 0
    for line in lines:
        if not line.strip():
            cur = None
            continue
        m = _BULLET_BOLD.match(line) or _BULLET_PLAIN.match(line) or _ENTRY_BOLD.match(line)
        if m:
            gd = m.groupdict()
            cur = Entry(_clean_label(gd["label"], gd.get("qual") or ""),
                        gd["rest"], order)
            order += 1
            entries.append(cur)
        elif cur is not None:
            cur.body += "\n" + line.strip()
    return [e for e in entries
            if e.label and e.label.strip(" .:").lower() not in GENERIC_LABELS]


# Prose right after a formula that makes the formula conditional: the condition
# lives outside the code span, so blanking the formula would ask for a coin flip
# ("Syndrome bit: sᵢ = +1 **if** E commutes with gᵢ, -1 if they anticommute").
_CONDITIONAL = re.compile(
    r"^(if|when|whenever|unless|otherwise|provided|only if|depending)\b", re.I)


def blobs_of(body: str) -> tuple[list[tuple[str, str]], bool]:
    """(formula, following prose) for each blob, and whether they are LaTeX.

    ``$$…$$`` display blocks win; failing that, inline `` `code` `` spans, which
    the corpus writes directly in Unicode.
    """
    for pattern, is_latex in ((r"\$\$(.+?)\$\$", True), (r"`([^`]+)`", False)):
        spans = list(re.finditer(pattern, body, re.S))
        if not spans:
            continue
        out: list[tuple[str, str]] = []
        for k, m in enumerate(spans):
            end = spans[k + 1].start() if k + 1 < len(spans) else len(body)
            tail = body[m.end():end].lstrip(" \t\n,;:.")
            # A formula the prose puts in brackets is an aside about the formula
            # before it ("L = √γ σ₋ (`T₁ = 1/γ`)"), not an entry of its own — it
            # would be blanked under the neighbour's label.
            if body[max(0, m.start() - 1):m.start()] == "(" and tail.startswith(")"):
                continue
            out.append((m.group(1).strip(), tail))
        return out, is_latex
    return [], False


# --------------------------------------------------------------------------
# Clause splitting and the cloze gates
# --------------------------------------------------------------------------

RELATIONS = ["⟺", "⟹", "⇒", "⟶", "↔", "↦", "→", "←", "≢", "≡", "≈", "≃", "≅",
             "≰", "≱", "≤", "≥", "≠", "∝", "⊄", "⊆", "⊂", "⊇", "⊃", "∉", "∈",
             "∼", "≪", "≫", "=", "<", ">"]
PIVOTS = {"=", "≈", "≡", "∝", "≤", "≥"}

STOPWORDS = {
    "the", "a", "an", "of", "for", "and", "or", "with", "when", "where",
    "is", "are", "was", "all", "any", "each", "every", "to", "in", "on",
    "by", "iff", "if", "then", "per", "vs", "via", "gives", "give", "has",
    "have", "best", "such", "that", "than", "from", "into", "over", "under",
    "not", "no", "yes", "be", "it", "its", "this", "these", "those", "we",
    "one", "two", "three", "times", "state", "states", "error", "about",
    "between", "using", "after", "before", "most", "least", "both", "up",
    "down", "out", "at", "as", "so", "but", "also", "only", "which", "while",
}

_PROTECT = re.compile(r"(⟨[^⟨⟩]*?⟩|⟨[^⟨⟩|]*?\||\|[^⟨⟩|]*?⟩)")


def _protect_kets(s: str) -> str:
    return _PROTECT.sub(lambda m: m.group(0).replace(",", COMMA), s)


def split_clauses(blob: str) -> list[str]:
    s = _protect_kets(blob)
    pieces, depth, start = [], 0, 0
    for idx, ch in enumerate(s):
        if ch in "([{" or ch == LB:
            depth += 1
        elif ch in ")]}" or ch == RB:
            depth = max(0, depth - 1)
        elif depth == 0 and (ch in ",;" or ch == QUAD):
            pieces.append(s[start:idx])
            start = idx + 1
    pieces.append(s[start:])
    return [p.strip() for p in pieces if p.strip()]


def _top_level_relations(s: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    depth, idx = 0, 0
    while idx < len(s):
        ch = s[idx]
        if ch in "([{" or ch == LB:
            depth += 1
            idx += 1
            continue
        if ch in ")]}" or ch == RB:
            depth = max(0, depth - 1)
            idx += 1
            continue
        if depth == 0:
            for rel in RELATIONS:
                if s.startswith(rel, idx):
                    hits.append((idx, rel))
                    idx += len(rel)
                    break
            else:
                idx += 1
            continue
        idx += 1
    return hits


def _balanced(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{", RB: LB}
    stack: list[str] = []
    for ch in s:
        if ch in "([{" or ch == LB:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def _text_segments(s: str) -> list[str]:
    return re.findall(TXT_O + r"([^" + TXT_C + r"]*)" + TXT_C, s)


def _strip_trailing_note(clause: str) -> tuple[str, str]:
    """Move a trailing ``\\text{…}`` qualifier out of the formula into a note."""
    note_parts: list[str] = []
    s = clause
    while True:
        m = re.search(TXT_O + r"([^" + TXT_C + r"]*)" + TXT_C + r"\s*$", s)
        if not m:
            break
        note_parts.insert(0, m.group(1).strip())
        s = s[:m.start()].rstrip().rstrip(QUAD).rstrip()
    return s.strip(), " ".join(p for p in note_parts if p).strip()


_WORD = re.compile(r"[A-Za-z][A-Za-z\-']*")
_ID_OK = re.compile(r"^[A-Za-z][A-Za-z0-9\-]*$")


def _lhs_ok(lhs: str) -> bool:
    if not (1 <= len(render(lhs)) <= 40):
        return False
    if not _balanced(lhs):
        return False
    for seg in _text_segments(lhs):
        if not _ID_OK.match(seg) or len(seg) > 12:
            return False
    plain = render(lhs)
    if plain.isdigit():
        return False
    if len(plain.split()) > 3:
        return False
    if any(w.lower() in STOPWORDS for w in _WORD.findall(plain)):
        return False
    if "…" in plain or "⋯" in plain or "..." in plain:
        return False
    return any(ch.isalnum() or ch in "ℏℓ∂∇" for ch in plain)


def _rhs_ok(rhs: str) -> bool:
    plain = render(rhs)
    if not (1 <= len(plain) <= 110):
        return False
    if not _balanced(rhs):
        return False
    if "…" in plain or "⋯" in plain or "..." in plain:
        return False
    if "?" in plain:
        return False
    for seg in _text_segments(rhs):
        if len(seg.split()) > 3:
            return False
    return any(ch.isalnum() or ch in "ℏℓ∂∇(|[√∞∅" for ch in plain)


def _bare(s: str) -> str:
    """Strip decoration so ``γ†`` and ``γ`` compare equal."""
    return re.sub(r"[\s†*′^_]", "", _strip_marks(s))


def cloze_from_clause(clause: str) -> tuple[str, str, str, str] | None:
    """(lhs, relation, rhs, note) for a clause that can be blanked safely."""
    body, note = _strip_trailing_note(clause)
    if not body:
        return None
    rels = _top_level_relations(body)
    if not rels:
        return None
    pos, pivot = rels[0]
    if pivot not in PIVOTS:
        return None
    if pivot == "=":
        if any(r != "=" for _, r in rels):
            return None
    elif len(rels) != 1:
        return None
    lhs = body[:pos].strip()
    rhs = body[pos + len(pivot):].strip()
    if not lhs or not rhs:
        return None
    if not _lhs_ok(lhs) or not _rhs_ok(rhs):
        return None
    if render(lhs) == render(rhs):
        return None
    # An answer that is the prompt wearing a decoration ("γ = γ†") tests nothing.
    if _bare(render(lhs)) == _bare(render(rhs)):
        return None
    return lhs, pivot, rhs, note


# --------------------------------------------------------------------------
# Card assembly
# --------------------------------------------------------------------------

MAX_FRONT = 110
MAX_BACK = 300


@dataclass
class Card:
    id: str
    front: str
    back: str
    source: str
    label: str
    lhs: str
    rhs: str


def _chapter_code(rel: Path) -> str:
    parts: list[str] = []
    for chunk in (rel.parent.name, rel.stem):
        m = re.match(r"^(\d+)", chunk)
        parts.append(m.group(1) if m else re.sub(r"[^A-Za-z0-9]+", "", chunk)[:6])
    return "_".join(p for p in parts if p)


def _slug(text: str, limit: int = 28) -> str:
    s = unicodedata.normalize("NFKD", text)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return s[:limit].strip("_") or "x"


def build_card(relpath: str, title: str, entry: Entry, blob: str,
               lhs: str, pivot: str, rhs: str, note: str) -> Card | None:
    front = f"{entry.label}:  {render(lhs)} {pivot} {BLANK}"
    if len(front) > MAX_FRONT:
        return None
    answer = f"{render(lhs)} {pivot} {render(rhs)}"
    if note:
        answer += f"  {note}" if note.startswith("(") else f"  ({note})"
    # Never let the prompt (or the label) contain the answer.  One- and
    # two-character answers are exempt: "Postulate 1 — Normalization" is not a
    # give-away for the answer "1".
    flat_ans = re.sub(r"\s+", "", render(rhs))
    if len(flat_ans) >= 3 and flat_ans in re.sub(r"\s+", "", front):
        return None

    parts = [answer]
    full = render(blob)
    flat = lambda t: re.sub(r"\s+", "", t)
    if full and flat(full) != flat(f"{render(lhs)}{pivot}{render(rhs)}") and len(full) <= 150:
        parts.append(f"Full entry: {full}")
    parts.append(f"Source: {relpath} — {title}")
    back = "  ·  ".join(parts)
    if len(back) > MAX_BACK:
        back = "  ·  ".join([answer, f"Source: {relpath} — {title}"])
    if len(back) > MAX_BACK:
        return None

    digest = hashlib.sha256(
        f"{relpath}\x00{entry.label}\x00{render(lhs)}".encode("utf-8")
    ).hexdigest()[:8]
    cid = f"{ID_PREFIX}{_chapter_code(Path(relpath))}_{_slug(entry.label)}_{digest}"
    if not re.match(r"^[A-Za-z0-9_\-]+$", cid):
        return None
    return Card(id=cid, front=front, back=back, source=relpath,
                label=entry.label, lhs=render(lhs), rhs=render(rhs))


def _label_keywords(label: str) -> frozenset[str]:
    words = {w.lower() for w in _WORD.findall(label)}
    return frozenset(words - STOPWORDS - {"postulate", "general", "projective"})


@dataclass
class Stats:
    chapters: int = 0
    entries: int = 0
    blobs: int = 0
    conv_failed: int = 0
    clauses: int = 0
    rejected: int = 0
    deduped: int = 0


def generate(docs_dir: Path = DOCS_DIR) -> tuple[list[Card], Stats]:
    stats = Stats()
    cards: list[Card] = []
    for md in sorted(docs_dir.rglob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        text = md.read_text(encoding="utf-8")
        lines = key_formula_lines(text)
        if not lines:
            continue
        stats.chapters += 1
        rel = md.relative_to(REPO_ROOT).as_posix()
        title = chapter_title(text, md.stem)
        for entry in parse_entries(lines):
            stats.entries += 1
            blobs, is_latex = blobs_of(entry.body)
            hits: list[tuple[str, tuple[str, str, str, str]]] = []
            for blob, tail in blobs:
                stats.blobs += 1
                if _CONDITIONAL.match(tail):
                    stats.rejected += 1
                    continue
                try:
                    converted = to_unicode(blob, latex=is_latex)
                except ConvError:
                    stats.conv_failed += 1
                    continue
                for clause in split_clauses(converted):
                    stats.clauses += 1
                    hit = cloze_from_clause(clause)
                    if hit is None:
                        stats.rejected += 1
                        continue
                    hits.append((converted, hit))

            # An entry that states two different right-hand sides for the same
            # left-hand side (three jump operators all called ``L``, the
            # bit-flip and phase-flip ``|0_L⟩``) cannot be blanked without
            # making the answer a guess — so it is dropped whole.
            answers: dict[str, set[str]] = {}
            for _, (lhs, _piv, rhs, _n) in hits:
                answers.setdefault(render(lhs), set()).add(render(rhs))

            for converted, hit in hits:
                if len(answers[render(hit[0])]) > 1:
                    stats.rejected += 1
                    continue
                card = build_card(rel, title, entry, converted, *hit)
                if card is None:
                    stats.rejected += 1
                    continue
                cards.append(card)
                break

    kept: list[Card] = []
    seen_pair: set[tuple[str, str]] = set()
    seen_q: set[tuple[str, frozenset[str]]] = set()
    seen_front: set[str] = set()
    seen_id: set[str] = set()
    by_lhs: dict[str, list[str]] = {}

    def flat(t: str) -> str:
        return re.sub(r"\s+", "", t)
    for c in cards:
        key_lhs, key_rhs = flat(c.lhs), flat(c.rhs)
        pair = (key_lhs, key_rhs)
        question = (key_lhs, _label_keywords(c.label))
        if (pair in seen_pair or question in seen_q
                or flat(c.front) in seen_front or c.id in seen_id):
            stats.deduped += 1
            continue
        # Two chapters that state the same identity to different depths (``⟨M⟩ =
        # ⟨ψ|M|ψ⟩`` and ``⟨M⟩ = ⟨ψ|M|ψ⟩ = Σ_m m p(m)``) would become two prompts
        # with the same left-hand side and two different "right" answers.
        me = key_rhs
        prior = by_lhs.setdefault(key_lhs, [])
        if any(me.startswith(o) or o.startswith(me) for o in prior):
            stats.deduped += 1
            continue
        prior.append(me)
        seen_pair.add(pair)
        seen_q.add(question)
        seen_front.add(flat(c.front))
        seen_id.add(c.id)
        kept.append(c)
    return kept, stats


# --------------------------------------------------------------------------
# Writing the card modules
# --------------------------------------------------------------------------

MODULE = '''"""Card: {cid}

Generated by tools/gen_cloze.py from {source} — do not edit by hand.
"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id={cid!r},
    category={category!r},
    front={front!r},
    back={back!r},
)
'''


def module_text(card: Card) -> str:
    return MODULE.format(cid=card.id, source=card.source, category=CATEGORY,
                         front=card.front, back=card.back)


def existing_files(card_dir: Path = CARD_DIR) -> list[Path]:
    if not card_dir.is_dir():
        return []
    return sorted(p for p in card_dir.glob(f"{ID_PREFIX}*.py"))


def write_cards(cards: list[Card], card_dir: Path = CARD_DIR) -> dict[str, list[str]]:
    card_dir.mkdir(parents=True, exist_ok=True)
    init = card_dir / "__init__.py"
    changed = {"created": [], "updated": [], "removed": [], "unchanged": []}
    if not init.exists():
        init.write_text("", encoding="utf-8")
        changed["created"].append(init.name)

    wanted = {f"{c.id}.py": module_text(c) for c in cards}
    for name, body in sorted(wanted.items()):
        path = card_dir / name
        if path.exists():
            if path.read_text(encoding="utf-8") == body:
                changed["unchanged"].append(name)
                continue
            changed["updated"].append(name)
        else:
            changed["created"].append(name)
        path.write_text(body, encoding="utf-8")

    for path in existing_files(card_dir):
        if path.name not in wanted:
            path.unlink()
            changed["removed"].append(path.name)
    return changed


def clean(card_dir: Path = CARD_DIR) -> list[str]:
    """Remove every generated card and the directory itself."""
    removed: list[str] = []
    if not card_dir.is_dir():
        return removed
    for path in existing_files(card_dir):
        path.unlink()
        removed.append(path.name)
    cache = card_dir / "__pycache__"
    if cache.is_dir():
        for p in cache.iterdir():
            if p.is_file():
                p.unlink()
        cache.rmdir()
    init = card_dir / "__init__.py"
    if init.exists() and not any(p.suffix == ".py" and p.name != "__init__.py"
                                 for p in card_dir.iterdir()):
        init.unlink()
        removed.append(init.name)
    if not any(card_dir.iterdir()):
        card_dir.rmdir()
    return removed


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _report(cards: list[Card], stats: Stats) -> None:
    by_chapter: dict[str, int] = {}
    for c in cards:
        by_chapter[c.source] = by_chapter.get(c.source, 0) + 1
    print(f"chapters with a Key Formulas section : {stats.chapters}")
    print(f"entries parsed                       : {stats.entries}")
    print(f"formula blobs                        : {stats.blobs}"
          f"  ({stats.conv_failed} unconvertible, skipped)")
    print(f"clauses examined                     : {stats.clauses}"
          f"  ({stats.rejected} rejected by the gates)")
    print(f"duplicates removed                   : {stats.deduped}")
    print(f"cards                                : {len(cards)}")
    print()
    for src in sorted(by_chapter):
        print(f"  {by_chapter[src]:3d}  {src}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate cloze flashcards from the docs Key Formulas sections.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be written (the default)")
    ap.add_argument("--write", action="store_true", help="write the card files")
    ap.add_argument("--clean", action="store_true",
                    help="remove every generated card, then stop")
    ap.add_argument("--limit", type=int, default=None, metavar="N",
                    help="keep only the first N cards, in corpus order")
    ap.add_argument("--sample", type=int, default=0, metavar="N",
                    help="print N randomly chosen cards for review")
    ap.add_argument("--seed", type=int, default=0, help="seed for --sample")
    args = ap.parse_args(argv)

    if args.clean:
        removed = clean()
        print(f"removed {len(removed)} generated file(s) from {CARD_DIR}")
        for name in removed:
            print(f"  - {name}")
        return 0

    cards, stats = generate()
    if args.limit is not None:
        cards = cards[:max(0, args.limit)]

    _report(cards, stats)

    if args.sample:
        rng = random.Random(args.seed)
        picks = rng.sample(cards, min(args.sample, len(cards)))
        print(f"\n--- random sample of {len(picks)} (seed {args.seed}) ---")
        for i, c in enumerate(picks, 1):
            print(f"\n[{i}] {c.id}")
            print(f"  FRONT: {c.front}")
            print(f"  BACK : {c.back}")

    if args.write:
        changed = write_cards(cards)
        print(f"\nwrote {CARD_DIR}")
        for kind in ("created", "updated", "removed"):
            if changed[kind]:
                print(f"  {kind}: {len(changed[kind])}")
        print(f"  unchanged: {len(changed['unchanged'])}")
    else:
        print("\n(dry run — nothing written; pass --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
