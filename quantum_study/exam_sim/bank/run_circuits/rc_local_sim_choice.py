"""Question: rc_local_sim_choice"""
from quantum_study.exam_sim.core.models import Question

QUESTION = Question(
    id='rc_local_sim_choice',
    section='Run circuits',
    question='Which description of the three local execution paths is correct?',
    options=[
        'StatevectorSampler is ideal; AerSimulator can carry a noise model; BackendSamplerV2 wraps a backend',
        'All three are noiseless and differ only in their result classes',
        'StatevectorSampler and BackendSamplerV2 both require ISA circuits; only AerSimulator accepts arbitrary gates',
        'AerSimulator returns a PrimitiveResult, while the two samplers return a Result with get_counts()',
    ],
    correct_index=0,
    explanation='StatevectorSampler simulates the full statevector and then samples it, with no noise and no ISA requirement. AerSimulator is a backend whose run() returns a Job/Result and which can be given a noise model (e.g. via from_backend). BackendSamplerV2(backend=...) adapts any BackendV2 — Aer included — to the V2 pub/PrimitiveResult interface.',
    difficulty='medium',
)
