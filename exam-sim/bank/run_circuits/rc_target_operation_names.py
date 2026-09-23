"""Question: rc_target_operation_names"""
from core.models import Question

QUESTION = Question(
    id='rc_target_operation_names',
    section='Run circuits',
    question='Which expression gives the names of the gates a BackendV2 executes natively?',
    options=[
        'backend.target.operation_names',
        'backend.basis_gates()',
        'backend.configuration().basis_gates',
        'backend.target.gates',
    ],
    correct_index=0,
    explanation='Target.operation_names is the set of instruction names in the target (for IBM hardware typically rz, sx, x, cx or cz, plus measure, reset, delay); BackendV2 also mirrors it as backend.operation_names. basis_gates as a method and configuration().basis_gates are BackendV1 idioms, and Target has no .gates attribute.',
    difficulty='medium',
)
