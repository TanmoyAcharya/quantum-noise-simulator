# ⚛️ Quantum Decoherence & Noise Impact Simulator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.x-6929C4?logo=qiskit&logoColor=white)](https://qiskit.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/TanmoyAcharya/quantum-noise-simulator?style=social)](https://github.com/TanmoyAcharya/quantum-noise-simulator)

Interactive web app to simulate and visualize how quantum noise degrades quantum circuit fidelity — built with Qiskit and Streamlit.

---

## 🚀 Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quantum-noise-simulator.streamlit.app/)

🔗 **[https://quantum-noise-simulator.streamlit.app/](https://quantum-noise-simulator.streamlit.app/)**

---

## ✨ Features

- **5 Noise Models**: Bit Flip, Phase Flip, Depolarizing, Amplitude Damping (T1), Phase Damping (T2)
- **5 Quantum Circuits**: Superposition, Bell State, GHZ State, Phase Kickback, T Gate
- **Interactive 3D Bloch Sphere** showing ideal vs noisy qubit state with purity display
- **Fidelity decay sweep curve** across noise probabilities
- **Side-by-side measurement probability bar charts** (Ideal vs Noisy)
- **Real-time fidelity metric** with 4-panel KPI dashboard
- **Zero-Noise Extrapolation (ZNE)** — quantum error mitigation simulation
- **T1/T2 Time Decay curves** — time-based coherence simulation in microseconds
- **Density Matrix Heatmap** — visualize decoherence in the density matrix
- **Noise Comparison Mode** — all 5 noise models side by side
- **Grover's Algorithm** — see how noise breaks amplitude amplification
- **Bell Inequality (CHSH) Test** — quantum vs classical bounds under noise
- **Dark-themed UI** optimized for data visualization

---

## 📸 Screenshots

<!-- Add screenshots here after deploying -->

---

## 🛠️ Local Setup

```bash
git clone https://github.com/TanmoyAcharya/quantum-noise-simulator.git
cd quantum-noise-simulator
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Fork or push this repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** and select your repository.
4. Set the **Main file path** to `app.py`.
5. Click **"Deploy!"** — your app will be live in minutes.

---

## 🧠 Concepts Explained

| Concept | Description |
|---|---|
| **Qubit** | The fundamental unit of quantum information; can exist as a superposition of 0 and 1 |
| **Superposition** | A qubit's ability to be in multiple states simultaneously until measured |
| **Entanglement** | Quantum correlation between qubits where the state of one instantly influences another |
| **Decoherence** | The loss of quantum coherence due to environmental noise, turning pure states into mixed states |
| **T1 decay** | Energy relaxation time — how long a qubit stays in the excited \|1⟩ state before decaying to \|0⟩ |
| **T2 decay** | Dephasing time — how long a qubit maintains phase coherence in a superposition |
| **Fidelity** | A measure (0–1) of how closely a noisy quantum state matches the ideal state |
| **Bloch Sphere** | A geometric representation of a qubit's state as a point on (or inside) a unit sphere |
| **Noise Model** | A mathematical description of the errors that affect quantum gates and qubits |
| **ZNE** | Zero-Noise Extrapolation — a quantum error mitigation technique that estimates ideal results by extrapolating from noisy runs |
| **Density Matrix** | A matrix representation of a quantum state that handles both pure and mixed (noisy) states |
| **CHSH Inequality** | A Bell test — quantum mechanics violates it (S > 2), classical physics cannot |

---

## 📁 Project Structure

```
quantum-noise-simulator/
├── app.py                        # Main Streamlit app entry point
├── simulator/
│   ├── __init__.py
│   ├── circuits.py               # Quantum circuit builders
│   ├── noise_models.py           # Noise model definitions
│   ├── visualizer.py             # Plots: bar chart, fidelity curve
│   ├── bloch.py                  # Bloch sphere visualizer
│   ├── mitigation.py             # Zero-Noise Extrapolation (ZNE)
│   ├── coherence.py              # T1/T2 time decay simulation
│   ├── density_matrix.py         # Density matrix heatmap
│   ├── comparison.py             # Noise comparison across models
│   ├── grover.py                 # Grover's algorithm with noise
│   └── bell.py                   # Bell inequality (CHSH) test
├── pages/
│   ├── 1_🧮_Error_Mitigation.py  # ZNE page
│   ├── 2_🌡️_Coherence_Decay.py  # T1/T2 page
│   ├── 3_🔥_Density_Matrix.py    # Density matrix page
│   ├── 4_📡_Noise_Comparison.py  # Comparison page
│   ├── 5_🔍_Grovers_Algorithm.py # Grover's page
│   └── 6_🔗_Bell_Inequality.py   # Bell inequality page
├── .streamlit/
│   └── config.toml               # Streamlit dark theme config
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🔬 Relevance to Quantum Hardware

This simulator directly mirrors the challenges faced by QPU engineers at companies like **IQM Quantum Computers**:

- **Qubit calibration**: T1 and T2 times must be measured and optimized for each physical qubit; this app visualizes their effect on circuit fidelity.
- **Gate fidelity**: Every quantum gate introduces noise; the depolarizing and Pauli error models here approximate real gate error rates.
- **Noise mitigation**: Zero-Noise Extrapolation and other techniques are implemented to show how engineers recover ideal results from noisy hardware.
- **Bloch sphere diagnostics**: QPU engineers use Bloch sphere representations to visualize qubit state drift during calibration sequences.
- **Randomized benchmarking**: The noise comparison and fidelity sweep tools mirror standard QPU characterization workflows.

By interactively exploring noise parameters, users gain intuition for the engineering trade-offs at the heart of near-term quantum computing.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).