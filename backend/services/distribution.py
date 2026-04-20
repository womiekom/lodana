import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class DistributionModel:
    def __init__(
        self, 
        alpha: float = 0.7, 
        beta: float = 0.3, 
        consumption_proxy: float = 2.2
    ):
        """
        Initialize the distribution model with configurable heuristics.
        :param alpha: Weight for infrastructure (Customers)
        :param beta: Weight for human potential (Population)
        :param consumption_proxy: Estimated kWh needed per customer per day
        """
        self.alpha = alpha
        self.beta = beta
        self.consumption_proxy = consumption_proxy

    def distribute(self, total_energy_kwh: float, master_snapshot: pd.DataFrame) -> pd.DataFrame:
        """
        Allocate total energy across districts based on weights.
        :param total_energy_kwh: The total kWh produced/forecasted for Sumba.
        :param master_snapshot: DataFrame containing 'district', 'customers', and 'population'.
        """
        df = master_snapshot.copy()

        # 1. Calculate Weights
        sum_customers = df['customers'].sum()
        sum_population = df['population'].sum()

        df['customer_weight'] = df['customers'] / sum_customers
        df['population_weight'] = df['population'] / sum_population
        
        # Lodana Index (Weighted Score)
        df['lodana_index'] = (self.alpha * df['customer_weight']) + (self.beta * df['population_weight'])

        # 2. Allocate Supply
        df['allocated_supply_kwh'] = total_energy_kwh * df['lodana_index']

        # 3. Estimate Demand
        df['estimated_demand_kwh'] = df['customers'] * self.consumption_proxy

        # 4. Decision Metrics
        df['utilization_ratio'] = (df['allocated_supply_kwh'] / df['estimated_demand_kwh']) * 100
        df['gap_kwh'] = df['allocated_supply_kwh'] - df['estimated_demand_kwh']
        df['status'] = df['gap_kwh'].apply(lambda x: 'Surplus' if x >= 0 else 'Deficit')

        return df

    def to_decision_json(self, distribution_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Format the dataframe into a clean, JSON-ready list for policy decision making.
        """
        # Select and rename
        output = distribution_df[[
            'district', 
            'allocated_supply_kwh', 
            'estimated_demand_kwh', 
            'utilization_ratio', 
            'status'
        ]].copy()
        
        # Replace non-finite values (NaN, inf) with 0 to ensure JSON compliance
        output = output.replace([np.inf, -np.inf], 0).fillna(0)
        
        # Rounded for readability
        output = output.round(2)
        
        return output.to_dict(orient='records')
