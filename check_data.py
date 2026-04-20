import pandas as pd
import os

data_dir = r"D:\Raiyan\Coding\Lodana\data"
files = ["p.xlsx", "pl(2023).xlsx", "plts.xlsx"]

for file in files:
    path = os.path.join(data_dir, file)
    print(f"\n--- Analyzing: {file} ---")
    try:
        # Read only first few rows for schema detection
        df = pd.read_excel(path)
        print(f"Columns: {list(df.columns)}")
        print("Sample Data:")
        print(df.head(3))
        print(f"Shape: {df.shape}")
    except Exception as e:
        print(f"Error reading {file}: {e}")
