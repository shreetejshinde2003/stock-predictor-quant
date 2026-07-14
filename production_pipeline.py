import os
import json
import time
import argparse
import datetime
import pytz
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from tslearn.metrics import dtw

# --- CONFIGURATION LABELS ---

NIFTY_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "SBIN.NS", "INFY.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
    "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS",
    "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS",
    "AXISBANK.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "COALINDIA.NS",
    "BAJAJFINSV.NS", "BAJAJ-AUTO.NS", "POWERGRID.NS", "NESTLEIND.NS", "WIPRO.NS",
    "M&M.NS", "IOC.NS", "HAL.NS", "DLF.NS", "ADANIGREEN.NS",
    "TATASTEEL.NS", "SIEMENS.NS", "VBL.NS", "ZOMATO.NS", "PIDILITIND.NS",
    "GRASIM.NS", "SBILIFE.NS", "BEL.NS", "LTIM.NS", "TRENT.NS",
    "INDUSINDBK.NS", "HINDALCO.NS", "BRITANNIA.NS", "TECHM.NS", "EICHERMOT.NS"
]
GRAVEYARD_TICKERS = ["YESBANK.NS", "IDEA.NS", "SUZLON.NS"]

# --- LAYER 1: TIME GATEKEEPER & LOCAL BYPASS ---
def is_market_open_today():
    if os.getenv("LOCAL_QUANT_TEST") == "TRUE":
        print("🛠️ LOCAL TESTING MODE: Bypassing Calendar Gatekeeper.")
        return True

    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.datetime.now(ist).date()
    if today.weekday() >= 5: return False
        
    nse_holidays = [datetime.date(2026, 8, 15), datetime.date(2026, 10, 2), datetime.date(2026, 11, 8)]
    if today in nse_holidays: return False
    return True

