import sys
import os
import pandas as pd

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_cleaner import DatasetCleaner
from services.nasa_power import NasaPowerService
from services.production import ProductionModel

def test_energy_production_pipeline():
    # 1. Setup
    cleaner = DatasetCleaner()
    nasa = NasaPowerService()
    model = ProductionModel(efficiency=0.18, performance_ratio=0.75)
    
    # 2. Get Master Dataset
    print("Fetching and cleaning data...")
    nasa_df = nasa.get_as_dataframe("20230101", "20230105")
    master_df = cleaner.create_master_dataset(nasa_df)
    
    # 3. Apply Production Model
    # Assume each customer has an average of 2 m2 of solar panel potential
    print("Applying energy production model (assuming 2m2 per customer)...")
    final_df = model.apply_to_dataframe(master_df, area_per_customer=2.0)
    
    # 4. Results
    print("\n--- Production Results (Sample) ---")
    cols_to_show = ['date', 'district', 'solar_radiation', 'customers', 'energy_kwh_per_m2', 'estimated_total_kwh']
    print(final_df[cols_to_show].head(10))
    
    # Validation
    # Energy per m2 should be radiation * 0.18 * 0.75 = radiation * 0.135
    sample_rad = final_df['solar_radiation'].iloc[0]
    expected_per_m2 = sample_rad * 0.135
    actual_per_m2 = final_df['energy_kwh_per_m2'].iloc[0]
    
    assert abs(actual_per_m2 - expected_per_m2) < 1e-6
    print("\nValidation Successful: Energy conversion matches physics formula.")

if __name__ == "__main__":
    test_energy_production_pipeline()
