#!/usr/bin/env python3
"""Turn the flashcard deck into an audio deck you can drill while walking.

The deck lives one-card-per-file under ``flashcard-drill/cards/``.  That is the
single source of truth; this script never copies card text into itself.  It
imports flashcard-drill's own registry (``cards.all_cards``), rewrites each
card's front and back from mathematical notation into *spoken English*, and
synthesises them with whatever offline text-to-speech engine this machine has.

For every card it emits:  front  ->  a silent gap for recall  ->  back.
Default output is one continuous track per category plus a chapter sidecar, so
a phone can skip card-by-card inside the track; ``--per-card`` emits one file
per card instead.  Either way an M3U playlist ties the tracks together.

Usage
-----
    python3 tools/export_audio.py --dry-run --limit 60
    python3 tools/export_audio.py --list-engines
    python3 tools/export_audio.py --category "Pauli Matrices" --pause 5
    python3 tools/export_audio.py --out ~/audio-deck --encode mp3
    python3 tools/export_audio.py --per-card --category Theorems

``--dry-run`` prints the raw card text next to the spoken text and synthesises
nothing.  It is the cheap way to review (and extend) the pronunciation layer.

No network, no API key
----------------------
Every engine below is local.  Nothing in this file opens a socket, and the
tool exits non-zero with an install line rather than reaching for a cloud
voice.  ``--limit``/``--category`` keep a review run small.

Engines
-------
Surveyed in quality order and the first one that is actually installed wins
(``--engine`` overrides, ``--list-engines`` shows the survey):

    piper       neural, by far the most listenable; needs a .onnx voice model
    say         macOS' built-in synthesiser
    pico2wave   SVOX Pico (libttspico-utils) -- small but natural
    espeak-ng   robotic, but universal, fast and rate-controllable
    espeak      the older eSpeak
    flite       CMU Flite
    pyttsx3     Python wrapper; last resort (on Linux it just drives espeak)

If none is installed the tool prints the install lines and exits 3 without
writing anything.

Dependencies
------------
Standard library only.  Nothing here is in requirements.txt or
requirements-dev.txt, and nothing needs to be: six of the seven engines are
system packages rather than pip installs, and the seventh (``pyttsx3``) is
imported lazily, so ``pip install pyttsx3`` is enough if you want it.
``--encode mp3|opus`` shells out to ``ffmpeg`` and is likewise optional --
the default WAV output needs nothing beyond the standard library.
"""
from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import wave
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "flashcard-drill"
CARD_DIR = APP_DIR / "cards"
DEFAULT_OUT = REPO_ROOT / "exports" / "audio"

PLAYLIST_NAME = "quantum-study.m3u"


class AudioError(RuntimeError):
    """Anything that should stop the export with a readable message."""


# ===========================================================================
#  THE PRONUNCIATION LAYER
#
#  Card text is written to be *read*, not heard: "XZ = −iY", "⟨ψ|P_m|ψ⟩",
#  "O(√N)", "[[7,1,3]]".  Fed to a synthesiser raw, that comes out as "ex-zed
#  equals why", "psi pee em psi" or silence.  The tables below rewrite the
#  corpus notation into spoken English before synthesis.
#
#  They are deliberately plain data so they can be extended: add a row, run
#  `--dry-run` over the affected cards, listen to the sentence in your head.
#  Everything the tables do not recognise is reported by `--dry-run` under
#  "unmapped characters", which is the list to work from.
#
#  Passes run in the order of `spoken()` at the bottom of this section.  The
#  order matters and is commented there.
# ===========================================================================

# --- Greek letters ---------------------------------------------------------
# Spelled the way eSpeak/Pico actually say them, not the way they are
# transliterated: "chi" comes out "chee", "xi" is read as a Roman numeral.
GREEK: dict[str, str] = {
    "α": "alpha",   "β": "beta",    "γ": "gamma",   "δ": "delta",
    "ε": "epsilon", "ζ": "zeta",    "η": "eta",     "θ": "theta",
    "ι": "iota",    "κ": "kappa",   "λ": "lambda",  "μ": "mu",
    "ν": "nu",      "ξ": "ksi",     "ο": "omicron", "π": "pi",
    "ρ": "rho",     "σ": "sigma",   "ς": "sigma",   "τ": "tau",
    "υ": "upsilon", "φ": "phi",     "ϕ": "phi",     "χ": "kai",
    "ψ": "psi",     "ω": "omega",
    # Capitals.  Σ, Π, Θ( and Ω( are operators in this corpus and _big_o() and
    # _big_operators() consume them first; the Σ/Π entries here are only a
    # backstop, and Π's is "projector" for the reason given in that pass.
    "Γ": "gamma",   "Δ": "delta",   "Θ": "theta",   "Λ": "lambda",
    "Ξ": "ksi",     "Φ": "phi",     "Ψ": "psi",     "Ω": "omega",
    "Σ": " the sum of ", "Π": " projector ",
}

# --- Operators, relations and the rest of the symbol set -------------------
# One character in, spoken words out.  Spaces are deliberate: these land
# mid-formula.
SYMBOLS: dict[str, str] = {
    # structure
    "⊗": " tensor ",          "†": " dagger ",        "⊕": " xor ",
    "×": " times ",           "∘": " composed with ", "◇": " diamond ",
    # relations
    "=": " equals ",          "≈": " is approximately ",
    "≡": " is equivalent to ", "≠": " is not equal to ",
    "≤": " is at most ",      "≥": " is at least ",
    "≪": " is much less than ", "≫": " is much greater than ",
    "∝": " is proportional to ", "≺": " is majorized by ",
    "⊆": " is contained in ", "⊇": " contains ",
    "⊊": " is strictly contained in ", "⊄": " is not contained in ",
    "∈": " in ",              "∩": " intersect ",     "∪": " union ",
    "<": " is less than ",    ">": " is greater than ",
    "⊂": " is contained in ", "⊃": " contains ",
    "⊥": " perp ",            "±": " plus or minus ", "∓": " minus or plus ",
    "→": " goes to ",         "↔": " maps both ways to ",
    "⇒": " implies ",         "⟹": " implies ",       "↦": " maps to ",
    "∀": " for all ",         "∃": " there exists ",
    # objects
    "ℏ": " h bar ",           "ℂ": " the complex numbers ",
    "ℝ": " the reals ",       "ℤ": " the integers ",
    "ℋ": " Hilbert space ",   "∞": " infinity ",
    "∂": " partial ",         "∇": " grad ",
    "√": " root ",            "…": " and so on ",
    "↑": " up ",              "↓": " down ",
    "½": " one half ",        "¼": " one quarter ",   "¾": " three quarters ",
    "′": "'",                # U+2212/U+2010 are normalised in _strip_editorial
    # accented Latin used in physicists' names (Mølmer, Sørensen, Schrödinger)
    "ø": "o", "Ø": "O", "ö": "o", "ä": "a", "é": "e", "è": "e", "å": "a",
}

