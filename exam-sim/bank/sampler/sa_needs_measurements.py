"""Question: sa_needs_measurements"""
from core.models import Question

QUESTION = Question(
    id='sa_needs_measurements',
    section='Sampler',
    question='A circuit with NO classical registers and no measurements is passed to StatevectorSampler.run([qc]). What happens?',
    options=[
        "The job runs, but the pub result's data is empty — samplers only return measured classical data",
        'The sampler measures every qubit automatically in the Z basis',
        'It raises a CircuitError before running',
        'The sampler returns the full statevector instead',
    ],
    correct_index=0,
    explanation="The sampler emits a warning ('Did you mean to add measurement instructions?') and produces an empty DataBin — there are no classical registers to sample from. Nothing is measured implicitly, and samplers never return statevectors; that is what quantum_info's Statevector is for.",
    difficulty='medium',
)
