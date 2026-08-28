import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_forecast(processed_path: str, preds_path: str, output_path: str) -> None:
    """
    Create a simple plot showing historical INPC and forecast points.
    """
    # Load historical data
    df_hist = pd.read_csv(processed_path, parse_dates=['date'])
    # Load predictions
    df_pred = pd.read_csv(preds_path)
    
    # Compute future dates based on last historical date and horizon
    last_date = df_hist['date'].iloc[-1]
    future_dates = [last_date + pd.DateOffset(months=int(h)) for h in df_pred['horizon_months']]
    
    plt.figure(figsize=(10, 6))
    plt.plot(df_hist['date'], df_hist['inpc'], label='Historical INPC', color='blue')
    plt.scatter(future_dates, df_pred['predicted_inpc'], color='red', zorder=5, label='Forecast')
    # Connect last historical point to each forecast for clarity
    for fd, pred in zip(future_dates, df_pred['predicted_inpc']):
        plt.plot([last_date, fd], [df_hist['inpc'].iloc[-1], pred], color='red', linestyle='--', linewidth=1)
    
    plt.title('INPC Historical and Forecast')
    plt.xlabel('Date')
    plt.ylabel('INPC (2010 = 100)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f'Forecast plot saved to {output_path}')

if __name__ == '__main__':
    # Example usage when run directly
    processed = os.path.join('data', 'inpc_processed.csv')
    preds = os.path.join('results', 'predictions.csv')
    out = os.path.join('results', 'forecast.png')
    plot_forecast(processed, preds, out)