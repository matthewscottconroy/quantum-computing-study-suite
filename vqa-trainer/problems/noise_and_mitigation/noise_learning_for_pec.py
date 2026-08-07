"""Problem: noise_learning_for_pec"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_learning_for_pec',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question="What is the 'noise learning' step required before applying Probabilistic Error Cancellation (PEC)?",
    choices=[
        'Characterising the noise channel of each gate via process tomography or randomized benchmarking to obtain the quasi-probability decomposition coefficients {cᵢ}',
        'Training a classical neural network on noisy circuit outputs to learn the noise-to-noiseless mapping',
        'Running the target circuit many times to build a statistical model of the output distribution',
        'Performing readout calibration to learn the measurement error matrix before applying PEC corrections',
    ],
    correct_index=0,
    explanation='PEC requires decomposing each ideal gate G_ideal as Σᵢ cᵢ εᵢ where {εᵢ} are implementable noisy operations on the specific device. To find {cᵢ}, one must first characterise the actual noise channel of each gate — typically via gate set tomography (GST), sparse process tomography, or cycle benchmarking. This noise learning phase is expensive (many calibration circuits) but done once per device calibration cycle. The quality of PEC is limited by the accuracy of the noise model — uncharacterised noise correlations become systematic errors.',
    hints=[
        "PEC needs the noise channel's Kraus operators or Pauli representation to compute cᵢ.",
    ],
    grade_mode=GradeMode.MC,
)
