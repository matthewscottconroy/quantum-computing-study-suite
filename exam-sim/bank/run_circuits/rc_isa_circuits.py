"""Question: rc_isa_circuits"""
from core.models import Question

QUESTION = Question(
    id='rc_isa_circuits',
    section='Run circuits',
    question='Before submitting a circuit to an IBM Quantum backend through the Runtime primitives (SamplerV2 / EstimatorV2), what must you do to the circuit?',
    options=[
        "Transpile it to the backend's ISA (native gates and connectivity), e.g. with generate_preset_pass_manager(backend=backend)",
        'Nothing — the Runtime service transpiles every circuit server-side automatically',
        'Convert it to OpenQASM 2 first',
        'Add save_statevector() so the primitive can compute results',
    ],
    correct_index=0,
    explanation="Since Qiskit Runtime's V2 primitives, backends only accept ISA circuits — circuits already expressed in the target's basis gates and respecting its connectivity. You run a preset pass manager built from the backend target before calling the primitive. Server-side auto-transpilation was retired with the V1 stack.",
    difficulty='hard',
)
