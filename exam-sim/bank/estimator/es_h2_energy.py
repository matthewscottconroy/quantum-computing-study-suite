"""Question: es_h2_energy"""
from core.models import Question

QUESTION = Question(
    id='es_h2_energy',
    section='Estimator',
    question='What does this print?\n\n```python\nqc = QuantumCircuit(2)\nqc.x(0)\n\nH = SparsePauliOp.from_list([("II", -1.052), ("IZ", 0.398),\n                             ("ZI", -0.398), ("ZZ", -0.011), ("XX", 0.181)])\n\nev = StatevectorEstimator().run([(qc, H)]).result()[0].data.evs\nprint(round(float(ev), 3))\n```',
    options=[
        '-1.837',
        '-1.063',
        '-0.245',
        '-1.052',
    ],
    correct_index=0,
    explanation='X on qubit 0 prepares |01⟩ (written q1 q0). Term by term: ⟨II⟩ = 1, ⟨IZ⟩ = −1 because Z sits on qubit 0, which is |1⟩; ⟨ZI⟩ = +1; ⟨ZZ⟩ = −1; ⟨XX⟩ = 0. Weighted: −1.052 − 0.398 − 0.398 + 0.011 + 0 = −1.837. Reading the labels left to right instead gives −0.245, and −1.063 is the energy of |00⟩.',
    difficulty='hard',
)
