import pandas as pd
import matplotlib.pyplot as plt
import os

from nasa_power import NasaPowerService
from preprocess import DataPreprocessor
from prediction import SolarForecaster


def plot_actual_vs_predicted():
    nasa = NasaPowerService()
    df_raw = nasa.get_as_dataframe("20230101", "20231231")

    prep = DataPreprocessor(df_raw)
    df = (
        prep
        .resample_daily()
        .handle_missing_values()
        .detect_outliers()
        .add_features()
        .get_processed_data()
    )

    # TRAIN MODEL
    forecaster = SolarForecaster(order=(1,1,1))
    model_res = forecaster.train(df)

    # IN-SAMPLE PREDICTION (INI YANG BENER)
    y = df['solar_radiation']
    exog = df[['sin_365', 'cos_365']]

    pred_res = model_res.get_prediction(start=0, end=len(df)-1, exog=exog)
    pred_df = pred_res.summary_frame()

    # PLOT
    plt.figure(figsize=(12,6))

    plt.plot(df.index, y, label='Actual', linewidth=2)
    plt.plot(df.index, pred_df['mean'], label='Predicted (SARIMAX)', linestyle='--')

    plt.title("Actual vs Predicted Solar Radiation (SARIMAX)")
    plt.xlabel("Date")
    plt.ylabel("Solar Radiation (kWh/m²/day)")
    plt.legend()
    plt.grid()

    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/sarimax_actual_vs_pred.png")
    plt.close()

    print("✅ Saved: plots/sarimax_actual_vs_pred.png")


if __name__ == "__main__":
    plot_actual_vs_predicted()