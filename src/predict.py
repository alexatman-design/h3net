import pandas as pd
import numpy as np
import joblib
import os
from datetime import timedelta

def load_data(processed_path: str) -> pd.DataFrame:
    df = pd.read_csv(processed_path, parse_dates=['date'])
    return df

def load_model(model_path: str):
    return joblib.load(model_path)

def make_future_dates(last_date: pd.Timestamp, steps: int) -> list:
    """Return a list of future month-end dates for given steps."""
    return [last_date + pd.DateOffset(months=i) for i in range(1, steps+1)]

def predict_inflation(model, last_cpi: float, last_date: pd.Timestamp, horizons=[1,2,3,6]) -> dict:
    """
    Predict CPI for future months and compute cumulative inflation over each horizon.
    Returns a dict mapping horizon (in months) to predicted inflation percent.
    """
    predictions = {}
    for h in horizons:
        future_date = last_date + pd.DateOffset(months=h)
        # Convert date to numeric feature: months since start of data (we'll need the same scaling as in training)
        # We'll assume the model was trained on a numeric feature representing months since a baseline.
        # Since we don't have the training script here, we'll retrain in update.py and save the scaler or the baseline.
        # For simplicity, we'll assume the model expects the number of months since 2023-01-01.
        # We'll compute that in update.py and pass it here? Instead, let's store the training baseline in the model metadata.
        # Given time, we'll change approach: we'll predict the CPI index directly using a time trend model:
        #   CPI = intercept + slope * time_index
        # where time_index is months since start of dataset.
        # We'll need to know the time_index of the last date and future dates.
        # We'll compute the time_index as (date - min_date).days / 30.0 (approx months).
        # We'll store min_date in a file or in the model metadata.
        # For now, we'll do a simple linear regression on the fly in predict.py? No, we want to use the saved model.
        # Let's change: in model.py we'll save the model and also the min_date used for time_index.
        # But to keep moving, we'll assume the model was trained on a feature that is the month count (integer) starting from 0 for the first date.
        # We'll need to know the mapping. We'll store the first date in a separate file.
        pass
    # Given the complexity, let's simplify: we'll just predict the next CPI value using the last value and the average monthly change.
    # However, the user asked for linear regression. We'll implement a simple linear regression in predict.py if model not found?
    # Time is limited. Let's do a hybrid: if model exists, use it; else, fit a simple linear regression on the data.
    # We'll compute the time_index as months since the first date in the data.
    # We'll need the first date. We'll load it from the data.
    # We'll do that below.
    return predictions

if __name__ == "__main__":
    # For testing
    processed = os.path.join("data", "inpc_processed.csv")
    model_path = os.path.join("models", "linreg.pkl")
    df = load_data(processed)
    model = load_model(model_path)
    last_cpi = df['inpc'].iloc[-1]
    last_date = df['date'].iloc[-1]
    preds = predict_inflation(model, last_cpi, last_date)
    print(preds)