# --- LAYER 2: ARMORED IN-MEMORY FETCH ---
def fetch_in_memory_data(tickers, period="5y"):
    df_list = []
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    for ticker in tickers:
        success = False
        for attempt in range(3):
            try:
                data = yf.download(ticker, period=period, session=session, timeout=10, progress=False, auto_adjust=True)
                if data.empty or len(data) < 100:
                    raise ValueError("Insufficient rows returned from API.")
                
                # FIX: Flatten MultiIndex columns if present in newer yfinance versions
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                data = data.dropna()
                vol_col = 'Volume' if 'Volume' in data else 'volume'
                
                rolling_vol = data[vol_col].rolling(window=10).mean()
                data = data[data[vol_col] >= (rolling_vol * 0.20)]
                
                data['ticker'] = ticker
                df_list.append(data)
                success = True
                break
            except Exception as e:
                print(f"⚠️ Attempt {attempt+1} failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        if not success:
            print(f"🚨 Circuit Breaker: Quarantined {ticker}")
            
    return pd.concat(df_list) if df_list else pd.DataFrame()

# --- AUXILIARY: GEOMETRY EXTRACTION ---
def extract_current_shape(df, ticker, days=14):
    ticker_df = df[df['ticker'] == ticker].tail(days)
    close_col = 'Close' if 'Close' in ticker_df else 'close'
    if len(ticker_df) < days: return np.zeros((days, 1))
    
    prices = ticker_df[close_col].values.flatten()
    z_scores = (prices - np.mean(prices)) / (np.std(prices) + 1e-9)
    return z_scores.reshape(-1, 1)

# --- LAYER 3: MORNING HUNTER ---
def run_morning_hunter():
    print("Executing Morning Scan...")
    if not is_market_open_today(): return
        
    nifty_df = fetch_in_memory_data(NIFTY_TICKERS)
    if nifty_df.empty:
        print("🚨 CRITICAL: Master DataFrame is completely empty. Fetching failed.")
        return
    
    if os.path.exists("lesson_ledger.json"):
        with open("lesson_ledger.json", "r") as f: memories = json.load(f)
    else: memories = {"toxic_shapes": [], "stagnation_shapes": []}
        
    signals_output = []
    close_col = 'Close' if 'Close' in nifty_df else 'close'
    
    for ticker in NIFTY_TICKERS:
        try:
            today_shape = extract_current_shape(nifty_df, ticker)
            
            # Filter rows for this specific stock
            ticker_rows = nifty_df[nifty_df['ticker'] == ticker]
            if ticker_rows.empty:
                print(f"❌ Missing filtered data row for {ticker}")
                continue
                
            current_price = float(ticker_rows[close_col].iloc[-1])
            
            verdict = "BUY"
            reason = "Clean Algorithmic Setup"
            
            # Cognitive Feedback Check
            for toxic in memories["toxic_shapes"]:
                if dtw(today_shape, np.array(toxic)) < 0.35:
                    verdict, reason = "REJECTED", "Matches past Stop-Loss trauma."
            for trap in memories["stagnation_shapes"]:
                if dtw(today_shape, np.array(trap)) < 0.35:
                    verdict, reason = "REJECTED", "Matches past Stagnation capital trap."
            
            signals_output.append({
                "date": str(datetime.date.today()),
                "ticker": ticker,
                "entry_price": round(current_price, 2),
                "target": round(current_price * 1.05, 2),
                "stop_loss": round(current_price * 0.97, 2),
                "verdict": verdict,
                "reason": reason,
                "shape": today_shape.flatten().tolist()
            })
            print(f"🎯 Successfully processed {ticker} at ₹{round(current_price, 2)}")
            
        except Exception as e:
            # UNMASKED ERROR: Let the console tell us exactly why it failed
            print(f"❌ Failed processing loop for {ticker}. Error details: {e}")
            
       if not signals_output:
        print("🚨 HUNT FAILED: Zero valid signals were generated.")
        print("🛡️ Existing signals.json has been preserved.")
        raise RuntimeError(
            "Morning Hunt generated zero valid signals. "
            "Refusing to overwrite the previous signal data."
        )

    with open("signals.json", "w") as f:
        json.dump(signals_output, f, indent=4)

    print(
        f"✅ Processing complete. "
        f"Generated {len(signals_output)} signals inside signals.json."
    )

# --- LAYER 4: EVENING AUDITOR ---
def run_evening_auditor():
    print("Executing Evening Audit Analysis...")
    if not is_market_open_today() or not os.path.exists("signals.json"): return
        
    with open("signals.json", "r") as f: active_trades = json.load(f)
    if os.path.exists("lesson_ledger.json"):
        with open("lesson_ledger.json", "r") as f: memories = json.load(f)
    else: memories = {"toxic_shapes": [], "stagnation_shapes": []}
        
    for trade in active_trades:
        if trade["verdict"] == "REJECTED": continue
        ticker = trade["ticker"]
        try:
            live_close = float(yf.Ticker(ticker).fast_info['lastPrice'])
            if live_close < (trade["entry_price"] * 0.50):
                print(f"⚠️ DANGER: {ticker} price seems corrupted. Skipping.")
                continue
        except Exception as e:
            print(f"❌ Auditor could not fetch instant spot price for {ticker}: {e}")
            continue
            
        try:
            trade_runway = yf.download(ticker, start=trade["date"], progress=False)
            if isinstance(trade_runway.columns, pd.MultiIndex):
                trade_runway.columns = trade_runway.columns.get_level_values(0)
            trading_sessions = len(trade_runway)
        except: trading_sessions = 0
        
        if live_close <= trade["stop_loss"]:
            memories["toxic_shapes"].append(trade["shape"])
            trade["verdict"] = "CLOSED (LOSS)"
        elif live_close >= trade["target"]:
            trade["verdict"] = "CLOSED (WIN)"
        elif trading_sessions >= 4:
            memories["stagnation_shapes"].append(trade["shape"])
            trade["verdict"] = "CLOSED (TIME STOP)"
            
    with open("lesson_ledger.json", "w") as f: json.dump(memories, f, indent=4)
    with open("signals.json", "w") as f: json.dump(active_trades, f, indent=4)
    print("✅ Evening audit complete. Memory updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required=True, choices=['hunt', 'audit'])
    args = parser.parse_args()
    
    if args.mode == 'hunt': run_morning_hunter()
    elif args.mode == 'audit': run_evening_auditor()
