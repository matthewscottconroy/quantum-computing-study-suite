"""Question: vz_circuit_drawer_func"""
from core.models import Question

QUESTION = Question(
    id='vz_circuit_drawer_func',
    section='Visualization',
    question='Which pair of calls produces the same matplotlib Figure of a circuit?',
    options=[
        'qc.draw("mpl") and circuit_drawer(qc, output="mpl")',
        'qc.draw("mpl") and plot_circuit(qc)',
        'qc.draw("mpl") and circuit_drawer(qc, output="png")',
        'qc.draw("mpl") and dag_drawer(qc)',
    ],
    correct_index=0,
    explanation='QuantumCircuit.draw is a thin wrapper around qiskit.visualization.circuit_drawer, so both accept the same output modes and options and return the same object. dag_drawer takes a DAGCircuit (build one with circuit_to_dag), there is no plot_circuit, and output="png" is rejected — the valid modes are text, latex, latex_source and mpl.',
    difficulty='easy',
)
