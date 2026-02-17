import sqlite3
import os
from datetime import datetime

# Define database path
DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_FOLDER, 'prices.db')

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    return sqlite3.connect(DB_PATH)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='price_data'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("PRAGMA table_info(price_data)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'website' not in columns:
            print("Website column missing. Recreating table...")
            cursor.execute("DROP TABLE price_data")
            table_exists = None
    
    if not table_exists:
        cursor.execute('''
            CREATE TABLE price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price REAL,
                website TEXT
            )
        ''')
    
    conn.commit()
    conn.close()

def insert_price(date, item_name, price, website):
    """
    Inserts a new price record into the database.
    
    Args:
        date (str): Date in 'YYYY-MM-DD' format.
        item_name (str): Name of the product.
        price (float): Price of the product.
        website (str): Website name (e.g. 'BigBasket').
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO price_data (date, item_name, price, website)
        VALUES (?, ?, ?, ?)
    ''', (date, item_name, price, website))
    
    conn.commit()
    conn.close()

def fetch_all_data():
    """
    Fetches all data from the price_data table.
    
    Returns:
        pd.DataFrame: DataFrame containing all price data.
    """
    import pandas as pd
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM price_data", conn)
    except Exception as e:
        print(f"Error fetching data: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

if __name__ == "__main__":
    create_table()
    print(f"Database setup complete at {DB_PATH}")
