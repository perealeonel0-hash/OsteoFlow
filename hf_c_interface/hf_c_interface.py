#!/usr/bin/env python3
"""
Hf-C INTERFACE CREATOR
======================
Purpose: Creates chemical bonds between graphene and HfO₂.

Based on Vitória Júnior (2015):
- With vacancies, Hf-C bonds form
- Bond energy: -0.22 eV (2× stronger than van der Waals)
- Distance: 3.00 Å

This is the MAP. The real chip would execute these voltages.
"""

import numpy as np
from dataclasses import dataclass

# Import vacancy creator (relative path)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from03_material_synthesizer.vacancy_creator import VacancyCreator

@dataclass
class InterfaceProperties:
    """Properties of graphene-HfO₂ interface"""
    vdw_distance: float = 3.05e-10      # meters (without bonds)
    vdw_energy: float = -0.110           # eV (weak)
    
    hfc_distance: float = 3.00e-10       # meters (with Hf-C bonds)
    hfc_energy: float = -0.220            # eV (strong, 2×)
    
    required_C_vacancies: float = 0.01    # need 1% C vacancies
    required_O_vacancies: float = 0.05    # need 5% O vacancies
    formation_voltage: float = 2.5         # V (typical)
    formation_temp: float = 450            # K (activation temperature)

class HfBondFormer:
    """
    Forms Hf-C bonds when conditions are right.
    """
    
    def __init__(self):
        self.props = InterfaceProperties()
        
    def calculate_bond_probability(self, C_vac: float, O_vac: float, temperature_K: float) -> float:
        """
        Probability that Hf-C bonds form given:
        - Carbon vacancies in graphene
        - Oxygen vacancies in HfO₂
        - Temperature (helps overcome barriers)
        """
        # Need minimum vacancies
        if C_vac < self.props.required_C_vacancies:
            return 0.0
        if O_vac < self.props.required_O_vacancies:
            return 0.0
            
        # Base probability from vacancies
        base_prob = min(C_vac / 0.05, 1.0) * min(O_vac / 0.10, 1.0)
        
        # Temperature helps (Arrhenius)
        T_activation = 400  # K
        if temperature_K > T_activation:
            thermal_factor = 1 - np.exp(-(temperature_K - T_activation) / 100)
        else:
            thermal_factor = 0
            
        prob = min(base_prob + thermal_factor, 1.0)
        return prob
    
    def apply_pulse_sequence(self, voltages: list, times_ms: list) -> dict:
        """
        Apply sequence of voltage pulses and track interface formation.
        """
        vc = VacancyCreator()
        total_C_vac = 0
        total_O_vac = 0
        temperature = 300  # K start
        history = []
        
        for i, (V, t) in enumerate(zip(voltages, times_ms)):
            # Create vacancies with each pulse
            C_vac = vc.create_c_vacancies(V, t)
            O_vac = vc.create_o_vacancies(V, t)
            
            total_C_vac += C_vac
            total_O_vac += O_vac
            
            # Joule heating
            power = V**2 / 100e3  # R=100kΩ
            energy = power * (t * 1e-3)
            delta_T = energy / 1e-12  # rough estimate
            temperature += delta_T
            
            # Probability of bond formation
            prob = self.calculate_bond_probability(total_C_vac, total_O_vac, temperature)
            
            step = {
                'step': i+1,
                'voltage': V,
                'time_ms': t,
                'C_vac': total_C_vac,
                'O_vac': total_O_vac,
                'temp_C': temperature - 273,
                'bond_prob': prob,
                'bonds_formed': prob > 0.5
            }
            history.append(step)
            
            print(f"Step {i+1}: C vac={total_C_vac*100:.2f}%, O vac={total_O_vac*100:.2f}%, "
                  f"T={temperature-273:.0f}°C, Prob={prob*100:.1f}%")
            
        return {
            'history': history,
            'final_C_vac': total_C_vac,
            'final_O_vac': total_O_vac,
            'final_temp': temperature,
            'bonds_formed': history[-1]['bonds_formed'] if history else False
        }

# ==================== TEST ====================
if __name__ == "__main__":
    former = HfBondFormer()
    
    # Standard protocol from papers
    voltages = [3.5, 3.0, 2.5, 2.0, 1.5]
    times = [100, 50, 20, 10, 5]
    
    print("Creating Hf-C interface...")
    result = former.apply_pulse_sequence(voltages, times)
    
    print("\n" + "="*50)
    if result['bonds_formed']:
        print("✅ Hf-C INTERFACE FORMED")
        print(f"   Bond energy: {former.props.hfc_energy:.3f} eV")
        print(f"   Distance: {former.props.hfc_distance*1e10:.2f} Å")
        print(f"   2× stronger than van der Waals")
    else:
        print("❌ Interface not formed - try higher voltages")