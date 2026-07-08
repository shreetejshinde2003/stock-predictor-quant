import sqlite3
import pandas as pd
import numpy as np
import json

def main():
    conn = sqlite3.connect("market_memory.db")
    
    try:
        # Pull the actual live matches produced by the Chaos Engine
        matches = pd.read_sql_query("SELECT * FROM active_runtime_matches", conn)
    except Exception:
        print("❌ No active runtime matches found. Please execute chaos_engine.py first!")
        return

    outcomes = []
    target_gain = 0.02  # +2% target
    stop_loss = 0.01    # -1% protection cushion
    
    print(f"Evaluating the 3-day forward runtime performance for {len(matches)} historical precedents...\n")
    
    for _, row in matches.iterrows():
        table = row['stock_id']
        match_date = row['date']
        
        # Select the entry day close plus the subsequent 3 trading days
        query = f"""
            SELECT date, close FROM [{table}] 
            WHERE date >= '{match_date}' 
            ORDER BY date ASC LIMIT 4
        """
        price_data = pd.read_sql_query(query, conn)
        
        if len(price_data) == 4:
            entry_price = price_data['close'].iloc[0]
            future_prices = price_data['close'].iloc[1:4].values
            
            # Compute real historic price fluctuations
            percentage_moves = (future_prices - entry_price) / entry_price
            max_move = np.max(percentage_moves)
            min_move = np.min(percentage_moves)
            final_move = percentage_moves[-1]
            
            # Risk/Reward execution logic evaluation
            if min_move <= -stop_loss and max_move < target_gain:
                success = 0  # Hit stop loss first
            elif max_move >= target_gain:
                success = 1  # Hit profit target smoothly
            else:
                success = 1 if final_move > 0 else 0 # Stagnant capital evaluation
                
            outcomes.append({
                'return': final_move,
                'success': success
            })

    if not outcomes:
        print("❌ Missing subsequent tracking runway data rows in database historical files.")
        conn.close()
        return
        
    # Compute Probability Distribution Outputs
    total = len(outcomes)
    wins = sum([t['success'] for t in outcomes])
    avg_ret = np.mean([t['return'] for t in outcomes])
    win_rate = (wins / total) * 100
    
    signal = "BUY" if win_rate >= 60 else "SELL" if win_rate <= 40 else "HOLD (STAGNANT)"
    
    final_output = {
        "Trade_Signal": signal,
        "Probability_Of_Success": f"{win_rate:.1f}%",
        "Expected_Average_Return": f"{avg_ret * 100:.2f}%",
        "Historical_Precedents_Evaluated": total
    }
    
    print("--- INTEGRATED PROBABILITY MATRIX OUTPUT ---")
    print(json.dumps(final_output, indent=4))
    
    conn.close()

if __name__ == "__main__":
    main()
