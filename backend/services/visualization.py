import pandas as pd
import matplotlib.pyplot as plt
import os

from nasa_power import NasaPowerService
from preprocess import DataPreprocessor


def visualize_preprocessing(df_raw: pd.DataFrame):
    df_raw = df_raw.copy()

    # pastikan datetime index
    if 'date' in df_raw.columns:
        df_raw['date'] = pd.to_datetime(df_raw['date'])
        df_raw.set_index('date', inplace=True)

    df_raw.sort_index(inplace=True)

    prep = DataPreprocessor(df_raw)

    df_clean = (
        prep
        .resample_daily()
        .handle_missing_values()
        .detect_outliers()
        .add_features()
        .get_processed_data()
    )

    # align index
    common_index = df_raw.index.intersection(df_clean.index)
    df_raw_aligned = df_raw.loc[common_index]
    df_clean_aligned = df_clean.loc[common_index]

    plt.figure(figsize=(12,6))
    plt.plot(df_raw_aligned.index, df_raw_aligned['solar_radiation'], label='Before', alpha=0.6)
    plt.plot(df_clean_aligned.index, df_clean_aligned['solar_radiation'], label='After', linewidth=2)

    plt.legend()
    plt.title("Before vs After Preprocessing (Aligned)")
    plt.xlabel("Date")
    plt.ylabel("Solar Radiation")
    plt.grid()

    # save ke folder plots
    save_path = os.path.join("plots", "preprocessing_comparison.png")
    plt.savefig(save_path)
    plt.close()

    print(f"Saved to: {save_path}")
    print("RAW:", df_raw.index.min(), "→", df_raw.index.max())
    print("CLEAN:", df_clean.index.min(), "→", df_clean.index.max())


if __name__ == "__main__":
    nasa = NasaPowerService()

    print("Fetching NASA data...")
    df_nasa = nasa.get_as_dataframe("20230101", "20231231")

    visualize_preprocessing(df_nasa)