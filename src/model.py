import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os

def train_model(X, y, model_path: str) -> LinearRegression:
    """
    Fit a linear regression model (least squares) and save it.
    """
    model = LinearRegression()
    model.fit(X, y)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model trained and saved to {model_path}")
    return model

def load_model(model_path: str) -> LinearRegression:
    """
    Load a previously saved model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    model = joblib.load(model_path)
    print(f"Model loaded from {model_path}")
    return model

if __name__ == "__main__":
    # Example usage (not called when imported)
    pass