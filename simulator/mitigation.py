"""Zero-Noise Extrapolation (ZNE) error mitigation module.

Runs the same circuit at multiple noise scale factors, then extrapolates
to estimate the ideal (zero-noise) fidelity using polynomial fitting.
"""

import numpy as np
import plotly.graph_objects as go
from qiskit import transpile
from qiskit_aer import AerSimulator

from simulator.circuits import build_circuit
from simulator.noise_models import get_noise_model


def _compute_fidelity(ideal: dict, noisy: dict, n_shots: int) -> float:
    """Bhattacharyya coefficient as fidelity proxy."""
    all_keys = set(ideal) | set(noisy)
    ip = np.array([ideal.get(k, 0) / n_shots for k in all_keys])
    np_ = np.array([noisy.get(k, 0) / n_shots for k in all_keys])
    return float(np.sum(np.sqrt(ip * np_)) ** 2)


def run_zne(
    circuit_type: str,
    noise_type: str,
    base_probability: float,
    scale_factors: list,
    shots: int = 4096,
) -> dict:
    """Run Zero-Noise Extrapolation by scaling noise probability.

    Args:
        circuit_type: Name of the quantum circuit to simulate.
        noise_type: Type of noise model to apply.
        base_probability: Base noise probability to scale from.
        scale_factors: List of multiplicative scale factors for the noise.
        shots: Number of measurement shots per simulation.

    Returns:
        Dictionary with keys:
            - ``scale_factors``: list of scale factors used
            - ``fidelities``: list of fidelity values at each scale
            - ``extrapolated_fidelity``: estimated zero-noise fidelity
            - ``fit_coeffs``: polynomial fit coefficients (degree 2)
    """
    qc = build_circuit(circuit_type)

    # Ideal (noiseless) simulation
    ideal_backend = AerSimulator()
    ideal_qc = transpile(qc, ideal_backend)
    ideal_counts = ideal_backend.run(ideal_qc, shots=shots).result().get_counts()

    fidelities = []
    for scale in scale_factors:
        scaled_prob = min(base_probability * scale, 0.5)
        noise_model = get_noise_model(noise_type, scaled_prob)
        noisy_backend = AerSimulator(noise_model=noise_model)
        noisy_qc = transpile(qc, noisy_backend)
        noisy_counts = noisy_backend.run(noisy_qc, shots=shots).result().get_counts()
        fidelities.append(_compute_fidelity(ideal_counts, noisy_counts, shots))

    # Polynomial extrapolation (degree min(2, len-1)) to scale=0
    deg = min(2, len(scale_factors) - 1)
    coeffs = np.polyfit(scale_factors, fidelities, deg)
    extrapolated_fidelity = float(np.clip(np.polyval(coeffs, 0), 0.0, 1.0))

    return {
        "scale_factors": list(scale_factors),
        "fidelities": fidelities,
        "extrapolated_fidelity": extrapolated_fidelity,
        "fit_coeffs": coeffs.tolist(),
    }


def zne_plot(
    scale_factors: list,
    fidelities: list,
    extrapolated_fidelity: float,
) -> go.Figure:
    """Plot fidelity vs noise scale factor with polynomial extrapolation.

    Args:
        scale_factors: Noise scale factors used in simulation.
        fidelities: Measured fidelity at each scale factor.
        extrapolated_fidelity: Estimated zero-noise fidelity.

    Returns:
        Plotly Figure showing the ZNE result.
    """
    deg = min(2, len(scale_factors) - 1)
    coeffs = np.polyfit(scale_factors, fidelities, deg)
    x_smooth = np.linspace(0, max(scale_factors) * 1.05, 200)
    y_smooth = np.clip(np.polyval(coeffs, x_smooth), 0.0, 1.0)

    fig = go.Figure()

    # Extrapolation curve
    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=y_smooth,
        mode="lines",
        line=dict(color="royalblue", width=2, dash="dash"),
        name="Polynomial Fit",
    ))

    # Measured data points
    fig.add_trace(go.Scatter(
        x=scale_factors,
        y=fidelities,
        mode="markers",
        marker=dict(size=12, color="tomato", symbol="circle"),
        name="Measured Fidelity",
    ))

    # Zero-noise extrapolated point
    fig.add_trace(go.Scatter(
        x=[0],
        y=[extrapolated_fidelity],
        mode="markers",
        marker=dict(size=16, color="lime", symbol="star"),
        name=f"ZNE Estimate: {extrapolated_fidelity:.4f}",
    ))

    fig.update_layout(
        title="Zero-Noise Extrapolation (ZNE)",
        xaxis_title="Noise Scale Factor",
        yaxis_title="Fidelity",
        yaxis=dict(range=[0, 1.1]),
        xaxis=dict(range=[-0.1, max(scale_factors) * 1.1]),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        legend=dict(x=0.55, y=0.05),
        margin=dict(t=50, b=40),
    )
    return fig
