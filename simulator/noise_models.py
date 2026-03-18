from qiskit_aer.noise import (
    NoiseModel,
    pauli_error,
    amplitude_damping_error,
    phase_damping_error,
    depolarizing_error,
)


def get_noise_model(noise_type: str, probability: float) -> NoiseModel:
    """Build a Qiskit noise model based on type and probability."""
    noise_model = NoiseModel()

    if probability <= 0:
        return noise_model

    if noise_type == "Bit Flip":
        error = pauli_error([("X", probability), ("I", 1 - probability)])
        noise_model.add_all_qubit_quantum_error(error, ["h", "x", "rx", "ry", "rz", "id", "cx"])

    elif noise_type == "Phase Flip":
        error = pauli_error([("Z", probability), ("I", 1 - probability)])
        noise_model.add_all_qubit_quantum_error(error, ["h", "x", "rx", "ry", "rz", "id", "cx"])

    elif noise_type == "Depolarizing":
        error_1q = depolarizing_error(probability, 1)
        error_2q = depolarizing_error(probability, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, ["h", "x", "rx", "ry", "rz", "id", "t"])
        noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])

    elif noise_type == "Amplitude Damping (T1 decay)":
        error = amplitude_damping_error(probability)
        noise_model.add_all_qubit_quantum_error(error, ["h", "x", "rx", "ry", "rz", "id", "t"])

    elif noise_type == "Phase Damping (T2 decay)":
        error = phase_damping_error(probability)
        noise_model.add_all_qubit_quantum_error(error, ["h", "x", "rx", "ry", "rz", "id", "t"])

    return noise_model
