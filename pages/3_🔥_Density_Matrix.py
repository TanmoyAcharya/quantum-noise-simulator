"""Streamlit page — Density Matrix Heatmap.

Computes and displays the density matrix of a quantum circuit (ideal
and noisy), showing how decoherence collapses the off-diagonal elements.
"""

import numpy as np
import streamlit as st

from simulator.density_matrix import density_matrix_heatmap, get_density_matrix
from simulator.noise_models import get_noise_model

st.set_page_config(
    page_title="Density Matrix",
    page_icon="🔥",
    layout="wide",
)

st.title("🔥 Density Matrix Heatmap")
st.markdown(
    """
    The **density matrix** ρ is the most complete description of a quantum state.
    A pure state has all information concentrated in off-diagonal *coherences*.
    Noise destroys these coherences — watch them shrink as noise increases!

    | Property | Formula | Meaning |
    |---|---|---|
    | **Purity** | Tr(ρ²) | 1 = pure state, < 1 = mixed/noisy |
    | **Von Neumann Entropy** | −Tr(ρ log ρ) | 0 = pure, > 0 = decoherent |
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Density Matrix Controls")

circuit_type = st.sidebar.selectbox(
    "Quantum Circuit",
    [
        "Bell State (Entanglement)",
        "Superposition (H gate)",
        "GHZ State (3 Qubits)",
        "Phase Kickback",
        "T Gate (pi/8 gate)",
    ],
)

noise_type = st.sidebar.selectbox(
    "Noise Model",
    [
        "Depolarizing",
        "Bit Flip",
        "Phase Flip",
        "Amplitude Damping (T1 decay)",
        "Phase Damping (T2 decay)",
    ],
)

noise_prob = st.sidebar.slider(
    "Noise Probability",
    min_value=0.0, max_value=0.5, value=0.1, step=0.01,
)

st.sidebar.divider()
st.sidebar.markdown(
    """
### 🔬 Reading the Heatmap
- **Diagonal** (bright squares) = populations — probability of being in each state
- **Off-diagonal** = coherences — quantum superposition information
- **After decoherence** → off-diagonals fade to zero = classical mixture
"""
)


# ── Compute Density Matrices ───────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _get_dm(circuit_type, noise_type, noise_prob):
    ideal_rho = get_density_matrix(circuit_type, noise_model=None)
    nm = get_noise_model(noise_type, noise_prob)
    noisy_rho = get_density_matrix(circuit_type, noise_model=nm)
    return ideal_rho, noisy_rho


with st.spinner("⏳ Computing density matrices…"):
    ideal_rho, noisy_rho = _get_dm(circuit_type, noise_type, noise_prob)


def _purity(rho: np.ndarray) -> float:
    return float(np.real(np.trace(rho @ rho)))


def _von_neumann_entropy(rho: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    return float(-np.sum(eigenvalues * np.log2(eigenvalues)))


ideal_purity = _purity(ideal_rho)
noisy_purity = _purity(noisy_rho)
ideal_entropy = _von_neumann_entropy(ideal_rho)
noisy_entropy = _von_neumann_entropy(noisy_rho)

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("✅ Ideal Purity", f"{ideal_purity:.4f}")
col2.metric("⚠️ Noisy Purity", f"{noisy_purity:.4f}",
            delta=f"{noisy_purity - ideal_purity:.4f}", delta_color="inverse")
col3.metric("✅ Ideal Entropy (bits)", f"{ideal_entropy:.4f}")
col4.metric("⚠️ Noisy Entropy (bits)", f"{noisy_entropy:.4f}",
            delta=f"+{noisy_entropy - ideal_entropy:.4f}", delta_color="inverse")

st.divider()

# ── Heatmaps ──────────────────────────────────────────────────────────────────
st.subheader("✅ Ideal Density Matrix")
st.plotly_chart(
    density_matrix_heatmap(ideal_rho, title="Ideal"),
    use_container_width=True,
)

st.subheader("⚠️ Noisy Density Matrix")
st.plotly_chart(
    density_matrix_heatmap(noisy_rho, title=f"Noisy ({noise_type}, p={noise_prob:.2f})"),
    use_container_width=True,
)

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
