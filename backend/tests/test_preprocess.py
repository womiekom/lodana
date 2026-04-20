import pandas as pd
import numpy as np
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.preprocess import DataPreprocessor

def test_preprocessing():
    # 1. Create dummy data with gaps and outliers
    dates = pd.date_range(start="2023-01-01", periods=10, freq='D')
    solar_values = [5.0, 5.2, np.nan, 5.1, 15.0, 5.3, 5.2, 5.4, np.nan, 5.5] # 15.0 is an outlier
    
    df = pd.DataFrame({
        'date': dates,
        'solar_radiation': solar_values
    })
    
    # Intentionally remove a row to test resampling
    df = df.drop(df.index[6]) # Remove 2023-01-07
    
    print("Original Data with missing values and outlier:")
    print(df)
    
    # 2. Run preprocessing
    preprocessor = DataPreprocessor(df)
    processed_df = (preprocessor
                    .resample_daily()
                    .handle_missing_values()
                    .detect_outliers(threshold=2.0)
                    .add_features(lags=[1], windows=[3])
                    .get_processed_data())
    
    print("\nProcessed Data:")
    print(processed_df)
    
    # 3. Assertions
    assert not processed_df.isnull().values.any(), "Should not have any NaNs"
    assert 'lag_1' in processed_df.columns, "Should have lag_1 feature"
    assert 'rolling_mean_3' in processed_df.columns, "Should have rolling_mean_3 feature"
    assert len(processed_df) < 10, "Should have fewer rows due to dropna in add_features"
    
    # Check outlier clipping
    assert processed_df.loc[processed_df.index == "2023-01-05", "is_outlier"].values[0] == True
    radiation_value = processed_df.loc[processed_df.index == "2023-01-05", "solar_radiation"].values[0]
    assert radiation_value < 15.0, f"Outlier should be clipped, but is {radiation_value}"

    print("\nPre-processing test passed!")

if __name__ == "__main__":
    test_preprocessing()
