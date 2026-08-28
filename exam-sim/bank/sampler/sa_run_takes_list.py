"""Question: sa_run_takes_list"""
from core.models import Question

QUESTION = Question(
    id='sa_run_takes_list',
    section='Sampler',
    question='Why does this fail?\n\n```python\nfrom qiskit.primitives import StatevectorSampler\n\nsampler = StatevectorSampler()\njob = sampler.run(qc)        # qc is a measured QuantumCircuit\n```',
    options=[
        'run() takes a LIST of pubs — it must be sampler.run([qc])',
        'StatevectorSampler needs a backend argument in its constructor',
        'run() requires an explicit shots argument',
        'The circuit must be converted to a pub with Pub.from_circuit(qc) first',
    ],
    correct_index=0,
    explanation="V2 primitives always accept an iterable of pubs (primitive unified blocs). Passing a bare circuit makes the sampler iterate over the circuit's instructions and fail with 'An invalid Sampler pub-like was given'. Wrapping it in a list — run([qc]) — is the fix; shots is optional (defaults apply).",
    difficulty='medium',
)
