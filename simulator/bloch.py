import numpy as np
import plotly.graph_objects as go
from qiskit.quantum_info import DensityMatrix, partial_trace, Statevector


def density_matrix_to_bloch(rho: np.ndarray) -> tuple:
    """Convert a single-qubit density matrix to Bloch sphere (x, y, z) coordinates."""
    x = float(2 * np.real(rho[0, 1]))
    y = float(2 * np.imag(rho[1, 0]))
    z = float(np.real(rho[0, 0] - rho[1, 1]))
    return x, y, z


def get_bloch_vectors(circuit_type: str, noise_model=None) -> list:
    """
    Compute Bloch vectors for each qubit in the circuit.
    Returns a list of (x_ideal, y_ideal, z_ideal, x_noisy, y_noisy, z_noisy) per qubit.
    """
    from simulator.circuits import build_statevector_circuit
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    from qiskit_aer.noise import NoiseModel

    qc = build_statevector_circuit(circuit_type)
    n_qubits = qc.num_qubits

    # --- Ideal: statevector simulation ---
    ideal_backend = AerSimulator(method="statevector")
    qc_sv = qc.copy()
    qc_sv.save_statevector()
    tqc_sv = transpile(qc_sv, ideal_backend)
    sv_data = ideal_backend.run(tqc_sv).result().get_statevector()
    ideal_state = Statevector(sv_data)

    # --- Noisy: density matrix simulation ---
    if noise_model is None:
        noise_model = NoiseModel()
    noisy_backend = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc_dm = qc.copy()
    qc_dm.save_density_matrix()
    tqc_dm = transpile(qc_dm, noisy_backend)
    dm_data = noisy_backend.run(tqc_dm).result().data()["density_matrix"]
    noisy_dm = DensityMatrix(dm_data)

    results = []
    for qubit_idx in range(n_qubits):
        other_qubits = [q for q in range(n_qubits) if q != qubit_idx]

        # Ideal reduced density matrix
        if other_qubits:
            ideal_reduced = partial_trace(ideal_state, other_qubits)
        else:
            ideal_reduced = DensityMatrix(ideal_state)
        ideal_rho = np.array(ideal_reduced.data)

        # Noisy reduced density matrix
        if other_qubits:
            noisy_reduced = partial_trace(noisy_dm, other_qubits)
        else:
            noisy_reduced = noisy_dm
        noisy_rho = np.array(noisy_reduced.data)

        xi, yi, zi = density_matrix_to_bloch(ideal_rho)
        xn, yn, zn = density_matrix_to_bloch(noisy_rho)
        results.append((xi, yi, zi, xn, yn, zn))

    return results


def build_bloch_sphere_figure(bloch_vectors: list, qubit_idx: int = 0) -> go.Figure:
    """
    Build a full 3D Bloch sphere Plotly figure showing ideal vs noisy state vectors.
    """
    xi, yi, zi, xn, yn, zn = bloch_vectors[qubit_idx]

    # Sphere surface
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    sx = np.outer(np.cos(u), np.sin(v))
    sy = np.outer(np.sin(u), np.sin(v))
    sz = np.outer(np.ones(np.size(u)), np.cos(v))

    fig = go.Figure()

    # Transparent sphere
    fig.add_trace(go.Surface(
        x=sx, y=sy, z=sz,
        opacity=0.10,
        colorscale=[[0, "royalblue"], [1, "royalblue"]],
        showscale=False,
        hoverinfo="skip",
        name="Bloch Sphere",
    ))

    # Axis lines and labels
    axis_range = 1.35
    for axis, color, label_pos, label in [
        ((1, 0, 0), "red",   ( axis_range, 0, 0), "|+⟩"),
        ((-1, 0, 0), "red",   (-axis_range, 0, 0), "|−⟩"),
        ((0, 1, 0), "green", (0,  axis_range, 0), "|i+⟩"),
        ((0,-1, 0), "green", (0, -axis_range, 0), "|i−⟩"),
        ((0, 0, 1), "white", (0, 0,  axis_range), "|0⟩"),
        ((0, 0,-1), "white", (0, 0, -axis_range), "|1⟩"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[0, axis[0] * 1.2], y=[0, axis[1] * 1.2], z=[0, axis[2] * 1.2],
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter3d(
            x=[label_pos[0]], y=[label_pos[1]], z=[label_pos[2]],
            mode="text",
            text=[label],
            textfont=dict(color=color, size=13),
            showlegend=False, hoverinfo="skip",
        ))

    # Equator circle
    theta = np.linspace(0, 2 * np.pi, 100)
    fig.add_trace(go.Scatter3d(
        x=np.cos(theta), y=np.sin(theta), z=np.zeros_like(theta),
        mode="lines", line=dict(color="gray", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))

    # Meridian circles
    fig.add_trace(go.Scatter3d(
        x=np.zeros_like(theta), y=np.cos(theta), z=np.sin(theta),
        mode="lines", line=dict(color="gray", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter3d(
        x=np.cos(theta), y=np.zeros_like(theta), z=np.sin(theta),
        mode="lines", line=dict(color="gray", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))

    # Ideal state vector (green)
    fig.add_trace(go.Scatter3d(
        x=[0, xi], y=[0, yi], z=[0, zi],
        mode="lines+markers",
        line=dict(color="lime", width=6),
        marker=dict(size=[2, 10], color="lime", symbol=["circle", "diamond"]),
        name=f"✅ Ideal  ({xi:.2f}, {yi:.2f}, {zi:.2f})",
    ))

    # Noisy state vector (red)
    fig.add_trace(go.Scatter3d(
        x=[0, xn], y=[0, yn], z=[0, zn],
        mode="lines+markers",
        line=dict(color="tomato", width=6),
        marker=dict(size=[2, 10], color="tomato", symbol=["circle", "diamond"]),
        name=f"⚠️ Noisy  ({xn:.2f}, {yn:.2f}, {zn:.2f})",
    ))

    # Yellow dashed line showing state shift
    fig.add_trace(go.Scatter3d(
        x=[xi, xn], y=[yi, yn], z=[zi, zn],
        mode="lines",
        line=dict(color="yellow", width=3, dash="dash"),
        name="State Shift (Noise Effect)",
    ))

    bloch_len_ideal = np.sqrt(xi**2 + yi**2 + zi**2)
    bloch_len_noisy = np.sqrt(xn**2 + yn**2 + zn**2)

    fig.update_layout(
        title=(
            f"Bloch Sphere — Qubit {qubit_idx}  |  "
            f"Purity:  Ideal = {bloch_len_ideal:.3f}   Noisy = {bloch_len_noisy:.3f}"
        ),
        scene=dict(
            xaxis=dict(title="X", range=[-1.5, 1.5], showbackground=False, gridcolor="gray"),
            yaxis=dict(title="Y", range=[-1.5, 1.5], showbackground=False, gridcolor="gray"),
            zaxis=dict(title="Z", range=[-1.5, 1.5], showbackground=False, gridcolor="gray"),
            bgcolor="rgb(17, 17, 17)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
        ),
        template="plotly_dark",
        legend=dict(x=0.0, y=0.95, font=dict(size=11)),
        margin=dict(l=0, r=0, t=50, b=0),
        height=520,
    )
    return fig
