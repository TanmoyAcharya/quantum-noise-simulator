"""Density matrix computation and heatmap visualization module.

Uses Qiskit Aer's density matrix simulator to compute the full
density matrix of a quantum circuit (with or without noise) and
renders it as an interactive Plotly heatmap.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from qiskit import transpile
from qiskit_aer import AerSimulator

from simulator.circuits import build_statevector_circuit


def get_density_matrix(circuit_type: str, noise_model=None) -> np.ndarray:
    """Compute the density matrix of a circuit using Aer's density_matrix method.

    Args:
        circuit_type: Name of the quantum circuit to simulate.
        noise_model: Optional Qiskit Aer NoiseModel. If None, ideal simulation.

    Returns:
        Density matrix as a complex numpy array of shape (2^n, 2^n).
    """
    from qiskit.quantum_info import DensityMatrix

    qc = build_statevector_circuit(circuit_type)
    qc_dm = qc.copy()
    qc_dm.save_density_matrix()

    backend = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(qc_dm, backend)
    result = backend.run(tqc).result()
    dm_data = result.data()["density_matrix"]
    return np.array(DensityMatrix(dm_data).data)


def density_matrix_heatmap(rho: np.ndarray, title: str = "Density Matrix") -> go.Figure:
    """Create a 2-panel heatmap for the real and imaginary parts of a density matrix.

    Args:
        rho: Complex density matrix array of shape (2^n, 2^n).
        title: Title prefix for the figure.

    Returns:
        Plotly Figure with two side-by-side heatmaps (Re and Im parts).
    """
    n = rho.shape[0]
    labels = [format(i, f"0{int(np.log2(n))}b") for i in range(n)]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[f"{title} — Real Part", f"{title} — Imaginary Part"],
    )

    # Real part
    fig.add_trace(
        go.Heatmap(
            z=np.real(rho),
            x=labels,
            y=labels,
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(x=0.45, title="Re(ρ)", title_font_color="#FAFAFA"),
            hovertemplate="Row: %{y}<br>Col: %{x}<br>Re(ρ): %{z:.4f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Imaginary part
    fig.add_trace(
        go.Heatmap(
            z=np.imag(rho),
            x=labels,
            y=labels,
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(x=1.0, title="Im(ρ)", title_font_color="#FAFAFA"),
            hovertemplate="Row: %{y}<br>Col: %{x}<br>Im(ρ): %{z:.4f}<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.update_layout(
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        margin=dict(t=60, b=40),
        height=420,
    )
    return fig
