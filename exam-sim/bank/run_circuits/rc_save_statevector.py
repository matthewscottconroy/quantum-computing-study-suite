"""Question: rc_save_statevector"""
from core.models import Question

QUESTION = Question(
    id='rc_save_statevector',
    section='Run circuits',
    question='Which snippet correctly retrieves the ideal statevector of a circuit from AerSimulator?',
    options=[
        'qc.save_statevector(); result = AerSimulator().run(qc).result(); sv = result.get_statevector()',
        "sv = AerSimulator().run(qc, output='statevector').result()",
        'sv = AerSimulator().statevector(qc)',
        'result = AerSimulator().run(qc).result(); sv = result.get_statevector()  # no other change needed',
    ],
    correct_index=0,
    explanation="Aer only returns data you ask it to save: append save_statevector() to the circuit, run it, then call result.get_statevector(). Without the save instruction, get_statevector() has nothing to return; the other two APIs don't exist.",
    difficulty='medium',
)
