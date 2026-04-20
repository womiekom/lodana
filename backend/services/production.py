import pandas as pd
import numpy as np
from typing import Optional

class ProductionModel:
    def __init__(self, efficiency: float = 0.18, performance_ratio: float = 0.75):
        """
        Initialize with PV system parameters.
        :param efficiency: Solar panel efficiency (fraction, e.g., 0.18 for 18%)
        :param performance_ratio: System performance ratio (losses, e.g., 0.75)
        """
        self.efficiency = efficiency
        self.performance_ratio = performance_ratio

    def calculate_kwh(self, radiation: float, area: float = 1.0) -> float:
        """
        Convert radiation to kWh.
        Formula: E = A * r * H * PR
        E: Energy (kWh)
        A: Area (m2)
        r: Efficiency
        H: Radiation (kWh/m2/day)
        PR: Performance Ratio
        """
        return area * self.efficiency * radiation * self.performance_ratio

    def apply_to_dataframe(self, df: pd.DataFrame, area_per_customer: Optional[float] = None) -> pd.DataFrame:
        """
        Applies energy conversion to a master dataset.
        If area_per_customer is provided, it scales energy by district customer counts.
        Otherwise, it provides energy potential per m2.
        """
        df = df.copy()
        
        # Calculate Base Potential (per m2)
        df['energy_kwh_per_m2'] = df['solar_radiation'] * self.efficiency * self.performance_ratio
        
        # If we assume an average installation area per customer (e.g. 2m2 for a small residential setup)
        if area_per_customer:
            df['estimated_total_kwh'] = df['energy_kwh_per_m2'] * df['customers'] * area_per_customer
        else:
            # Default to 1m2 if no customer scaling is requested
            df['estimated_total_kwh'] = df['energy_kwh_per_m2']
            
        return df

if __name__ == "__main__":
    # Quick Test
    model = ProductionModel()
    # Test with 5.0 kWh/m2/day (typical Sumba value)
    kwh = model.calculate_kwh(5.0, area=1.0)
    print(f"Radiation: 5.0 kWh/m2/day -> Energy: {kwh:.4f} kWh per m2")
    
    # Test with 10m2 area
    kwh_10 = model.calculate_kwh(5.0, area=10.0)
    print(f"Radiation: 5.0 kWh/m2/day -> Energy: {kwh_10:.4f} kWh for 10m2")
