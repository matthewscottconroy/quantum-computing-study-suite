#!/usr/bin/env python3
"""run_all.py -- milestones 4, 5 and 6 end to end.

    python run_all.py            # ~40 s
    python run_all.py --fast     # ~5 s, coarser statistics

Writes into results/:
    weight1.md              the 21 weight-1 errors, syndromes and corrections
    threshold.csv           p, shots, failures, p_L, stderr
    noisy.csv               the milestone-6 sweep
    logical_vs_physical.png the payoff plot
    noisy_extraction.png    milestone 6
    RESULTS.md              every number, rendered
"""

from __future__ import annotations

import argparse
import csv
import itertools
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import decode
import montecarlo as mc
import vizstyle
from steane_code import N_QUBITS, is_logical, is_stabilizer, syndrome, syndrome_to_int

vizstyle.use_style()
OUT = Path(__file__).resolve().parent / "results"

P_GRID = np.logspace(-4, np.log10(0.3), 12)
PAULIS = ("X", "Y", "Z")


def weight1_table():
    """Milestone 4: every weight-1 error is corrected, with its syndrome."""
    rows = []
    for q in range(N_QUBITS):
        for pauli in PAULIS:
            ex, ez = decode.single_qubit_error(q, pauli)
            sz = syndrome_to_int(syndrome(ex))      # Z-checks see X errors
            sx = syndrome_to_int(syndrome(ez))
            rx, rz = decode.correct(ex), decode.correct(ez)
            rows.append({
                "qubit": q, "pauli": pauli,
                "x_check": int(sx), "z_check": int(sz),
                "corrected": decode.corrects_perfectly(ex, ez),
                "residual_x": "".join(map(str, rx)),
                "residual_z": "".join(map(str, rz)),
            })
    return rows


def weight2_failures():
    """Find the weight-2 errors the distance-3 code cannot handle."""
    failures = []
    for (q1, p1), (q2, p2) in itertools.combinations(
            [(q, p) for q in range(N_QUBITS) for p in PAULIS], 2):
        if q1 == q2:
            continue
        ex1, ez1 = decode.single_qubit_error(q1, p1)
        ex2, ez2 = decode.single_qubit_error(q2, p2)
        ex, ez = ex1 ^ ex2, ez1 ^ ez2
        cls = (int(decode.classify(decode.correct(ex))),
               int(decode.classify(decode.correct(ez))))
        if 1 in cls:
            failures.append((f"{p1}{q1}", f"{p2}{q2}", cls))
    return failures


def sweep_perfect(shots_scale: float):
    pts = []
    for p in P_GRID:
        shots = max(10_000, int(mc.adaptive_shots(float(p)) * shots_scale))
        pts.append(mc.run_perfect(float(p), shots, seed=int(p * 1e9) + 1))
    return pts


def sweep_noisy(shots_scale: float):
    """p_m = p, one round vs three rounds with majority voting."""
    out = {1: [], 3: []}
    for rounds in (1, 3):
        for p in P_GRID:
            base = mc.adaptive_shots(float(p), c_guess=6.0 if rounds == 1 else 20.0)
            shots = max(10_000, int(base * shots_scale))
            bad, log = mc.run_noisy(float(p), shots, p_meas=float(p),
                                    rounds=rounds, seed=int(p * 1e9) + rounds)
            out[rounds].append((bad, log))
    return out


