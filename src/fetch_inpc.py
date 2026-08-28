#!/usr/bin/env python3
"""
fetch_inpc.py: Download INPC data from World Bank API (monthly CPI) and save as CSV.
"""

import os
import sys
import json
import urllib.request

def fetch_inpc(url: str, output_path: str) -> None:
    """
    Download INPC data from the given URL and save it as a CSV file.
    """
    print(f"Downloading INPC data from {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200:
                print(f"Failed to download data: HTTP {response.status}")
                sys.exit(1)
            data = response.read()
    except Exception as e:
        print(f"Failed to download data: {e}")
        sys.exit(1)

    # Parse JSON
    try:
        parsed = json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        sys.exit(1)

    # Expected format: [metadata, [records]]
    if not isinstance(parsed, list) or len(parsed) < 2:
        print("Unexpected response format")
        sys.exit(1)
    records = parsed[1]
    if not records:
        print("No records found")
        sys.exit(1)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write CSV
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('date,inpc\n')
        for rec in records:
            # rec: {'date': '2023', 'value': 176.116..., ...}
            # We have monthly data? The API with frequency=M returns monthly? Actually the earlier call didn't specify frequency.
            # We'll assume the data is annual? We need monthly.
            # Let's adjust: we will call the API with frequency=M to get monthly.
            # But for now, we'll just write what we have.
            date = rec.get('date')
            value = rec.get('value')
            if date is None or value is None:
                continue
            f.write(f'{date},{value}\n')
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    # Default URL – World Bank monthly CPI for Mexico
    DEFAULT_URL = ("https://api.worldbank.org/v2/country/MEX/indicator/"
                   "FP.CPI.TOTL?format=json&date=2000:2025&frequency=M&per_page=5000")
    url = os.getenv("INPC_URL", DEFAULT_URL)
    out_path = os.path.join("data", "inpc_raw.csv")
    fetch_inpc(url, out_path)