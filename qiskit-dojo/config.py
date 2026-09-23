"""App-wide constants.

Every data path comes from :mod:`common.datadir`, which is the one place in
the suite that reads ``QUANTUM_STUDY_DATA_DIR``.  The constants below are
snapshots taken at import time and are kept because they are this app's
published contract (its README and its tests name them); the *functions* in
``persistence.py`` resolve their paths through ``common.datadir`` on every
call, so a test only has to set the environment variable.
"""
import common_path  # noqa: F401  (puts the repo root on sys.path)

from pathlib import Path

from common import datadir

APP_NAME           = "Qiskit Dojo"
APP_DIR_NAME       = "qiskit-dojo"          # "app" field in flagged entries (coach.py)
DATA_DIR           = datadir.data_dir()
HISTORY_FILE       = datadir.app_file(APP_DIR_NAME, "history")    # dojo_history.json
FLAGGED_FILE       = datadir.app_file(APP_DIR_NAME, "flagged")    # dojo_flagged.json
# Suite-wide study-analytics files (shared schema across all ten apps).
MISTAKES_FILE      = datadir.mistakes_file()
CONFIDENCE_FILE    = datadir.confidence_file()
# App-local UI preferences (e.g. the confidence-strip opt-out).
SETTINGS_FILE      = datadir.app_file(APP_DIR_NAME, "settings")   # dojo_settings.json
API_KEY_FILE       = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL              = "claude-sonnet-4-6"
DEFAULT_KATA_COUNT = 8
RUN_TIMEOUT_SECS   = 20
WINDOW_TITLE       = "Qiskit Dojo — Hands-On Qiskit Katas"
WINDOW_MIN_SIZE    = (1080, 700)

#: Chapter of the shared docs corpus the Reference screen opens on, and the
#: kata-section -> chapter map behind its "Jump to topic" picker.  These are
#: the only two things this app's Reference screen does differently from the
#: other nine, which is why they are constructor arguments rather than a fork
#: of ``common.ui.reference``.
DOCS_DEFAULT_CHAPTER = "03_quantum_gates_and_circuits"
DOCS_FOR_SECTION: dict[str, str] = {
    "Create circuits":    "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    "Quantum operations": "03_quantum_gates_and_circuits/02_multi_qubit_gates.md",
    "Run circuits":       "07_quantum_hardware/05_modern_benchmarking.md",
    "Sampler":            "02_quantum_mechanics/03_quantum_measurements.md",
    "Estimator":          "06_variational_quantum_algorithms/01_vqe_fundamentals.md",
    "Visualization":      "02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md",
    "Results analysis":   "01_mathematical_foundations/06_probability_and_statistics.md",
    "OpenQASM":           "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    "Debugging":          "01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md",
    "Modernization":      "07_quantum_hardware/05_modern_benchmarking.md",
}
