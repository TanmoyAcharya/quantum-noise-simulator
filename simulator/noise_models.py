from qiskit_aer.noise import (
    NoiseModel,
    pauli_error,
    amplitude_damping_error,
    phase_damping_error,
    depolarizing_error,
)

# 1-qubit gates only — cx is a 2-qubit gate and needs a separate 2-qubit error
_SINGLE_QUBIT_GATES = ["h", "x", "rx", "ry", "rz", "id", "t", "s", "sdg", "tdg"]
_TWO_QUBIT_GATES = ["cx"]

def get_noise_model(noise_type: str, probability: float) -> NoiseModel:
    """Build a Qiskit noise model based on type and probability.

    Key rule: single-qubit errors can only be applied to single-qubit gates,
    and two-qubit errors can only be applied to two-qubit gates.
    """
    noise_model = NoiseModel()

    if probability <= 0:
        return noise_model

    if noise_type == "Bit Flip":
        # 1-qubit Pauli X error
        error_1q = pauli_error([("X", probability), ("I", 1 - probability)])
        noise_model.add_all_qubit_quantum_error(error_1q, _SINGLE_QUBIT_GATES)
        # 2-qubit version: tensor product of two independent bit-flip errors
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_2q, _TWO_QUBIT_GATES)

    elif noise_type == "Phase Flip":
        # 1-qubit Pauli Z error
        error_1q = pauli_error([("Z", probability), ("I", 1 - probability)])
        noise_model.add_all_qubit_quantum_error(error_1q, _SINGLE_QUBIT_GATES)
        # 2-qubit version
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_2q, _TWO_QUBIT_GATES)

    elif noise_type == "Depolarizing":
        # depolarizing_error(p, num_qubits) already handles qubit count correctly
        error_1q = depolarizing_error(probability, 1)
        error_2q = depolarizing_error(probability, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, _SINGLE_QUBIT_GATES)
        noise_model.add_all_qubit_quantum_error(error_2q, _TWO_QUBIT_GATES)

    elif noise_type == "Amplitude Damping (T1 decay)":
        # amplitude_damping_error is always 1-qubit
        error_1q = amplitude_damping_error(probability)
        noise_model.add_all_qubit_quantum_error(error_1q, _SINGLE_QUBIT_GATES)
        # Extend to 2-qubit gate by tensoring: each qubit decays independently
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_2q, _TWO_QUBIT_GATES)

    elif noise_type == "Phase Damping (T2 decay)":
        # phase_damping_error is always 1-qubit
        error_1q = phase_damping_error(probability)
        noise_model.add_all_qubit_quantum_error(error_1q, _SINGLE_QUBIT_GATES)
        # Extend to 2-qubit gate by tensoring
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_2q, _TWO_QUBIT_GATES)

    return noise_model
