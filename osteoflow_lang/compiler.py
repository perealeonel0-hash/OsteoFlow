#!/usr/bin/env python3
"""
OSTEOFLOW LANG COMPILER
=======================
Purpose: Compiles .ofl code to voltage pulses.

A program like:
    SYNAPSE 0 100 0.8
    
Becomes:
    [PULSE] 1.5V 10ns (SET)
    [PULSE] 1.5V 10ns (SET)
    [PULSE] 1.5V 10ns (SET) ... until target resistance reached

The chip executes these pulses, NOT instructions.
"""

import numpy as np

class OsteoflowCompiler:
    """
    Compiler from high-level language to voltage pulses.
    """
    
    def __init__(self):
        self.neurons = {}      # Store neuron configurations
        self.synapses = []     # Store synapse connections
        self.pulses = []       # Output: sequence of voltage pulses
        self.labels = {}       # For jumps/gotos
        
    def compile(self, filename: str) -> list:
        """
        Read .ofl file, generate pulse sequence.
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        # First pass: find labels for jumps
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('LABEL'):
                label = line.split()[1]
                self.labels[label] = i
                
        # Second pass: compile each instruction
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip comments and empty lines
            if line.startswith(';') or line == '':
                i += 1
                continue
                
            parts = line.split()
            cmd = parts[0]
            
            if cmd == 'NEURON':
                self._cmd_neuron(parts)
            elif cmd == 'SYNAPSE':
                self._cmd_synapse(parts)
            elif cmd == 'RELEASE':
                self._cmd_release(parts)
            elif cmd == 'WAIT':
                self._cmd_wait(parts)
            # More commands can be added
                
            i += 1
            
        return self.pulses
    
    def _cmd_neuron(self, parts):
        """NEURON id threshold=V leak=uA layer=n"""
        neuron_id = int(parts[1])
        # Store neuron config (not used in compilation yet)
        self.neurons[neuron_id] = {'threshold': 0.5, 'leak': 0.01}
        
    def _cmd_synapse(self, parts):
        """SYNAPSE source target weight"""
        source = int(parts[1])
        target = int(parts[2])
        weight = float(parts[3])
        
        # Convert weight (0-1) to target resistance (10kΩ - 1MΩ)
        # weight 1.0 = strong connection = low resistance = 10kΩ
        # weight 0.0 = weak connection = high resistance = 1MΩ
        target_R = 10e3 + (1e6 - 10e3) * (1 - weight)
        
        # Generate SET/RESET pulses to reach that resistance
        self._program_resistance(target_R)
        
    def _program_resistance(self, target_R: float):
        """
        Generate sequence of SET/RESET pulses to achieve target_R.
        Starting from 100kΩ (default), each pulse changes R by 3%.
        """
        R = 100e3  # start at default
        while abs(R - target_R) > 0.01 * target_R:  # within 1%
            if R > target_R:
                # Need lower resistance → SET pulse
                self.pulses.append({
                    'type': 'SET',
                    'voltage': 1.5,
                    'duration': 10e-9  # 10ns
                })
                R *= 0.97  # -3%
            else:
                # Need higher resistance → RESET pulse
                self.pulses.append({
                    'type': 'RESET',
                    'voltage': -1.5,
                    'duration': 10e-9
                })
                R *= 1.03  # +3%
                
    def _cmd_release(self, parts):
        """RELEASE actuator_id dose"""
        actuator = int(parts[1])
        dose = float(parts[2])  # 0.0 to 1.0
        
        # Convert dose to pulse duration (0-100µs)
        duration = dose * 100e-6
        
        self.pulses.append({
            'type': 'ACTUATE',
            'actuator': actuator,
            'voltage': 3.3,
            'duration': duration
        })
        
    def _cmd_wait(self, parts):
        """WAIT time_us"""
        time_us = int(parts[1])
        self.pulses.append({
            'type': 'WAIT',
            'duration': time_us * 1e-6  # convert to seconds
        })

# ==================== TEST ====================
if __name__ == "__main__":
    print("Osteoflow Lang Compiler v1.0")
    print("Compiles .ofl code to voltage pulses")