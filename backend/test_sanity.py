import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    print("Testing imports...")
    from services.nasa_power import NasaPowerService
    from services.preprocess import DataPreprocessor
    from services.prediction import SolarForecaster
    from services.production import ProductionModel
    from services.distribution import DistributionModel
    from services.data_cleaner import DatasetCleaner
    import statsmodels.api as sm
    import pandas as pd
    import openpyxl
    print("All imports successful!")
    
    print("\nTesting Data Cleaner with absolute path...")
    cleaner = DatasetCleaner()
    cust_ts = cleaner.load_customer_timeseries()
    print(f"Loaded customer data, shape: {cust_ts.shape}")
    
    print("\nTesting NASA Service (short range)...")
    nasa = NasaPowerService()
    df = nasa.get_as_dataframe("20230101", "20230102")
    print(f"NASA data fetched, shape: {df.shape}")

    print("\nAll sanity checks passed!")
except Exception as e:
    import traceback
    print(f"\nSanity check FAILED:")
    print(traceback.format_exc())
