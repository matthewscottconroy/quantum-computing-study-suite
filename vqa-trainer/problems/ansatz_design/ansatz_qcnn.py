"""Problem: ansatz_qcnn"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_qcnn',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is a quantum convolutional neural network (QCNN) ansatz and what are its key structural properties?',
    choices=[
        'A hierarchical ansatz with convolutional (translationally invariant) layers followed by pooling (qubit reduction) layers, giving O(log n) depth and O(log n) parameters',
        'A quantum circuit that implements a classical convolutional neural network by encoding image data into qubit amplitudes',
        'An ansatz where each gate is a quantum analogue of a convolutional filter applied in Fourier space',
        'A hardware-efficient ansatz with n/2 parameters arranged in a 2D grid matching CNN architecture',
    ],
    correct_index=0,
    explanation='The QCNN (Cong et al. 2019) applies a sequence of: (1) convolutional layers — parameterised 2-qubit gates applied translationally-invariantly (same parameters) across all neighbouring pairs; (2) pooling layers — measure half the qubits and apply classically-controlled corrections, halving the active qubit count. After O(log n) rounds, one qubit remains and is measured for the classification/cost. Key properties: O(log n) depth, O(log n) parameters (due to parameter sharing), provably free of barren plateaus for certain problem classes.',
    hints=[
        'QCNN borrows CNN ideas: convolution (shared weights) + pooling (compression).',
    ],
    grade_mode=GradeMode.MC,
)
