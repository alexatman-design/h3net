# h3net - INPC Inflation Prediction Project

This project collects historical INPC (Índice Nacional de Precios al Consumidor) data, trains a simple linear regression model (least squares), and predicts inflation for the next monthly, bimonthly, quarterly, and semester periods.

## Data Source

The script currently fetches data from the World Bank API (indicator `FP.CPI.TOTL` – Consumer price index (2010 = 100)) for Mexico. If you prefer to use official INEGI data, replace the download URL in `src/fetch_inpc.py` with the direct CSV link from INEGI.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the full update pipeline:

```bash
python src/update.py
```

This will:
1. Download the latest INPC data.
2. Preprocess (ensure monthly frequency).
3. Fit a linear regression model (time as predictor).
4. Generate predictions for the next 1, 2, 3, and 6 months.
5. Save predictions to `results/predictions.csv`.
6. (Optional) Create a simple line plot of the historical INPC and forecast saved as `results/forecast.png`.

## How to read the predictions

Open `results/predictions.csv` (or view it directly on GitHub). The file contains three columns:

| Column | Meaning |
|--------|---------|
| `horizon_months` | Number of months ahead for which the prediction is made (1, 2, 3, 6). |
| `predicted_inpc` | Forecasted value of the INPC index for that future month. |
| `cumulative_inflation_pct` | Expected **cumulative inflation (or deflation)** between the last known INPC and the forecasted month, expressed as a percentage. <br>Formula: <br>`((predicted_inpc / last_known_inpc) – 1) × 100` |

- A **negative** `cumulative_inflation_pct` indicates the model expects the INPC to fall (deflation) relative to today.
- A **positive** value indicates expected price increase (inflation).

### Example

If the last known INPC is 191.45 and the forecast for 1 month ahead is 171.68, then:

```
cumulative_inflation = (171.68 / 191.45 – 1) × 100 ≈ –10.33 %
```

This suggests a **10.33 % deflation** over the next month.

## Visualization

After running `src/update.py`, a plot `results/forecast.png` is generated showing:

- Historical INPC (blue line).
- Point forecasts for the next 1, 2, 3, and 6 months (red markers).
- A dashed line connecting the last historical point to each forecast to visualise the trend.

You can view the image directly on GitHub under `results/forecast.png` or download it.

## Project Structure

```
h3net/
├─ data/                # Raw and processed data
│   ├─ inpc_raw.csv     # Downloaded series
│   └─ inpc_processed.csv# Cleaned monthly series
├─ src/
│   ├─ fetch_inpc.py    # Download data (World Bank API by default)
│   ├─ preprocess.py    # Ensure monthly frequency
│   ├─ model.py         # Linear regression training / loading
│   ├─ predict.py       # Prediction logic (used by update.py)
│   ├─ plot.py          # Create forecast plot
│   └─ update.py        # Orchestrates the pipeline
├─ models/              # Trained model and baseline date
│   ├─ linreg.pkl
│   └─ linreg_baseline.txt
├─ results/
│   ├─ predictions.csv  # Forecast table
│   └─ forecast.png     # Visualisation (created after first run)
├─ notebooks/           # Optional exploratory analysis
└─ requirements.txt
```

## Customization

- **Change prediction horizon:** edit the list `horizons = [1,2,3,6]` in `src/predict.py`.
- **Add features (e.g., seasonality):** modify `src/preprocess.py`.
- **Replace the model:** use a different algorithm in `src/model.py` and adjust `src/update.py` accordingly.
- **Use official INEGI data:** replace the URL in `src/fetch_inpc.py` with the direct CSV link from INEGI.

## License

MIT