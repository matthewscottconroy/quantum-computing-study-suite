"""Question: vz_bloch_spherical"""
from core.models import Question

QUESTION = Question(
    id='vz_bloch_spherical',
    section='Visualization',
    question='A pure qubit state sits at polar angle θ = π/2 and azimuth φ = π/4 on the Bloch sphere. Which call draws it?',
    options=[
        'plot_bloch_vector([1, np.pi / 2, np.pi / 4], coord_type="spherical")',
        'plot_bloch_vector([np.pi / 2, np.pi / 4], coord_type="polar")',
        'plot_bloch_vector(1, np.pi / 2, np.pi / 4)',
        'plot_bloch_multivector([1, np.pi / 2, np.pi / 4])',
    ],
    correct_index=0,
    explanation='With coord_type="spherical" the single list argument is read as [r, θ, φ] — radius first, then polar and azimuthal angle; the default coord_type="cartesian" reads the same list as [x, y, z]. The coordinates always arrive as ONE sequence, and plot_bloch_multivector expects a quantum state rather than coordinates.',
    difficulty='medium',
)
