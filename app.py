import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Algothink Chaos Engine Dashboard", page_icon="📈", layout="wide")

# Force custom slate dark theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffcc; font-size: 38px; font-weight: bold; }
    .stAlert { background-color: #1e2633; border-radius: 8px; border: 1px solid #384d70; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Algothink Chaos Engine — Local Prototype View")
st.markdown("---")

SIGNALS_FILE = "signals.json"
LEDGER_FILE = "lesson_ledger.json"

# Read signals
if os.path.exists(SIGNALS_FILE):
    with open(SIGNALS_FILE, "r") as f:
        signals_data = json.load(f)
    df = pd.DataFrame(signals_data)
else:
    df = pd.DataFrame()

# Read ledger memory
if os.path.exists(LEDGER_FILE):
    with open(LEDGER_FILE, "r") as f:
        ledger_data = json.load(f)
    toxic_count = len(ledger_data.get("toxic_shapes", []))
    trap_count = len(ledger_data.get("stagnation_shapes", []))
else:
    toxic_count, trap_count = 0, 0

# Metrics Banner
col1, col2, col3 = st.columns(3)
col1.metric(label="Scanner Status", value="ACTIVE (5 Tickers)")
col2.metric(label="Memorized Stop-Loss Traumas", value=toxic_count)
col3.metric(label="Memorized Stagnation Traps", value=trap_count)

st.markdown("### 📡 Current Active Scanning Signals")

if not df.empty:
    # Reorder columns for clean display
    display_df = df[["date", "ticker", "entry_price", "target", "stop_loss", "verdict", "reason"]]
    st.dataframe(display_df, use_container_width=True)
    
    # Visual geometric chart selection
    st.markdown("---")
    st.markdown("### 📊 Live Z-Score Shape Visualizer")
    selected_ticker = st.selectbox("Select a ticker to see its 14-day lookback shape:", df["ticker"].unique())
    
    ticker_row = df[df["ticker"] == selected_ticker].iloc[0]
    shape_data = ticker_row["shape"]
    
    chart_df = pd.DataFrame(shape_data, columns=["Z-Score Price Trend"])
    st.line_chart(chart_df)
else:
    st.info("No active signals file found. Run the Morning Hunter script first.")