# --- Unicode superscripts and subscripts -> their ASCII meaning ------------
SUPERSCRIPT: dict[str, str] = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "ⁿ": "n", "ⁱ": "i", "ᵀ": "T", "ˣ": "x", "ʳ": "r", "ᵏ": "k",
    "ᵐ": "m", "ᵃ": "a", "ᵇ": "b", "ᵈ": "d", "ᵉ": "e", "ᵍ": "g",
    "⁺": "+", "⁻": "-", "⁼": "=",
}
SUBSCRIPT: dict[str, str] = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
    "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "ᵢ": "i", "ⱼ": "j", "ₖ": "k", "ₐ": "a", "ₙ": "n", "ₓ": "x",
    "ₗ": "l", "ₜ": "t", "ₘ": "m", "ₚ": "p", "ₛ": "s", "ₑ": "e",
    "ᵣ": "r", "ᵤ": "u", "ᵥ": "v", "ₕ": "h", "ⱽ": "V",
    "ᵦ": "beta", "ᵧ": "gamma", "ᵨ": "rho", "ᵪ": "kai",
    "₊": "+", "₋": "-", "₌": "=",
}
# Exponents that have an English name of their own.
# Trailing spaces matter: "∂²f" has to become "partial squared f".
EXPONENT_WORDS: dict[str, str] = {
    "2": " squared ",  "3": " cubed ",  "-1": " inverse ",
    "†": " dagger ",   "*": " conjugate ",
    "+": " plus ",     "-": " minus ",  "⊥": " perp ",     # |Φ^+⟩, H^⊥
    "T": " transpose ",                                    # H₁ᵀ, Gᵀ
}

# --- Combining marks: â, x̂, n̄, ρ̃, r⃗ ----------------------------------------
COMBINING: dict[str, str] = {
    "̂": " hat",     # ◌̂  â, x̂, Ĥ, Ĵ, n̂
    "̃": " tilde",   # ◌̃
    "̄": " bar",     # ◌̄  n̄
    "̇": " dot",     # ◌̇
    "⃗": " vector",  # ◌⃗
    # Accents on names (Schrodinger, Cramer, Sorensen) carry no sound.
    "\u0308": "", "\u0301": "", "\u0300": "",
    "\u030a": "", "\u0327": "", "\u0327": "",
}

# Letters that carry a hat as a single code point (operators: â, Ĥ, Ĵ, Ŝ).
PRECOMPOSED: dict[str, str] = {
    "â": "a hat", "Â": "A hat", "ê": "e hat", "î": "i hat", "ô": "o hat",
    "û": "u hat", "Ĥ": "H hat", "Ĵ": "J hat", "Ŝ": "S hat", "Ĉ": "C hat",
    "Ô": "O hat", "Û": "U hat", "Ê": "E hat", "Î": "I hat", "ŷ": "y hat",
}


# --- Multi-character phrases, replaced before anything is tokenised --------
PHRASES: list[tuple[str, str]] = [
    ("e.g.", "for example,"),   ("e.g", "for example,"),
    ("i.e.", "that is,"),       ("i.e", "that is,"),
    ("et al.", "and others"),   ("cf.", "compare"),
    ("h.c.", "Hermitian conjugate"),
    ("w.r.t.", "with respect to"),
    ("#P", "sharp P"),
    (" vs ", " versus "),       (" vs. ", " versus "),
    # NOTE: only literals that cannot occur inside a longer word belong here.
    # "iff" does not: it lives in WORD_PHRASES below, matched whole-word.
    ("Mølmer", "Merlmer"),      # ø -> "er" reads closer than a bare "o"
]

# --- Whole-word phrases (regex, so they cannot fire inside a longer word) --
WORD_PHRASES: list[tuple[str, str]] = [
    (r"\biff\b", "if and only if"),
    (r"\bs\.t\.", "such that"),
    (r"(\d+)!", r"\1 factorial"),
    (r"\.\.\.+", " and so on "),
    (r"=\s*\?", " equals what?"),
    (r"#\s*(?=[A-Za-zα-ω])", "number of "),
]


# --- Words the synthesiser gets wrong --------------------------------------
# Left column is matched whole-word (case-sensitive), right column is what is
# actually spoken.  Two kinds of entry live here:
#   * acronyms eSpeak tries to pronounce as words ("LOCC" -> "lock",
#     "GHZ" -> "gigahertz", "POVM" -> "povvum", "EPR" -> "epper");
#   * ordinary words it mis-stresses ("eigen" -> "eye-jen").
# Acronyms it already spells out correctly (BQP, QFT, CSS, HHL, ...) are
# deliberately absent -- only fix what is broken.
SPOKEN_WORDS: dict[str, str] = {
    # -- acronyms eSpeak reads as a word, but a human spells out --
    "LOCC": "L O C C",   "QEC": "Q E C",    "XEB": "X E B",
    "GHZ": "G H Z",      "MIP": "M I P",    "CU": "C U",
    "EC": "E C",         "IQP": "I Q P",    "NEXP": "N E X P",
    "QBER": "Q B E R",   "ISA": "I S A",    "QIP": "Q I P",
    "UCCSD": "U C C S D", "AKLT": "A K L T", "HOM": "H O M",
    "PEC": "P E C",      "QED": "Q E D",    "TEBD": "T E B D",
    "TFIM": "T F I M",   "EPR": "E P R",    "SU": "S U",
    "SO": "S O",         "POVM": "P O V M", "QAOA": "Q A O A",
    "KAK": "K A K",      "XOR": "ex or",    "xor": "ex or",
    "PSD": "P S D",      "SZS": "S Z S",    "GKSL": "G K S L",
    "QFIM": "Q F I M",   "BBPSSW": "B B P S S W", "DEJMPS": "D E J M P S",
    "MWPM": "M W P M",   "QSVT": "Q S V T", "QSVM": "Q S V M",
    "VQLS": "V Q L S",   "VQPE": "V Q P E", "QSL": "Q S L",
    "BB84": "B B eighty four", "E91": "E ninety one",
    # -- acronyms said as words: keep them as words --
    "NISQ": "nisk",      "QASM": "kazm",    "qasm": "kazm",
    "OPENQASM": "open kazm", "OpenQASM": "open kazm",
    "QRAM": "cue ram",   "CLOPS": "clops",  "SIC": "sick",
    "QITE": "kite",      "OTOC": "oh tock", "PSPACE": "P space",
    "BQPSPACE": "B Q P space",
    # -- gate/register shorthands that appear as Python names --
    "qc": "Q C", "np": "N P", "sv": "S V", "qr": "Q R", "cr": "C R",
    "V1": "V one", "V2": "V two", "v1": "V one", "v2": "V two",
    # -- ordinary English eSpeak mis-stresses --
    "eigenstate": "eye ghen state",     "eigenstates": "eye ghen states",
    "eigenvalue": "eye ghen value",     "eigenvalues": "eye ghen values",
    "eigenvector": "eye ghen vector",   "eigenvectors": "eye ghen vectors",
    "eigenbasis": "eye ghen basis",     "eigenphase": "eye ghen phase",
    "eigenspace": "eye ghen space",     "eigendecomposition": "eye ghen decomposition",
    "qutrit": "cue trit",               "qutrits": "cue trits",
    "qudit": "cue dit",                 "qudits": "cue dits",
    "ansatz": "an satz",                "ansatze": "an satzy",
    # "bra" and "ket" are deliberately absent: eSpeak already says
    # "brah"/"ket" correctly, and respelling them only hurts --dry-run.
    "Ax": "A x",   "Uf": "U f",   "Rx": "R x",   "Ry": "R y",
    "Rz": "R z",   "Rzz": "R z z", "Rxx": "R x x", "Ryy": "R y y",
    "iSWAP": "i swap", "CSWAP": "C swap", "CCX": "C C X",
}

