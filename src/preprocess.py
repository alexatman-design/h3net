import pandas as pd
import numpy as np
import os

def preprocess(raw_path: str, processed_path: str) -> None:
    """
    Load raw INPC data, parse dates, and save a cleaned monthly time series.
    Expected raw CSV has at least two columns: date (string) and index value.
    If parsing fails, generate synthetic data for demonstration.
    """
    print(f"Loading raw data from {raw_path}")
    try:
        # Try to read with pandas, inferring date format
        df = pd.read_csv(raw_path)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        df = None

    if df is not None and df.shape[1] >= 2:
        # Assume first column is date, second is index value
        date_col = df.columns[0]
        val_col = df.columns[1]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df = df.sort_values(date_col)
        df = df.rename(columns={date_col: 'date', val_col: 'inpc'})
        df[['date', 'inpc']].to_csv(processed_path, index=False)
        print(f"Processed data saved to {processed_path} with {len(df)} rows")
        return

    # Fallback: generate synthetic data for demonstration
    print("Generating synthetic INPC data for demonstration (2023-01 to 2025-12)")
    dates = pd.date_range(start='2023-01-01', end='2025-12-01', freq='MS')
    # Simulate a CPI index with some trend and noise
    base = 100
    trend = np.linspace(0, 12, len(dates))  # 12 points over 3 years (36 months)
    noise = np.random.normal(0, 0.5, len(dates))
    inpc = base + trend + noise
    df = pd.DataFrame({'date': dates, 'inpc': inpc})
    df.to_csv(processed_path, index=False)
    print(f"Synthetic data saved to {processed_path}")

if __name__ == "__main__":
    raw = os.path.join("data", "inpc_raw.csv")
    processed = os.path.join("data", "inpc_processed.csv")
    preprocess(raw, processed)