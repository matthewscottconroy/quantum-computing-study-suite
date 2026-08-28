# tools/

## verify_docs.py

Regression checks for the study corpus (`docs/` and `lesson-plans/`). Run it
after editing corpus files; it exits `0` when everything passes and `1` with a
report when something broke.

```bash
python3 tools/verify_docs.py                 # all checks, incl. snippet execution
python3 tools/verify_docs.py --no-snippets   # static checks only (no venv needed)
python3 tools/verify_docs.py --structure     # one specific check
python3 tools/verify_docs.py --snippets -v   # run snippets, show passing blocks too
```

### Checks

| Flag | What it verifies |
|---|---|
| `--structure` | Every `docs/<chapter>/*.md` has `## Exercises` and `## Further Reading`; `<details>` tags are balanced and at least one per exercise item; every `<details>` block contains `<summary>Solution</summary>`; no empty sections; file is not truncated. |
| `--lint` | No AI self-talk leftovers ("wait, let…", "hmm,…", "let me recompute", …), no `TODO`/`FIXME`/`XXX ` markers, no stranded `·...` fragments (Pauli strings like `XXXX` are excluded). |
| `--crossrefs` | Markdown links and backtick paths that look like repo-relative `.md` file (or directory-link) references resolve to existing files. |
| `--readme` | `docs/README.md` file-map tables name files that exist in their chapter dirs (chapter files missing from a map are a warning, not a failure); `lesson-plans/README.md` lesson-table links resolve. |
| `--snippets` | Extracts the ` ```python ` blocks from `lesson-plans/06-qiskit.md`, `07-qasm.md`, and `10-transpiling.md` and executes them **cumulatively per file** (each block sees the namespace built by earlier blocks, matching how the lessons build context). Reports pass/skip/fail per block. |

Default (no flags) = all checks. `--no-snippets` drops the snippet run from
the default set. Warnings never affect the exit status.

### Snippet execution details

- **Requires the project venv**: blocks run under
  `.venv/bin/python` (the static checks need only system Python 3.14+, stdlib
  only). If the venv is missing, use `--no-snippets`.
- Blocks run in a **temporary working directory** (file-writing snippets never
  pollute the repo) with `MPLBACKEND=Agg` so matplotlib never opens windows.
- Blocks are **skipped automatically** with a note when they:
  - import `qiskit_ibm_runtime` or `pytket` (need external services/packages),
  - import any module not installed in the venv,
  - need an optional lazy dependency (e.g. `qiskit.qasm3.loads` needs
    `qiskit-qasm3-import`),
  - use names defined only in skipped blocks, or never defined by any prior
    block (lesson fragments that assume "your circuit").
- Manual skips: start a block with `# verify: skip — reason`, add an entry to
  `MANUAL_SKIPS` in the script, or pass `--skip 06-qiskit.md:3,5` at the CLI.
- `--timeout SEC` sets the per-block timeout (default 120 s).

To increase snippet coverage, install the optional packages in the venv:
`pip install qiskit-qasm3-import` (enables the OpenQASM 3 round-trip block in
`07-qasm.md`); `qiskit-ibm-runtime` would enable the fake-backend blocks.
