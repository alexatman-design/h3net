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
2. Preprocess (ensure monthly frequency, compute month-over-month inflation if desired).
3. Fit a linear regression model (time as predictor).
4. Generate predictions for the next 1, 2, 3, and 6 months.
5. Save predictions to `results/predictions.csv`.

## Project Structure

```
h3net/
├─ data/                # Raw and processed data
├─ src/
│   ├─ fetch_inpc.py    # Download data
│   ├─ preprocess.py    # Clean & feature engineering
│   ├─ model.py         # Linear regression training
│   ├─ predict.py       # Forecast generation
│   └─ update.py        # Orchestrates the pipeline
├─ results/             # Output predictions
├─ notebooks/           # Optional exploratory analysis
└─ requirements.txt
```

## Customization

- To change the prediction horizon, edit `src/predict.py`.
- To use additional features (e.g., seasonality), modify `src/preprocess.py`.
- Model currently uses a simple time trend; replace with more sophisticated models in `src/model.py`.

## License

MIT