#!/usr/bin/env python3
"""run_curve.py -- milestones 4 and 5, end to end.

    python run_curve.py            # everything (~2 minutes)
    python run_curve.py --quick    # skip the noisy backend runs (~10 seconds)

Writes into ``results/``:
    curve.csv            exact / noiseless-VQE energies for every ansatz
    noisy.csv            noisy-VQE energies, 3 seeds per distance
    error_budget.csv     the milestone-5 split at three geometries
    optimisers.csv       COBYLA vs parameter-shift evaluation counts
    h2_dissociation.png  the milestone-4 figure
    error_budget.png     the milestone-5 figure
    RESULTS.md           every table above, rendered
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import ansatz as ansatz_mod
import hamiltonians as H
import vizstyle
import vqe

vizstyle.use_style()

OUT = Path(__file__).resolve().parent / "results"
NOISY_SEEDS = (11, 23, 47)
# The noisy sweep costs ~0.1 s per circuit; every second tabulated distance is
# plenty to show the penalty trend and keeps the whole script near 100 s.
NOISY_DISTANCES = (0.300, 0.500, 0.700, 0.735, 0.900, 1.100, 1.500, 2.000, 2.500)

# Categorical slots, assigned once per entity and never recycled (vizstyle.py).
C_EXACT = vizstyle.INK
C_NOISY = vizstyle.SERIES[1]        # orange
C_BAND = vizstyle.SERIES[2]         # aqua
C_ANSATZ = {"hardware_efficient": vizstyle.SERIES[0],
            "real_pair": vizstyle.SERIES[2],
            "ucc_single": vizstyle.SERIES[6],
            "product": vizstyle.SERIES[3]}


def write_csv(path: Path, header, rows) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- noiseless
def noiseless_curve():
    """Exact + noiseless VQE for every ansatz at every tabulated distance."""
    rows = []
    for d in H.DISTANCES:
        ham = H.hamiltonian(d)
        exact = H.exact_energy(d)
        nuc = H.nuclear_repulsion(d)
        rec = {"d": d, "exact_el": exact, "e_nuc": nuc, "exact_total": exact + nuc}
        for a in ansatz_mod.all_ansatze(include_control=True):
            res = vqe.run_gradient(a, ham)
            if a.name == "hardware_efficient":
                # 8 parameters: one L-BFGS pass can stall on a plateau, so
                # take the better of a gradient run and a COBYLA run.
                alt = vqe.run_cobyla(a, ham, maxiter=500)
                if alt.energy < res.energy:
                    res = alt
            rec[a.name] = res.energy
            rec[a.name + "_nfev"] = res.n_circuits
        rows.append(rec)
    return rows


def optimiser_comparison():
    """Milestone 3: COBYLA vs parameter-shift gradient, at equilibrium."""
    ham = H.hamiltonian(0.735)
    exact = H.exact_energy(0.735)
    rows = []
    for a in ansatz_mod.all_ansatze(include_control=True):
        c = vqe.run_cobyla(a, ham, maxiter=500)
        g = vqe.run_gradient(a, ham)
        p = vqe.run_plain_gradient_descent(a, ham, lr=0.4, maxiter=300)
        rows.append([a.name, a.num_parameters,
                     c.n_circuits, 1e3 * (c.energy - exact),
                     g.n_circuits, 1e3 * (g.energy - exact),
                     p.n_circuits, 1e3 * (p.energy - exact)])
    return rows


# -------------------------------------------------------------------- noisy
def noisy_curve(distances):
    import noisy  # imported lazily: only this path needs qiskit-ibm-runtime
    a = ansatz_mod.get("ucc_single")
    rows = []
    for d in distances:
        ham = H.hamiltonian(d)
        energies, stderrs = [], []
        for seed in NOISY_SEEDS:
            r = noisy.run_noisy_vqe(a, ham, seed_simulator=seed, shots=2048, maxiter=40)
            energies.append(r.energy)
            stderrs.append(r.stderr)
        e = np.array(energies)
        rows.append({"d": d, "mean": e.mean(), "sd": e.std(ddof=1),
                     "shot_stderr": float(np.mean(stderrs)),
                     "exact": H.exact_energy(d),
                     "penalty_mHa": 1e3 * (e.mean() - H.exact_energy(d))})
    return rows


# ------------------------------------------------------------ error budget
def error_budget(distances, noisy_rows):
    """Milestone 5: split the total error into four additive contributions.

    expressibility  grid/global minimum of the ansatz   - exact
    optimisation    converged VQE energy                - grid minimum
    sampling        finite-precision estimator          - noiseless converged
    hardware        fake-backend VQE                    - finite-precision
    """
    noisy_by_d = {r["d"]: r for r in noisy_rows}
    rows = []
    prec = 1.0 / np.sqrt(2048)          # shot noise of a 2048-shot estimate
    for d in distances:
        ham = H.hamiltonian(d)
        exact = H.exact_energy(d)
        for name in ("ucc_single", "product"):
            a = ansatz_mod.get(name)
            truth = vqe.EnergyFunction(a, ham)          # exact, precision 0
            floor, _ = vqe.grid_minimum(a, ham)
            # take the better of the two noiseless optimisers: a practitioner
            # would, and it stops a single L-BFGS stall from being reported as
            # an "optimisation error" of 150 mHa.
            conv = min(vqe.run_gradient(a, ham).energy,
                       vqe.run_cobyla(a, ham, maxiter=500).energy)
            # TRAP: never report the optimiser's final *noisy* value as the VQE
            # energy -- that number is one shot-noise draw, not an energy, and
            # with a fixed estimator seed it is the same draw for every ansatz.
            # Report the true energy at the parameters shot noise led you to.
            samp = float(np.mean([
                truth(vqe.run_cobyla(a, ham, precision=prec, seed=s, maxiter=80).x)
                for s in (101, 202, 303)]))
            hw = noisy_by_d[d]["mean"] if (name == "ucc_single" and d in noisy_by_d) else np.nan
            rows.append({
                "d": d, "ansatz": name,
                "expressibility": 1e3 * (floor - exact),
                "optimisation": 1e3 * (conv - floor),
                "sampling": 1e3 * (samp - conv),
                "hardware": 1e3 * (hw - samp) if np.isfinite(hw) else np.nan,
                "total": 1e3 * ((hw if np.isfinite(hw) else samp) - exact),
            })
    return rows


def schmidt_table(distances):
    """Schmidt coefficients of the exact ground state -- why stretching hurts."""
    rows = []
    for d in distances:
        psi = H.exact_ground_state(d).reshape(2, 2)   # (q1, q0)
        s = np.linalg.svd(psi, compute_uv=False)
        s = s / np.linalg.norm(s)
        ent = float(-sum(x ** 2 * np.log2(x ** 2) for x in s if x > 1e-15))
        rows.append([d, float(s[0]), float(s[1]), ent])
    return rows


# ------------------------------------------------------------------- plots
def plot_curve(rows, noisy_rows):
    d = np.array([r["d"] for r in rows])
    exact = np.array([r["exact_total"] for r in rows])
    nuc = {r["d"]: r["e_nuc"] for r in rows}

    fig, (ax, axr) = plt.subplots(
        2, 1, figsize=(8.2, 7.4), sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.09})

    ax.plot(d, exact, "-", color=C_EXACT, lw=1.8, zorder=3,
            label="exact diagonalisation")
    # real_pair and ucc_single land on the exact curve to machine precision, so
    # their markers sit underneath ucc_single's; the residual panel separates them.
    for name in ansatz_mod.SPEC_ANSATZE:
        y = np.array([r[name] + r["e_nuc"] for r in rows])
        ax.plot(d, y, "o", ms=6, mfc="none", mew=1.3, color=C_ANSATZ[name],
                zorder=4, label=f"noiseless VQE - {name}")
    if noisy_rows:
        nd = np.array([r["d"] for r in noisy_rows])
        ny = np.array([r["mean"] + nuc[r["d"]] for r in noisy_rows])
        ne = np.array([r["sd"] for r in noisy_rows])
        ax.errorbar(nd, ny, yerr=ne, fmt="s", ms=6, color=C_NOISY, capsize=3,
                    lw=1.2, mec=vizstyle.SURFACE, mew=0.8, zorder=5,
                    label="noisy VQE - FakeManilaV2, 2048 shots")

    d_eq = H.equilibrium_distance()
    ax.axvline(d_eq, color=vizstyle.INK_MUTED, ls=":", lw=1.0, zorder=1)
    ax.annotate(f"equilibrium {d_eq:.3f} " + r"$\AA$",
                xy=(d_eq, exact.min()), xytext=(d_eq + 0.10, exact.min() - 0.035),
                fontsize=9, color=vizstyle.INK_2)
    ax.set_ylabel("total energy  (hartree)")
    ax.set_title(r"H$_2$ dissociation curve, STO-3G, 2-qubit VQE")
    ax.legend(loc="lower right", ncol=1)
    vizstyle.despine(ax)

    # residual panel: the accuracy story, on its own scale
    axr.axhspan(1e-10, H.CHEMICAL_ACCURACY * 1e3, color=C_BAND, alpha=0.13, zorder=0)
    axr.axhline(H.CHEMICAL_ACCURACY * 1e3, color=C_BAND, lw=1.6, zorder=1)
    axr.text(d[-1], H.CHEMICAL_ACCURACY * 1e3 * 1.9, "chemical accuracy, 1.6 mHa",
             ha="right", va="bottom", fontsize=9, color=vizstyle.INK_2)
    for name in ansatz_mod.SPEC_ANSATZE:
        err = np.array([abs(r[name] - r["exact_el"]) * 1e3 for r in rows])
        axr.semilogy(d, np.maximum(err, 1e-9), "-o", ms=4.5, lw=1.2, mfc="none",
                     mew=1.1, color=C_ANSATZ[name], zorder=3)
    if noisy_rows:
        axr.semilogy([r["d"] for r in noisy_rows],
                     [abs(r["penalty_mHa"]) for r in noisy_rows], "-s", ms=5,
                     lw=1.2, color=C_NOISY, mec=vizstyle.SURFACE, mew=0.7, zorder=4)
    # direct labels instead of a second legend box
    last = d[-1]
    if noisy_rows:
        axr.annotate("noisy", xy=(noisy_rows[-1]["d"], abs(noisy_rows[-1]["penalty_mHa"])),
                     xytext=(-4, 7), textcoords="offset points", fontsize=9,
                     ha="right", color=C_NOISY)
    axr.annotate("hardware_efficient",
                 xy=(last, max(abs(rows[-1]["hardware_efficient"] - rows[-1]["exact_el"]) * 1e3, 1e-9)),
                 xytext=(-4, 6), textcoords="offset points", fontsize=9,
                 ha="right", color=C_ANSATZ["hardware_efficient"])
    axr.annotate("ucc_single / real_pair  (machine precision)", xy=(d[3], 1e-9),
                 xytext=(0, 5), textcoords="offset points", fontsize=9,
                 color=C_ANSATZ["ucc_single"])
    axr.set_xlabel(r"bond distance  ($\AA$)")
    axr.set_ylabel("|error vs exact|  (mHa)")
    axr.set_ylim(1e-10, 3e3)
    vizstyle.despine(axr)
    fig.savefig(OUT / "h2_dissociation.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_budget(rows):
    """Grouped bars, log scale.

    NOT stacked: the four contributions span thirteen orders of magnitude, and
    a stacked bar on a log axis is unreadable (every segment starts at the
    axis floor, so the small ones vanish and every bar looks full height).
    Grouped bars let each term be read against the same scale.
    """
    keys = ["expressibility", "optimisation", "sampling", "hardware"]
    colours = [vizstyle.SERIES[i] for i in range(4)]
    floor = 1e-6
    labels = [f"{r['ansatz']}\n{r['d']:.3f} " + r"$\AA$" for r in rows]
    vals = np.array([[abs(r[k]) if np.isfinite(r[k]) else np.nan for k in keys]
                     for r in rows])

    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    x = np.arange(len(rows))
    w = 0.2
    for j, (k, c) in enumerate(zip(keys, colours)):
        y = vals[:, j]
        drawn = np.where(np.isnan(y), np.nan, np.maximum(y, floor))
        bars = ax.bar(x + (j - 1.5) * w, drawn, width=w * 0.88, color=c,
                      label=k, edgecolor=vizstyle.SURFACE, linewidth=1.2)
        for xi, (bar, raw) in enumerate(zip(bars, y)):
            if np.isnan(raw):
                ax.text(bar.get_x() + bar.get_width() / 2, floor * 1.4, "n/a",
                        ha="center", va="bottom", fontsize=7.5,
                        color=vizstyle.INK_MUTED, rotation=90)
            else:
                txt = "<1e-6" if raw < floor else f"{raw:.3g}"
                ax.text(bar.get_x() + bar.get_width() / 2, max(raw, floor) * 1.35,
                        txt, ha="center", va="bottom", fontsize=7.5,
                        color=vizstyle.INK_2, rotation=90)
    ax.axhline(H.CHEMICAL_ACCURACY * 1e3, color=vizstyle.INK, ls="--", lw=1.2)
    ax.text(len(rows) - 0.45, H.CHEMICAL_ACCURACY * 1e3 * 1.25, "chemical accuracy",
            fontsize=9, ha="right", color=vizstyle.INK_2)
    ax.set_yscale("log")
    ax.set_ylim(floor * 0.6, 5e3)
    ax.set_xticks(x, labels)
    ax.set_ylabel("|error contribution|  (mHa)")
    ax.set_title("Where the VQE error comes from (grouped, log scale)")
    ax.legend(ncol=4, loc="upper left")
    ax.grid(axis="x", visible=False)
    vizstyle.despine(ax)
    fig.savefig(OUT / "error_budget.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# -------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip the noisy backend runs")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    print("M4  noiseless curve ...")
    rows = noiseless_curve()
    write_csv(OUT / "curve.csv",
              ["d_angstrom", "exact_electronic", "e_nuc", "exact_total"]
              + [n for a in ansatz_mod.all_ansatze(True) for n in (a.name, a.name + "_circuits")],
              [[r["d"], r["exact_el"], r["e_nuc"], r["exact_total"]]
               + [v for a in ansatz_mod.all_ansatze(True)
                  for v in (r[a.name], r[a.name + "_nfev"])] for r in rows])

    print("M3  optimiser comparison ...")
    opt = optimiser_comparison()
    write_csv(OUT / "optimisers.csv",
              ["ansatz", "n_params", "cobyla_circuits", "cobyla_err_mHa",
               "psr_lbfgs_circuits", "psr_lbfgs_err_mHa",
               "psr_gd_circuits", "psr_gd_err_mHa"], opt)

    noisy_rows = []
    if not args.quick:
        print("M4  noisy curve (FakeManilaV2) ...")
        noisy_rows = noisy_curve(NOISY_DISTANCES)
        write_csv(OUT / "noisy.csv",
                  ["d_angstrom", "mean_energy", "sd_over_seeds",
                   "mean_shot_stderr", "exact_electronic", "penalty_mHa"],
                  [[r["d"], r["mean"], r["sd"], r["shot_stderr"], r["exact"],
                    r["penalty_mHa"]] for r in noisy_rows])

    print("M5  error budget ...")
    budget_d = (0.500, 0.735, 2.000)   # short, equilibrium, stretched
    budget = error_budget(budget_d, noisy_rows)
    write_csv(OUT / "error_budget.csv",
              ["d_angstrom", "ansatz", "expressibility_mHa", "optimisation_mHa",
               "sampling_mHa", "hardware_mHa", "total_mHa"],
              [[r["d"], r["ansatz"], r["expressibility"], r["optimisation"],
                r["sampling"], r["hardware"], r["total"]] for r in budget])

    schmidt = schmidt_table(H.DISTANCES)
    write_csv(OUT / "schmidt.csv",
              ["d_angstrom", "lambda_1", "lambda_2", "entanglement_entropy_bits"],
              schmidt)

    print("     plots ...")
    plot_curve(rows, noisy_rows)
    plot_budget(budget)

    # ------------------------------------------------------------ RESULTS.md
    worst = max(max(abs(r[n] - r["exact_el"]) for n in ansatz_mod.SPEC_ANSATZE)
                for r in rows)
    vqe_curve = {r["d"]: r["ucc_single"] + r["e_nuc"] for r in rows}
    d_eq_vqe = H.equilibrium_distance(vqe_curve)
    d_eq_exact = H.equilibrium_distance()

    with (OUT / "RESULTS.md").open("w") as fh:
        w = fh.write
        w("# Project 1 -- reference-solution results\n\n")
        w(f"Generated by `run_curve.py` in {time.time() - t0:.1f} s"
          f"{' (--quick, noisy runs skipped)' if args.quick else ''}.\n\n")
        w("## Headline numbers\n\n")
        w(f"- exact electronic energy at 0.735 A: **{H.exact_energy(0.735):.6f} Ha** "
          "(spec anchor -1.857275)\n")
        w(f"- exact total energy at 0.735 A: **{H.total_energy(0.735):.6f} Ha**\n")
        w(f"- equilibrium distance, exact curve: **{d_eq_exact:.3f} A**; "
          f"from the VQE curve: **{d_eq_vqe:.3f} A** "
          f"(difference {abs(d_eq_vqe - d_eq_exact):.3f} A, criterion < 0.05 A)\n")
        w(f"- worst noiseless-VQE error over all 17 distances x 3 spec ansaetze: "
          f"**{worst * 1e3:.2e} mHa** (chemical accuracy = 1.6 mHa)\n\n")

        w("## M3 -- optimiser comparison at 0.735 A\n\n")
        w("| ansatz | params | COBYLA circuits | err (mHa) | "
          "param-shift + L-BFGS circuits | err (mHa) | plain GD circuits | err (mHa) |\n")
        w("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in opt:
            w(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:+.2e} | {r[4]} | {r[5]:+.2e} "
              f"| {r[6]} | {r[7]:+.2e} |\n")
        w("\n`circuits` counts every circuit actually executed, so the "
          "parameter-shift columns already pay their 2 circuits per parameter "
          "per gradient.\n\n")

        w("## M4 -- noiseless accuracy at every distance\n\n")
        w("| d (A) | exact total (Ha) | ucc_single err (mHa) | real_pair err (mHa) "
          "| hardware_efficient err (mHa) |\n|---:|---:|---:|---:|---:|\n")
        for r in rows:
            w(f"| {r['d']:.3f} | {r['exact_total']:.6f} | "
              f"{1e3 * (r['ucc_single'] - r['exact_el']):+.2e} | "
              f"{1e3 * (r['real_pair'] - r['exact_el']):+.2e} | "
              f"{1e3 * (r['hardware_efficient'] - r['exact_el']):+.2e} |\n")

        if noisy_rows:
            w("\n## M4 -- noise penalty (FakeManilaV2, 2048 shots, 3 seeds)\n\n")
            w("| d (A) | noisy mean (Ha) | sd over seeds (Ha) | penalty (mHa) |\n")
            w("|---:|---:|---:|---:|\n")
            for r in noisy_rows:
                w(f"| {r['d']:.3f} | {r['mean']:.6f} | {r['sd']:.2e} | "
                  f"{r['penalty_mHa']:+.1f} |\n")
            pens = [r["penalty_mHa"] for r in noisy_rows]
            w(f"\nPenalty range: **{min(pens):+.1f} to {max(pens):+.1f} mHa** "
              f"(mean {np.mean(pens):+.1f}).\n")

        w("\n## M5 -- error budget\n\n")
        w("| d (A) | ansatz | expressibility | optimisation | sampling | hardware | total |\n")
        w("|---:|---|---:|---:|---:|---:|---:|\n")
        for r in budget:
            hw = "n/a" if not np.isfinite(r["hardware"]) else f"{r['hardware']:+.2f}"
            w(f"| {r['d']:.3f} | {r['ansatz']} | {r['expressibility']:+.2e} | "
              f"{r['optimisation']:+.2e} | {r['sampling']:+.3f} | {hw} | "
              f"{r['total']:+.3f} |\n")
        w("\nAll entries in mHa.\n\n")

        w("## M5 -- Schmidt coefficients of the exact ground state\n\n")
        w("| d (A) | lambda_1 | lambda_2 | entanglement entropy (bits) |\n")
        w("|---:|---:|---:|---:|\n")
        for d, l1, l2, s in schmidt:
            w(f"| {d:.3f} | {l1:.6f} | {l2:.6f} | {s:.4f} |\n")

    print(f"\ndone in {time.time() - t0:.1f} s -> {OUT}")
    print(f"  equilibrium: exact {d_eq_exact:.3f} A, VQE {d_eq_vqe:.3f} A")
    print(f"  worst noiseless error: {worst * 1e3:.3e} mHa "
          f"({'PASS' if worst < H.CHEMICAL_ACCURACY else 'FAIL'} chemical accuracy)")
    if noisy_rows:
        pens = [r["penalty_mHa"] for r in noisy_rows]
        print(f"  noise penalty: {min(pens):+.1f} .. {max(pens):+.1f} mHa")
    return 0


if __name__ == "__main__":   # forkserver guard (Python 3.14 + Aer)
    raise SystemExit(main())
