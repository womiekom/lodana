import pandas as pd
import numpy as np
from typing import List, Dict, Any

class DataPreprocessor:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a DataFrame containing 'date' and 'solar_radiation' columns.
        """
        self.df = df.copy()
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df.set_index('date', inplace=True)
        self.df.sort_index(inplace=True)

    def handle_missing_values(self, method: str = 'linear') -> 'DataPreprocessor':
        """
        Fill missing values using interpolation.
        """
        self.df['solar_radiation'] = self.df['solar_radiation'].interpolate(method=method)
        # Final fallback for any remaining NaNs at edges
        self.df['solar_radiation'] = self.df['solar_radiation'].ffill().bfill()
        return self

    def resample_daily(self) -> 'DataPreprocessor':
        """
        Ensure daily continuity in the time series.
        """
        self.df = self.df.resample('D').asfreq()
        # After resampling, we might have new NaNs, so handle them
        return self.handle_missing_values()

    def detect_outliers(self, threshold: float = 3.0) -> 'DataPreprocessor':
        """
        Identify outliers using Z-score and clip them to the threshold.
        Alternatively, could just flag them, but clipping helps model stability.
        """
        mean = self.df['solar_radiation'].mean()
        std = self.df['solar_radiation'].std()
        
        z_scores = (self.df['solar_radiation'] - mean) / std
        
        # Clip outliers to mean +/- threshold * std
        self.df['is_outlier'] = np.abs(z_scores) > threshold
        lower_limit = mean - threshold * std
        upper_limit = mean + threshold * std
        
        self.df['solar_radiation'] = self.df['solar_radiation'].clip(lower=lower_limit, upper=upper_limit)
        return self

    def add_features(self, lags: List[int] = [1, 7], windows: List[int] = [7, 30]) -> 'DataPreprocessor':
        """
        Add lag features, rolling means, and Fourier terms for seasonality.
        """
        # Lag features
        for lag in lags:
            self.df[f'lag_{lag}'] = self.df['solar_radiation'].shift(lag)
            
        # Rolling features
        for window in windows:
            self.df[f'rolling_mean_{window}'] = self.df['solar_radiation'].rolling(window=window).mean()
            
        # Time-based features
        day_of_year = self.df.index.dayofyear
        self.df['day_of_year'] = day_of_year
        self.df['month'] = self.df.index.month
        
        # Fourier Terms (Annual Seasonality)
        # Period = 365.25 for daily data
        self.df['sin_365'] = np.sin(2 * np.pi * day_of_year / 365.25)
        self.df['cos_365'] = np.cos(2 * np.pi * day_of_year / 365.25)
        
        # Drop rows with NaNs created by lagging/rolling
        self.df.dropna(inplace=True)
        return self

    def get_processed_data(self) -> pd.DataFrame:
        return self.df

    def to_json_ready(self) -> List[Dict[str, Any]]:
        """
        Convert processed DataFrame back to a list of dicts for API response.
        """
        output_df = self.df.reset_index()
        output_df['date'] = output_df['date'].dt.strftime('%Y-%m-%d')
        return output_df.to_dict(orient='records')
