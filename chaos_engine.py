import sqlite3
import pandas as pd
import numpy as np
import os
from tslearn.metrics import dtw

def main():
    db_name = "market_memory.db"
    conn = sqlite3.connect(db_name)
    
    print("Loading optimized shape data from database...")
    # Read our master geometry table directly
    df = pd.read_sql_query("SELECT * FROM master_market_geometry ORDER BY stock_id, date", conn)
    
    # Define today's live input target vector (14 days of Z-Scores)
    todays_live_shape = np.array([-1.5, -1.6, -1.4, -1.2, -1.1, -0.9, -0.8, -0.8, -0.5, -0.2, 0.1, 0.3, 0.2, 0.4])
    
    candidates = []
    
    # Fast-pass vector segmentation downsampling to prevent RAM exhaustion
    grouped = df.groupby('stock_id')
    for stock_id, group in grouped:
        z_scores = group['price_z_score'].values
        dates = group['date'].values
        
        # Step in intervals of 3 to compress memory matrix density
        for i in range(0, len(z_scores) - 13, 3):
            window = z_scores[i:i+14]
            if len(window) == 14:
                # Fast linear distance check to rank viability instantly
                base_distance = np.sum(np.abs(window - todays_live_shape))
                candidates.append({
                    'stock_id': stock_id,
                    'date': dates[i+13],
                    'window': window,
                    'fast_dist': base_distance
                })
                
    # Sort candidates by basic proximity and isolate the top 500 rows to process via DTW
    candidate_df = pd.DataFrame(candidates).sort_values('fast_dist').head(500)
    print(f"Memory Safe: Filtered down to {len(candidate_df)} high-probability matches for DTW analysis.")
    
    # Compute precise Dynamic Time Warping ONLY on the filtered candidate subset
    dtw_results = []
    for _, row in candidate_df.iterrows():
        dtw_dist = dtw(todays_live_shape, row['window'])
        dtw_results.append({
            'stock_id': row['stock_id'],
            'date': row['date'],
            'dtw_distance': dtw_dist
        })
        
    # Isolate our final top 10 historical precedents
    final_matches = pd.DataFrame(dtw_results).sort_values('dtw_distance').head(10)
    
    print("\n🎉 CHAOS ENGINE MATRIX RESULTS (TOP 10 DTW MATCHES):")
    print("==================================================================")
    print(final_matches.to_string(index=False))
    print("==================================================================")
    
    # Save these exact real-time matches into a temp table for the Evaluator step
    final_matches.to_sql("active_runtime_matches", conn, if_exists="replace", index=False)
    
    conn.close()

if __name__ == "__main__":
    main()