# Runs of gate letters ("XZX", "HZH", "IXZZX", "SX") read as one mangled word.
# Split them into letters -- except for the handful that spell English.
GATE_LETTERS = "IXYZHST"
GATE_RUN_SKIP = {"IT", "IS", "HI", "HIS", "ITS", "SIT", "SITS", "THIS",
                 "HIT", "HITS", "SHY", "SIX", "TIS", "HIST"}

# Short subscripts that are abbreviations, not index letters: "p_th" is
# "p sub th", but "δ_{ij}" is "delta sub i j".
SUB_WORDS = {"min", "max", "th", "eff", "tot", "opt", "out", "in", "int",
             "avg", "ref", "err", "obs", "cl", "qu", "seq", "new", "old", "id",
             "mix", "nuc", "arm", "ops", "sys", "env", "log", "abs", "rel",
             "std", "num", "den", "res", "sim", "sum", "val", "var", "top",
             "mid", "end", "raw", "net", "phi", "psi", "rho", "tau", "eta"}

# Function names that should be read as English rather than spelled.
FUNCTIONS: list[tuple[str, str]] = [
    (r"\bTr\b", "trace of"),        (r"\btr\b", "trace of"),
    (r"\bRe\b", "the real part of"), (r"\bIm\b", "the imaginary part of"),
    (r"\bexp\b", "e to the power of"),
    (r"\bcos\b", "cosine"),         (r"\bsin\b", "sine"),
    (r"\btan\b", "tangent"),        (r"\barctan\b", "arc tangent"),
    (r"\barccos\b", "arc cosine"),  (r"\barcsin\b", "arc sine"),
    (r"\bln\b", "natural log"),     (r"\bdim\b", "dimension"),
    (r"\bmod\b", "modulo"),         (r"\bpoly\b", "polynomial"),
    (r"\barg\b", "argument"),       (r"\bwt\b", "weight"),
    (r"\bdet\b", "determinant"),    (r"\bRes\b", "residue"),
    (r"\bProb\b", "probability of"), (r"\bsgn\b", "sign of"),
]

# Dotted names that are English abbreviations, not Python identifiers.
NOT_IDENTIFIERS = {"e.g", "i.e", "cf", "et.al", "h.c", "w.r.t", "vs"}
# CamelCase that is a proper noun, not an API name: splitting "FeMoco"
# into "Fe Moco" makes it worse, not better.
CAMEL_KEEP = {"FeMoco", "McLachlan"}

# Characters that survive to the synthesiser.  Anything else is a gap in the
# tables above; `--dry-run` reports what it had to drop.
SPEAKABLE = re.compile(r"[A-Za-z0-9 ,.;:?'\-]")
# Grouping marks carry no sound: they are dropped on purpose and must not
# show up in --dry-run's "unmapped characters" list.
IGNORED_CHARS = set("()[]{}|⟨⟩‖!\"`\\<>@$")


# ---------------------------------------------------------------- passes ---

def _strip_editorial(text: str) -> str:
    """Drop the parts of a card that exist for the eye only."""
    # Cloze backs end with "  ·  Source: docs/01_.../02_x.md — Title".  A file
    # path read aloud is pure noise, so the citation goes.
    text = re.sub(r"\s+·\s+Source:.*$", "", text, flags=re.S)
    # "<short answer>  ·  Full entry: <same answer, stated fully>".  Aloud the
    # short form is pure repetition, so keep only the full entry.
    full = re.search(r"·\s+Full entry:\s*(.+)$", text, flags=re.S)
    if full:
        text = full.group(1)
    # "  ·  " (two spaces either side) separates clauses; a bare "·" multiplies.
    text = re.sub(r"\s{2,}·\s{2,}", ". ", text)
    # The cloze blank.
    text = re.sub(r"_{3,}", " blank ", text)
    # U+2212 MINUS and U+2010 HYPHEN have to become ASCII here, not in
    # SYMBOLS: _punctuation()'s minus rules run before the symbol table.
    text = text.replace("\u2212", "-").replace("\u2010", "-")
    # â, Ĥ, Ĵ, Ŝ are single code points, so COMBINING (which matches the
    # decomposed marks the rest of the corpus uses) never sees them.  A blanket
    # NFD would fix that and break ≠, which decomposes to "=" + U+0338 and
    # would then be spoken as "equals" -- so name them one by one.
    for src, dst in PRECOMPOSED.items():
        text = text.replace(src, dst)
    # Quoted single tokens ('h', 'cx') are dict keys, not primes.
    text = re.sub(r"'([A-Za-z_][A-Za-z0-9_]*)'", r"\1", text)
    return text


def _say_identifier(token: str) -> str:
    """``qc.count_ops()`` -> ``Q C dot count ops``; ``SparsePauliOp`` -> words."""
    words: list[str] = []
    for chunk in re.split(r"(\.)", token.replace("()", "")):
        if chunk == ".":
            words.append("dot")
            continue
        for part in chunk.split("_"):
            if not part:
                continue
            # Split CamelCase and letter/digit boundaries: SamplerV2 -> Sampler, V2.
            # [A-Z][0-9]+ first, or "SamplerV2" splits into "V" and "2" and
            # never reaches the SPOKEN_WORDS entry for "V2".
            pieces = r"[A-Z][0-9]+|[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+"
            for piece in re.findall(pieces, part):
                if piece in SPOKEN_WORDS:        # SamplerV2 -> "Sampler V two"
                    words.append(SPOKEN_WORDS[piece])
                    continue
                for atom in re.findall(r"[A-Za-z]+|[0-9]+", piece):
                    words.append(SPOKEN_WORDS.get(atom, atom))
    return " ".join(w for w in words if w)


def _identifiers(text: str) -> str:
    """Rewrite Python/Qiskit names before ``_`` and ``.`` mean something else."""
    dotted = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+(?:\(\))?"
    snake = r"[a-z][a-z0-9]+(?:_[a-z0-9]{2,})+(?:\(\))?"
    camel = r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+"
    call = r"[a-z][a-z0-9_]*\(\)"

    def repl(m: re.Match[str]) -> str:
        tok = m.group(0)
        if tok.rstrip(".").lower() in NOT_IDENTIFIERS or tok in CAMEL_KEEP:
            return tok
        return " " + _say_identifier(tok) + " "

    return re.sub(f"(?:{dotted})|(?:{snake})|(?:{camel})|(?:{call})", repl, text)


def _brakets(text: str) -> str:
    """Dirac notation.  Longest form first, or the short forms eat the pieces."""
    # |⟨a|b⟩|²  ->  the magnitude of ...
    text = re.sub(r"\|(⟨[^⟨⟩\n]*⟩)\|", r" the magnitude of \1 ", text)
    # ⟨a|B|c⟩   ->  bra a, B, ket c      (matrix element / expectation)
    text = re.sub(r"⟨([^⟨⟩|\n]+)\|([^⟨⟩|\n]+)\|([^⟨⟩|\n]+)⟩",
                  r" bra \1, \2, ket \3 ", text)
    # ⟨a|b⟩     ->  the inner product of a with b
    text = re.sub(r"⟨([^⟨⟩|\n]+)\|([^⟨⟩|\n]+)⟩",
                  r" the inner product of \1 with \2 ", text)
    # |a⟩⟨b|    ->  ket a bra b          (outer product / projector)
    text = re.sub(r"\|([^|⟨⟩\n]*)⟩\s*⟨([^|⟨⟩\n]*)\|", r" ket \1 bra \2 ", text)
    # |a⟩ and ⟨a|
    text = re.sub(r"\|([^|⟨⟩\n]*)⟩", r" ket \1 ", text)
    text = re.sub(r"⟨([^|⟨⟩\n]*)\|", r" bra \1 ", text)
    # ⟨A⟩       ->  the expectation of A
    text = re.sub(r"⟨([^⟨⟩\n]*)⟩", r" the expectation of \1 ", text)
    # ‖x‖ and the leftover |x| that is not a ket
    text = re.sub(r"‖([^‖\n]{1,40})‖\s*_?\s*◇", r" the diamond norm of \1 ", text)
    text = re.sub(r"‖([^‖\n]{1,40})‖\s*_?\s*∞", r" the infinity norm of \1 ", text)
    text = re.sub(r"‖([^‖\n]{1,40})‖\s*_?\s*₁", r" the trace norm of \1 ", text)
    text = re.sub(r"‖([^‖\n]{1,40})‖\s*_?\s*₂", r" the 2 norm of \1 ", text)
    text = re.sub(r"‖([^‖\n]{1,40})‖", r" the norm of \1 ", text)
    # An unpaired ‖ is the divider in a relative entropy, D(ρ‖σ).
    text = text.replace("‖", " relative to ")
    text = re.sub(r"\|([^|\n]{1,30})\|", r" the magnitude of \1 ", text)
    return text


