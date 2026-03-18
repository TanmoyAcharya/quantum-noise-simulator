"""Streamlit page — Bell Inequality (CHSH) Test.

Simulates the CHSH Bell inequality test and shows how quantum entanglement
produces S > 2 (violating the classical bound), and how noise degrades this.
"""

import numpy as np
import streamlit as st

from simulator.bell import chsh_plot, run_chsh_test

st.set_page_config(
    page_title="Bell Inequality (CHSH)",
    page_icon="🔗",
    layout="wide",
)

st.title("🔗 Bell Inequality — CHSH Test")
st.markdown(
    """
    The **CHSH Bell inequality** tests whether nature can be explained by classical hidden
    variables.  For a perfect entangled state, the quantum S parameter reaches **2√2 ≈ 2.828**,
    violating the classical bound of **S ≤ 2**.

    | Bound | Value | Meaning |
    |---|---|---|
    | **Classical** | S ≤ 2 | Any local hidden-variable theory |
    | **Quantum (Tsirelson)** | S ≤ 2√2 ≈ 2.828 | Maximum quantum correlation |

    > 💡 Noise drives S back toward (and below) the classical bound — exactly the decoherence
    > challenge QPU engineers must overcome.
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ CHSH Controls")

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
    min_value=0.0, max_value=0.3, value=0.0, step=0.005,
    format="%.3f",
)

shots = st.sidebar.select_slider(
    "Measurement Shots",
    options=[2048, 4096, 8192, 16384],
    value=8192,
)

st.sidebar.divider()
st.sidebar.markdown(
    """
### 📐 CHSH Measurement Settings
| Setting | Alice (θ_A) | Bob (θ_B) |
|---|---|---|
| (a,b)   | 0°   | 22.5° |
| (a,b')  | 0°   | 67.5° |
| (a',b)  | 45°  | 22.5° |
| (a',b') | 45°  | 67.5° |

**S = E(a,b) − E(a,b') + E(a',b) + E(a',b')**
"""
)

# ── Single CHSH Run ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _single_run(noise_type, noise_prob, shots):
    return run_chsh_test(noise_type, noise_prob, shots)


with st.spinner("⏳ Running CHSH test…"):
    chsh_result = _single_run(noise_type, noise_prob, shots)

s_val = chsh_result["S"]
classical_bound = chsh_result["classical_bound"]
quantum_bound = chsh_result["quantum_bound"]
violates = s_val > classical_bound

# ── S Value Display ────────────────────────────────────────────────────────────
s_color = "🟢" if violates else "🔴"
violation_text = "**Quantum violation!** S > 2" if violates else "**Classical regime.** S ≤ 2"

st.markdown(
    f"## {s_color} CHSH S = `{s_val:.4f}`  —  {violation_text}"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 S Value", f"{s_val:.4f}")
col2.metric("🔴 Classical Bound", f"{classical_bound:.3f}")
col3.metric("🟢 Quantum Bound (Tsirelson)", f"{quantum_bound:.3f}")
col4.metric("✅ Violation?", "Yes ✓" if violates else "No ✗",
            delta="Above classical" if violates else "Below classical",
            delta_color="normal" if violates else "inverse")

st.divider()

# ── Correlator Table ──────────────────────────────────────────────────────────
st.subheader("📋 CHSH Correlator Values")
correlators = chsh_result["correlators"]
table_data = {
    "Setting": list(correlators.keys()),
    "Correlator": [f"{v:.4f}" for v in correlators.values()],
}
st.table(table_data)

st.divider()

# ── S vs Noise Probability Sweep ───────────────────────────────────────────────
st.subheader("📈 CHSH S Parameter vs Noise Probability")
st.markdown("Sweep across noise levels to see how noise destroys quantum entanglement:")

sweep_probs = [0.0, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3]


@st.cache_data(show_spinner=False)
def _sweep(noise_type, shots, sweep_probs_tuple):
    sweep_results = []
    for p in sweep_probs_tuple:
        r = run_chsh_test(noise_type, p, shots)
        r["probability"] = p
        sweep_results.append(r)
    return sweep_results


with st.spinner("⏳ Sweeping noise levels for CHSH plot…"):
    sweep_results = _sweep(noise_type, min(shots, 4096), tuple(sweep_probs))

st.plotly_chart(chsh_plot(sweep_results), use_container_width=True)

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
