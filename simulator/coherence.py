"""T1/T2 coherence time decay simulation module.

Simulates the exponential decay of qubit populations (T1) and
coherences (T2) over time, mimicking real QPU decoherence dynamics.
"""

import numpy as np
import plotly.graph_objects as go


def simulate_t1_decay(
    t1_us: float,
    t_range_us: tuple = (0, 100),
    n_points: int = 100,
) -> dict:
    """Simulate qubit excited-state population decay due to T1 relaxation.

    Args:
        t1_us: T1 relaxation time in microseconds.
        t_range_us: Tuple (t_start, t_end) defining the time window (µs).
        n_points: Number of time points to compute.

    Returns:
        Dictionary with keys:
            - ``times``: array of time values (µs)
            - ``populations``: array of excited-state populations P(t) = exp(-t/T1)
    """
    times = np.linspace(t_range_us[0], t_range_us[1], n_points)
    populations = np.exp(-times / t1_us)
    return {"times": times.tolist(), "populations": populations.tolist()}


def simulate_t2_decay(
    t2_us: float,
    t1_us: float,
    t_range_us: tuple = (0, 100),
    n_points: int = 100,
) -> dict:
    """Simulate qubit coherence decay due to T2 dephasing.

    T2 is physically constrained by T2 <= 2*T1.

    Args:
        t2_us: T2 dephasing time in microseconds (will be clipped to 2*T1).
        t1_us: T1 relaxation time in microseconds.
        t_range_us: Tuple (t_start, t_end) defining the time window (µs).
        n_points: Number of time points to compute.

    Returns:
        Dictionary with keys:
            - ``times``: array of time values (µs)
            - ``coherences``: array of coherence values C(t) = exp(-t/T2)
    """
    t2_eff = min(t2_us, 2.0 * t1_us)
    times = np.linspace(t_range_us[0], t_range_us[1], n_points)
    coherences = np.exp(-times / t2_eff)
    return {"times": times.tolist(), "coherences": coherences.tolist()}


def coherence_plot(
    t1_data: dict,
    t2_data: dict,
    t1_us: float,
    t2_us: float,
) -> go.Figure:
    """Plot T1 and T2 decay curves on the same Plotly figure.

    Args:
        t1_data: Output of :func:`simulate_t1_decay`.
        t2_data: Output of :func:`simulate_t2_decay`.
        t1_us: T1 value used (for annotation).
        t2_us: T2 value used (for annotation).

    Returns:
        Plotly Figure with both decay curves in dark-theme styling.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t1_data["times"],
        y=t1_data["populations"],
        mode="lines",
        line=dict(color="royalblue", width=3),
        fill="tozeroy",
        fillcolor="rgba(65, 105, 225, 0.15)",
        name=f"T1 Decay  (T1 = {t1_us:.1f} µs)",
    ))

    fig.add_trace(go.Scatter(
        x=t2_data["times"],
        y=t2_data["coherences"],
        mode="lines",
        line=dict(color="tomato", width=3),
        fill="tozeroy",
        fillcolor="rgba(255, 99, 71, 0.12)",
        name=f"T2 Dephasing  (T2 = {t2_us:.1f} µs)",
    ))

    fig.add_hline(
        y=1 / np.e,
        line_dash="dash",
        line_color="gray",
        annotation_text="1/e ≈ 0.368",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Qubit Coherence Decay (T1 & T2)",
        xaxis_title="Time (µs)",
        yaxis_title="Population / Coherence",
        yaxis=dict(range=[0, 1.1]),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        legend=dict(x=0.55, y=0.95),
        margin=dict(t=50, b=40),
    )
    return fig
