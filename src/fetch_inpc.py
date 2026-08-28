import os
import sys
import pandas as pd

def fetch_inpc(url: str, output_path: str) -> None:
    """
    Load INPC data from a local CSV file.
    The `url` argument is ignored (kept for compatibility).
    The function expects the file to already exist at `output_path`.
    """
    if not os.path.exists(output_path):
        print(f"Error: Expected data file not found at {output_path}")
        print("Please ensure the historical INPC CSV is present in the data/ directory.")
        sys.exit(1)
    # Simply verify the file can be read
    try:
        df = pd.read_csv(output_path)
        # Ensure required columns exist; if not, try to infer
        if 'date' not in df.columns or 'inpc' not in df.columns:
            cols = df.columns.tolist()
            if len(cols) >= 2:
                df = df.rename(columns={cols[0]: 'date', cols[1]: 'inpc'})
            else:
                print("CSV does not have enough columns (need at least date and value).")
                sys.exit(1)
        # Save a cleaned version (ensuring proper types)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date')
        df.to_csv(output_path, index=False)
        print(f"Loaded and validated data from {output_path} with {len(df)} rows")
    except Exception as e:
        print(f"Failed to read or process CSV: {e}")
        sys.exit(1)