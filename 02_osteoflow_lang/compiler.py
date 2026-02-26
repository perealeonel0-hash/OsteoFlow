#!/usr/bin/env python3
# compiler.py - Compilador de Osteoflow Lang a voltajes

import numpy as np

class OsteoflowCompiler:
    def __init__(self):
        self.neurons = {}
        self.synapses = []
        self.sensors = []
        self.pulses = []
        self.labels = {}
        
    def compile(self, filename: str):
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if line.strip().startswith('LABEL'):
                label = line.strip().split()[1]
                self.labels[label] = i
                
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(';') or line == '':
                i += 1
                continue
                
            parts = line.split()
            cmd = parts[0]
            
            if cmd == 'NEURON':
                self._cmd_neuron(parts)
            elif cmd == 'SYNAPSE':
                self._cmd_synapse(parts)
            elif cmd == 'SENSOR':
                self._cmd_sensor(parts)
            elif cmd == 'RELEASE':
                self._cmd_release(parts)
            elif cmd == 'WAIT':
                self._cmd_wait(parts)
            i += 1
            
        return self.pulses
    
    def _cmd_neuron(self, parts):
        neuron_id = int(parts[1])
        self.neurons[neuron_id] = {'threshold': 0.5, 'leak': 0.01}
        
    def _cmd_synapse(self, parts):
        source = int(parts[1])
        target = int(parts[2])
        weight = float(parts[3])
        target_R = 10e3 + (1e6 - 10e3) * (1 - weight)
        self._program_resistance(target_R)
        
    def _program_resistance(self, target_R):
        R = 100e3
        while abs(R - target_R) > 0.01 * target_R:
            if R > target_R:
                self.pulses.append({'type': 'SET', 'voltage': 1.5, 'duration': 10e-9})
                R *= 0.97
            else:
                self.pulses.append({'type': 'RESET', 'voltage': -1.5, 'duration': 10e-9})
                R *= 1.03
                
    def _cmd_sensor(self, parts):
        pass
        
    def _cmd_release(self, parts):
        actuator = int(parts[1])
        dose = float(parts[2])
        duration = dose * 100e-6
        self.pulses.append({'type': 'ACTUATE', 'actuator': actuator, 'voltage': 3.3, 'duration': duration})
        
    def _cmd_wait(self, parts):
        time_us = int(parts[1])
        self.pulses.append({'type': 'WAIT', 'duration': time_us * 1e-6})

if __name__ == "__main__":
    print("Compilador de Osteoflow Lang v1.0")