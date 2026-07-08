import sqlite3
import pandas as pd
import os
from scipy.stats import rankdata

def load_table_names(connection):
    """Fetches original raw stock tables, ignoring statistical output tables."""
    cursor = connection.cursor()
    # Explicitly filter out master tables to avoid loop crashes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'master_%';")
    return [row[0] for row in cursor.fetchall()]

def calculate_market_geometry(df):
    """Transforms raw price scales into pure normalized shapes."""
    df = df.sort_values('date').copy()
    
    # 14-day Rolling Z-Score
    rolling_mean = df['close'].rolling(window=14).mean()
    rolling_std = df['close'].rolling(window=14).std()
    df['price_z_score'] = (df['close'] - rolling_mean) / rolling_std
    
    # 252-day Volume Percentile
    def get_last_value_percentile(window):
        if len(window) < 2: return 0.5
        ranks = rankdata(window)
        return (ranks[-1] - 1) / (len(window) - 1)
        
    df['volume_percentile'] = (
        df['volume']
        .rolling(window=252, min_periods=30)
        .apply(get_last_value_percentile, raw=True)
    )
    
    df = df.dropna(subset=['price_z_score', 'volume_percentile'])
    return df[['date', 'price_z_score', 'volume_percentile']].copy()

def main():
    db_name = "market_memory.db"
    if not os.path.exists(db_name):
        print("❌ Could not find database. Run download_data.py first!")
        return

    conn = sqlite3.connect(db_name)
    tables = load_table_names(conn)
    print(f"Found {len(tables)} clean stock tables to process.")
    
    master_geometry_list = []
    
    for index, table in enumerate(tables, 1):
        # Universal bracket protection for safe querying
        query = f"SELECT date, close, volume FROM [{table}]"
        raw_df = pd.read_sql_query(query, conn)
        
        if len(raw_df) < 252:
            continue
            
        shape_matrix = calculate_market_geometry(raw_df)
        
        # Inject metadata so we know exactly which stock this shape belongs to!
        shape_matrix['stock_id'] = table
        master_geometry_list.append(shape_matrix)
        
    if master_geometry_list:
        final_anonymized_dataset = pd.concat(master_geometry_list, ignore_index=True)
        
        # Save as a structured master database matrix
        final_anonymized_dataset.to_sql("master_market_geometry", conn, if_exists="replace", index=False)
        print(f"🎉 Success! Generated {len(final_anonymized_dataset):,} sanitized geometric rows.")
    
    conn.close()

if __name__ == "__main__":
    main()
