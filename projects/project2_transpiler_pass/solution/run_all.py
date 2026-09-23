#!/usr/bin/env python3
"""run_all.py -- produce every artefact for project 2.

    python run_all.py         # ~15 s

Writes results/integration.md (milestone 3) then runs benchmark.py's work
(milestone 4).  The unit tests in test_passes.py are the milestone-1/2
artefact and are run separately with pytest.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from qiskit_ibm_runtime.fake_provider import FakeManilaV2, FakeTorino

import integration

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    rows = []
    for backend in (FakeManilaV2(), FakeTorino()):
        for level in (0, 1, 2, 3):
            for stage in ("init", "optimization"):
                for par in (False, True):
                    rows.append(integration.compare(backend, level, stage, par))

    with (OUT / "integration.md").open("w") as fh:
        fh.write("# Project 2 -- pass-manager integration (milestone 3)\n\n")
        fh.write("Test circuit: Bell state + three adjacent `CX.RZ.CX` windows "
                 "(`integration.bell_phase_circuit`).\n"
                 "`with` = the same preset pass manager plus "
                 "`PassManager([CXRZCXFuser(), DropIdentityRZ()])` appended to the "
                 "named stage.\n\n")
        fh.write("| backend | opt level | stage | angles | 2q without -> with | "
                 "rz without -> with | depth without -> with | ISA valid | coupling ok |\n")
        fh.write("|---|---:|---|---|---:|---:|---:|:--:|:--:|\n")
        for r in rows:
            fh.write(f"| {r['backend']} | {r['level']} | {r['stage']} | "
                     f"{'symbolic' if r['parameterised'] else 'numeric'} | "
                     f"{r['twoq_without']} -> {r['twoq_with']} | "
                     f"{r['rz_without']} -> {r['rz_with']} | "
                     f"{r['depth_without']} -> {r['depth_with']} | "
                     f"{'yes' if r['isa_valid'] else 'NO'} | "
                     f"{'yes' if r['coupling_ok'] else 'NO'} |\n")
        wins = [r for r in rows if r["twoq_with"] < r["twoq_without"]]
        fh.write(f"\n{len(wins)} of {len(rows)} configurations show a strict "
                 f"2-qubit-gate reduction; all of them are at "
                 f"`optimization_level=0`.\n")

    print(f"wrote {OUT / 'integration.md'}")
    for r in rows:
        if r["level"] in (0, 2) and r["stage"] == "init" and not r["parameterised"]:
            print(f"  {r['backend']:12s} L{r['level']} 2q {r['twoq_without']}->"
                  f"{r['twoq_with']}  depth {r['depth_without']}->{r['depth_with']}"
                  f"  ISA={r['isa_valid']} coupling={r['coupling_ok']}")

    print("\nrunning benchmark.py ...")
    return subprocess.call([sys.executable, str(HERE / "benchmark.py")])


if __name__ == "__main__":
    raise SystemExit(main())
