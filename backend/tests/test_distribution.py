import sys
import os
import pandas as pd

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_cleaner import DatasetCleaner
from services.nasa_power import NasaPowerService
from services.production import ProductionModel
from services.distribution import DistributionModel

def test_full_decision_pipeline():
    # 1. Prediction (Using real NASA data as a proxy for 'forecasted' radiation)
    nasa = NasaPowerService()
    nasa_df = nasa.get_as_dataframe("20230601", "20230601") # Just one day
    total_radiation = nasa_df['solar_radiation'].iloc[0]
    
    # 2. Production (Convert to kWh potential)
    prod_model = ProductionModel(efficiency=0.18, performance_ratio=0.75)
    
    # Let's assume a fixed total installation area for the whole of Sumba Timur
    # Or calculate it based on customers. For this test, let's assume 50,000 m2 total area.
    total_energy_kwh = prod_model.calculate_kwh(total_radiation, area=50000)
    
    print(f"Total Predicted Radiation: {total_radiation:.2f} kWh/m2/day")
    print(f"Total Estimated Production (50k m2): {total_energy_kwh:.2f} kWh")
    
    # 3. Clean Dataset Snapshot (for weights)
    cleaner = DatasetCleaner()
    cust_ts = cleaner.load_customer_timeseries()
    snapshot = cust_ts[cust_ts['year'] == 2023].copy()
    
    # Add population data (usually static for the year)
    pop_df = cleaner.load_population()
    pop_val = pop_df[pop_df['year'] == 2023]['population'].iloc[0]
    snapshot['population'] = pop_val
    
    # 4. Distribution
    dist_model = DistributionModel(alpha=0.7, beta=0.3, consumption_proxy=2.2)
    distribution_result = dist_model.distribute(total_energy_kwh, snapshot)
    
    # 5. Output
    decision_json = dist_model.to_decision_json(distribution_result)
    
    print("\n--- Distribution Decision Table ---")
    df_result = pd.DataFrame(decision_json)
    print(df_result.head(10))
    
    # Final check
    allocated_sum = df_result['allocated_supply_kwh'].sum()
    assert abs(allocated_sum - total_energy_kwh) < 1.0
    print(f"\nTotal Allocated: {allocated_sum:.2f} kWh (Matches Production)")
    print("Decision Support Pipeline Validated.")

if __name__ == "__main__":
    test_full_decision_pipeline()
