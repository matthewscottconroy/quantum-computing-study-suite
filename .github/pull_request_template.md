<!--
  Thanks for contributing.  The checklist below is the one in CONTRIBUTING.md
  ("Pull request checklist") -- keep the two in step if you change either.
  Delete the rows that genuinely do not apply, and say why in "Notes".
-->

## What this changes

<!-- One paragraph.  If it fixes an issue, write "Fixes #123". -->

## Why

<!-- The defect, the gap, or the study goal this serves. -->

## How it was verified

<!--
  Paste the commands you ran and the lines that matter from their output --
  the suite tally, verify_docs' exit line, the snippet that produced a number.
  "Tests pass" on its own is not a verification.
-->

```
$ bash tools/run_tests.sh
...
$ python tools/verify_docs.py --all
...
```

## Checklist

- [ ] Branched from `main`; one topic in this PR (a bank addition, a docs fix, an app change).
- [ ] `bash tools/run_tests.sh` passes locally — or the affected app's suite plus the root suite — and the tally is pasted above.
- [ ] `python tools/verify_docs.py --all` exits 0 (required if `docs/` or `lesson-plans/` changed).
- [ ] **Every number added or changed was verified by a script**, and the script or snippet is shown above or in the diff.
- [ ] Qiskit code is 2.x-current and was actually executed; the version is stated.
- [ ] New bank items: file stem equals the item `id`; the count constant in the bank test is bumped; the README count is updated; for exam-sim, `config.SECTIONS` and `DOCUMENTED_SECTIONS` too; for qiskit-dojo, the slow sweep passes.
- [ ] README and any other counts/tables that name what I changed are updated.
- [ ] App changes launch with `QT_QPA_PLATFORM=offscreen` **and with no API key present**.
- [ ] Docs math: inline in backticks, display in fenced blocks or `$$`, no inline `$`; chapter files keep the five-section ending.
- [ ] No API key, no personal data, nothing from `~/.local/share/quantum-study/`, and no real exam content in the diff.
- [ ] No change to an existing history JSON schema (`coach.py` and `dashboard.py` parse every file in the study-data directory; add a new file instead).

## Notes

<!-- Follow-ups, deliberate omissions, checklist rows you deleted and why. -->
