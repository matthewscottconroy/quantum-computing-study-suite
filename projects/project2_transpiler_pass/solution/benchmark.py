#!/usr/bin/env python3
"""benchmark.py -- milestone 4: how much does the pass actually buy?

    python benchmark.py            # 360 circuits, ~40 s
    python benchmark.py --seeds 5  # smaller sweep

Grid: widths {3, 5, 8} x depths {10, 30, 100} x {planted, unplanted} x N seeds.
Every circuit is first normalised to the ``cx/rz/sx/x`` basis at
``optimization_level=0`` so the transpiler does not do the pass's job for it.

Why "planted"
-------------
A purely random circuit almost never contains a clean CX-RZ-CX window: the
probability that the same control/target pair repeats with nothing in between
falls off fast with width.  Reporting only random circuits would make the pass
look useless; reporting only planted ones would make it look magic.  Both
populations are measured and reported separately, which is the honest form.

Outputs (results/):
    benchmark.csv        one row per circuit
    benchmark_summary.md the summary table
    benchmark.png        reduction by population + pass runtime vs gate count
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.random import random_circuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager

import vizstyle
from passes import CXRZCXFuser, DropIdentityRZ

vizstyle.use_style()

OUT = Path(__file__).resolve().parent / "results"
BASIS = ["cx", "rz", "sx", "x"]
WIDTHS = (3, 5, 8)
DEPTHS = (10, 30, 100)


def normalise(qc: QuantumCircuit) -> QuantumCircuit:
    return transpile(qc, basis_gates=BASIS, optimization_level=0, seed_transpiler=0)


def plant(qc: QuantumCircuit, n_blocks: int, rng: np.random.Generator) -> QuantumCircuit:
    """Insert ``n_blocks`` *pairs* of adjacent CX-RZ-CX windows.

    A pair is inserted as six consecutive instructions, so nothing separates the
    inner CXs on either wire and the pair is genuinely fusable:
    4 CX + 2 RZ collapse to 2 CX + 1 RZ.
    """
    data = list(qc.data)
    out = QuantumCircuit(*qc.qregs, *qc.cregs)
    cuts = sorted(rng.integers(0, len(data) + 1, size=n_blocks).tolist())
    ci = 0
    for i in range(len(data) + 1):
        while ci < len(cuts) and cuts[ci] == i:
            c, t = rng.choice(qc.num_qubits, size=2, replace=False).tolist()
            for _ in range(2):
                out.cx(c, t)
                out.rz(float(rng.uniform(0.05, 3.0)), t)
                out.cx(c, t)
            ci += 1
        if i < len(data):
            out.append(data[i].operation, data[i].qubits, data[i].clbits)
    return out


def one(width: int, depth: int, planted: bool, seed: int) -> dict:
    rng = np.random.default_rng(seed * 7919 + width * 97 + depth)
    qc = normalise(random_circuit(width, depth, max_operands=2, seed=seed))
    if planted:
        # Plant enough double-blocks that roughly half the CX gates in the
        # circuit belong to a fusable window.  A fixed count would make the
        # measured reduction an artefact of circuit size rather than of the
        # pass: deep circuits would look untouched and shallow ones magic.
        base_cx = qc.count_ops().get("cx", 0)
        qc = plant(qc, n_blocks=max(2, round(base_cx / 4)), rng=rng)
    # Benchmark the fuser ALONE, so every removed gate is attributable to it.
    # DropIdentityRZ would otherwise take credit for the rz(0) gates that basis
    # translation leaves behind.
    #
    # Time ``pass.run(dag)``, not ``PassManager.run(circuit)``: the latter adds
    # circuit->DAG->circuit conversion and property-set bookkeeping, which for
    # a few-thousand-gate circuit swamps the pass and makes the scaling plot a
    # picture of Qiskit's converters instead of the pass.  Best-of-two runs,
    # because a single timing on a loaded machine is mostly scheduler noise.
    n_gates = sum(qc.count_ops().values())
    dt = float("inf")
    out = None
    for _ in range(2):
        fuser = CXRZCXFuser()
        dag = circuit_to_dag(qc)
        t0 = time.perf_counter()
        fuser.run(dag)
        dt = min(dt, time.perf_counter() - t0)
        out = dag_to_circuit(dag)
    return {
        "seed": seed, "width": width, "depth": depth, "planted": int(planted),
        "gates_before": n_gates, "gates_after": sum(out.count_ops().values()),
        "cx_before": qc.count_ops().get("cx", 0),
        "cx_after": out.count_ops().get("cx", 0),
        "depth_before": qc.depth(), "depth_after": out.depth(),
        "fused": fuser.stats["fused"], "annihilated": fuser.stats["annihilated"],
        "pass_seconds": dt,
        "_before": qc, "_after": out,
    }


def summarise(rows, planted: bool):
    sel = [r for r in rows if r["planted"] == int(planted)]
    cxb = np.array([r["cx_before"] for r in sel], dtype=float)
    cxa = np.array([r["cx_after"] for r in sel], dtype=float)
    db = np.array([r["depth_before"] for r in sel], dtype=float)
    da = np.array([r["depth_after"] for r in sel], dtype=float)
    keep = cxb > 0
    return {
        "n": len(sel),
        "cx_red_pct": float(100 * (1 - cxa[keep].sum() / cxb[keep].sum())),
        "cx_red_pct_mean": float(np.mean(100 * (1 - cxa[keep] / cxb[keep]))),
        "depth_red_pct": float(100 * (1 - da.sum() / db.sum())),
        "fused": int(sum(r["fused"] for r in sel)),
        "annihilated": int(sum(r["annihilated"] for r in sel)),
        "ms_mean": float(1e3 * np.mean([r["pass_seconds"] for r in sel])),
    }


def plot(rows):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    # left: CX reduction by width, two populations -- grouped bars
    x = np.arange(len(WIDTHS))
    w = 0.34
    for j, (planted, colour, label) in enumerate(
            [(1, vizstyle.SERIES[0], "planted"), (0, vizstyle.SERIES[1], "unplanted")]):
        vals = []
        for wd in WIDTHS:
            sel = [r for r in rows if r["planted"] == planted and r["width"] == wd
                   and r["cx_before"] > 0]
            b = sum(r["cx_before"] for r in sel)
            a = sum(r["cx_after"] for r in sel)
            vals.append(100 * (1 - a / b) if b else 0.0)
        bars = ax1.bar(x + (j - 0.5) * w, vals, width=w * 0.9, color=colour,
                       label=label, edgecolor=vizstyle.SURFACE, linewidth=1.2)
        for bar, v in zip(bars, vals):
            ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.9, f"{v:.1f}%",
                     ha="center", fontsize=8.5, color=vizstyle.INK_2)
    ax1.axhline(20, color=vizstyle.INK, ls="--", lw=1.1)
    ax1.text(-0.45, 21.0, "milestone target, 20%", fontsize=8.5,
             ha="left", color=vizstyle.INK_2)
    ax1.set_xticks(x, [f"{v} qubits" for v in WIDTHS])
    ax1.set_ylabel("CX gates removed  (%)")
    ax1.set_title("CX reduction by circuit width")
    ax1.set_ylim(0, max(45, max(vals) + 12))
    ax1.legend(ncol=2, loc="upper right")
    ax1.grid(axis="x", visible=False)
    vizstyle.despine(ax1)

    # right: runtime vs gate count, one fit per population.  Planted circuits
    # do strictly more work per gate (every fusion is a DAG edit plus another
    # sweep), so pooling the two populations into one fit hides the real story.
    fits = {}
    for planted, colour, label in [(1, vizstyle.SERIES[0], "planted"),
                                   (0, vizstyle.SERIES[1], "unplanted")]:
        sel = [r for r in rows if r["planted"] == planted]
        g = np.array([r["gates_before"] for r in sel], dtype=float)
        t = np.array([r["pass_seconds"] for r in sel]) * 1e3
        ax2.scatter(g, t, s=16, color=colour, alpha=0.5, edgecolors="none")
        c = np.polyfit(g, t, 1)
        r2 = 1 - np.sum((t - np.polyval(c, g)) ** 2) / np.sum((t - t.mean()) ** 2)
        gs = np.linspace(g.min(), g.max(), 50)
        ax2.plot(gs, np.polyval(c, gs), color=colour, lw=1.8,
                 label=f"{label}: {c[0] * 1e3:.2f} us/gate, $R^2$={r2:.2f}")
        fits[label] = (c, r2)
    ax2.set_xlabel("gates in the input circuit")
    ax2.set_ylabel("pass runtime  (ms)")
    ax2.set_title("Pass runtime vs gate count (best of two, DAG-level)")
    ax2.legend(loc="upper left")
    vizstyle.despine(ax2)

    fig.tight_layout()
    fig.savefig(OUT / "benchmark.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return fits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--verify", type=int, default=60,
                    help="how many benchmark circuits to re-check with Operator.equiv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    rows, t0 = [], time.time()
    for width in WIDTHS:
        for depth in DEPTHS:
            for planted in (False, True):
                for seed in range(args.seeds):
                    rows.append(one(width, depth, planted, seed))
    print(f"{len(rows)} circuits in {time.time() - t0:.1f} s")

    # correctness spot-check on the small ones (Operator is 2^n x 2^n)
    checked = bad = 0
    for r in rows:
        if r["width"] > 5 or checked >= args.verify:
            continue
        if not Operator(r["_before"]).equiv(Operator(r["_after"])):
            bad += 1
        checked += 1
    print(f"unitary-equivalence spot check: {checked} circuits, {bad} mismatches")

    with (OUT / "benchmark.csv").open("w", newline="") as fh:
        cols = ["seed", "width", "depth", "planted", "gates_before", "gates_after",
                "cx_before", "cx_after", "depth_before", "depth_after",
                "fused", "annihilated", "pass_seconds"]
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows([[r[c] for c in cols] for r in rows])

    fits = plot(rows)
    sp, su = summarise(rows, True), summarise(rows, False)

    with (OUT / "benchmark_summary.md").open("w") as fh:
        fh.write("# Project 2 -- benchmark (milestone 4)\n\n")
        fh.write(f"{len(rows)} circuits: widths {WIDTHS}, depths {DEPTHS}, "
                 f"{args.seeds} seeds, both populations.\n")
        fh.write(f"Unitary-equivalence spot check: {checked} circuits "
                 f"(width <= 5), **{bad} mismatches**.\n\n")
        fh.write("| population | n | CX removed (pooled) | CX removed (mean per circuit) "
                 "| depth removed | fusions | annihilations | mean pass time |\n")
        fh.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for label, s in (("planted", sp), ("unplanted", su)):
            fh.write(f"| {label} | {s['n']} | {s['cx_red_pct']:.1f}% | "
                     f"{s['cx_red_pct_mean']:.1f}% | {s['depth_red_pct']:.1f}% | "
                     f"{s['fused']} | {s['annihilated']} | {s['ms_mean']:.2f} ms |\n")
        fh.write("\nPass runtime vs gate count (DAG-level, best of two runs):\n\n")
        fh.write("| population | slope | intercept | R^2 |\n|---|---:|---:|---:|\n")
        for label, (c, r2) in fits.items():
            fh.write(f"| {label} | {c[0] * 1e3:.2f} us/gate | "
                     f"{c[1] * 1e3:.0f} us | {r2:.3f} |\n")
        fh.write("\n## By width and depth (planted)\n\n")
        fh.write("| width | depth | CX before | CX after | reduction |\n|---:|---:|---:|---:|---:|\n")
        for wd in WIDTHS:
            for dp in DEPTHS:
                sel = [r for r in rows if r["planted"] == 1 and r["width"] == wd
                       and r["depth"] == dp]
                b = sum(r["cx_before"] for r in sel)
                a = sum(r["cx_after"] for r in sel)
                fh.write(f"| {wd} | {dp} | {b} | {a} | "
                         f"{100 * (1 - a / b) if b else 0:.1f}% |\n")

    print(f"planted  : CX -{sp['cx_red_pct']:.1f}% pooled, "
          f"-{sp['cx_red_pct_mean']:.1f}% mean, depth -{sp['depth_red_pct']:.1f}%")
    print(f"unplanted: CX -{su['cx_red_pct']:.1f}% pooled, "
          f"-{su['cx_red_pct_mean']:.1f}% mean, depth -{su['depth_red_pct']:.1f}%")
    for label, (c, r2) in fits.items():
        print(f"runtime {label:9s}: {c[0] * 1e3:.2f} us/gate (R^2={r2:.3f})")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
