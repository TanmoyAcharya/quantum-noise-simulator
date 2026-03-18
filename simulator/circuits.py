from qiskit import QuantumCircuit


def build_circuit(circuit_type: str) -> QuantumCircuit:
    """Build a named quantum circuit."""

    if circuit_type == "Superposition (H gate)":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)

    elif circuit_type == "Bell State (Entanglement)":
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

    elif circuit_type == "GHZ State (3 Qubits)":
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])

    elif circuit_type == "Phase Kickback":
        qc = QuantumCircuit(2, 1)
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
        qc.h(0)
        qc.measure(0, 0)

    elif circuit_type == "T Gate (pi/8 gate)":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.t(0)
        qc.h(0)
        qc.measure(0, 0)

    else:
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)

    return qc


def build_statevector_circuit(circuit_type: str) -> QuantumCircuit:
    """Build circuits WITHOUT measurements for statevector/density matrix simulation (Bloch sphere)."""

    if circuit_type == "Superposition (H gate)":
        qc = QuantumCircuit(1)
        qc.h(0)

    elif circuit_type == "Bell State (Entanglement)":
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

    elif circuit_type == "GHZ State (3 Qubits)":
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)

    elif circuit_type == "Phase Kickback":
        qc = QuantumCircuit(2)
        qc.x(1)
        qc.h(0)
        qc.cx(0, 1)
        qc.h(0)

    elif circuit_type == "T Gate (pi/8 gate)":
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.t(0)
        qc.h(0)

    else:
        qc = QuantumCircuit(1)
        qc.h(0)

    return qc
