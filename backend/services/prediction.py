import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

class SolarForecaster:
    def __init__(self, order=(1, 1, 1)):
        self.order = order
        self.model_res = None
        self.last_training_data = None

    def _generate_fourier_exog(self, index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Generate Fourier terms for the given index.
        """
        day_of_year = index.dayofyear
        exog = pd.DataFrame(index=index)
        exog['sin_365'] = np.sin(2 * np.pi * day_of_year / 365.25)
        exog['cos_365'] = np.cos(2 * np.pi * day_of_year / 365.25)
        return exog

    def train(self, df: pd.DataFrame):
        """
        Train SARIMAX model using solar_radiation as target and Fourier terms as exog.
        """
        self.last_training_data = df.copy()
        y = df['solar_radiation']
        exog = df[['sin_365', 'cos_365']]
        
        model = sm.tsa.statespace.SARIMAX(
            y, 
            exog=exog,
            order=self.order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        self.model_res = model.fit(disp=False)
        return self.model_res

    def forecast(self, steps: int = 7) -> pd.DataFrame:
        """
        Forecast future solar radiation.
        """
        if self.model_res is None or self.last_training_data is None:
            raise ValueError("Model must be trained before forecasting.")

        # Generate future dates
        last_date = self.last_training_data.index[-1]
        future_index = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
        
        # Generate future exogenous features (Fourier terms)
        future_exog = self._generate_fourier_exog(future_index)
        
        # Perform forecast
        forecast_res = self.model_res.get_forecast(steps=steps, exog=future_exog)
        forecast_df = forecast_res.summary_frame()
        forecast_df.index = future_index
        
        return forecast_df

    def get_forecast_json(self, steps: int = 7) -> List[Dict[str, Any]]:
        """
        Get forecast in JSON-ready format.
        """
        df = self.forecast(steps)
        df = df.reset_index().rename(columns={'index': 'date', 'mean': 'prediction'})
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        return df[['date', 'prediction', 'mean_ci_lower', 'mean_ci_upper']].to_dict(orient='records')

if __name__ == "__main__":
    # Test with dummy data
    from services.nasa_power import NasaPowerService
    from services.preprocess import DataPreprocessor
    
    print("Testing Forecaster...")
    nasa = NasaPowerService()
    raw_df = nasa.get_as_dataframe("20230101", "20231231")
    prep = DataPreprocessor(raw_df)
    train_df = prep.resample_daily().handle_missing_values().add_features().get_processed_data()
    
    forecaster = SolarForecaster()
    forecaster.train(train_df)
    forecast = forecaster.get_forecast_json(steps=5)
    
    print("\nForecast for next 5 days:")
    for f in forecast:
        print(f"{f['date']}: {f['prediction']:.4f}")
