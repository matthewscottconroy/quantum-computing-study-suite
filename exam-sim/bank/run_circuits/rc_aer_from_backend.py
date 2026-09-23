"""Question: rc_aer_from_backend"""
from core.models import Question

QUESTION = Question(
    id='rc_aer_from_backend',
    section='Run circuits',
    question='You want to rehearse a circuit locally with a realistic noise model taken from a real device. Which line does that?',
    options=[
        'sim = AerSimulator.from_backend(backend)',
        'sim = AerSimulator(noise=backend.properties())',
        'sim = AerSimulator(); sim.set_backend(backend)',
        'sim = StatevectorSampler(backend=backend)',
    ],
    correct_index=0,
    explanation="AerSimulator.from_backend() reads the target's gate errors, readout errors and coupling map and builds a matching NoiseModel, so local runs approximate the device. StatevectorSampler has no backend argument and is always exact; the other two calls do not exist.",
    difficulty='medium',
)
