"""Bell Inequality (CHSH) test simulation module.

Simulates the four CHSH measurement settings on a Bell state,
computes the correlators and the CHSH S parameter, and plots
how noise degrades the quantum advantage.
"""

import numpy as np
import plotly.graph_objects as go
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from simulator.noise_models import get_noise_model

# CHSH measurement angles (radians) — chosen to maximise the S parameter for |Φ+⟩.
# With ry(-2θ) rotation, the correlator is E(θ_a, θ_b) = cos(2(θ_a − θ_b)),
# so angles (0, π/4, π/8, 3π/8) give S = 2√2.
_ANGLE_A = 0.0
_ANGLE_A_PRIME = np.pi / 4
_ANGLE_B = np.pi / 8
_ANGLE_B_PRIME = 3 * np.pi / 8


def _bell_measurement_circuit(theta_a: float, theta_b: float) -> QuantumCircuit:
    """Build a 2-qubit Bell state circuit with rotated measurements.

    The Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 is prepared, then
    each qubit is rotated by the given angles before measurement.

    Args:
        theta_a: Rotation angle for qubit 0 (Alice).
        theta_b: Rotation angle for qubit 1 (Bob).

    Returns:
        QuantumCircuit ready for simulation.
    """
    qc = QuantumCircuit(2, 2)
    # Prepare Bell state |Φ+⟩
    qc.h(0)
    qc.cx(0, 1)
    # Measurement basis rotations
    qc.ry(-2 * theta_a, 0)
    qc.ry(-2 * theta_b, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def _correlator(counts: dict, shots: int) -> float:
    """Compute the two-qubit correlator E = (P++ + P-- - P+- - P-+).

    In bit notation: ``00`` and ``11`` are "++" / "--" (same outcomes),
    ``01`` and ``10`` are "+−" / "−+" (different outcomes).

    Args:
        counts: Measurement counts dictionary from Qiskit.
        shots: Total number of shots.

    Returns:
        Correlator value in [-1, 1].
    """
    same = counts.get("00", 0) + counts.get("11", 0)
    diff = counts.get("01", 0) + counts.get("10", 0)
    return (same - diff) / shots


def run_chsh_test(
    noise_type: str = "Depolarizing",
    probability: float = 0.0,
    shots: int = 8192,
) -> dict:
    """Simulate the CHSH Bell test with optional noise.

    The four measurement settings (a,b), (a,b'), (a',b), (a',b') are
    simulated and the CHSH S parameter is computed:
    ``S = E(a,b) - E(a,b') + E(a',b) + E(a',b')``.

    Args:
        noise_type: Noise model to apply.
        probability: Noise probability (0.0 = ideal).
        shots: Number of measurement shots per setting.

    Returns:
        Dictionary with keys:
            - ``S``: CHSH S parameter
            - ``correlators``: dict mapping setting name → correlator value
            - ``classical_bound``: 2.0
            - ``quantum_bound``: 2√2 ≈ 2.828
    """
    noise_model = get_noise_model(noise_type, probability)
    backend = AerSimulator(noise_model=noise_model)

    settings = {
        "E(a,b)":   (_ANGLE_A,       _ANGLE_B),
        "E(a,b')":  (_ANGLE_A,       _ANGLE_B_PRIME),
        "E(a',b)":  (_ANGLE_A_PRIME, _ANGLE_B),
        "E(a',b')": (_ANGLE_A_PRIME, _ANGLE_B_PRIME),
    }

    correlators = {}
    for name, (ta, tb) in settings.items():
        qc = _bell_measurement_circuit(ta, tb)
        tqc = transpile(qc, backend)
        counts = backend.run(tqc, shots=shots).result().get_counts()
        correlators[name] = _correlator(counts, shots)

    s_value = (
        correlators["E(a,b)"]
        - correlators["E(a,b')"]
        + correlators["E(a',b)"]
        + correlators["E(a',b')"]
    )

    return {
        "S": float(s_value),
        "correlators": correlators,
        "classical_bound": 2.0,
        "quantum_bound": float(2 * np.sqrt(2)),
    }


def chsh_plot(results_by_noise: list) -> go.Figure:
    """Plot CHSH S value vs noise probability.

    Args:
        results_by_noise: List of dicts, each containing keys
            ``"probability"`` and ``"S"`` (output of repeated
            :func:`run_chsh_test` calls at different noise levels).

    Returns:
        Plotly Figure with S vs noise probability, plus classical and
        quantum bound lines.
    """
    probs = [r["probability"] for r in results_by_noise]
    s_vals = [r["S"] for r in results_by_noise]

    fig = go.Figure()

    # S vs noise probability
    fig.add_trace(go.Scatter(
        x=probs,
        y=s_vals,
        mode="lines+markers",
        line=dict(color="#4F8BF9", width=3),
        marker=dict(size=8, color="#4F8BF9"),
        name="CHSH S value",
        fill="tozeroy",
        fillcolor="rgba(79, 139, 249, 0.12)",
    ))

    # Classical bound
    fig.add_hline(
        y=2.0,
        line_dash="dash",
        line_color="tomato",
        annotation_text="Classical Bound (S = 2)",
        annotation_position="top left",
    )

    # Quantum bound
    fig.add_hline(
        y=2 * np.sqrt(2),
        line_dash="dash",
        line_color="lime",
        annotation_text=f"Quantum Bound (S = 2√2 ≈ {2*np.sqrt(2):.3f})",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title="CHSH Bell Parameter vs Noise Probability",
        xaxis_title="Noise Probability",
        yaxis_title="CHSH S Parameter",
        yaxis=dict(range=[0, 3.2]),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        legend=dict(x=0.6, y=0.95),
        margin=dict(t=50, b=40),
    )
    return fig
