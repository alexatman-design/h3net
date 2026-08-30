import os
import sys
import pandas as pd
from datetime import datetime

def fetch_inpc(url: str, output_path: str) -> None:
    """
    Attempt to download INPC data from the given URL.
    If download succeeds, replace the local file.
    If download fails but a local file exists, keep the local file.
    If neither exists, raise an error.
    The `url` can be overridden via environment variable INPC_URL.
    """
    # Allow override via environment variable
    effective_url = os.getenv("INPC_URL", url)
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    downloaded = False
    if effective_url:
        try:
            print(f"Attempting to download INPC data from {effective_url}")
            # Use pandas to read CSV directly from URL (handles http/https)
            df = pd.read_csv(effective_url)
            # Expect at least two columns; try to standardize
            if len(df.columns) >= 2:
                # Assume first column is date, second is value
                df = df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'inpc'})
                # Ensure date parsing
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                df = df.sort_values('date')
                # Keep only needed columns
                df = df[['date', 'inpc']]
                df.to_csv(output_path, index=False)
                print(f"Downloaded and saved data to {output_path} with {len(df)} rows")
                downloaded = True
            else:
                print("Downloaded CSV does not have enough columns.")
        except Exception as e:
            print(f"Download failed: {e}")

    if not downloaded:
        # Fallback to local file if exists
        if os.path.exists(output_path):
            print(f"Using existing local file at {output_path}")
            # Validate local file
            try:
                df = pd.read_csv(output_path, parse_dates=['date'])
                if 'date' not in df.columns or 'inpc' not in df.columns:
                    # Try to infer
                    cols = df.columns.tolist()
                    if len(df.columns) >= 2:
                        df = df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'inpc'})
                    else:
                        raise ValueError("CSV does not have enough columns.")
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                df = df.sort_values('date')
                df = df[['date', 'inpc']]
                df.to_csv(output_path, index=False)
                print(f"Validated and saved local data with {len(df)} rows")
            except Exception as e:
                print(f"Local file is invalid: {e}")
                sys.exit(1)
        else:
            print(f"Error: Unable to download data and no local file found at {output_path}")
            sys.exit(1)