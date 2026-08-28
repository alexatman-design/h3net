#!/usr/bin/env python3
"""
update.py: Orchestrates the full pipeline for INPC inflation prediction.
Steps:
1. Fetch raw INPC data (using fetch_inpc module).
2. Preprocess to obtain monthly time series.
3. Feature engineering: create numeric time index (months since start).
4. Train linear regression model (least squares) to predict INPC index.
5. Predict future INPC values for next 1, 2, 3, 6 months.
6. Compute cumulative inflation over each horizon.
7. Save predictions to results/predictions.csv.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import joblib

# Import our own fetch function
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from fetch_inpc import fetch_inpc

# Paths
RAW_PATH = os.path.join("data", "inpc_raw.csv")
PROCESSED_PATH = os.path.join("data", "inpc_processed.csv")
MODEL_PATH = os.path.join("models", "linreg.pkl")
PREDS_PATH = os.path.join("results", "predictions.csv")

# Ensure directories exist
for p in [os.path.dirname(RAW_PATH), os.path.dirname(PROCESSED_PATH),
          os.path.dirname(MODEL_PATH), os.path.dirname(PREDS_PATH)]:
    os.makedirs(p, exist_ok=True)

def fetch_inpc_data():
    """Download INPC data using our fetch_inpc function."""
    # Use the default URL from fetch_inpc (which is World Bank monthly CPI)
    fetch_inpc(RAW_PATH)
    # Load the CSV we just saved
    df = pd.read_csv(RAW_PATH)
    # Expected columns: date, inpc
    if 'date' not in df.columns or 'inpc' not in df.columns:
        # If the CSV has different columns, try to adapt
        # Assume first column is date, second is value
        cols = df.columns.tolist()
        if len(cols) >= 2:
            df = df.rename(columns={cols[0]: 'date', cols[1]: 'inpc'})
        else:
            print("CSV does not have enough columns")
            sys.exit(1)
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values('date')
    # Save again (ensure clean)
    df.to_csv(RAW_PATH, index=False)
    print(f"Saved raw data to {RAW_PATH} with {len(df)} rows")
    return df

def preprocess(df: pd.DataFrame):
    """Ensure monthly frequency, fill missing if any."""
    # We expect monthly data, but if there are gaps we resample.
    df = df.set_index('date')
    # Resample to month start, taking the last observation
    df_monthly = df.resample('MS').last().reset_index()
    # Forward fill any missing (should not happen with good data)
    df_monthly['inpc'] = df_monthly['inpc'].ffill()
    df_monthly.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved processed data to {PROCESSED_PATH} with {len(df_monthly)} rows")
    return df_monthly

def train_model(df: pd.DataFrame):
    """Create feature: months since first date, train LinearRegression."""
    df = df.copy()
    df['months'] = (df['date'] - df['date'].iloc[0]).dt.days / 30.0
    X = df[['months']].values
    y = df['inpc'].values
    model = LinearRegression()
    model.fit(X, y)
    # Save model
    joblib.dump(model, MODEL_PATH)
    # Also save the baseline date for later use
    baseline = df['date'].iloc[0]
    baseline_path = MODEL_PATH.replace('.pkl', '_baseline.txt')
    with open(baseline_path, 'w') as f:
        f.write(baseline.isoformat())
    print(f"Model saved to {MODEL_PATH}, baseline saved to {baseline_path}")
    return model, baseline

def predict_future(model, baseline: pd.Timestamp, last_inpc: float, last_date: pd.Timestamp, horizons=[1,2,3,6]):
    """Predict INPC for future months and compute cumulative inflation."""
    # Compute months offset for last date
    last_months = (last_date - baseline).days / 30.0
    predictions = {}
    for h in horizons:
        future_months = last_months + h
        pred_inpc = model.predict([[future_months]])[0]
        # Cumulative inflation over h months: (pred_inpc / last_inpc - 1) * 100
        infl = (pred_inpc / last_inpc - 1) * 100.0
        predictions[h] = {
            'predicted_inpc': pred_inpc,
            'cumulative_inflation_pct': infl
        }
    return predictions

def main():
    # Step 1: fetch
    df_raw = fetch_inpc_data()
    # Step 2: preprocess
    df = preprocess(df_raw)
    # Step 3: train
    model, baseline = train_model(df)
    # Step 4: predict
    last_inpc = df['inpc'].iloc[-1]
    last_date = df['date'].iloc[-1]
    preds = predict_future(model, baseline, last_inpc, last_date, horizons=[1,2,3,6])
    # Step 5: save predictions
    rows = []
    for h, vals in preds.items():
        rows.append({
            'horizon_months': h,
            'predicted_inpc': vals['predicted_inpc'],
            'cumulative_inflation_pct': vals['cumulative_inflation_pct']
        })
    preds_df = pd.DataFrame(rows)
    preds_df.to_csv(PREDS_PATH, index=False)
    print(f"Predictions saved to {PREDS_PATH}")
    print(preds_df)

if __name__ == "__main__":
    main()
