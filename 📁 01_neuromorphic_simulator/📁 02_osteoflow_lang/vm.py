#!/usr/bin/env python3
# vm.py - Máquina virtual para ejecutar código Osteoflow Lang

import sys

class OsteoflowVM:
    def __init__(self):
        self.program = []
        self.pc = 0
        self.current_time = 0
        
    def load_program(self, pulses):
        self.program = pulses
        
    def run(self, max_steps=1000):
        step = 0
        while self.pc < len(self.program) and step < max_steps:
            pulse = self.program[self.pc]
            
            if pulse['type'] == 'SET':
                print(f"[{self.current_time*1e9:.0f}ns] SET pulse")
            elif pulse['type'] == 'RESET':
                print(f"[{self.current_time*1e9:.0f}ns] RESET pulse")
            elif pulse['type'] == 'ACTUATE':
                print(f"[{self.current_time*1e9:.0f}ns] ACTUADOR {pulse['actuator']} dosis {pulse['duration']*1e6:.1f}µs")
            elif pulse['type'] == 'WAIT':
                self.current_time += pulse['duration']
                
            self.pc += 1
            step += 1
            
        print(f"\n✅ Programa ejecutado en {self.current_time*1e3:.3f}ms")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from compiler import OsteoflowCompiler
        compiler = OsteoflowCompiler()
        pulses = compiler.compile(sys.argv[1])
        vm = OsteoflowVM()
        vm.load_program(pulses)
        vm.run()
    else:
        print("Uso: python vm.py archivo.ofl")