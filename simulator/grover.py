"""Grover's algorithm simulation module.

Builds and simulates Grover's search algorithm for 2 or 3 qubits,
comparing ideal and noisy results to illustrate how noise degrades
quantum amplitude amplification.
"""

import numpy as np
import plotly.graph_objects as go
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from simulator.noise_models import get_noise_model


def _oracle(n_qubits: int, target: str) -> QuantumCircuit:
    """Build a phase-oracle that marks the target bitstring.

    Args:
        n_qubits: Number of qubits.
        target: Target bitstring (e.g. ``"11"`` for 2-qubit search).

    Returns:
        Quantum circuit implementing the phase oracle.
    """
    qc = QuantumCircuit(n_qubits)
    # Flip qubits where target bit is '0' so that |target⟩ → |11…1⟩
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)
    # Multi-controlled Z via H + multi-controlled X + H on last qubit
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
    # Undo the flips
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)
    return qc


def _diffusion(n_qubits: int) -> QuantumCircuit:
    """Build the Grover diffusion (inversion-about-mean) operator.

    Args:
        n_qubits: Number of qubits.

    Returns:
        Quantum circuit implementing the diffusion operator.
    """
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc


def build_grover_circuit(n_qubits: int = 2, target: str = "11") -> QuantumCircuit:
    """Build a Grover's algorithm circuit for the given target state.

    The number of Grover iterations is chosen optimally:
    ``floor(π/4 * sqrt(N))`` where N = 2^n_qubits.

    Args:
        n_qubits: Number of search qubits (2 or 3 recommended).
        target: Target bitstring to search for.

    Returns:
        QuantumCircuit with measurements on all qubits.
    """
    n_states = 2 ** n_qubits
    n_iterations = max(1, int(np.round(np.pi / 4 * np.sqrt(n_states))))

    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial uniform superposition
    qc.h(range(n_qubits))

    oracle_qc = _oracle(n_qubits, target)
    diffusion_qc = _diffusion(n_qubits)

    for _ in range(n_iterations):
        qc.compose(oracle_qc, inplace=True)
        qc.compose(diffusion_qc, inplace=True)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def run_grover(
    n_qubits: int = 2,
    target: str = "11",
    noise_type: str = "Depolarizing",
    probability: float = 0.01,
    shots: int = 4096,
) -> dict:
    """Run Grover's algorithm with and without noise.

    Args:
        n_qubits: Number of search qubits.
        target: Target bitstring to search for.
        noise_type: Noise model to apply for the noisy run.
        probability: Noise probability for the noisy run.
        shots: Number of measurement shots.

    Returns:
        Dictionary with keys:
            - ``ideal_counts``: counts from noiseless simulation
            - ``noisy_counts``: counts from noisy simulation
            - ``target``: the target bitstring
            - ``ideal_prob``: ideal probability of measuring target
            - ``noisy_prob``: noisy probability of measuring target
    """
    qc = build_grover_circuit(n_qubits, target)

    # Ideal run
    ideal_backend = AerSimulator()
    ideal_qc = transpile(qc, ideal_backend)
    ideal_counts = ideal_backend.run(ideal_qc, shots=shots).result().get_counts()

    # Noisy run
    noise_model = get_noise_model(noise_type, probability)
    noisy_backend = AerSimulator(noise_model=noise_model)
    noisy_qc = transpile(qc, noisy_backend)
    noisy_counts = noisy_backend.run(noisy_qc, shots=shots).result().get_counts()

    ideal_prob = ideal_counts.get(target, 0) / shots
    noisy_prob = noisy_counts.get(target, 0) / shots

    return {
        "ideal_counts": ideal_counts,
        "noisy_counts": noisy_counts,
        "target": target,
        "ideal_prob": ideal_prob,
        "noisy_prob": noisy_prob,
    }


def grover_plot(results: dict, shots: int) -> go.Figure:
    """Plot ideal vs noisy measurement probabilities for all basis states.

    Args:
        results: Output of :func:`run_grover`.
        shots: Number of shots used (for normalisation).

    Returns:
        Plotly Figure with grouped bars for each basis state.
    """
    ideal_counts = results["ideal_counts"]
    noisy_counts = results["noisy_counts"]
    target = results["target"]
    n_qubits = len(target)
    all_states = sorted([format(i, f"0{n_qubits}b") for i in range(2 ** n_qubits)])

    ideal_probs = [ideal_counts.get(s, 0) / shots for s in all_states]
    noisy_probs = [noisy_counts.get(s, 0) / shots for s in all_states]

    # Highlight the target state
    bar_colors_ideal = ["lime" if s == target else "mediumseagreen" for s in all_states]
    bar_colors_noisy = ["orange" if s == target else "tomato" for s in all_states]

    fig = go.Figure(data=[
        go.Bar(
            name="✅ Ideal",
            x=all_states,
            y=ideal_probs,
            marker_color=bar_colors_ideal,
            opacity=0.9,
        ),
        go.Bar(
            name="⚠️ Noisy",
            x=all_states,
            y=noisy_probs,
            marker_color=bar_colors_noisy,
            opacity=0.9,
        ),
    ])

    fig.update_layout(
        barmode="group",
        title=f"Grover's Search — Target: |{target}⟩",
        xaxis_title="Basis State",
        yaxis_title="Probability",
        yaxis=dict(range=[0, 1.1]),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        legend=dict(x=0.75, y=1.0),
        margin=dict(t=50, b=40),
    )
    return fig
