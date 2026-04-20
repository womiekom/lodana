from evaluation import evaluate_sarimax_pipeline
from nasa_power import NasaPowerService
from preprocess import DataPreprocessor

def run_evaluation():
    nasa = NasaPowerService()
    raw_df = nasa.get_as_dataframe("20230101", "20231231")

    prep = DataPreprocessor(raw_df)
    df = prep.resample_daily().handle_missing_values().add_features().get_processed_data()

    metrics = evaluate_sarimax_pipeline(df)

    print("\n=== EVALUATION RESULT ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    run_evaluation()