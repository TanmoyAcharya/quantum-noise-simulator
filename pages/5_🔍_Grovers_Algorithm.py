"""Streamlit page — Grover's Algorithm.

Demonstrates Grover's quantum search algorithm and shows how noise
degrades the probability amplification effect.
"""

import streamlit as st

from simulator.grover import build_grover_circuit, grover_plot, run_grover

st.set_page_config(
    page_title="Grover's Algorithm",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Grover's Algorithm — Quantum Search")
st.markdown(
    """
    **Grover's algorithm** provides a quadratic speedup for searching an unsorted database.
    For N items it finds the target in **O(√N)** steps instead of O(N).

    The algorithm works by repeatedly applying an **oracle** (marks the target state)
    followed by a **diffusion operator** (amplifies the marked state's amplitude).

    > ⚠️ Noise disrupts this delicate amplitude amplification — the target probability
    > drops back toward the uniform 1/N as noise increases.
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Grover Controls")

n_qubits = st.sidebar.selectbox("Number of Qubits", [2, 3], index=0)

# Generate valid target states based on qubit count
all_targets = [format(i, f"0{n_qubits}b") for i in range(2 ** n_qubits)]
target = st.sidebar.selectbox("Target State", all_targets, index=len(all_targets) - 1)

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
    min_value=0.0, max_value=0.3, value=0.01, step=0.005,
    format="%.3f",
)

shots = st.sidebar.select_slider(
    "Measurement Shots",
    options=[1024, 2048, 4096, 8192],
    value=4096,
)

st.sidebar.divider()
n_states = 2 ** n_qubits
import numpy as np
n_iters = max(1, int(np.round(np.pi / 4 * np.sqrt(n_states))))
st.sidebar.markdown(
    f"""
### ℹ️ Algorithm Details
- **Search space**: {n_states} states
- **Grover iterations**: {n_iters}
- **Ideal success prob.**: ~{np.sin((2*n_iters+1)*np.arcsin(1/np.sqrt(n_states)))**2:.3f}
- **Classical random**: 1/{n_states} = {1/n_states:.3f}
"""
)

# ── Run Grover ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _run(n_qubits, target, noise_type, noise_prob, shots):
    return run_grover(n_qubits, target, noise_type, noise_prob, shots)


with st.spinner("⏳ Running Grover's algorithm (ideal + noisy)…"):
    results = _run(n_qubits, target, noise_type, noise_prob, shots)

ideal_prob = results["ideal_prob"]
noisy_prob = results["noisy_prob"]
degradation = ideal_prob - noisy_prob

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("✅ Ideal Target Prob.", f"{ideal_prob:.4f}")
col2.metric("⚠️ Noisy Target Prob.", f"{noisy_prob:.4f}",
            delta=f"{-degradation:.4f}", delta_color="inverse")
col3.metric("📉 Probability Drop", f"{degradation:.4f}",
            delta=f"{degradation/max(ideal_prob,1e-9)*100:.1f}%", delta_color="inverse")
col4.metric("🎯 Target State", f"|{target}⟩")

st.divider()

# ── Grover Plot ────────────────────────────────────────────────────────────────
st.subheader("📊 Ideal vs Noisy — All Basis States")
st.plotly_chart(grover_plot(results, shots), use_container_width=True)

st.divider()

# ── Circuit Diagram ────────────────────────────────────────────────────────────
st.subheader("🔬 Grover Circuit Diagram")
qc = build_grover_circuit(n_qubits, target)
st.code(qc.draw(output="text"), language="text")

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
