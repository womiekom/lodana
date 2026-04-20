import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nasa_power import NasaPowerService

def test_fetch_solar_data():
    service = NasaPowerService()
    start_date = "20230101"
    end_date = "20230105"
    
    print(f"Fetching data from {start_date} to {end_date}...")
    data = service.fetch_solar_data(start_date, end_date)
    
    if not data:
        print("Failed to fetch data.")
        return

    print(f"Successfully fetched {len(data)} records.")
    for record in data:
        print(f"Date: {record['date']}, Solar Radiation: {record['solar_radiation']}")
    
    # Validation
    assert len(data) == 5
    assert "date" in data[0]
    assert "solar_radiation" in data[0]
    print("Test passed!")

if __name__ == "__main__":
    test_fetch_solar_data()
