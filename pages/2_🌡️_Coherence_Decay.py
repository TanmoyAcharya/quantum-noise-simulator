"""Streamlit page — Coherence Decay (T1/T2).

Visualises how real qubits lose energy (T1) and phase coherence (T2)
over time using exponential decay models.
"""

import numpy as np
import streamlit as st

from simulator.coherence import coherence_plot, simulate_t1_decay, simulate_t2_decay

st.set_page_config(
    page_title="Coherence Decay (T1/T2)",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ Qubit Coherence Decay — T1 & T2 Times")
st.markdown(
    """
    Real qubits lose their quantum information in two distinct ways:

    | Quantity | Physics | Formula |
    |---|---|---|
    | **T1** (relaxation) | Qubit loses energy from \|1⟩ to \|0⟩ | P(t) = e^{−t/T₁} |
    | **T2** (dephasing)  | Qubit loses phase coherence | C(t) = e^{−t/T₂} |

    > 💡 T2 is always ≤ 2·T1.  IQM's superconducting qubits have T1 and T2 in the range of
    > tens to hundreds of microseconds.
    """
)
st.divider()

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Coherence Controls")

t1_us = st.sidebar.slider("T1 Relaxation Time (µs)", 1, 200, 50, 1)

t2_max = min(2 * t1_us, 200)
t2_us = st.sidebar.slider(
    "T2 Dephasing Time (µs)",
    min_value=1,
    max_value=t2_max,
    value=min(30, t2_max),
    step=1,
    help=f"Physically bounded by T2 ≤ 2·T1 = {2*t1_us} µs",
)

t_end = st.sidebar.slider(
    "Time Range End (µs)",
    min_value=10,
    max_value=500,
    value=min(4 * max(t1_us, t2_us), 500),
    step=10,
)

st.sidebar.divider()
st.sidebar.markdown(
    f"""
### 📊 Current Parameters
- **T1** = {t1_us} µs
- **T2** = {t2_us} µs
- **T2/T1 ratio** = {t2_us/t1_us:.2f}
- **Physical max T2** = {2*t1_us} µs
"""
)

# ── Compute Decays ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _compute(t1_us, t2_us, t_end):
    t1_data = simulate_t1_decay(t1_us, t_range_us=(0, t_end), n_points=200)
    t2_data = simulate_t2_decay(t2_us, t1_us, t_range_us=(0, t_end), n_points=200)
    return t1_data, t2_data


with st.spinner("⏳ Computing coherence curves…"):
    t1_data, t2_data = _compute(t1_us, t2_us, t_end)

# Midpoint coherence
mid_t = t_end / 2
t1_mid = float(np.exp(-mid_t / t1_us))
t2_mid = float(np.exp(-mid_t / min(t2_us, 2 * t1_us)))

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("⏱️ T1 (µs)", f"{t1_us}")
col2.metric("⚡ T2 (µs)", f"{t2_us}")
col3.metric("📐 T2/T1 Ratio", f"{t2_us/t1_us:.2f}")
col4.metric(f"🎯 Coherence at {mid_t:.0f} µs", f"{t2_mid:.3f}")

st.divider()

# ── Plot ──────────────────────────────────────────────────────────────────────
st.subheader("📉 Coherence Decay Curves")
st.plotly_chart(
    coherence_plot(t1_data, t2_data, t1_us, t2_us),
    use_container_width=True,
)

st.divider()

# ── Explanation ───────────────────────────────────────────────────────────────
st.subheader("🔬 T1 vs T2 — What's the Difference?")
col_l, col_r = st.columns(2)

with col_l:
    st.markdown(
        """
        ### T1 — Energy Relaxation
        - The qubit "falls" from |1⟩ to |0⟩ by emitting a photon
        - Sets the ultimate time limit for quantum computation
        - Caused by coupling to the thermal environment
        - **Analogy:** a spinning top slowly falling over
        """
    )

with col_r:
    st.markdown(
        """
        ### T2 — Dephasing
        - The qubit's phase relationship between |0⟩ and |1⟩ is randomised
        - T2 ≤ 2·T1 always (T1 contributes to T2 decay)
        - Additional sources: magnetic flux noise, charge noise
        - **Analogy:** two clocks that start in sync but drift apart
        """
    )

st.caption(
    "Built with ❤️ using [Qiskit](https://qiskit.org) + [Streamlit](https://streamlit.io)"
)
