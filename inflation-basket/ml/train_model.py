import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os
import sys
import joblib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import DB_PATH, fetch_all_data
from processing.feature_engineering import create_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

def train():
    print("Loading data...")
    df = fetch_all_data()

    if df.empty:
        print("No data to train on.")
        return

    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate daily basket cost
    # We aggregate by date to get total cost of basket per day
    daily_cost = df.pivot_table(index='date', columns='item_name', values='price', aggfunc='mean').sum(axis=1).reset_index()
    daily_cost.columns = ['date', 'total_cost']
    
    if len(daily_cost) < 2:
        print("Not enough data to train (need at least 2 days).")
        return

    # Create features
    daily_cost = create_features(daily_cost)
    
    # Features to use
    features = ['day_of_week', 'day_of_year', 'month', 'is_weekend', 'date_ordinal']
    X = daily_cost[features]
    y = daily_cost['total_cost']

    print("Training Random Forest model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    print(f"Model trained. Score: {model.score(X, y):.4f}")

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
