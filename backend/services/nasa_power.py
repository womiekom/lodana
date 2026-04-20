import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

class NasaPowerService:
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

    def __init__(self, latitude: float = -9.65, longitude: float = 120.26):
        self.latitude = latitude
        self.longitude = longitude

    def fetch_solar_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetch solar radiation data (ALLSKY_SFC_SW_DWN) from NASA POWER API.
        
        Args:
            start_date: YYYYMMDD format
            end_date: YYYYMMDD format
            
        Returns:
            List of dicts with 'date' and 'solar_radiation'
        """
        params = {
            "parameters": "ALLSKY_SFC_SW_DWN",
            "community": "RE",
            "longitude": self.longitude,
            "latitude": self.latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the solar radiation data
            # Structure: data['properties']['parameter']['ALLSKY_SFC_SW_DWN'] -> { "YYYYMMDD": value }
            solar_data = data.get('properties', {}).get('parameter', {}).get('ALLSKY_SFC_SW_DWN', {})
            
            clean_data = []
            for date_str, value in solar_data.items():
                # Convert YYYYMMDD to YYYY-MM-DD
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                clean_data.append({
                    "date": formatted_date,
                    "solar_radiation": value
                })
            
            # Sort by date
            clean_data.sort(key=lambda x: x['date'])
            
            return clean_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from NASA POWER API: {e}")
            return []

    def get_as_dataframe(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch data and return as pandas DataFrame for easier processing.
        """
        data = self.fetch_solar_data(start_date, end_date)
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df

if __name__ == "__main__":
    # Quick test
    service = NasaPowerService()
    test_data = service.fetch_solar_data("20230101", "20230110")
    print(test_data)
