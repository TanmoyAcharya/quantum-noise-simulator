"""Noise model comparison module.

Runs the same quantum circuit under all supported noise models at a given
probability, plus the ideal (no-noise) case, and returns side-by-side fidelity
and count results for easy comparison.
"""

import numpy as np
import plotly.graph_objects as go
from qiskit import transpile
from qiskit_aer import AerSimulator

from simulator.circuits import build_circuit
from simulator.noise_models import get_noise_model

_NOISE_TYPES = [
    "Bit Flip",
    "Phase Flip",
    "Depolarizing",
    "Amplitude Damping (T1 decay)",
    "Phase Damping (T2 decay)",
]

_BAR_COLORS = [
    "#4F8BF9",  # blue
    "#F97B4F",  # orange
    "#4FF9A0",  # green
    "#F94F7B",  # red
    "#BF4FF9",  # purple
    "#F9E64F",  # yellow — ideal
]


def _bhattacharyya(ideal: dict, noisy: dict, n_shots: int) -> float:
    """Bhattacharyya coefficient as fidelity proxy."""
    all_keys = set(ideal) | set(noisy)
    ip = np.array([ideal.get(k, 0) / n_shots for k in all_keys])
    np_ = np.array([noisy.get(k, 0) / n_shots for k in all_keys])
    return float(np.sum(np.sqrt(ip * np_)) ** 2)


def run_comparison(
    circuit_type: str,
    probability: float,
    shots: int = 2048,
) -> dict:
    """Run the circuit under all noise models and the ideal case.

    Args:
        circuit_type: Name of the quantum circuit to simulate.
        probability: Noise probability to apply to each noise model.
        shots: Number of measurement shots per simulation.

    Returns:
        Dictionary mapping noise type name (or ``"Ideal"``) to
        ``{"fidelity": float, "counts": dict}``.
    """
    qc = build_circuit(circuit_type)

    # Ideal baseline
    ideal_backend = AerSimulator()
    ideal_qc = transpile(qc, ideal_backend)
    ideal_counts = ideal_backend.run(ideal_qc, shots=shots).result().get_counts()

    results = {
        "Ideal": {"fidelity": 1.0, "counts": ideal_counts},
    }

    for noise_type in _NOISE_TYPES:
        nm = get_noise_model(noise_type, probability)
        backend = AerSimulator(noise_model=nm)
        tqc = transpile(qc, backend)
        counts = backend.run(tqc, shots=shots).result().get_counts()
        fidelity = _bhattacharyya(ideal_counts, counts, shots)
        results[noise_type] = {"fidelity": fidelity, "counts": counts}

    return results


def comparison_bar_chart(results: dict) -> go.Figure:
    """Create a grouped bar chart of fidelity across noise models.

    Args:
        results: Output of :func:`run_comparison`.

    Returns:
        Plotly Figure with one bar per noise model, colour-coded.
    """
    labels = list(results.keys())
    fidelities = [results[k]["fidelity"] for k in labels]
    colors = _BAR_COLORS[: len(labels)]

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=fidelities,
            marker_color=colors,
            text=[f"{f:.3f}" for f in fidelities],
            textposition="outside",
        )
    ])

    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="lime",
        annotation_text="Ideal",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Fidelity Comparison Across Noise Models",
        xaxis_title="Noise Model",
        yaxis_title="Fidelity vs Ideal",
        yaxis=dict(range=[0, 1.15]),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        margin=dict(t=50, b=80),
        showlegend=False,
    )
    return fig