def _brackets(text: str) -> str:
    """[[n,k,d]] codes, matrices, commutators, anticommutators, sets."""
    # [[7,1,3]] -> "the 7, 1, 3 code"; keep the commas, they pace it.
    text = re.sub(r"\[\[([^\[\]\n]+)\]\]", r" the \1 code ", text)
    # [[a,b],[c,d]] -> matrix rows
    def matrix(m: re.Match[str]) -> str:
        rows = re.findall(r"\[([^\[\]]*)\]", m.group(1))
        return " the matrix with rows " + "; ".join(r.strip() for r in rows) + ", "
    text = re.sub(r"\[((?:\s*\[[^\[\]]*\]\s*,?)+)\]", matrix, text)
    # [A,B] and {A,B}, innermost first so [A,[A,B]] resolves outwards.
    # Generous, because the outer bracket of [A,[A,[A,B]]] only matches once
    # the inner ones have already grown into "the commutator of A and ...".
    operand = r"[^,\[\]{}\n]{1,72}"
    for _ in range(4):
        before = text
        text = re.sub(r"\[(" + operand + r"),\s*(" + operand + r")\]",
                      r" the commutator of \1 and \2 ", text)
        text = re.sub(r"\{([A-Za-zα-ωΑ-Ω][A-Za-z0-9†⊗]{0,6}),\s*"
                      r"([A-Za-zα-ωΑ-Ω][A-Za-z0-9†⊗]{0,6})\}",
                      r" the anticommutator of \1 and \2 ", text)
        if text == before:
            break
    # Whatever braces are left are sets: {Mᵢ}, {0,1}, {ket 0, ket 1}.  The
    # lookbehind is essential: `Σ_{i=1}`, `δ_{ij}` and `e^{-A}` are scripts,
    # not sets, and _scripts() has not run yet.
    text = re.sub(r"(?<![_^])\{([^{}\n]{0,60})\}", r" the set \1 ", text)
    return text


def _big_o(text: str) -> str:
    text = re.sub(r"\bO\s*\(", " big O of (", text)
    text = re.sub(r"Θ\s*\(", " big theta of (", text)
    text = re.sub(r"Ω\s*\(", " big omega of (", text)
    text = re.sub(r"\bo\s*\(", " little o of (", text)
    return text


def _big_operators(text: str) -> str:
    """Σ, Π, ∫, ∮ with their limits."""
    sub_run = "[" + "".join(SUBSCRIPT) + "]+"
    sup_run = "[" + "".join(SUPERSCRIPT) + "]+"

    def _join(parts: list[str]) -> str:
        # "ₐᵦ" is "a beta", not "abeta": separate as soon as one piece is a word.
        return ("".join(parts) if all(len(p) == 1 for p in parts)
                else " ".join(parts))

    def unsub(s: str) -> str:
        return _join([SUBSCRIPT.get(c, c) for c in s])

    def unsup(s: str) -> str:
        return _join([SUPERSCRIPT.get(c, c) for c in s])

    # Π (U+03A0) is a product only when it carries limits or is followed by a
    # space and a capital ("LF = Π Fᵢ").  Glued to a subscript or a letter it
    # is a projector: Πₐ, ΠEₐ†EᵦΠ.  ∏ (U+220F) is always a product.
    text = re.sub(r"Π\s*_\s*\{", "∏_{", text)
    text = re.sub(r"Π\s+(?=[A-Z])", " the product of ", text)
    text = re.sub(rf"Π\s*({sub_run})",
                  lambda m: f" projector sub {unsub(m.group(1))} ", text)
    text = re.sub(r"Π", " projector ", text)

    def limits(word: str, lo: str, hi: str) -> str:
        return f" the {word} from {lo} to {hi} of "

    def over(word: str, lo: str) -> str:
        return f" the {word} over {lo} of "

    for sign, word in (("Σ", "sum"), ("∏", "product")):
        # Σ_{i=1}^n / Σ_{i=1}^{n}
        text = re.sub(sign + r"\s*_\{([^{}]*)\}\s*\^\s*\{?([^{}\s]+)\}?",
                      rf" the {word} from \1 to \2 of ", text)
        text = re.sub(sign + r"\s*_\{([^{}]*)\}", rf" the {word} over \1 of ", text)
        # Σᵢ₌₀^t  (unicode lower limit, ASCII upper limit)
        def uni_ascii(m: re.Match[str], w: str = word) -> str:
            return limits(w, unsub(m.group(1)), m.group(2))

        def uni_uni(m: re.Match[str], w: str = word) -> str:
            return limits(w, unsub(m.group(1)), unsup(m.group(2)))

        def uni_only(m: re.Match[str], w: str = word) -> str:
            return over(w, unsub(m.group(1)))

        text = re.sub(sign + rf"\s*({sub_run})\s*\^\s*\{{?([^{{}}\s]+)\}}?",
                      uni_ascii, text)
        # Σᵢ₌₁ᵏ  (unicode limits)
        text = re.sub(sign + rf"\s*({sub_run})\s*({sup_run})", uni_uni, text)
        text = re.sub(sign + rf"\s*({sub_run})", uni_only, text)
        text = re.sub(sign + r"\s*_\s*([A-Za-z])", rf" the {word} over \1 of ", text)
        text = re.sub(sign, rf" the {word} of ", text)

    for sign, word in (("∫", "integral"), ("∮", "contour integral")):
        def int_limits(m: re.Match[str], w: str = word) -> str:
            return limits(w, unsub(m.group(1)), m.group(2))

        text = re.sub(sign + rf"\s*({sub_run})\s*\^\s*\{{?([^{{}}\s]+)\}}?",
                      int_limits, text)
        text = re.sub(sign + r"\s*_\s*\{?([^{}\s]+)\}?",
                      rf" the {word} over \1 of ", text)
        text = re.sub(sign, rf" the {word} of ", text)

    text = re.sub(r"⌈([^⌈⌉\n]{1,30})⌉", r" the ceiling of \1 ", text)
    text = re.sub(r"⌊([^⌊⌋\n]{1,30})⌋", r" the floor of \1 ", text)
    return text


