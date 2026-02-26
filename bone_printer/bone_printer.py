#!/usr/bin/env python3
"""
BONE PRINTER
============
Purpose: Generates 3D bone implants with Gyroid structure.
         Also creates salt mold for casting.

The Gyroid structure:
- sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = t
- t controls wall thickness
- Gradient: thick walls outside (cortical bone)
           thin walls inside (trabecular bone)
"""

import numpy as np
import matplotlib.pyplot as plt

class BonePrinter:
    """
    Generates Gyroid-based bone implants.
    """
    
    def __init__(self):
        self.config = {
            'cell_size': 2.5e-3,           # 2.5mm unit cell
            'wall_thickness_min': 0.2e-3,   # 0.2mm (trabecular)
            'wall_thickness_max': 0.4e-3,   # 0.4mm (cortical)
            'porosity_target': 0.65          # 65% porous (like bone)
        }
        
    def gyroid_function(self, x, y, z, t=0):
        """
        Mathematical definition of Gyroid surface.
        sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = t
        """
        return (np.sin(x) * np.cos(y) + 
                np.sin(y) * np.cos(z) + 
                np.sin(z) * np.cos(x) - t)
    
    def generate_gyroid(self, size_mm: float = 10, resolution: float = 0.1):
        """
        Generate Gyroid structure within a cube.
        size_mm: cube side length in mm
        resolution: voxel size in mm
        """
        # Convert to meters
        size_m = size_mm * 1e-3
        res = resolution * 1e-3
        
        # Create coordinate grid
        x = np.arange(-size_m/2, size_m/2, res)
        y = np.arange(-size_m/2, size_m/2, res)
        z = np.arange(-size_m/2, size_m/2, res)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Scale to cell size
        cell_size = self.config['cell_size']
        X_norm = 2 * np.pi * X / cell_size
        Y_norm = 2 * np.pi * Y / cell_size
        Z_norm = 2 * np.pi * Z / cell_size
        
        # Evaluate Gyroid function
        gyroid_values = self.gyroid_function(X_norm, Y_norm, Z_norm, 0)
        
        # Create binary mask (1 = material, 0 = pore)
        # Values < 0 are material, > 0 are pore
        gyroid_mask = gyroid_values < 0
        
        # Calculate porosity
        porosity = 1 - np.mean(gyroid_mask)
        print(f"Porosity: {porosity*100:.1f}% (target: {self.config['porosity_target']*100:.1f}%)")
        
        return gyroid_mask
    
    def generate_mold(self, implant_mask):
        """
        Generate salt mold (negative of implant).
        For investment casting.
        """
        return ~implant_mask
    
    def save_stl(self, filename: str, mask):
        """
        Save mask as STL file (simulated).
        In real version, would use marching cubes.
        """
        print(f"Saving {filename}... (simulated)")
        # In real code: use skimage.measure.marching_cubes

# ==================== TEST ====================
if __name__ == "__main__":
    printer = BonePrinter()
    
    print("Generating Gyroid structure...")
    implant = printer.generate_gyroid(size_mm=5)
    
    print(f"Implant shape: {implant.shape}")
    print(f"Material voxels: {np.sum(implant)}/{implant.size}")
    
    mold = printer.generate_mold(implant)
    print(f"Mold shape: {mold.shape}")
    
    printer.save_stl("implant.stl", implant)
    printer.save_stl("mold.stl", mold)