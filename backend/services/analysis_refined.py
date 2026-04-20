import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nasa_power import NasaPowerService
from services.preprocess import DataPreprocessor

class SolarAnalysisRefined:
    def __init__(self):
        self.nasa_service = NasaPowerService()
        self.plot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots")
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)

    def get_data(self, start="20210101", end="20231231"):
        df = self.nasa_service.get_as_dataframe(start, end)
        preprocessor = DataPreprocessor(df)
        return preprocessor.resample_daily().handle_missing_values().get_processed_data()

    def perform_domain_analysis(self, df):
        """
        Analyze data based on Sumba's dry/wet season characteristics.
        """
        df = df.copy()
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['month_name'] = df.index.strftime('%b')

        # 1. Seasonal Boxplot (Monthly distribution)
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='month_name', y='solar_radiation', data=df, 
                    order=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        plt.title("Sumba Solar Radiation Distribution by Month (2021-2023)")
        plt.ylabel("Solar Radiation (kW-hr/m²/day)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(self.plot_dir, "monthly_distribution_boxplot.png"))
        plt.close()

        # 2. Monthly Averages (Trend across years)
        monthly_avg = df.groupby(['year', 'month'])['solar_radiation'].mean().unstack(level=0)
        monthly_avg.plot(figsize=(12, 6), marker='o')
        plt.title("Comparison of Monthly Average Solar Radiation (Year-over-Year)")
        plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        plt.ylabel("Avg Solar Radiation")
        plt.legend(title="Year")
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.plot_dir, "yoy_monthly_comparison.png"))
        plt.close()

        # 3. Dry vs Wet Season Statistics
        # Dry: May (5) to Oct (10), Wet: Nov (11) to Apr (4)
        df['season'] = df['month'].apply(lambda x: 'Dry' if 5 <= x <= 10 else 'Wet')
        season_stats = df.groupby('season')['solar_radiation'].agg(['mean', 'std', 'min', 'max']).to_dict()
        
        return season_stats

if __name__ == "__main__":
    analysis = SolarAnalysisRefined()
    print("Fetching data for refined domain analysis...")
    df = analysis.get_data()
    
    print("Performing seasonal analysis...")
    stats = analysis.perform_domain_analysis(df)
    
    print("\n--- Domain Analysis Insights (Sumba) ---")
    print(f"Wet Season (Nov-Apr) Mean: {stats['mean']['Wet']:.2f} (Std: {stats['std']['Wet']:.2f})")
    print(f"Dry Season (May-Oct) Mean: {stats['mean']['Dry']:.2f} (Std: {stats['std']['Dry']:.2f})")
    
    diff = stats['mean']['Dry'] - stats['mean']['Wet']
    print(f"Mean Difference: {diff:.2f} kW-hr/m²/day ({ (diff/stats['mean']['Wet'])*100:.1f}% increase in dry season)")
    
    print(f"\nRefined plots saved in: {analysis.plot_dir}")