def _scripts(text: str) -> str:
    """Superscripts and subscripts, unicode and ASCII."""
    sub_run = "[" + "".join(SUBSCRIPT) + "]+"
    sup_run = "[" + "".join(SUPERSCRIPT) + "]+"

    def sup_words(body: str) -> str:
        body = body.strip()
        if body in EXPONENT_WORDS:
            return EXPONENT_WORDS[body]
        if body.startswith("⊗"):
            return " to the tensor power " + body[1:]
        return " to the power of " + body + " "

    def sub_words(body: str) -> str:
        body = body.strip()
        if body in ("+", "-"):
            return " plus" if body == "+" else " minus"
        if body.isdigit():                      # Z₁Z₂ -> "Z 1 Z 2"
            return " " + body + " "
        if body.isalpha() and len(body) <= 3 and body.lower() not in SUB_WORDS:
            body = " ".join(body)               # δ_{ij} -> "delta sub i j"
        return " sub " + body + " "

    # ^{...} and _{...}, one level of nesting deep: e^{iω_{fi}t}
    braced = r"\{((?:[^{}\n]|\{[^{}\n]*\})*)\}"
    text = re.sub(r"\^\s*" + braced, lambda m: sup_words(m.group(1)), text)
    text = re.sub(r"_\s*" + braced, lambda m: sub_words(m.group(1)), text)
    # ^x and _x (single token).  The class has to reach past ASCII: Φ^+, H^⊥,
    # p^λ, U_φ, Var_θ and ‖·‖_◇ all occur in this corpus.
    script = r"[A-Za-z0-9*†⊥⊗◇∞\u0370-\u03ff]"
    token = rf"[-+]{script}*|{script}+"     # "^+" in |Φ^+⟩ is a bare sign
    text = re.sub(r"\^\s*⊗\s*([A-Za-z0-9]+)", r" to the tensor power \1 ", text)
    text = re.sub(r"\^\s*(" + token + r")", lambda m: sup_words(m.group(1)), text)
    text = re.sub(r"_\s*(" + token + r")", lambda m: sub_words(m.group(1)), text)
    # unicode runs
    def _join(parts: list[str]) -> str:
        return ("".join(parts) if all(len(p) == 1 for p in parts)
                else " ".join(parts))

    text = re.sub(sup_run, lambda m: sup_words(
        _join([SUPERSCRIPT[c] for c in m.group(0)])), text)
    text = re.sub(sub_run, lambda m: sub_words(
        _join([SUBSCRIPT[c] for c in m.group(0)])), text)
    return text


def _numbers(text: str) -> str:
    fractions = {("1", "2"): " one half ", ("1", "3"): " one third ",
                 ("2", "3"): " two thirds ", ("1", "4"): " one quarter ",
                 ("3", "4"): " three quarters ", ("1", "8"): " one eighth "}

    def frac(m: re.Match[str]) -> str:
        key = (m.group(1), m.group(2))
        return fractions.get(key, f" {m.group(1)} over {m.group(2)} ")

    # Before the fraction rule, or "~1/4ⁿ" loses its "approximately".
    text = re.sub(r"~\s*ms\b", "approximately milliseconds", text)
    text = re.sub(r"~\s*(?=[\dA-Za-zα-ωΑ-Ω(√])", "approximately ", text)
    text = re.sub(r"\b(\d+)\s*/\s*(\d+)\b", frac, text)
    text = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", text)      # 50–1000
    text = re.sub(r"(\d+):(\d+)", r"\1 \2", text)                # 50:50
    # A slash is a division when a number, a root or a bracket follows it, and
    # a literal "slash" otherwise ("assumptions/caveats", "rz/sx/x/cx").
    text = re.sub(r"(?<=[\d)\]])\s*/\s*(?=[\dΑ-Ωα-ω√(∂])", " over ", text)
    text = re.sub(r"(?<=\d)\s*/\s*(?=[A-Za-z(])", " over ", text)
    text = re.sub(r"(?<=[α-ωΑ-Ω)])\s*/\s*(?=[\dA-Za-zα-ω(∂])", " over ", text)
    text = re.sub(r"(?<=[A-Za-z])\s*/\s*(?=∂)", " over ", text)
    text = re.sub(r"(?<=[A-Za-zα-ωΑ-Ωℏ\)\]])\s*/\s*(?=[\d(√ℏ])", " over ", text)
    text = re.sub(r"/", " slash ", text)
    text = re.sub(r"(\d)\s*%", r"\1 percent", text)
    text = re.sub(r"(\d)\s*μs\b", r"\1 microseconds", text)
    text = re.sub(r"(\d)\s*ns\b", r"\1 nanoseconds", text)
    text = re.sub(r"(\d)\s*ms\b", r"\1 milliseconds", text)
    return text


def _say_token(tok: str) -> str:
    if tok in SPOKEN_WORDS:
        return SPOKEN_WORDS[tok]
    if (2 <= len(tok) <= 6 and tok.upper() == tok
            and all(c in GATE_LETTERS for c in tok)
            and tok not in GATE_RUN_SKIP):
        return " ".join(tok)            # XZX -> "X Z X"
    return tok


def _words(text: str) -> str:
    """Whole-word fixes: acronyms and gate runs."""
    def repl(m: re.Match[str]) -> str:
        tok = m.group(0)
        if tok in SPOKEN_WORDS:
            return SPOKEN_WORDS[tok]
        # The imaginary unit glued to an operator: -iY, iHt, iZZ.
        if tok[:1] == "i" and tok[1:2].isupper():
            return "i " + _say_token(tok[1:])
        return _say_token(tok)

    return re.sub(r"[A-Za-z][A-Za-z0-9]*", repl, text)


def _punctuation(text: str) -> str:
    text = text.replace("—", ". ").replace("–", ", ")
    text = re.sub(r"\^\s*\*", " conjugate ", text)
    text = re.sub(r"(?<=[A-Za-z0-9Ͱ-Ͽ)])\*", " conjugate ", text)
    text = text.replace("*", " times ")
    text = re.sub(r"(?<=[A-Za-z])'(?![a-z])", " prime ", text)
    text = text.replace("+", " plus ")
    # Minus: only where both sides are standalone tokens, so "no-cloning" and
    # "2-qubit" keep their hyphen.
    text = re.sub(r"(?<![A-Za-z])([A-Za-z0-9α-ωΑ-Ω])\s*-\s*"
                  r"([A-Za-z0-9α-ωΑ-Ω])(?![A-Za-z])", r"\1 minus \2", text)
    text = re.sub(r"(?<=[\s(\[)\],;→↔⇒⟹↦=±<>])-\s*(?=[\dA-Za-zα-ωΑ-Ω(])",
                  "minus ", text)
    text = re.sub(r"\s+-\s+", " minus ", text)
    # A sign standing alone between punctuation: "f(+,-)".  Hyphens inside
    # a word have letters on both sides and are left alone.
    text = re.sub(r"(?<![A-Za-z0-9])-+(?![A-Za-z0-9])", " minus ", text)
    text = text.replace("·", " times ")
    for sign, word in SYMBOLS.items():
        text = text.replace(sign, word)
    for sign, word in GREEK.items():
        # Padded: "iε" must become "i epsilon", not "iepsilon".
        text = text.replace(sign, f" {word} ")
    for mark, word in COMBINING.items():
        text = text.replace(mark, word)
    text = _parens(text)
    return text


