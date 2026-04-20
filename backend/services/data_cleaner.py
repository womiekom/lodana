import pandas as pd
import numpy as np
import os
from typing import Dict, List, Any

class DatasetCleaner:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Absolute path for stability
            self.data_dir = r"D:\Raiyan\Coding\Lodana\data"
        else:
            self.data_dir = data_dir

    def load_population(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, "p.xlsx")
        df = pd.read_excel(path)
        melted_df = df.melt(id_vars=['Kabupaten'], var_name='year', value_name='population')
        melted_df['year'] = melted_df['year'].astype(int)
        melted_df.rename(columns={'Kabupaten': 'regency'}, inplace=True)
        return melted_df

    def load_customer_timeseries(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, "plts.xlsx")
        df = pd.read_excel(path)
        mapping = {'Tahun': 'year', 'Kecamatan': 'district', 'Pelanggan': 'customers'}
        df.rename(columns=mapping, inplace=True)
        df['year'] = df['year'].astype(int)
        df['customers'] = df['customers'].astype(int)
        df['district'] = df['district'].str.strip()
        return df

    def create_master_dataset(self, nasa_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merges NASA daily data with yearly Population and Customer data.
        Broadcases NASA radiation across all districts.
        """
        # 1. Clean NASA data
        nasa_df = nasa_df.copy()
        nasa_df['date'] = pd.to_datetime(nasa_df['date'])
        nasa_df['year'] = nasa_df['date'].dt.year
        
        # 2. Load Local Data
        pop_df = self.load_population()
        cust_df = self.load_customer_timeseries()
        
        # 3. Get all unique districts from our records
        districts = cust_df['district'].unique()
        
        # 4. Create a Master Grid (Dates x Districts)
        dates = nasa_df['date'].unique()
        grid = pd.MultiIndex.from_product([dates, districts], names=['date', 'district'])
        master_df = pd.DataFrame(index=grid).reset_index()
        master_df['year'] = master_df['date'].dt.year
        
        # 5. Merge NASA Radiation (Broadcasted to all districts for each date)
        master_df = master_df.merge(
            nasa_df[['date', 'solar_radiation']], 
            on='date', 
            how='left'
        )
        
        # 6. Merge Population (Regency level - same for all districts in Sumba Timur)
        # We join on 'year'
        master_df = master_df.merge(
            pop_df[['year', 'population']], 
            on='year', 
            how='left'
        )
        
        # 7. Merge Customer Timeseries (District level)
        # We join on 'year' and 'district'
        master_df = master_df.merge(
            cust_df[['year', 'district', 'customers']], 
            on=['year', 'district'], 
            how='left'
        )
        
        # 8. Handling Gaps
        # For years where we don't have customer data, we might need to interpolate or ffill
        # but for now, we'll keep it as is and let the preprocessor handle it
        master_df['customers'] = master_df.groupby('district')['customers'].ffill().bfill()
        
        # 9. Cleanup
        master_df.sort_values(['date', 'district'], inplace=True)
        
        return master_df

if __name__ == "__main__":
    from services.nasa_power import NasaPowerService
    
    cleaner = DatasetCleaner()
    nasa = NasaPowerService()
    
    print("Fetching NASA data for alignment...")
    nasa_data = nasa.get_as_dataframe("20210101", "20231231")
    
    print("Creating Master Dataset...")
    master = cleaner.create_master_dataset(nasa_data)
    
    print("\n--- Master Dataset Summary ---")
    print(master.head())
    print(f"\nTotal Rows: {len(master)}")
    print(f"Columns: {master.columns.tolist()}")
    print(f"Missing Values:\n{master.isnull().sum()}")
    
    # Save a sample to CSV for inspection
    # master.to_csv("master_dataset_sample.csv", index=False)
