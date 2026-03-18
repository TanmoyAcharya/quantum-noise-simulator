import numpy as np
import plotly.graph_objects as go


def counts_bar_chart(ideal_counts: dict, noisy_counts: dict, shots: int) -> go.Figure:
    """Side-by-side bar chart: Ideal vs Noisy measurement probabilities."""
    all_keys = sorted(set(list(ideal_counts.keys()) + list(noisy_counts.keys())))
    ideal_vals = [ideal_counts.get(k, 0) / shots for k in all_keys]
    noisy_vals = [noisy_counts.get(k, 0) / shots for k in all_keys]

    fig = go.Figure(data=[
        go.Bar(name="✅ Ideal (No Noise)", x=all_keys, y=ideal_vals,
               marker_color="mediumseagreen", opacity=0.9),
        go.Bar(name="⚠️ Noisy Simulation", x=all_keys, y=noisy_vals,
               marker_color="tomato", opacity=0.9),
    ])
    fig.update_layout(
        barmode="group",
        title="Measurement Probabilities: Ideal vs Noisy",
        xaxis_title="Bitstring Outcome",
        yaxis_title="Probability",
        yaxis=dict(range=[0, 1.05]),
        template="plotly_dark",
        legend=dict(x=0.65, y=1.0),
        margin=dict(t=50, b=40),
    )
    return fig


def fidelity_vs_noise_plot(noise_levels: list, fidelities: list, noise_type: str) -> go.Figure:
    """Plot fidelity decay as noise probability increases."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=noise_levels,
        y=fidelities,
        mode="lines+markers",
        line=dict(color="royalblue", width=3),
        marker=dict(size=7, color="royalblue"),
        name="Fidelity",
        fill="tozeroy",
        fillcolor="rgba(65, 105, 225, 0.15)",
    ))
    fig.add_hline(
        y=1.0, line_dash="dash", line_color="lime",
        annotation_text="Ideal (p=0)", annotation_position="top right"
    )
    fig.update_layout(
        title=f"Fidelity Decay Under {noise_type} Noise",
        xaxis_title="Noise Probability (p)",
        yaxis_title="Fidelity vs Ideal",
        yaxis=dict(range=[0, 1.1]),
        template="plotly_dark",
        margin=dict(t=50, b=40),
    )
    return fig