def plot_threshold(pts, thr, slope, c):
    p = np.array([pt.p for pt in pts])
    y = np.array([pt.rate for pt in pts])
    e = np.array([pt.stderr for pt in pts])
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.plot(p, p, ls="--", lw=1.4, color=vizstyle.INK_MUTED)
    ax.annotate("unencoded qubit,  $p_L = p$", xy=(p[2], p[2]),
                xytext=(6, 8), textcoords="offset points", fontsize=9,
                color=vizstyle.INK_2, ha="left", rotation=33, rotation_mode="anchor")
    fit_x = np.array([p.min(), 0.02])
    ax.plot(fit_x, c * fit_x ** slope, ls=":", lw=1.4, color=vizstyle.SERIES[2])
    ax.annotate(f"low-$p$ fit  $p_L = {c:.1f}\\,p^{{{slope:.2f}}}$",
                xy=(fit_x[0] * 4, c * (fit_x[0] * 4) ** slope), xytext=(8, -16),
                textcoords="offset points", fontsize=9, color=vizstyle.SERIES[2])
    mask = np.array([pt.failures > 0 for pt in pts])
    ax.errorbar(p[mask], y[mask], yerr=e[mask], fmt="o-", ms=6, lw=1.6, capsize=3,
                color=vizstyle.SERIES[0], mec=vizstyle.SURFACE, mew=0.8,
                label="Steane [[7,1,3]], perfect extraction")
    if not np.all(mask):
        ax.plot(p[~mask], [pt.stderr for pt in np.array(pts, dtype=object)[~mask]],
                "v", ms=6, color=vizstyle.SERIES[0], mfc="none",
                label="zero failures observed (upper bound)")
    if np.isfinite(thr):
        ax.plot([thr], [thr], "*", ms=15, color=vizstyle.SERIES[1], zorder=6)
        ax.annotate(f"pseudo-threshold\n$p^*$ = {thr:.3f}", xy=(thr, thr),
                    xytext=(10, -34), textcoords="offset points", fontsize=9.5,
                    color=vizstyle.SERIES[1], ha="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("physical error rate  $p$  (depolarising, per qubit)")
    ax.set_ylabel("logical error rate  $p_L$")
    ax.set_title("The payoff plot: encoding helps below the pseudo-threshold")
    ax.legend(loc="upper left")
    vizstyle.despine(ax)
    fig.savefig(OUT / "logical_vs_physical.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_noisy(perfect, noisy, slopes):
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    p = np.array([pt.p for pt in perfect])
    ax.plot(p, p, ls="--", lw=1.2, color=vizstyle.INK_MUTED)
    series = [
        ("perfect syndrome", [pt.rate for pt in perfect],
         [pt.stderr for pt in perfect], vizstyle.SERIES[0], slopes["perfect"]),
        ("$p_m = p$, 1 round", [b.rate for b, _ in noisy[1]],
         [b.stderr for b, _ in noisy[1]], vizstyle.SERIES[1], slopes[1]),
        ("$p_m = p$, 3 rounds + majority vote", [b.rate for b, _ in noisy[3]],
         [b.stderr for b, _ in noisy[3]], vizstyle.SERIES[2], slopes[3]),
    ]
    for label, y, e, colour, slope in series:
        y = np.array(y)
        m = y > 0
        ax.errorbar(p[m], y[m], yerr=np.array(e)[m], fmt="o-", ms=5.5, lw=1.6,
                    capsize=2.5, color=colour, mec=vizstyle.SURFACE, mew=0.7,
                    label=f"{label}   (slope {slope:.2f})")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("physical error rate  $p$")
    ax.set_ylabel("failure rate  (residual is not a stabiliser)")
    ax.set_title("Measurement error destroys the $p^2$ law; repetition restores it")
    ax.legend(loc="upper left")
    vizstyle.despine(ax)
    fig.savefig(OUT / "noisy_extraction.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    scale = 0.02 if args.fast else 1.0
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    print("M4  weight-1 and weight-2 errors ...")
    w1 = weight1_table()
    w2 = weight2_failures()

    print("M5  threshold sweep ...")
    perfect = sweep_perfect(scale)
    slope, c, n_fit = mc.fit_slope(perfect)
    thr = mc.pseudo_threshold(perfect)

    print("M6  noisy extraction sweep ...")
    noisy = sweep_noisy(scale)
    slopes = {"perfect": slope,
              1: mc.fit_slope([b for b, _ in noisy[1]])[0],
              3: mc.fit_slope([b for b, _ in noisy[3]])[0]}

    print("    plots ...")
    plot_threshold(perfect, thr, slope, c)
    plot_noisy(perfect, noisy, slopes)

    with (OUT / "threshold.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["p", "shots", "failures", "p_logical", "stderr"])
        w.writerows([[pt.p, pt.shots, pt.failures, pt.rate, pt.stderr] for pt in perfect])
    with (OUT / "noisy.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rounds", "p", "p_meas", "shots", "not_restored",
                    "rate_not_restored", "logical_only", "rate_logical_only"])
        for rounds, rows in noisy.items():
            for bad, log in rows:
                w.writerow([rounds, bad.p, bad.p, bad.shots, bad.failures,
                            bad.rate, log.failures, log.rate])
    with (OUT / "weight1.md").open("w") as fh:
        fh.write("# All 21 weight-1 errors (milestones 3 and 4)\n\n")
        fh.write("| error | X-checks | Z-checks | corrected |\n|---|---:|---:|:--:|\n")
        for r in w1:
            fh.write(f"| {r['pauli']}{r['qubit']} | {r['x_check']} | {r['z_check']} "
                     f"| {'yes' if r['corrected'] else 'NO'} |\n")

    with (OUT / "RESULTS.md").open("w") as fh:
        w = fh.write
        w("# Project 3 -- reference-solution results\n\n")
        w(f"Generated by `run_all.py{' --fast' if args.fast else ''}` "
          f"in {time.time() - t0:.1f} s.\n\n")
        w("## M4 -- correction\n\n")
        w(f"- all **{len(w1)}** weight-1 Pauli errors are corrected "
          f"({sum(r['corrected'] for r in w1)}/{len(w1)}); "
          "the syndromes are in `weight1.md`\n")
        w(f"- **{len(w2)}** of the weight-2 two-site errors cause a logical failure\n")
        for a, b, cls in w2[:4]:
            w(f"  - `{a} {b}` -> sector classes {cls} (1 = logical)\n")
        w("\n## M5 -- logical vs physical error rate (perfect extraction)\n\n")
        w("| p | shots | failures | p_L | binomial stderr | p_L / p |\n")
        w("|---:|---:|---:|---:|---:|---:|\n")
        for pt in perfect:
            w(f"| {pt.p:.3e} | {pt.shots:,} | {pt.failures:,} | {pt.rate:.3e} "
              f"| {pt.stderr:.1e} | {pt.rate / pt.p:.3f} |\n")
        w(f"\n- low-p fit over the {n_fit} points with p <= 0.01: "
          f"**p_L = {c:.2f} p^{slope:.3f}** (criterion: slope 2.0 +- 0.2)\n")
        w(f"- pseudo-threshold (p_L = p crossing): **p* = {thr:.4f}** "
          f"({100 * thr:.2f}%)\n")
        w(f"- smallest-p point has **{perfect[0].failures}** failure events "
          f"in {perfect[0].shots:,} shots\n")
        w("\n## M6 -- noisy syndrome extraction (p_m = p)\n\n")
        w(f"| p | 1 round: not restored | 3 rounds: not restored "
          f"| 1 round: logical only | 3 rounds: logical only |\n")
        w("|---:|---:|---:|---:|---:|\n")
        for i, pt in enumerate(perfect):
            b1, l1 = noisy[1][i]
            b3, l3 = noisy[3][i]
            w(f"| {pt.p:.3e} | {b1.rate:.3e} | {b3.rate:.3e} "
              f"| {l1.rate:.3e} | {l3.rate:.3e} |\n")
        w(f"\n- low-p slope, perfect extraction: **{slopes['perfect']:.2f}**\n")
        w(f"- low-p slope, 1 noisy round: **{slopes[1]:.2f}** "
          "(the quadratic law is gone)\n")
        w(f"- low-p slope, 3 rounds + majority vote: **{slopes[3]:.2f}** "
          "(restored)\n")

    print(f"\ndone in {time.time() - t0:.1f} s -> {OUT}")
    print(f"  slope (perfect) = {slope:.3f}, c = {c:.2f}, "
          f"pseudo-threshold = {thr:.4f}")
    print(f"  slope 1 noisy round = {slopes[1]:.3f}, 3 rounds = {slopes[3]:.3f}")
    print(f"  weight-1 corrected: {sum(r['corrected'] for r in w1)}/{len(w1)}; "
          f"weight-2 logical failures: {len(w2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
