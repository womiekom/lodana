import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_model(y_true, y_pred):
    """
    Evaluate SARIMAX model performance.
    """

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    # Hindari division by zero
    y_true_safe = np.where(y_true == 0, 1e-8, y_true)
    mape = np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "MAPE": float(mape),
    }


def evaluate_sarimax_pipeline(train_df):
    """
    Full pipeline:
    split → train → predict → evaluate
    """

    from prediction import SolarForecaster

    # 1. Split data (80:20)
    split_idx = int(len(train_df) * 0.8)
    train = train_df.iloc[:split_idx]
    test = train_df.iloc[split_idx:]

    # 2. Train model
    forecaster = SolarForecaster()
    forecaster.train(train)

    # 3. Predict test set
    exog_test = test[['sin_365', 'cos_365']]

    pred = forecaster.model_res.get_prediction(
        start=test.index[0],
        end=test.index[-1],
        exog=exog_test
    )

    y_pred = pred.predicted_mean
    y_true = test['solar_radiation']

    # 4. Evaluate
    metrics = evaluate_model(y_true, y_pred)

    return metrics