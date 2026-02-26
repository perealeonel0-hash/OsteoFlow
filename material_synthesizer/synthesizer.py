#!/usr/bin/env python3
"""
MATERIAL SYNTHESIZER
====================
Purpose: Simulates creating new materials using voltage sequences.

Instead of using heat or acids, we use VOLTAGE to:
- Create atomic vacancies
- Diffuse atoms
- Form new chemical bonds
- Create gradient alloys

This is the MAP. The real chip would execute these voltages.
"""

import numpy as np
from dataclasses import dataclass
from scipy import constants

@dataclass
class MaterialProperties:
    """Properties of materials we work with"""
    Hf_atomic_radius: float = 0.78e-10      # meters
    Hf_mass: float = 178.49                  # g/mol
    Hf_bandgap: float = 5.7                   # eV (HfO₂)
    
    Zr_atomic_radius: float = 0.79e-10       # meters
    Zr_mass: float = 91.22                    # g/mol
    Zr_bandgap: float = 5.8                    # eV (ZrO₂)

class VoltageSynthesizer:
    """
    Main synthesis engine.
    Applies voltage pulses and predicts resulting material.
    """
    
    def __init__(self):
        self.props = MaterialProperties()
        self.history = []  # Track all synthesis steps
        
    def calculate_diffusion(self, temperature_K: float, time_s: float, element: str) -> float:
        """
        Calculate how far atoms diffuse at given temperature.
        d = sqrt(2 * D * t)
        D = D0 * exp(-Ea / kT)
        """
        if element == "Hf":
            D0 = 1e-6       # m²/s (diffusion coefficient pre-factor)
            Ea = 2.5        # eV (activation energy)
        else:  # Zr
            D0 = 1.2e-6
            Ea = 2.4        # eV (slightly lower = diffuses faster)
            
        k = constants.k / constants.e  # Boltzmann in eV/K
        D = D0 * np.exp(-Ea / (k * temperature_K))
        distance = np.sqrt(2 * D * time_s)
        return distance * 1e9  # convert to nm
        
    def apply_voltage_pulse(self, voltage_V: float, duration_s: float, composition: float) -> dict:
        """
        Apply one voltage pulse and calculate result.
        composition = current fraction of Hf (0 to 1)
        """
        # Joule heating: P = V²/R
        resistance = 100e3  # Ω (typical memristor)
        power = voltage_V**2 / resistance
        energy = power * duration_s
        
        # Temperature rise (simplified)
        volume = 100e-27  # m³ (100nm³)
        density = 10000    # kg/m³
        mass = volume * density
        specific_heat = 300  # J/kg·K
        delta_T = energy / (mass * specific_heat)
        
        base_temp = 300  # K (27°C)
        local_temp = base_temp + delta_T
        
        # Atoms diffuse based on temperature
        diff_Hf = self.calculate_diffusion(local_temp, duration_s, "Hf")
        diff_Zr = self.calculate_diffusion(local_temp, duration_s, "Zr")
        
        # Zr diffuses faster → composition changes
        new_composition = composition + 0.01 * (diff_Zr - diff_Hf)
        new_composition = np.clip(new_composition, 0, 1)
        
        # Estimate new property (bandgap)
        bandgap = (new_composition * self.props.Hf_bandgap + 
                  (1 - new_composition) * self.props.Zr_bandgap)
        
        result = {
            'voltage': voltage_V,
            'duration': duration_s,
            'local_temp_C': local_temp - 273,
            'diffusion_Hf_nm': diff_Hf,
            'diffusion_Zr_nm': diff_Zr,
            'composition_Hf': new_composition,
            'bandgap_eV': bandgap,
            'material': f"(Hf{new_composition*100:.0f}Zr{(1-new_composition)*100:.0f})O₂"
        }
        
        self.history.append(result)
        return result

# ==================== TEST ====================
if __name__ == "__main__":
    synth = VoltageSynthesizer()
    
    # Try a pulse sequence
    print("Applying voltage pulses...")
    comp = 0.5  # start at 50% Hf
    
    for V in [2.0, 2.5, 3.0]:
        result = synth.apply_voltage_pulse(V, 0.001, comp)
        comp = result['composition_Hf']
        print(f"\nAfter {V}V:")
        print(f"  Material: {result['material']}")
        print(f"  Temperature: {result['local_temp_C']:.0f}°C")
        print(f"  Bandgap: {result['bandgap_eV']:.3f}eV")