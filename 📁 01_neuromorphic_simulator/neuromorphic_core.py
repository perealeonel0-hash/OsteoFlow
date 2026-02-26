#!/usr/bin/env python3
# neuromorphic_core.py - Chip neuromórfico con memristors HfO₂

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import time

@dataclass
class MaterialProperties:
    grafeno_thermal_conductivity: float = 5000
    hfo2_resistance_range: tuple = (10e3, 1e6)
    hfo2_target_resistance: float = 100e3
    hfo2_variability: float = 0.04
    num_layers: int = 8
    neurons_per_layer: int = 1250

class HfO2Memristor:
    def __init__(self, target_resistance: float = None):
        self.props = MaterialProperties()
        r_min, r_max = self.props.hfo2_resistance_range
        target = target_resistance or self.props.hfo2_target_resistance
        
        log_target = np.log10(target)
        log_std = self.props.hfo2_variability / 2
        log_variability = np.random.normal(0, log_std)
        log_r = log_target + log_variability
        self.resistance = 10 ** log_r
        self.resistance = np.clip(self.resistance, r_min * 0.9, r_max * 1.1)
        self.filament = 1.0 / self.resistance
        self.cycles = 0
        self.degraded = False
        self.history = [self.resistance]
        
    def pulse(self, voltage: float):
        if self.degraded:
            return
        self.cycles += 1
        if voltage > 1.0:
            self.resistance *= 0.97
        elif voltage < -1.0:
            self.resistance *= 1.03
        r_min, r_max = self.props.hfo2_resistance_range
        self.resistance = np.clip(self.resistance, r_min, r_max)
        if self.cycles > 10000 and np.random.random() < 0.0001:
            self.degraded = True
        self.filament = 1.0 / self.resistance
        self.history.append(self.resistance)
        
    def read(self, voltage: float = 0.2) -> float:
        if self.degraded:
            return 0
        return voltage / self.resistance

class BayesianNeuron:
    def __init__(self, neuron_id: int, layer: int):
        self.id = neuron_id
        self.layer = layer
        self.synapses = [HfO2Memristor() for _ in range(100)]
        self.threshold = np.random.uniform(0.3, 0.7)
        self.potential = 0.0
        self.spike_count = 0
        
    def process(self, inputs: np.ndarray) -> float:
        total_current = 0.0
        for i, val in enumerate(inputs[:len(self.synapses)]):
            total_current += val / self.synapses[i].resistance
        self.potential = 0.9 * self.potential + 0.1 * total_current
        x = (self.potential - self.threshold) * 5
        prob = 1.0 / (1.0 + np.exp(-x))
        if np.random.random() < prob:
            self.spike_count += 1
            self.potential = 0.0
            return prob
        return 0.0

class NeuromorphicChip:
    def __init__(self):
        self.props = MaterialProperties()
        self.layers = []
        total = 0
        for layer in range(self.props.num_layers):
            layer_neurons = [BayesianNeuron(total + i, layer) for i in range(self.props.neurons_per_layer)]
            self.layers.append(layer_neurons)
            total += len(layer_neurons)
        self.total_neurons = total
        self.temperature = 300
        self.power_draw = 0.0
        
    def thermal_simulation(self, ambient: float = 300):
        self.temperature = ambient + (self.power_draw * 0.1)
        return self.temperature - 273
        
    def process_random_spike(self) -> float:
        layer = np.random.randint(0, self.props.num_layers)
        neuron = np.random.randint(0, self.props.neurons_per_layer)
        inputs = np.random.random(100) * 0.5
        start = time.time()
        spike = self.layers[layer][neuron].process(inputs)
        latency = (time.time() - start) * 1e6
        if spike > 0:
            self.power_draw += 1e-12 * 10
        return latency
    
    def get_stats(self) -> dict:
        all_resistances = []
        degraded = 0
        for layer in self.layers:
            for neuron in layer:
                for syn in neuron.synapses:
                    all_resistances.append(syn.resistance)
                    if syn.degraded:
                        degraded += 1
        return {
            'neurons': self.total_neurons,
            'synapses': len(all_resistances),
            'mean_resistance': np.mean(all_resistances),
            'std_resistance': np.std(all_resistances),
            'variability_percent': (np.std(all_resistances) / np.mean(all_resistances)) * 100,
            'degraded_percent': (degraded / len(all_resistances)) * 100,
            'temperature_C': self.thermal_simulation(),
            'power_W': self.power_draw
        }

if __name__ == "__main__":
    chip = NeuromorphicChip()
    print(f"Chip creado con {chip.total_neurons} neuronas")
    stats = chip.get_stats()
    print(f"Consumo: {stats['power_W']*1000:.2f} mW")
    print(f"Temperatura: {stats['temperature_C']:.1f}°C")