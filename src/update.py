#!/usr/bin/env python3
"""
update.py: Orchestrates the full pipeline for INPC inflation prediction.
Steps:
1. Load local INPC data (CSV) – expected to be updated by user periodically.
   The fetch_inpc function will estimate missing months if needed.
2. Keep only the last 36 months (3 years) of data for training, discarding the oldest month when a new month is added.
3. Feature engineering: months since start of window.
4. Train linear regression model (least squares) to predict INPC index.
5. Predict future INPC values for next 1, 2, 3, 6 months.
6. Compute cumulative inflation over each horizon.
7. Save predictions to results/predictions.csv with extra metadata:
   - base_month: the month of the last known INPC (YYYY-MM)
   - forecast_month: the target month for each horizon (YYYY-MM)
8. Generate a simple forecast plot saved to results/forecast.png.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import joblib

# Import our own fetch function (now just a loader/estimator)
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from fetch_inpc import fetch_inpc
from plot import plot_forecast

# Paths
RAW_PATH = os.path.join("data", "inpc_raw.csv")
PROCESSED_PATH = os.path.join("data", "inpc_processed.csv")
MODEL_PATH = os.path.join("models", "linreg.pkl")
PREDS_PATH = os.path.join("results", "predictions.csv")
PLOT_PATH = os.path.join("results", "forecast.png")

# Ensure directories exist
for p in [os.path.dirname(RAW_PATH), os.path.dirname(PROCESSED_PATH),
          os.path.dirname(MODEL_PATH), os.path.dirname(PREDS_PATH),
          os.path.dirname(PLOT_PATH)]:
    os.makedirs(p, exist_ok=True)

def load_and_update_data():
    """Load CSV, estimate missing months if needed, ensure columns, parse dates, sort."""
    if not os.path.exists(RAW_PATH):
        print(f"Error: Expected data file not found at {RAW_PATH}")
        print("Please place a CSV with columns 'date' and 'inpc' in the data/ directory.")
        sys.exit(1)
    # Use fetch_inpc to load/update and estimate missing months
    fetch_inpc("", RAW_PATH)
    df = pd.read_csv(RAW_PATH, parse_dates=['date'])
    # Standardize column names
    cols = [c.strip().lower() for c in df.columns]
    if 'date' not in cols or 'inpc' not in cols:
        # Try to infer: first column date, second column value
        if len(df.columns) >= 2:
            df = df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'inpc'})
        else:
            print("CSV does not have enough columns (need at least date and value).")
            sys.exit(1)
    # Ensure estimated column exists
    if 'estimated' not in df.columns:
        df['estimated'] = False
    else:
        df['estimated'] = df['estimated'].fillna(False).astype(bool)
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values('date')
    # Save cleaned version (ensuring proper format)
    df.to_csv(RAW_PATH, index=False)
    print(f"Loaded and validated data from {RAW_PATH} with {len(df)} rows")
    if df['estimated'].any():
        est_count = df['estimated'].sum()
        print(f"Warning: {est_count} row(s) are estimated (flagged). Replace with official data when available.")
    return df

def preprocess(df: pd.DataFrame):
    """Ensure monthly frequency, forward fill missing months."""
    df = df.set_index('date')
    # Resample to month start, taking last observation
    df_monthly = df.resample('MS').last().reset_index()
    df_monthly['inpc'] = df_monthly['inpc'].ffill()
    df_monthly.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved processed data to {PROCESSED_PATH} with {len(df_monthly)} rows")
    return df_monthly

def train_model(df: pd.DataFrame):
    """Create feature: months since window start, train LinearRegression."""
    df = df.copy()
    # Use months since first date in the window
    df['months'] = (df['date'] - df['date'].iloc[0]).dt.days / 30.0
    X = df[['months']].values
    y = df['inpc'].values
    model = LinearRegression()
    model.fit(X, y)
    # Save model
    joblib.dump(model, MODEL_PATH)
    # Save baseline (window start date) for later use in prediction
    baseline = df['date'].iloc[0]
    baseline_path = MODEL_PATH.replace('.pkl', '_baseline.txt')
    with open(baseline_path, 'w') as f:
        f.write(baseline.isoformat())
    print(f"Model saved to {MODEL_PATH}, baseline saved to {baseline_path}")
    return model, baseline

def predict_future(model, baseline: pd.Timestamp, last_inpc: float, last_date: pd.Timestamp, horizons=[1,2,3,6,12]):
    """Predict INPC for future months and compute cumulative inflation."""
    last_months = (last_date - baseline).days / 30.0
    predictions = []
    base_month_str = last_date.strftime('%Y-%m')
    for h in horizons:
        future_months = last_months + h
        pred_inpc = model.predict([[future_months]])[0]
        infl = (pred_inpc / last_inpc - 1) * 100.0
        forecast_date = last_date + pd.DateOffset(months=h)
        forecast_month_str = forecast_date.strftime('%Y-%m')
        predictions.append({
            'horizon_months': h,
            'base_month': base_month_str,
            'forecast_month': forecast_month_str,
            'predicted_inpc': round(pred_inpc, 2),
            'cumulative_inflation_pct': round(infl, 2)
        })
    return predictions

def main():
    # Step 1: load/update data
    df_raw = load_and_update_data()
    # Step 2: preprocess to monthly
    df_monthly = preprocess(df_raw)
    # Step 3: keep only last 36 months (3 years) for training
    max_date = df_monthly['date'].iloc[-1]
    window_start = max_date - pd.DateOffset(months=35)
    df_train = df_monthly[(df_monthly['date'] >= window_start) & (df_monthly['date'] <= max_date)].copy()
    print(f"Training window: {window_start.date()} to {max_date.date()} ({len(df_train)} months)")
    if len(df_train) < 2:
        print("Not enough data in the last 36 months to train a model.")
        sys.exit(1)
    # Step 4: train model
    model, baseline = train_model(df_train)
    # Step 5: predict
    last_inpc = df_monthly['inpc'].iloc[-1]
    last_date = df_monthly['date'].iloc[-1]
    preds = predict_future(model, baseline, last_inpc, last_date, horizons=[1,2,3,6,12])
    # Step 6: save predictions
    preds_df = pd.DataFrame(preds, columns=['horizon_months','base_month','forecast_month','predicted_inpc','cumulative_inflation_pct'])
    preds_df.to_csv(PREDS_PATH, index=False)
    print(f"Predictions saved to {PREDS_PATH}")
    print(preds_df.to_string(index=False))
    # Step 7: plot
    plot_forecast(PROCESSED_PATH, PREDS_PATH, PLOT_PATH)

if __name__ == "__main__":
    main()