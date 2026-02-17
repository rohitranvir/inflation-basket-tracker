import pandas as pd
import numpy as np

def create_features(df):
    """
    Creates time-series features for the forecasting model.
    
    Args:
        df (pd.DataFrame): DataFrame with 'date' and 'total_cost' columns.
        
    Returns:
        pd.DataFrame: DataFrame with added features.
    """
    df = df.copy()
    
    # Ensure date is datetime
    if not np.issubdtype(df['date'].dtype, np.datetime64):
        df['date'] = pd.to_datetime(df['date'])
    
    # Date-based features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Timestamp ordinal for trend
    df['date_ordinal'] = df['date'].map(pd.Timestamp.toordinal)
    
    return df
