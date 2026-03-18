"""Streamlit page — Noise Comparison Mode.

Runs the same quantum circuit under all 5 noise models at a given
probability and displays fidelity results side-by-side for easy comparison.
"""

import streamlit as st

from simulator.comparison import comparison_bar_chart, run_comparison

st.set_page_config(
    page_title="Noise Comparison",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Noise Model Comparison")
st.markdown(
    """
    Different noise models affect quantum circuits in fundamentally different ways.
    This page runs **the same circuit under all 5 noise models** simultaneously,
    so you can compare their impact on fidelity at a glance.
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Comparison Controls")

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

noise_prob = st.sidebar.slider(
    "Noise Probability",
    min_value=0.0, max_value=0.5, value=0.1, step=0.01,
    help="Applied identically to all noise models",
)

shots = st.sidebar.select_slider(
    "Measurement Shots",
    options=[512, 1024, 2048, 4096],
    value=2048,
)

st.sidebar.divider()
st.sidebar.markdown(
    """
### 🔬 Noise Models
| Model | Description |
|---|---|
| **Bit Flip** | Random X (|0⟩↔|1⟩) error |
| **Phase Flip** | Random Z (phase) error |
| **Depolarizing** | Random X/Y/Z error |
| **Amplitude Damping** | T1 energy relaxation |
| **Phase Damping** | T2 dephasing |
"""
)

# ── Run Comparison ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _compare(circuit_type, noise_prob, shots):
    return run_comparison(circuit_type, noise_prob, shots)


with st.spinner("⏳ Running comparison across all noise models…"):
    results = _compare(circuit_type, noise_prob, shots)

# ── Bar Chart ─────────────────────────────────────────────────────────────────
st.subheader("📊 Fidelity Across Noise Models")
st.plotly_chart(comparison_bar_chart(results), use_container_width=True)

st.divider()

# ── Fidelity Table ────────────────────────────────────────────────────────────
st.subheader("📋 Fidelity Summary Table")

noise_descriptions = {
    "Ideal": "No noise — perfect quantum simulation",
    "Bit Flip": "Random X error: |0⟩ ↔ |1⟩ flip with probability p",
    "Phase Flip": "Random Z error: |+⟩ ↔ |−⟩ phase error with probability p",
    "Depolarizing": "Completely random Pauli error (X, Y, or Z) with probability p",
    "Amplitude Damping (T1 decay)": "Energy relaxation: |1⟩ → |0⟩ (T1 process)",
    "Phase Damping (T2 decay)": "Dephasing: loss of phase coherence without energy loss",
}

table_data = {
    "Noise Model": [],
    "Fidelity": [],
    "Description": [],
}

for name, data in results.items():
    table_data["Noise Model"].append(name)
    table_data["Fidelity"].append(f"{data['fidelity']:.4f}")
    table_data["Description"].append(noise_descriptions.get(name, ""))

st.table(table_data)

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
