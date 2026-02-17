import pandas as pd
import numpy as np
import joblib
import os
import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.feature_engineering import create_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
PREDICTIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'predictions.csv')

def predict_future():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Run train_model.py first.")
        return

    print("Loading model...")
    model = joblib.load(MODEL_PATH)

    # Predict for next 7 days
    today = datetime.date.today()
    future_dates = [today + datetime.timedelta(days=i) for i in range(1, 8)]
    
    # Create DataFrame for future dates
    future_df = pd.DataFrame({'date': future_dates})
    future_df['date'] = pd.to_datetime(future_df['date'])
    
    # Generate features
    future_features = create_features(future_df)
    
    # Features to use (must match training)
    features = ['day_of_week', 'day_of_year', 'month', 'is_weekend', 'date_ordinal']
    X_future = future_features[features]

    print("Predicting...")
    predictions = model.predict(X_future)

    # Create DataFrame
    pred_df = pd.DataFrame({
        'date': future_dates,
        'predicted_cost': predictions
    })

    print(pred_df)

    # Save to CSV
    pred_df.to_csv(PREDICTIONS_PATH, index=False)
    print(f"Predictions saved to {PREDICTIONS_PATH}")

if __name__ == "__main__":
    predict_future()
