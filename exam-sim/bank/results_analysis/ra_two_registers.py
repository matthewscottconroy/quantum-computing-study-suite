"""Question: ra_two_registers"""
from core.models import Question

QUESTION = Question(
    id='ra_two_registers',
    section='Results analysis',
    question="A circuit has two classical registers, a = ClassicalRegister(1, 'a') and b = ClassicalRegister(1, 'b'). Qubit 0 is flipped to |1⟩ and measured into a[0]; qubit 1 (still |0⟩) is measured into b[0]. What do the counts look like?",
    options=[
        "{'0 1': N} — registers are space-separated, later-added register on the left",
        "{'01': N} — registers are concatenated without separators",
        "{'a1 b0': N} — keys carry register names",
        'Only one register can be measured per circuit',
    ],
    correct_index=0,
    explanation="With multiple classical registers, count keys show one group per register separated by spaces, ordered with the register added last on the left. Register b holds 0 and register a holds 1, giving '0 1'. This surprises people whose parsing assumes a single unbroken bitstring.",
    difficulty='hard',
)
