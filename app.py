import numpy as np
import streamlit as st
from qiskit import transpile
from qiskit_aer import AerSimulator

from simulator.bloch import build_bloch_sphere_figure, get_bloch_vectors
from simulator.circuits import build_circuit
from simulator.noise_models import get_noise_model
from simulator.visualizer import counts_bar_chart, fidelity_vs_noise_plot

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚛️ Quantum Noise Simulator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("⚛️ Quantum Decoherence & Noise Impact Simulator")
st.markdown(
    """
    > Explore how **quantum noise** degrades the performance of quantum circuits.
    > Visualize the gap between the *ideal quantum world* and *real noisy hardware* —
    > the very challenge engineers at companies like **IQM** solve every day.
    """
)
st.divider()

# ── Sidebar Controls ─────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Simulation Controls")

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
        "Bit Flip",
        "Phase Flip",
        "Depolarizing",
        "Amplitude Damping (T1 decay)",
        "Phase Damping (T2 decay)",
    ],
)

noise_prob = st.sidebar.slider(
    "Noise Probability (p)",
    0.0, 0.5, 0.05, 0.01,
    help="Higher = more noise = worse quantum performance",
)

shots = st.sidebar.slider("Measurement Shots", 512, 8192, 2048, 512)

st.sidebar.divider()
st.sidebar.markdown(
    """
### 📖 Noise Types Explained
| Type | Physics |
|---|---|
| **Bit Flip** | Random |0⟩↔|1⟩ flip |
| **Phase Flip** | |+⟩↔|−⟩ phase error |
| **Depolarizing** | Random X/Y/Z error |
| **Amplitude Damping** | T1 energy relaxation |
| **Phase Damping** | T2 dephasing |

### 🔬 Circuits
| Circuit | Qubits |
|---|---|
| Superposition | 1 |
| Bell State | 2 |
| GHZ State | 3 |
| Phase Kickback | 2 |
| T Gate | 1 |
"""
)

# ── Run Simulations ───────────────────────────────────────────────────────────
noise_model = get_noise_model(noise_type, noise_prob)
qc = build_circuit(circuit_type)

# Ideal run
ideal_backend = AerSimulator()
ideal_qc = transpile(qc, ideal_backend)
ideal_counts = ideal_backend.run(ideal_qc, shots=shots).result().get_counts()

# Noisy run
noisy_backend = AerSimulator(noise_model=noise_model)
noisy_qc = transpile(qc, noisy_backend)
noisy_counts = noisy_backend.run(noisy_qc, shots=shots).result().get_counts()


def compute_fidelity(ideal: dict, noisy: dict, n_shots: int) -> float:
    """Bhattacharyya coefficient as fidelity proxy."""
    all_keys = set(list(ideal.keys()) + list(noisy.keys()))
    ip = np.array([ideal.get(k, 0) / n_shots for k in all_keys])
    noisy_probs = np.array([noisy.get(k, 0) / n_shots for k in all_keys])
    return float(np.sum(np.sqrt(ip * noisy_probs)) ** 2)


fidelity = compute_fidelity(ideal_counts, noisy_counts, shots)

# Fidelity sweep across noise levels
noise_levels = np.linspace(0, 0.5, 20)
fidelities = []
for p in noise_levels:
    nm = get_noise_model(noise_type, float(p))
    nb = AerSimulator(noise_model=nm)
    tqc = transpile(qc, nb)
    res = nb.run(tqc, shots=1024).result().get_counts()
    fidelities.append(compute_fidelity(ideal_counts, res, 1024))

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Fidelity", f"{fidelity:.3f}", delta=f"{fidelity - 1.0:.3f}", delta_color="inverse")
col2.metric("📡 Noise Type", noise_type.split(" ")[0])
col3.metric("🔧 Noise Probability", f"{noise_prob:.2f}")
col4.metric("🔢 Circuit Qubits", str(qc.num_qubits))

st.divider()

# ── Measurement Results + Fidelity Curve ─────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Ideal vs Noisy Measurements")
    st.plotly_chart(
        counts_bar_chart(ideal_counts, noisy_counts, shots),
        use_container_width=True,
    )

with col_right:
    st.subheader("📉 Fidelity Decay Curve")
    st.plotly_chart(
        fidelity_vs_noise_plot(noise_levels, fidelities, noise_type),
        use_container_width=True,
    )

st.divider()

# ── Bloch Sphere ─────────────────────────────────────────────────────────────
st.subheader("🌐 Bloch Sphere Visualizer")
st.markdown(
    """
    The Bloch sphere represents a single qubit's quantum state as a point on a unit sphere.
    - 🟢 **Green arrow** → Ideal state (no noise) — pure state on the surface
    - 🔴 **Red arrow** → Noisy state — pulled toward the center (mixed state)
    - 🟡 **Yellow dashed line** → How far noise has shifted the qubit state
    - **Purity** = length of the Bloch vector (1.0 = pure state, < 1.0 = mixed/decoherent)
    """
)

try:
    with st.spinner("Computing Bloch sphere states..."):
        bloch_vectors = get_bloch_vectors(circuit_type, noise_model=noise_model)

    n_qubits = qc.num_qubits
    if n_qubits == 1:
        st.plotly_chart(
            build_bloch_sphere_figure(bloch_vectors, qubit_idx=0),
            use_container_width=True,
        )
    else:
        qubit_tabs = st.tabs([f"Qubit {i}" for i in range(n_qubits)])
        for i, tab in enumerate(qubit_tabs):
            with tab:
                st.plotly_chart(
                    build_bloch_sphere_figure(bloch_vectors, qubit_idx=i),
                    use_container_width=True,
                )
except Exception as e:
    st.warning(f"Bloch sphere visualization unavailable for this configuration: {e}")

st.divider()

# ── Circuit Diagram ───────────────────────────────────────────────────────────
st.subheader("🔬 Circuit Diagram")
st.code(qc.draw(output="text"), language="text")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io) "
    "| Inspired by QPU engineering challenges at IQM Quantum Computers "
    "| [GitHub](https://github.com/TanmoyAcharya/quantum-noise-simulator)"
)
