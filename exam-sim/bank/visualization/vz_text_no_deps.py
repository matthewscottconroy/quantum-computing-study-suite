"""Question: vz_text_no_deps"""
from core.models import Question

QUESTION = Question(
    id='vz_text_no_deps',
    section='Visualization',
    question="A colleague on a minimal server install (no matplotlib) wants to inspect a circuit's structure. Which drawer works?",
    options=[
        "print(qc.draw('text')) — the text drawer has no plotting dependencies",
        "qc.draw('mpl') — matplotlib is bundled inside qiskit",
        "qc.draw('latex') — it renders in the terminal",
        'Circuits cannot be inspected without matplotlib',
    ],
    correct_index=0,
    explanation="The 'text' output builds pure-ASCII art with no third-party plotting libraries, so it works everywhere. 'mpl' needs matplotlib (an optional dependency of qiskit) and 'latex' requires a LaTeX toolchain and pillow.",
    difficulty='easy',
)
