"""Shared expectations about the question bank.

Two numbers live here so the rest of the suite never hard-codes them:

* ``BANK_TOTAL`` — the exact size of the bank. This is the single constant to
  bump when questions are added; every other count assertion is expressed as a
  proportion, a minimum, or a non-emptiness check so growing one section does
  not cascade into a dozen test edits.
* ``EXAM_WEIGHTS`` — the *published* C1000-179 section weights in percent
  (see ``lesson-plans/11-certification-prep.md``). The bank is built to mirror
  them, and ``bank._proportional_allocation`` draws each exam against them, so
  they are the thing worth asserting against rather than any particular
  snapshot of per-section counts.
"""
from __future__ import annotations

# Exact bank size. Bump this one number when the bank grows.
BANK_TOTAL = 300

# Floor the bank must never fall below (the size the app was designed around:
# enough that a 68-question exam never repeats and every section can fill a
# 10-question sprint several times over).
BANK_MINIMUM = 300

# Published C1000-179 section weights, in percent. Sums to 100.
EXAM_WEIGHTS = {
    "Create circuits":    18,
    "Quantum operations": 16,
    "Run circuits":       15,
    "Sampler":            12,
    "Estimator":          12,
    "Visualization":      11,
    "Results analysis":   10,
    "OpenQASM":            6,
}

# How far a section's share of the bank may drift from its exam weight, in
# percentage points. 1.5 pp is loose enough to survive adding a handful of
# questions to one section, tight enough that a section drifting a whole
# question-slot out of proportion (at exam scale) trips it.
WEIGHT_TOLERANCE_PP = 1.5

# Every section must hold at least this many questions so a sprint of
# SPRINT_QUESTION_COUNT is always a full draw from a single section.
MIN_QUESTIONS_PER_SECTION = 18

# Directory name under bank/ -> section label carried by its questions.
SECTION_DIRS = {
    "create_circuits":    "Create circuits",
    "quantum_operations": "Quantum operations",
    "run_circuits":       "Run circuits",
    "sampler":            "Sampler",
    "estimator":          "Estimator",
    "visualization":      "Visualization",
    "results_analysis":   "Results analysis",
    "openqasm":           "OpenQASM",
}

# Question files whose stem deliberately (or historically) differs from the
# question id they define. Keep this empty; an entry here is a wart to fix in
# bank/, not a pattern to copy — rename the file to match the id and delete the
# line. Maps file stem -> question id.
KNOWN_FILENAME_ID_MISMATCHES = {
    "cc_if_test_control_flow": "cc_if_test",
}

DIFFICULTIES = {"easy", "medium", "hard"}

# Similarity above which two questions are treated as near-duplicates. Measured
# over the question text plus its (sorted) options, so two items that merely
# share a code-snippet preamble but ask different things stay well clear. The
# worst legitimate pair in the bank scores ~0.86 (cc_depth vs cc_size: same
# circuit, one asks for depth and one for size).
NEAR_DUPLICATE_RATIO = 0.92
