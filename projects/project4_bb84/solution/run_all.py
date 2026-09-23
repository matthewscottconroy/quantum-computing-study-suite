#!/usr/bin/env python3
"""run_all.py -- every milestone artefact for project 4.

    python run_all.py            # ~25 s

Writes into results/:
    qber_vs_eta.csv     milestone 2 verification
    finite_size.csv     milestone 3 ROC-style analysis
    key_rate.csv        milestone 5 secret-key fractions
    key_rate.png        the milestone-5 figure
    finite_size.png     the milestone-3 figure
    RESULTS.md          all of it, rendered, plus the end-to-end ledger
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import bb84
import infotheory as it
import protocol
import quantum
import vizstyle

vizstyle.use_style()
OUT = Path(__file__).resolve().parent / "results"

N_QBER = 400_000
ETAS_CHECK = (0.0, 0.25, 0.5, 1.0)
SAMPLE_SIZES = (50, 200, 1000)
ETAS_ROC = (0.0, 0.10, 0.25, 0.40, 0.4091, 0.45, 0.50)
THRESHOLD = 0.11


def qber_table():
    rows = []
    for eta in ETAS_CHECK:
        run = bb84.simulate(N_QBER, eta=eta, seed=1234)
        view = bb84.sift(run, seed=99)
        rows.append({
            "eta": eta,
            "sifted_fraction": view.n_sifted / len(run),
            "qber_true": bb84.true_qber(run),
            "qber_sampled": view.qber,
            "qber_theory": eta / 4.0,
            "eve_agreement": bb84.eve_agreement_on_sifted(run),
            "n_sample": view.n_sample,
        })
    return rows


def finite_size_table():
    rows = []
    for n_sample in SAMPLE_SIZES:
        for eta in ETAS_ROC:
            rows.append({
                "n_sample": n_sample, "eta": eta, "qber": eta / 4.0,
                "p_abort": protocol.detection_probability(n_sample, eta, THRESHOLD,
                                                          seed=7),
                "p_abort_noisy_channel": protocol.detection_probability(
                    n_sample, eta, THRESHOLD, p_channel=0.02, seed=7),
            })
    return rows


def key_rate_curves():
    etas = np.linspace(0.0, 1.0, 201)
    q = etas / 4.0
    ind = np.array([it.secret_fraction(qq, it.eve_info_individual(e))
                    for qq, e in zip(q, etas)])
    con = np.array([it.secret_fraction(qq, it.eve_info_conservative(qq))
                    for qq in q])
    return etas, q, ind, con


def simulated_points():
    pts = []
    for eta in (0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0):
        row = {"eta": eta}
        for acc in ("individual", "conservative"):
            ledger, key, _, _ = protocol.run_protocol(
                200_000, eta, accounting=acc, threshold=1.01, seed=2024)
            row[acc] = ledger.n_secret / max(ledger.n_key_sift, 1) if False else \
                ledger.n_secret / max(ledger.n_corrected, 1)
            row[acc + "_bits"] = ledger.n_secret
            row["qber"] = ledger.qber
        pts.append(row)
    return pts


def plot_key_rate(etas, ind, con, pts):
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    ax.plot(etas, ind, lw=2.0, color=vizstyle.SERIES[0],
            label=r"individual attack,  $I_E = \eta/2$")
    ax.plot(etas, con, lw=2.0, color=vizstyle.SERIES[1],
            label=r"conservative one-way bound,  $I_E = h(Q)$")
    ax.plot([p["eta"] for p in pts], [p["individual"] for p in pts], "o",
            ms=7, mfc="none", mew=1.4, color=vizstyle.SERIES[0])
    ax.plot([p["eta"] for p in pts], [p["conservative"] for p in pts], "s",
            ms=6.5, mfc="none", mew=1.4, color=vizstyle.SERIES[1])
    ax.plot([], [], "o", ms=7, mfc="none", color=vizstyle.INK_MUTED,
            label="simulated runs, $n = 200{,}000$")

    for f, style, colour in ((1.0, ":", vizstyle.SERIES[2]),
                             (1.1, "--", vizstyle.SERIES[1])):
        q0 = it.zero_rate_qber(f)
        eta0 = 4 * q0
        ax.axvline(eta0, ls=style, lw=1.3, color=colour)
        ax.annotate(f"$f={f}$:  $\\eta$={eta0:.3f},  Q={100 * q0:.2f}%",
                    xy=(eta0, 0.78 if f == 1.0 else 0.88), xytext=(6, 0),
                    textcoords="offset points", fontsize=9, color=colour)
    ax.set_xlabel(r"Eve's interception rate  $\eta$")
    ax.set_ylabel(r"secret-key fraction  $\ell / n_{\rm sift}$")
    ax.set_title("What the accounting assumption is worth")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.02, 1.0)
    ax.legend(loc="lower left")
    vizstyle.despine(ax)
    secax = ax.secondary_xaxis("top", functions=(lambda e: e / 4, lambda q: 4 * q))
    secax.set_xlabel("QBER  $Q = \\eta/4$")
    fig.savefig(OUT / "key_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_finite_size(rows):
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    for i, n_sample in enumerate(SAMPLE_SIZES):
        sel = [r for r in rows if r["n_sample"] == n_sample]
        ax.plot([r["eta"] for r in sel], [r["p_abort"] for r in sel], "o-",
                ms=6, lw=1.8, color=vizstyle.SERIES[i], mec=vizstyle.SURFACE,
                mew=0.8, label=f"{n_sample} bits compared")
    q0 = it.zero_rate_qber(1.1)
    ax.axvline(4 * q0, ls="--", lw=1.3, color=vizstyle.INK_MUTED)
    ax.annotate("key rate reaches zero here\n"
                f"($Q = {100 * q0:.2f}\\%$, $\\eta = {4 * q0:.3f}$)",
                xy=(4 * q0, 0.55), xytext=(8, 0), textcoords="offset points",
                fontsize=9, color=vizstyle.INK_2)
    ax.axhline(0.5, ls=":", lw=1.0, color=vizstyle.INK_MUTED)
    ax.set_xlabel(r"Eve's interception rate  $\eta$")
    ax.set_ylabel(f"P(estimated QBER > {THRESHOLD:.0%})")
    ax.set_title("Finite-size statistics: how sharp is the abort decision?")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="upper left")
    vizstyle.despine(ax)
    fig.savefig(OUT / "finite_size.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    print("M1/M2  QBER vs eta ...")
    qber = qber_table()
    print("M3     finite-size analysis ...")
    fs = finite_size_table()
    print("M5     key-rate curves ...")
    etas, q, ind, con = key_rate_curves()
    pts = simulated_points()

    print("       plots ...")
    plot_key_rate(etas, ind, con, pts)
    plot_finite_size(fs)

    with (OUT / "qber_vs_eta.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qber[0]))
        w.writeheader()
        w.writerows(qber)
    with (OUT / "finite_size.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fs[0]))
        w.writeheader()
        w.writerows(fs)
    with (OUT / "key_rate.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["eta", "qber", "secret_fraction_individual",
                    "secret_fraction_conservative"])
        w.writerows(np.stack([etas, q, ind, con], axis=1).tolist())

    ledgers = {acc: protocol.run_protocol(100_000, 0.2, accounting=acc, seed=11)[0]
               for acc in ("individual", "conservative")}
    zero = {acc: protocol.run_protocol(100_000, 1.0, accounting=acc,
                                       threshold=1.01, seed=11)[0]
            for acc in ("individual", "conservative")}

    with (OUT / "RESULTS.md").open("w") as fh:
        w = fh.write
        w("# Project 4 -- reference-solution results\n\n")
        w(f"Generated by `run_all.py` in {time.time() - t0:.1f} s.\n\n")

        w("## M1 -- the quantum mechanics, from Statevector\n\n")
        w("| prepared | measured in Z | measured in X |\n|---|---|---|\n")
        for (bit, basis), label in quantum.STATES.items():
            pz = quantum.measurement_distribution(bit, basis, 0)
            px = quantum.measurement_distribution(bit, basis, 1)
            w(f"| {label} | {pz[0]:.2f} / {pz[1]:.2f} | {px[0]:.2f} / {px[1]:.2f} |\n")

        w(f"\n## M2 -- QBER vs eta  (n = {N_QBER:,} per row)\n\n")
        w("| eta | sifted fraction | QBER (all sifted) | QBER (10% sample) "
          "| theory eta/4 | P(Eve bit = Alice bit) |\n")
        w("|---:|---:|---:|---:|---:|---:|\n")
        for r in qber:
            agree = "n/a" if not np.isfinite(r["eve_agreement"]) \
                else f"{r['eve_agreement']:.4f}"
            w(f"| {r['eta']:.2f} | {r['sifted_fraction']:.4f} | "
              f"{r['qber_true']:.5f} | {r['qber_sampled']:.5f} | "
              f"{r['qber_theory']:.5f} | {agree} |\n")

        w(f"\n## M3 -- finite-size abort statistics (threshold {THRESHOLD:.0%})\n\n")
        w("| n compared | eta | true QBER | P(abort) | P(abort), 2% channel noise |\n")
        w("|---:|---:|---:|---:|---:|\n")
        for r in fs:
            w(f"| {r['n_sample']} | {r['eta']:.4f} | {r['qber']:.4f} | "
              f"{r['p_abort']:.3f} | {r['p_abort_noisy_channel']:.3f} |\n")

        w("\n## M4/M5 -- end-to-end ledger, eta = 0.2, n = 100,000\n\n")
        for acc, ledger in ledgers.items():
            w(f"### {acc}\n\n```\n{ledger.render()}\n```\n\n")
        w("### Sanity: eta = 1.0 (abort disabled so the accounting can speak)\n\n")
        w("| accounting | QBER | leak_EC/bit | I_E/bit | secret fraction | key bits |\n")
        w("|---|---:|---:|---:|---:|---:|\n")
        for acc, ledger in zero.items():
            w(f"| {acc} | {ledger.qber:.4f} | {ledger.leak_ec_per_bit:.4f} | "
              f"{ledger.eve_info_per_bit:.4f} | {ledger.secret_fraction:.4f} "
              f"| {ledger.n_secret} |\n")

        w("\n## M5 -- secret-key fraction vs eta\n\n")
        w("| eta | QBER | individual (theory) | individual (simulated) "
          "| conservative (theory) | conservative (simulated) |\n")
        w("|---:|---:|---:|---:|---:|---:|\n")
        for p in pts:
            e = p["eta"]
            ti = it.secret_fraction(e / 4, it.eve_info_individual(e))
            tc = it.secret_fraction(e / 4, it.eve_info_conservative(e / 4))
            w(f"| {e:.2f} | {p['qber']:.4f} | {ti:.4f} | {p['individual']:.4f} "
              f"| {tc:.4f} | {p['conservative']:.4f} |\n")
        w(f"\n- conservative rate reaches zero at QBER **{100 * it.zero_rate_qber(1.0):.2f}%** "
          f"(eta = {4 * it.zero_rate_qber(1.0):.3f}) with f = 1, the textbook "
          "`r = 1 - 2h(Q)` threshold\n")
        w(f"- with the realistic f = 1.1 used here it reaches zero earlier, at "
          f"QBER **{100 * it.zero_rate_qber(1.1):.2f}%** "
          f"(eta = {4 * it.zero_rate_qber(1.1):.3f})\n")

    print(f"\ndone in {time.time() - t0:.1f} s -> {OUT}")
    for acc, ledger in ledgers.items():
        print(f"  eta=0.2 {acc:13s}: QBER {ledger.qber:.4f}, "
              f"fraction {ledger.secret_fraction:.4f}, key {ledger.n_secret:,} bits")
    for acc, ledger in zero.items():
        print(f"  eta=1.0 {acc:13s}: fraction {ledger.secret_fraction:.4f}, "
              f"key {ledger.n_secret} bits")
    print(f"  zero-rate QBER: f=1.0 -> {100 * it.zero_rate_qber(1.0):.2f}% "
          f"(eta {4 * it.zero_rate_qber(1.0):.3f}); "
          f"f=1.1 -> {100 * it.zero_rate_qber(1.1):.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
