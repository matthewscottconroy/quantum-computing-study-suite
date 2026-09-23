"""Question: rc_save_account"""
from core.models import Question

QUESTION = Question(
    id='rc_save_account',
    section='Run circuits',
    question='Which call stores credentials on disk so that a later QiskitRuntimeService() picks them up with no arguments?',
    options=[
        'QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token=TOKEN, instance=CRN, set_as_default=True)',
        'QiskitRuntimeService().save_credentials(TOKEN)',
        'IBMQ.save_account(TOKEN)',
        'QiskitRuntimeService.store_token(TOKEN, overwrite=True)',
    ],
    correct_index=0,
    explanation='save_account() is a classmethod that writes ~/.qiskit/qiskit-ibm.json; set_as_default=True marks it the account an argument-less QiskitRuntimeService() loads, and overwrite=True is needed to replace an existing entry of the same name. IBMQ.save_account belongs to the long-removed qiskit-ibmq-provider; the other two methods do not exist.',
    difficulty='easy',
)
