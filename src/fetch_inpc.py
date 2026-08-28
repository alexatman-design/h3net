import os
import sys
import pandas as pd
from datetime import datetime, timedelta

def fetch_inpc(output_path: str) -> None:
    """
    Load or update INPC data from a local CSV file.
    If the file exists but is outdated (missing the current month),
    it will estimate the missing month(s) using the average monthly change
    and flag them as estimated.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # If file does not exist, create an empty template with expected columns
    if not os.path.exists(output_path):
        df = pd.DataFrame(columns=['date', 'inpc', 'estimated'])
        df.to_csv(output_path, index=False)
        print(f"Created empty data file at {output_path}")
        return

    # Load existing data
    try:
        df = pd.read_csv(output_path, parse_dates=['date'])
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        sys.exit(1)

    # Ensure expected columns exist
    expected_cols = {'date', 'inpc'}
    if not expected_cols.issubset(set(df.columns)):
        # Try to infer: first column date, second column value
        cols = df.columns.tolist()
        if len(cols) >= 2:
            df = df.rename(columns={cols[0]: 'date', cols[1]: 'inpc'})
        else:
            print("CSV does not have enough columns (need at least date and value).")
            sys.exit(1)

    # Ensure estimated column exists, default False
    if 'estimated' not in df.columns:
        df['estimated'] = False
    else:
        # Ensure boolean type
        df['estimated'] = df['estimated'].fillna(False).astype(bool)

    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    # Determine the first day of the current month
    today = pd.Timestamp(datetime.now())
    current_month_first = today.replace(day=1)

    # Find the latest date in the data
    if df.empty:
        last_date = pd.Timestamp('1900-01-01')
    else:
        last_date = df['date'].max()

    # If we are missing data for the current month (or later), estimate missing months
    # We'll estimate month by month until we reach the current month (first day)
    # We'll stop when last_date >= current_month_first
    if last_date < current_month_first:
        # Compute average monthly change from existing data (excluding estimated rows if desired)
        # Use all data for simplicity
        if len(df) >= 2:
            df['inpc_diff'] = df['inpc'].diff()
            avg_monthly_change = df['inpc_diff'].mean()
        else:
            avg_monthly_change = 0.0

        # Estimate missing months
        cur = last_date + pd.DateOffset(months=1)
        while cur < current_month_first:
            # Predict next month's INPC using average change
            last_inpc = df.loc[df['date'] == df['date'].max(), 'inpc'].values[0]
            predicted_inpc = last_inpc + avg_monthly_change
            new_row = pd.DataFrame({
                'date': [cur],
                'inpc': [predicted_inpc],
                'estimated': [True]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            cur += pd.DateOffset(months=1)

        # After loop, if last_date is still before current_month_first (should be equal now)
        # Ensure we have data up to the month before current month (we don't estimate current month itself)
        # Actually we want to have data up to the previous month; we stop before current_month_first.
        # So after loop, last_date will be the date of the last estimated month, which is < current_month_first.
        # That's fine; we will not have an estimate for the current month itself (the month we are in).
        # The user can later replace the estimated rows with official data when available.

    # Drop the helper column if we added it
    if 'inpc_diff' in df.columns:
        df = df.drop(columns=['inpc_diff'])

    # Save back
    df.to_csv(output_path, index=False)
    print(f"Data loaded/updated and saved to {output_path} with {len(df)} rows")
    if df['estimated'].any():
        est_count = df['estimated'].sum()
        print(f"Warning: {est_count} row(s) are estimated (flagged). Replace with official data when available.")