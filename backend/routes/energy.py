from fastapi import APIRouter, HTTPException
from services.nasa_power import NasaPowerService
from services.preprocess import DataPreprocessor
from services.prediction import SolarForecaster
from services.production import ProductionModel
from services.distribution import DistributionModel
from services.data_cleaner import DatasetCleaner
import traceback
import pandas as pd
import sys
from typing import List, Dict, Any

router = APIRouter()
nasa_service = NasaPowerService()
forecaster = SolarForecaster(order=(1, 1, 1))
production_model = ProductionModel()
distribution_model = DistributionModel()
cleaner = DatasetCleaner()

@router.get("/debug-data")
async def debug_data():
    """Simple check for data loading."""
    try:
        cust_ts = cleaner.load_customer_timeseries()
        pop_df = cleaner.load_population()
        return {
            "customer_rows": len(cust_ts),
            "pop_rows": len(pop_df),
            "latest_year": int(cust_ts['year'].max())
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribute-energy")
async def distribute_energy(total_area: float = 50000):
    try:
        # 1. Prediction (Shortened for speed)
        df_nasa = nasa_service.get_as_dataframe("20231001", "20231231")
        if df_nasa.empty:
            raise ValueError("NASA data fetch failed")

        prep = DataPreprocessor(df_nasa)
        train_df = prep.resample_daily().handle_missing_values().detect_outliers().add_features().get_processed_data()
        
        forecaster.train(train_df)
        forecast_df = forecaster.forecast(steps=7)
        avg_predicted_radiation = float(forecast_df['mean'].mean())

        # 2. Production
        total_kwh = float(production_model.calculate_kwh(avg_predicted_radiation, area=total_area))

        # 3. Distribution Data
        cust_ts = cleaner.load_customer_timeseries()
        latest_year = int(cust_ts['year'].max())
        snapshot = cust_ts[cust_ts['year'] == latest_year].copy()
        
        pop_df = cleaner.load_population()
        pop_match = pop_df[pop_df['year'] == latest_year]
        pop_val = int(pop_match['population'].iloc[0]) if not pop_match.empty else int(pop_df['population'].iloc[-1])
            
        snapshot['population'] = pop_val

        # 4. Allocate
        dist_df = distribution_model.distribute(total_kwh, snapshot)
        decision_json = distribution_model.to_decision_json(dist_df)

        return {
            "total_production_kwh": round(total_kwh, 2),
            "avg_radiation": round(avg_predicted_radiation, 2),
            "distribution": decision_json
        }
    except Exception as e:
        print("!!! ERROR IN DISTRIBUTE-ENERGY !!!", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise e
