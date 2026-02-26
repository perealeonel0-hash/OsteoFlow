#!/usr/bin/env python3
# quantum_effects.py - Efectos cuánticos en el chip

import numpy as np
import matplotlib.pyplot as plt
from scipy import constants

class QuantumTunneling:
    def __init__(self):
        self.hbar = constants.hbar
        self.m_e = constants.m_e
        self.e = constants.e
        
    def tunneling_probability(self, barrier_height_eV: float, barrier_width_nm: float, electron_energy_eV: float) -> float:
        V = barrier_height_eV * self.e
        E = electron_energy_eV * self.e
        d = barrier_width_nm * 1e-9
        if E >= V:
            return 1.0
        kappa = np.sqrt(2 * self.m_e * (V - E)) / self.hbar
        T = np.exp(-2 * kappa * d)
        return T

class QuantumNoise:
    def shot_noise(self, current_A: float, bandwidth_Hz: float) -> float:
        e = constants.e
        noise = np.sqrt(2 * e * current_A * bandwidth_Hz)
        return noise
    
    def thermal_noise(self, resistance_Ω: float, bandwidth_Hz: float, temperature_K: float = 300) -> float:
        k_B = constants.k
        noise = np.sqrt(4 * k_B * temperature_K * resistance_Ω * bandwidth_Hz)
        return noise

if __name__ == "__main__":
    qt = QuantumTunneling()
    prob = qt.tunneling_probability(2.0, 2.0, 0.5)
    print(f"Probabilidad de tunneling: {prob*100:.4f}%")