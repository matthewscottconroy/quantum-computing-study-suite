"""The Quantum Computing Study Suite.

One package:

``quantum_study.<app>``     the ten PyQt6 trainers (``python -m quantum_study.exam_sim``)
``quantum_study.common``    what they share: data directory, journals, theme, Reference screen
``quantum_study.launch``    the launcher          (``quantum-study``, or ``python launch.py``)
``quantum_study.coach``     the daily study coach (``quantum-coach``, or ``python coach.py``)
``quantum_study.dashboard`` the mastery dashboard (``quantum-dashboard``)

The teaching corpus (``docs/``, ``lesson-plans/``, ``labs/``, ``notebooks/``,
``projects/``) and the maintenance scripts (``tools/``) live beside the
package in the repository, not inside it.
"""
from __future__ import annotations

__version__ = "0.3.0"

#: Package name of each app, keyed by the app id used in study-history files,
#: journals and on the command line.  The ids are stable; do not rename them.
APPS: dict[str, str] = {
    "circuit-trainer": "circuit_trainer",
    "exam-sim": "exam_sim",
    "flashcard-drill": "flashcard_drill",
    "math-quiz": "math_quiz",
    "paper-drill": "paper_drill",
    "problem-trainer": "problem_trainer",
    "qec-trainer": "qec_trainer",
    "qiskit-dojo": "qiskit_dojo",
    "quantum-quiz": "quantum_quiz",
    "vqa-trainer": "vqa_trainer",
}

__all__ = ["APPS", "__version__"]
