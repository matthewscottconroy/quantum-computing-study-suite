"""Question: rc_memory_shots"""
from core.models import Question

QUESTION = Question(
    id='rc_memory_shots',
    section='Run circuits',
    question='You need the individual bitstring of every single shot (in order), not the aggregated histogram. Which AerSimulator call pattern gives you that?',
    options=[
        'job = sim.run(qc, shots=100, memory=True); shots_list = job.result().get_memory()',
        'job = sim.run(qc, shots=100); shots_list = job.result().get_counts(raw=True)',
        'job = sim.run(qc, shots=100, per_shot=True); shots_list = job.result().get_shots()',
        'Impossible — simulators only ever return aggregated counts',
    ],
    correct_index=0,
    explanation="Passing memory=True makes the backend record each shot's outcome; result.get_memory() then returns a list of bitstrings, one per shot, in execution order. get_counts() has no raw flag and get_shots()/per_shot do not exist.",
    difficulty='hard',
)
