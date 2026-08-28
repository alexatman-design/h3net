\"\"\"auto_update.py: Simple watcher that runs the prediction pipeline
when new INPC data appears.

It checks, on days 1, 2, and 3 of each month, whether the CSV
`data/inpc_raw.csv` contains data for the current month (i.e., the
latest month in the file is >= current month). If so, it executes
the prediction pipeline (via src.pipeline.run_predictions) and then
waits until the next day to avoid multiple runs.

This script is intended to be run continuously in the background
(e.g., via `nohup python src/auto_update.py &` or a process manager).
It does **not** rely on external cron services; the timing logic is
self-contained.

Dependencies: only those already required by the project
(pandas, numpy, scikit-learn, matplotlib, joblib).
\"\""

import os
import time
import datetime as dt
from src.pipeline import run_predictions

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'inpc_raw.csv')

def _get_latest_month_from_csv(csv_path: str) -> dt.date:
    """Return the latest month (as date with day=1) present in the CSV."""
    if not os.path.exists(csv_path):
        # No data yet
        return dt.date.min
    import pandas as pd
    df = pd.read_csv(csv_path, parse_dates=['date'])
    if df.empty:
        return dt.date.min
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    latest = df['date'].max()
    # Return first day of that month for easy comparison
    return dt.date(latest.year, latest.month, 1)

def _should_run_today() -> bool:
    """Determine if we should attempt a run today.
    Run only on days 1, 2, 3 of the month.
    """
    today = dt.date.today()
    return today.day in (1, 2, 3)

def _is_new_data_available() -> bool:
    """Check if the CSV contains data for the current month.
    We consider that we have data for the current month if the
    latest month in the file is >= today's month (year/month).
    """
    latest_month = _get_latest_month_from_csv(CSV_PATH)
    today = dt.date.today()
    # Compare year*12 + month to avoid year rollover issues
    latest_key = latest_month.year * 12 + latest_month.month
    today_key = today.year * 12 + today.month
    return latest_key >= today_key

def start_auto_update(check_interval_hours: float = 24.0):
    """Run an infinite loop that checks for new data and triggers
    the prediction pipeline when appropriate.

    Parameters
    ----------
    check_interval_hours : float
        How many hours to wait between checks when conditions are not met.
        Default is 24 hours (once per day). Set lower for more responsive
        checking during the first days of the month.
    """
    print("Starting automatic INPC update watcher...")
    print(f"Checking CSV: {CSV_PATH}")
    while True:
        try:
            if _should_run_today() and _is_new_data_available():
                print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] "
                      "New data detected – running prediction pipeline...")
                run_predictions()
                print("Pipeline completed. Waiting for next day to avoid duplicate runs.")
                # Sleep for a day to avoid multiple runs on the same day
                time.sleep(60 * 60 * 24)
            else:
                # Not yet time or no new data; wait a bit before checking again
                hrs = check_interval_hours
                print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] "
                      f"No action needed. Sleeping {hrs} hour(s)...")
                time.sleep(hrs * 3600)
        except Exception as e:
            print(f"Error during auto-update cycle: {e}")
            # Continue after a short pause to avoid tight error loops
            time.sleep(5 * 60)  # 5 minutes

if __name__ == "__main__":
    # When run directly, start the watcher with default 24h interval.
    # You can adjust the interval via env var AUTO_UPDATE_INTERVAL_HOURS.
    interval = float(os.getenv("AUTO_UPDATE_INTERVAL_HOURS", "24.0"))
    start_auto_update(check_interval_hours=interval)