def _parens(text: str) -> str:
    """`(Simon's problem construction)` is an aside; `(m)` is just grouping.

    Brackets make no sound, so an aside that simply loses them runs into the
    sentence around it.  Asides of two words or more become a comma pair;
    a one-word bracket ("(m)", "(2001)", "(MBL)") is grouping and is dropped.
    A bracket that follows "of" is a function argument -- "big O of (n
    squared)" -- and only earns commas when it is long enough to need them.
    """
    def one(m: re.Match[str]) -> str:
        after_of = m.group(1) == "of"
        body = m.group(2).strip()
        need = 5 if after_of else 2
        joined = f", {body}, " if len(body.split()) >= need else f" {body} "
        return m.group(1) + joined

    for _ in range(4):
        new = re.sub(r"(\S*)\s*\(([^()\n]{0,200})\)", one, text)
        if new == text:
            break
        text = new
    return text


def _tidy(text: str) -> tuple[str, set[str]]:
    """Final scrub.  Returns the speakable text and the characters dropped."""
    dropped = {c for c in text
               if not SPEAKABLE.match(c) and not c.isspace()
               and c not in IGNORED_CHARS}
    text = "".join(c if SPEAKABLE.match(c) else " " for c in text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:?])", r"\1", text)
    text = re.sub(r"([,;:])[\s,;:]*\1", r"\1", text)
    text = re.sub(r",\s*([.;:?])", r"\1", text)
    text = re.sub(r"([.;:?])\s*,", r"\1", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"(?<=[,;:])(?=\S)", " ", text)
    text = re.sub(r"\b(a|an|the)\s+the\b", r"\1", text)
    text = re.sub(r"\b(set|sets)\s+the set\b", r"\1", text)
    text = re.sub(r"\bcode (codes?)\b", r"\1", text)
    text = re.sub(r"\bprojector projector\b", "projector", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;:")
    # An em dash became a full stop, so the clause after it starts lower case.
    # Only capitalise words of two letters or more: a lone "i" is the imaginary
    # unit, not a pronoun.
    text = re.sub(r"(^|(?<=[.?] ))([a-z]{2,})",
                  lambda m: m.group(1) + m.group(2).capitalize(), text)
    if text and text[-1] not in ".!?":
        text += "."
    return text, dropped


def spoken(text: str) -> tuple[str, set[str]]:
    """Rewrite one card side into speech.  Returns (text, unmapped chars).

    The order below is load-bearing:
      1  editorial  -- drop the doc citation before its path meets `/`
      2  phrases    -- multi-character literals, before anything splits them
      3  identifiers-- Qiskit names, before `_` and `.` become maths
      4  brakets    -- Dirac notation, before `|` and `⟨⟩` become other things
      5  brackets   -- [[n,k,d]], matrices, commutators, sets
      6  big-O      -- O(, Θ(, Ω( before Θ/Ω become Greek letters
      7  big ops    -- Σ/Π/∫ with their limits, before generic sub/superscripts
      8  scripts    -- ^{...}, _{...} and the unicode script characters
      9  functions  -- Tr, exp, cos ...
     10  numbers    -- fractions, ranges, units, the remaining `/`
     11  words      -- acronym and gate-run fixes (ASCII only by now)
     12  punctuation-- operators, relations, Greek, combining marks
     13  tidy       -- scrub to a speakable character set
    """
    t = _strip_editorial(text)
    for src, dst in PHRASES:
        t = t.replace(src, dst)
    for pat, dst in WORD_PHRASES:
        t = re.sub(pat, dst, t)
    t = _identifiers(t)
    t = _brakets(t)
    t = _brackets(t)
    t = _big_o(t)
    t = _big_operators(t)
    t = _scripts(t)
    for pat, word in FUNCTIONS:
        t = re.sub(pat, word, t)
    t = _numbers(t)
    t = _words(t)
    t = _punctuation(t)
    return _tidy(t)


# ===========================================================================
#  Deck loading -- through flashcard-drill's own registry, never a copy
# ===========================================================================

@dataclass(frozen=True)
class Card:
    id: str
    category: str
    front: str
    back: str


def load_cards() -> list[Card]:
    """Import ``cards.all_cards`` the way tools/export_cards.py does."""
    if not CARD_DIR.is_dir():
        raise AudioError(f"card directory not found: {CARD_DIR}")
    app_dir = str(APP_DIR)
    inserted = app_dir not in sys.path
    if inserted:
        sys.path.insert(0, app_dir)
    try:
        from cards import all_cards  # type: ignore[import-not-found]
        raw = all_cards()
    except ImportError as exc:  # pragma: no cover - defensive
        raise AudioError(f"could not import flashcard-drill's card registry: {exc}") from exc
    finally:
        if inserted:
            with contextlib.suppress(ValueError):
                sys.path.remove(app_dir)

    expected = sum(1 for p in CARD_DIR.glob("*/*.py") if p.stem != "__init__")
    if len(raw) != expected:
        # all_cards() swallows per-module exceptions, so a broken card file
        # would silently shrink the deck.  Refuse to narrate a partial one.
        raise AudioError(
            f"loaded {len(raw)} cards but {expected} card modules exist under "
            f"{CARD_DIR} — a card module failed to import; fix it first")
    if not raw:
        raise AudioError(f"no cards found under {CARD_DIR}")
    cards = [Card(c.id, c.category, c.front, c.back) for c in raw]
    cards.sort(key=lambda c: (c.category, c.id))
    return cards


def slug(name: str) -> str:
    out = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    out = out.replace("&", "and")
    out = re.sub(r"[^A-Za-z0-9]+", "-", out).strip("-").lower()
    return out or "deck"


# ===========================================================================
#  Text-to-speech engines -- all local, all optional
# ===========================================================================

@dataclass
class Engine:
    name: str
    quality: int                  # lower is better; the survey sorts on it
    install: str                  # how to get it
    note: str = ""
    default_voice: str | None = None

    def available(self) -> bool:
        return shutil.which(self.name) is not None

    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        raise NotImplementedError


@dataclass
class PiperEngine(Engine):
    def _model(self, voice: str | None) -> Path | None:
        candidate = voice or os.environ.get("PIPER_VOICE")
        if candidate and Path(candidate).is_file():
            return Path(candidate)
        return None

    def available(self) -> bool:
        return shutil.which("piper") is not None and self._model(None) is not None

    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        model = self._model(voice)
        if model is None:
            raise AudioError("piper needs a voice model: --voice /path/to/en_US-*.onnx "
                             "or set PIPER_VOICE")
        _run(["piper", "--model", str(model), "--output_file", str(out)], text)


@dataclass
class SayEngine(Engine):
    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        cmd = ["say", "-r", str(rate), "--data-format=LEI16@22050", "-o", str(out)]
        if voice:
            cmd[1:1] = ["-v", voice]
        _run(cmd, text)


@dataclass
class PicoEngine(Engine):
    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        # pico2wave takes no rate flag and wants the text as an argument.
        _run(["pico2wave", "-l", voice or "en-US", "-w", str(out), text], None)


@dataclass
class EspeakEngine(Engine):
    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        _run([self.name, "-v", voice or "en-us", "-s", str(rate),
              "-w", str(out)], text)


@dataclass
class FliteEngine(Engine):
    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        cmd = ["flite", "-o", str(out)]
        if voice:
            cmd += ["-voice", voice]
        # flite's rate knob is a duration multiplier, not words per minute.
        cmd += ["--setf", f"duration_stretch={max(0.5, 170 / max(rate, 60)):.3f}",
                "-t", text]
        _run(cmd, None)


@dataclass
class Pyttsx3Engine(Engine):
    def available(self) -> bool:
        import importlib.util
        return importlib.util.find_spec("pyttsx3") is not None

    def synth(self, text: str, out: Path, voice: str | None, rate: int) -> None:
        import pyttsx3  # type: ignore[import-not-found]  # optional extra
        eng = pyttsx3.init()
        eng.setProperty("rate", rate)
        if voice:
            eng.setProperty("voice", voice)
        eng.save_to_file(text, str(out))
        eng.runAndWait()


def engines() -> list[Engine]:
    """The survey, best first."""
    return [
        PiperEngine("piper", 1,
                    "https://github.com/rhasspy/piper (binary + a .onnx voice)",
                    "neural; needs --voice model.onnx or PIPER_VOICE"),
        SayEngine("say", 2, "built in to macOS", "macOS only"),
        PicoEngine("pico2wave", 3,
                   "apt install libttspico-utils   |   dnf install svox-pico-tts",
                   "small and natural; no rate control"),
        EspeakEngine("espeak-ng", 4,
                     "apt install espeak-ng   |   dnf install espeak-ng",
                     "robotic but clear, fast and rate-controllable"),
        EspeakEngine("espeak", 5, "apt install espeak   |   dnf install espeak"),
        FliteEngine("flite", 6, "apt install flite   |   dnf install flite"),
        Pyttsx3Engine("pyttsx3", 7,
                      "pip install pyttsx3   (optional, not in any requirements file)",
                      "Python wrapper; on Linux it just drives espeak"),
    ]


def pick_engine(requested: str | None) -> Engine:
    survey = engines()
    if requested:
        for e in survey:
            if e.name == requested:
                if not e.available():
                    raise AudioError(
                        f"--engine {requested} is not installed on this machine.\n"
                        f"  install: {e.install}")
                return e
        raise AudioError(f"unknown engine {requested!r}; "
                         f"choose from: {', '.join(e.name for e in survey)}")
    for e in survey:
        if e.available():
            return e
    lines = ["no offline text-to-speech engine found — nothing was written.",
             "", "Install one of these (best first):"]
    for e in survey:
        lines.append(f"  {e.name:<10} {e.install}")
    lines += ["",
              "On this distribution the quickest is usually:",
              "  sudo dnf install espeak-ng      # Fedora/RHEL",
              "  sudo apt install espeak-ng      # Debian/Ubuntu",
              "",
              "Then re-run.  Nothing here ever calls a network service, so a "
              "cloud voice is not an option.",
              "Use --dry-run to review the spoken text without an engine."]
    raise AudioError("\n".join(lines))


def _run(cmd: list[str], stdin_text: str | None) -> None:
    try:
        proc = subprocess.run(
            cmd, input=(stdin_text or "").encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError as exc:
        raise AudioError(f"{cmd[0]} disappeared mid-run: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise AudioError(f"{cmd[0]} timed out after 120s") from exc
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()
        raise AudioError(f"{cmd[0]} failed ({proc.returncode}): {err}")


# ===========================================================================
#  WAV assembly
# ===========================================================================

@dataclass
class Clip:
    params: wave._wave_params          # type: ignore[name-defined]
    frames: bytes

    @property
    def seconds(self) -> float:
        rate = self.params.framerate * self.params.nchannels * self.params.sampwidth
        return len(self.frames) / rate if rate else 0.0


def read_wav(path: Path) -> Clip:
    with wave.open(str(path), "rb") as w:
        return Clip(w.getparams(), w.readframes(w.getnframes()))


def silence(params: "wave._wave_params", seconds: float) -> Clip:  # type: ignore[name-defined]
    n = int(params.framerate * max(seconds, 0.0))
    return Clip(params, b"\x00" * (n * params.nchannels * params.sampwidth))


class WavWriter:
    """Append clips to a WAV as they are synthesised.

    A whole-category track is 20-80 minutes of PCM; holding it in a list before
    writing would cost hundreds of megabytes of RAM for no reason.  The file is
    built under a ``.part`` name and only moved into place on ``close()``, so a
    crash or a Ctrl-C never leaves a half-written track behind.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.temp = path.with_suffix(path.suffix + ".part")
        self.seconds = 0.0
        self._w: wave.Wave_write | None = None
        self._head: tuple[int, int, int] | None = None

    def add(self, clip: Clip) -> None:
        shape = (clip.params.framerate, clip.params.nchannels,
                 clip.params.sampwidth)
        if self._w is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._w = wave.open(str(self.temp), "wb")
            self._w.setnchannels(clip.params.nchannels)
            self._w.setsampwidth(clip.params.sampwidth)
            self._w.setframerate(clip.params.framerate)
            self._head = shape
        elif shape != self._head:
            raise AudioError(
                "the engine returned clips with different audio formats "
                f"({self._head} vs {shape}) — cannot concatenate them")
        self._w.writeframes(clip.frames)
        self.seconds += clip.seconds

    def close(self) -> float:
        if self._w is None:
            raise AudioError(f"nothing to write to {self.path}")
        self._w.close()
        self._w = None
        self.temp.replace(self.path)
        return self.seconds

    def abandon(self) -> None:
        if self._w is not None:
            self._w.close()
            self._w = None
        self.temp.unlink(missing_ok=True)


def write_wav(path: Path, clips: list[Clip]) -> float:
    w = WavWriter(path)
    try:
        for c in clips:
            w.add(c)
        return w.close()
    except BaseException:
        w.abandon()
        raise


def check_encoder(fmt: str) -> None:
    """Fail before synthesis, not after it, when the encoder is missing."""
    if fmt != "wav" and shutil.which("ffmpeg") is None:
        raise AudioError(f"--encode {fmt} needs ffmpeg on PATH "
                         "(apt install ffmpeg | dnf install ffmpeg); "
                         "the default --encode wav needs nothing")


def encode(src: Path, fmt: str) -> Path:
    """Re-encode a WAV with ffmpeg.  The whole deck in WAV is well over 1 GB."""
    if fmt == "wav":
        return src
    dst = src.with_suffix("." + fmt)
    codec = ["-c:a", "libmp3lame", "-q:a", "6"] if fmt == "mp3" else \
            ["-c:a", "libopus", "-b:a", "24k"]
    _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(src),
          *codec, str(dst)], None)
    src.unlink()
    return dst


# ===========================================================================
#  Playlist and chapters
# ===========================================================================

def write_m3u(path: Path, entries: list[tuple[Path, int, str]]) -> None:
    lines = ["#EXTM3U"]
    for track, secs, title in entries:
        lines.append(f"#EXTINF:{secs},{title}")
        lines.append(os.path.relpath(track, path.parent))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cue_time(seconds: float) -> str:
    total = int(round(seconds * 75))
    frames, total = total % 75, total // 75
    return f"{total // 60:02d}:{total % 60:02d}:{frames:02d}"


def write_cue(path: Path, audio: Path, title: str,
              marks: list[tuple[float, str]]) -> None:
    lines = [f'TITLE "{title}"', 'PERFORMER "Quantum Study Suite"',
             f'FILE "{audio.name}" WAVE']
    for i, (start, name) in enumerate(marks, 1):
        lines += [f"  TRACK {i:02d} AUDIO",
                  f'    TITLE "{name}"',
                  f"    INDEX 01 {_cue_time(start)}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ffmetadata(path: Path, marks: list[tuple[float, str]],
                     total: float) -> None:
    """Chapters for `ffmpeg -i track.wav -i this -map_metadata 1 out.m4b`."""
    out = [";FFMETADATA1"]
    bounds = [m[0] for m in marks] + [total]
    for i, (start, name) in enumerate(marks):
        out += ["[CHAPTER]", "TIMEBASE=1/1000",
                f"START={int(start * 1000)}",
                f"END={int(bounds[i + 1] * 1000)}",
                f"title={name}"]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


# ===========================================================================
#  CLI
# ===========================================================================

def select(cards: list[Card], category: list[str] | None,
           limit: int | None) -> list[Card]:
    if category:
        wanted = {c.lower() for c in category}
        known = {c.category.lower() for c in cards}
        unknown = wanted - known
        if unknown:
            raise AudioError(
                "unknown category: " + ", ".join(sorted(unknown)) + "\n  known: "
                + ", ".join(sorted({c.category for c in cards})))
        cards = [c for c in cards if c.category.lower() in wanted]
    if limit is not None and limit > 0:
        # Spread the limit across categories so a small run still samples the
        # whole deck rather than stopping inside "Algorithms".
        per: dict[str, list[Card]] = {}
        for c in cards:
            per.setdefault(c.category, []).append(c)
        out: list[Card] = []
        index = 0
        while len(out) < limit and any(index < len(v) for v in per.values()):
            for cat in sorted(per):
                if index < len(per[cat]) and len(out) < limit:
                    out.append(per[cat][index])
            index += 1
        cards = sorted(out, key=lambda c: (c.category, c.id))
    return cards


def do_dry_run(cards: list[Card], pause: float, rate: int) -> int:
    dropped: set[str] = set()
    words = 0
    current = ""
    for card in cards:
        if card.category != current:
            current = card.category
            print(f"\n{'=' * 72}\n== {current}\n{'=' * 72}")
        front, d1 = spoken(card.front)
        back, d2 = spoken(card.back)
        dropped |= d1 | d2
        words += len(front.split()) + len(back.split())
        print(f"\n-- {card.id}")
        print(f"   raw front : {card.front}")
        print(f"   SPOKEN    : {front}")
        print(f"   raw back  : {card.back}")
        print(f"   SPOKEN    : {back}")
    secs = words / max(rate, 1) * 60 + len(cards) * (pause + 1.2)
    print(f"\n{'=' * 72}")
    print(f"{len(cards)} cards, ~{words} spoken words")
    print(f"estimated runtime at {rate} wpm with a {pause:g}s gap: "
          f"{secs / 60:.0f} min ({secs / 3600:.1f} h)")
    if dropped:
        print("unmapped characters (extend the tables at the top of this file): "
              + " ".join(sorted(dropped)))
    else:
        print("unmapped characters: none")
    return 0


def do_export(cards: list[Card], args: argparse.Namespace, engine: Engine) -> int:
    check_encoder(args.encode)
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / ".tmp"
    tmp.mkdir(exist_ok=True)

    per: dict[str, list[Card]] = {}
    for c in cards:
        per.setdefault(c.category, []).append(c)

    playlist: list[tuple[Path, int, str]] = []
    print(f"engine: {engine.name}   voice: {args.voice or 'default'}   "
          f"rate: {args.rate} wpm   gap: {args.pause:g}s")

    try:
        for n, category in enumerate(sorted(per), 1):
            group = per[category]
            stem = f"{n:02d}-{slug(category)}"
            marks: list[tuple[float, str]] = []
            writer = None if args.per_card else WavWriter(out / f"{stem}.wav")
            try:
                for i, card in enumerate(group, 1):
                    front, _ = spoken(card.front)
                    back, _ = spoken(card.back)
                    print(f"  [{category} {i}/{len(group)}] {card.id}", flush=True)
                    fw, bw = tmp / "front.wav", tmp / "back.wav"
                    engine.synth(front, fw, args.voice, args.rate)
                    engine.synth(back, bw, args.voice, args.rate)
                    fc, bc = read_wav(fw), read_wav(bw)
                    parts = [fc, silence(fc.params, args.pause), bc,
                             silence(fc.params, 0.8)]
                    if writer is None:
                        track = out / slug(category) / f"{i:04d}-{card.id}.wav"
                        secs = write_wav(track, parts)
                        track = encode(track, args.encode)
                        playlist.append((track, int(secs),
                                         f"{category}: {card.id}"))
                    else:
                        marks.append((writer.seconds, card.id))
                        for clip in parts:
                            writer.add(clip)
            except BaseException:
                if writer is not None:
                    writer.abandon()
                raise
            if writer is not None and marks:
                secs = writer.close()
                track = writer.path
                write_cue(out / f"{stem}.cue", track, category, marks)
                write_ffmetadata(out / f"{stem}.chapters.txt", marks, secs)
                track = encode(track, args.encode)
                playlist.append((track, int(secs), category))
                print(f"  -> {track.name}  {secs / 60:.1f} min  "
                      f"{track.stat().st_size / 1e6:.1f} MB  "
                      f"({len(marks)} chapters)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if args.playlist and playlist:
        write_m3u(out / PLAYLIST_NAME, playlist)
        print(f"playlist: {out / PLAYLIST_NAME}  ({len(playlist)} tracks)")
    total = sum(t[1] for t in playlist)
    print(f"done: {len(cards)} cards, {len(playlist)} tracks, "
          f"{total / 60:.0f} min in {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="export_audio.py",
        description="Text-to-speech audio deck from the flashcard-drill cards.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Review the pronunciation layer first:\n"
               "  python3 tools/export_audio.py --dry-run --limit 60")
    p.add_argument("--category", action="append", metavar="NAME",
                   help="only this category (repeatable; case-insensitive)")
    p.add_argument("--limit", type=int, metavar="N",
                   help="at most N cards, spread across the chosen categories")
    p.add_argument("--pause", type=float, default=4.0, metavar="SECONDS",
                   help="silent recall gap between front and back (default 4)")
    p.add_argument("--voice", metavar="NAME",
                   help="engine voice (espeak: en-us, en-gb; piper: a .onnx path)")
    p.add_argument("--rate", type=int, default=150, metavar="WPM",
                   help="speaking rate in words per minute (default 150)")
    p.add_argument("--out", default=str(DEFAULT_OUT), metavar="DIR",
                   help=f"output directory (default {DEFAULT_OUT})")
    p.add_argument("--dry-run", action="store_true",
                   help="print the spoken text and synthesise nothing")
    p.add_argument("--playlist", action=argparse.BooleanOptionalAction, default=True,
                   help="write an M3U playlist next to the tracks (default: yes)")
    p.add_argument("--per-card", action="store_true",
                   help="one file per card instead of one track per category")
    p.add_argument("--encode", choices=("wav", "mp3", "opus"), default="wav",
                   help="re-encode with ffmpeg; wav needs nothing (default wav)")
    p.add_argument("--engine", metavar="NAME",
                   help="force a TTS engine instead of the best installed one")
    p.add_argument("--list-engines", action="store_true",
                   help="show the engine survey for this machine and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_engines:
        print(f"{'engine':<11} {'status':<14} notes / install")
        for e in engines():
            status = "INSTALLED" if e.available() else "not found"
            print(f"{e.name:<11} {status:<14} {e.note or e.install}")
            if not e.available():
                print(f"{'':<26} {e.install}")
        return 0

    try:
        cards = select(load_cards(), args.category, args.limit)
        if not cards:
            raise AudioError("no cards selected")
        if args.dry_run:
            return do_dry_run(cards, args.pause, args.rate)
        return do_export(cards, args, pick_engine(args.engine))
    except AudioError as exc:
        print(f"export_audio: {exc}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:  # pragma: no cover
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
