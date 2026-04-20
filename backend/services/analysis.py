import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from services.nasa_power import NasaPowerService
from services.preprocess import DataPreprocessor

class SolarAnalysis:
    def __init__(self):
        self.nasa_service = NasaPowerService()
        self.plot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots")
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)

    def get_analysis_data(self, start="20210101", end="20231231"):
        df = self.nasa_service.get_as_dataframe(start, end)
        preprocessor = DataPreprocessor(df)
        processed_df = (preprocessor
                        .resample_daily()
                        .handle_missing_values()
                        .get_processed_data())
        return processed_df

    def check_stationarity(self, series):
        result = adfuller(series.dropna())
        return {
            "adf_statistic": result[0],
            "p_value": result[1],
            "is_stationary": result[1] < 0.05,
            "critical_values": result[4]
        }

    def save_eda_plots(self, series, period=365):
        """
        Generate and save plots for Trend, Seasonality (Annual), ACF, and PACF.
        """
        # 1. Decomposition
        # Using period=365 for annual cycle in daily data
        try:
            decomposition = seasonal_decompose(series.dropna(), model='additive', period=period)
            fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
            decomposition.observed.plot(ax=axes[0], title='Observed')
            decomposition.trend.plot(ax=axes[1], title='Trend')
            decomposition.seasonal.plot(ax=axes[2], title='Seasonal (Annual)')
            decomposition.resid.plot(ax=axes[3], title='Residual')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plot_dir, "decomposition_annual.png"))
            plt.close()
        except Exception as e:
            print(f"Decomposition failed: {e}")

        # 2. ACF and PACF
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        plot_acf(series.dropna(), lags=400, ax=ax1) # Increased lags to see seasonality
        plot_pacf(series.dropna(), lags=40, ax=ax2)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, "acf_pacf_long.png"))
        plt.close()
        
        return self.plot_dir

if __name__ == "__main__":
    analysis = SolarAnalysis()
    print("Fetching 3 years of data...")
    df = analysis.get_analysis_data()
    series = df['solar_radiation']
    
    print("--- Stationarity Test ---")
    stat_results = analysis.check_stationarity(series)
    print(f"ADF Statistic: {stat_results['adf_statistic']}")
    print(f"p-value: {stat_results['p_value']}")
    print(f"Stationary: {stat_results['is_stationary']}")

    print("\nGenerating annual decomposition and long-lag ACF plots...")
    plot_path = analysis.save_eda_plots(series)
    print(f"Plots saved in: {plot_path}")

    # Check for seasonal ACF spikes at ~365
    lag_acf = acf(series.dropna(), nlags=400)
    seasonal_lag_idx = np.argmax(lag_acf[350:380]) + 350
    print(f"\nPotential seasonal peak in ACF found at lag: {seasonal_lag_idx} with value {lag_acf[seasonal_lag_idx]}")
