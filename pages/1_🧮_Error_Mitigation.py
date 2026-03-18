"""Streamlit page — Error Mitigation (Zero-Noise Extrapolation).

Demonstrates how ZNE estimates the ideal fidelity by running a circuit
at multiple noise scale factors and extrapolating to zero noise.
"""

import streamlit as st

from simulator.mitigation import run_zne, zne_plot

st.set_page_config(
    page_title="Error Mitigation (ZNE)",
    page_icon="🧮",
    layout="wide",
)

st.title("🧮 Quantum Error Mitigation — Zero-Noise Extrapolation")
st.markdown(
    """
    **Zero-Noise Extrapolation (ZNE)** is a practical error-mitigation technique used on real
    quantum hardware.  Instead of correcting errors directly, ZNE *amplifies* the noise at
    multiple levels, measures the fidelity at each level, then **extrapolates the curve back to
    zero noise** to estimate what the ideal result would have been.

    > 💡 This is one of the core error-mitigation strategies used by QPU engineers at companies
    > like IQM Quantum Computers.
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ ZNE Controls")

circuit_type = st.sidebar.selectbox(
    "Quantum Circuit",
    [
        "Superposition (H gate)",
        "Bell State (Entanglement)",
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

base_prob = st.sidebar.slider(
    "Base Noise Probability",
    min_value=0.001, max_value=0.2, value=0.05, step=0.001,
    format="%.3f",
    help="The circuit will be run at 1×, 2×, and 3× this probability.",
)

shots = st.sidebar.select_slider(
    "Measurement Shots",
    options=[512, 1024, 2048, 4096, 8192],
    value=4096,
)

scale_factors = [1, 2, 3]

st.sidebar.divider()
st.sidebar.markdown(
    """
### ℹ️ How ZNE Works
1. Run the circuit at **1×**, **2×**, **3×** noise
2. Fit a polynomial through the measured fidelities
3. Extrapolate the curve to **noise = 0**
4. The y-intercept is the **ZNE-mitigated estimate**
"""
)

# ── Run Simulation ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _run_zne(circuit_type, noise_type, base_prob, shots):
    return run_zne(circuit_type, noise_type, base_prob, scale_factors, shots)


with st.spinner("⏳ Running ZNE simulation…"):
    zne_results = _run_zne(circuit_type, noise_type, base_prob, shots)

raw_fidelity = zne_results["fidelities"][0]
zne_fidelity = zne_results["extrapolated_fidelity"]
improvement = (zne_fidelity - raw_fidelity) / max(raw_fidelity, 1e-9) * 100

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("📉 Raw Fidelity (1× noise)", f"{raw_fidelity:.4f}")
col2.metric("✨ ZNE-Mitigated Fidelity", f"{zne_fidelity:.4f}",
            delta=f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%")
col3.metric("🔧 Base Noise Probability", f"{base_prob:.3f}")

st.divider()

# ── ZNE Plot ──────────────────────────────────────────────────────────────────
st.subheader("📈 Fidelity vs Noise Scale Factor")
st.plotly_chart(
    zne_plot(
        zne_results["scale_factors"],
        zne_results["fidelities"],
        zne_results["extrapolated_fidelity"],
    ),
    use_container_width=True,
)

st.divider()

# ── Data Table ────────────────────────────────────────────────────────────────
st.subheader("📋 Fidelity at Each Scale Factor")
table_data = {
    "Scale Factor": [f"{s}×" for s in scale_factors],
    "Noise Probability": [f"{base_prob * s:.4f}" for s in scale_factors],
    "Fidelity": [f"{f:.4f}" for f in zne_results["fidelities"]],
}
st.table(table_data)

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
