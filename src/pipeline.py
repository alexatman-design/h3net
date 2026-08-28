\"\"\"
pipeline.py: Self-contained function to run the INPC prediction pipeline.
Provides `run_predictions(csv_path=None)` which loads the CSV, preprocesses,
trains a linear regression model on the last 3 years, predicts the next
1, 2, 3, and 6 months, and saves the results to `results/predictions.csv`
and a plot to `results/forecast.png`.

If `csv_path` is None, defaults to "data/inpc_raw.csv".
\"\"\"

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import joblib
import matplotlib.pyplot as plt

def _load_and_validate_data(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    df = pd.read_csv(csv_path, parse_dates=['date'])
    # Standardize column names
    cols = [c.strip().lower() for c in df.columns]
    if 'date' not in cols or 'inpc' not in cols:
        # infer first two columns
        if len(df.columns) >= 2:
            df = df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'inpc'})
        else:
            raise ValueError("CSV must have at least two columns: date and inpc.")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values('date')
    return df[['date', 'inpc']]

def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index('date')
    # resample to month start, take last observation, forward fill missing
    df_monthly = df.resample('MS').last().reset_index()
    df_monthly['inpc'] = df_monthly['inpc'].ffill()
    return df_monthly

def _train_model(df: pd.DataFrame):
    df = df.copy()
    # window of last 3 years
    max_date = df['date'].iloc[-1]
    window_start = max_date - pd.DateOffset(years=3)
    df_train = df[(df['date'] >= window_start) & (df['date'] <= max_date)].copy()
    if len(df_train) < 2:
        raise ValueError("Not enough data in the last 3 years to train a model.")
    df_train['months'] = (df_train['date'] - df_train['date'].iloc[0]).dt.days / 30.0
    X = df_train[['months']].values
    y = df_train['inpc'].values
    model = LinearRegression()
    model.fit(X, y)
    return model, df_train['date'].iloc[0]  # baseline

def _predict_future(model, baseline: pd.Timestamp, last_inpc: float, last_date: pd.Timestamp, horizons=[1,2,3,6,12]):
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
            'predicted_inpc': pred_inpc,
            'cumulative_inflation_pct': infl
        })
    return predictions

def _save_predictions(preds, output_csv: str):
    preds_df = pd.DataFrame(preds, columns=['horizon_months','base_month','forecast_month','predicted_inpc','cumulative_inflation_pct'])
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    preds_df.to_csv(output_csv, index=False)
    return preds_df

def _plot_forecast(processed_df: pd.DataFrame, preds_df: pd.DataFrame, output_png: str):
    # historical
    hist = processed_df.copy()
    # forecast points
    last_date = hist['date'].iloc[-1]
    future_dates = [last_date + pd.DateOffset(months=int(h)) for h in preds_df['horizon_months']]
    plt.figure(figsize=(10,6))
    plt.plot(hist['date'], hist['inpc'], label='Historical INPC', color='blue')
    plt.scatter(future_dates, preds_df['predicted_inpc'], color='red', zorder=5, label='Forecast')
    for fd, pred in zip(future_dates, preds_df['predicted_inpc']):
        plt.plot([last_date, fd], [hist['inpc'].iloc[-1], pred], color='red', linestyle='--', linewidth=1)
    plt.title('INPC Historical and Forecast')
    plt.xlabel('Date')
    plt.ylabel('INPC (2010 = 100)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, dpi=150)
    plt.close()

def run_predictions(csv_path: str = None):
    """
    Execute the full prediction pipeline.
    Parameters
    ----------
    csv_path : str, optional
        Path to the CSV containing columns `date` and `inpc`.
        If None, uses "data/inpc_raw.csv" relative to this file's directory.
    Returns
    -------
    preds_df : pandas.DataFrame
        DataFrame with columns:
        horizon_months, base_month, forecast_month, predicted_inpc, cumulative_inflation_pct
    Side effects
    ------------
    Writes `results/predictions.csv` and `results/forecast.png`.
    """
    if csv_path is None:
        # default relative to this file
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        csv_path = os.path.join(base_dir, 'data', 'inpc_raw.csv')
    # 1. Load data
    df_raw = _load_and_validate_data(csv_path)
    # 2. Preprocess
    df_monthly = _preprocess(df_raw)
    # 3. Train model
    model, baseline = _train_model(df_monthly)
    # 4. Predict
    last_inpc = df_monthly['inpc'].iloc[-1]
    last_date = df_monthly['date'].iloc[-1]
    preds = _predict_future(model, baseline, last_inpc, last_date, horizons=[1,2,3,6])
    # Define output paths relative to this file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    preds_csv = os.path.join(base_dir, 'results', 'predictions.csv')
    forecast_png = os.path.join(base_dir, 'results', 'forecast.png')
    # 5. Save
    preds_df = _save_predictions(preds, preds_csv)
    _plot_forecast(df_monthly, preds_df, forecast_png)
    return preds_df

if __name__ == "__main__":
    # When run as script, just execute and print results
    df = run_predictions()
    print("Predictions saved:")
    print(df.to_string(index=False))