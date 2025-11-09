import streamlit as st
import pandas as pd
import alpaca_trade_api as tradeapi
import finnhub
import os
import time

# --- Environment Variables & API Initialization ---
ALPACA_API_KEY_ID = os.getenv("ALPACA_API_KEY_ID")
ALPACA_API_SECRET_KEY = os.getenv("ALPACA_API_SECRET_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Alpaca API
api = tradeapi.REST(ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY, base_url='https://paper-api.alpaca.markets')

# Finnhub API
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# --- Trading Logic ---
def fetch_historical_data(symbol, resolution, from_ts, to_ts):
    """Fetches historical data from Finnhub."""
    return finnhub_client.stock_candles(symbol, resolution, from_ts, to_ts)

def generate_signal(close_prices):
    """Generates a trading signal based on a simple moving average crossover."""
    if len(close_prices) < 50:
        return "HOLD"

    short_sma = pd.Series(close_prices).rolling(window=20).mean().iloc[-1]
    long_sma = pd.Series(close_prices).rolling(window=50).mean().iloc[-1]

    if short_sma > long_sma:
        return "BUY"
    elif short_sma < long_sma:
        return "SELL"
    else:
        return "HOLD"

def calculate_position_size(entry_price, stop_loss_price, account_balance, risk_per_trade):
    """Calculates the position size for a trade."""
    risk_amount = account_balance * (risk_per_trade / 100)
    price_difference = abs(entry_price - stop_loss_price)
    return risk_amount / price_difference

def place_order(symbol, qty, side, order_type, time_in_force):
    """Places an order with Alpaca."""
    api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type=order_type,
        time_in_force=time_in_force,
    )

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("AionVanguard - Trading Agent Dashboard")

# --- Configuration ---
st.sidebar.header("Configuration")
symbols = st.sidebar.text_input("Symbols (comma-separated)", "AAPL,TSLA")
risk_per_trade = st.sidebar.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0, 0.1)
risk_reward_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 3.0, 0.1)
time_based_exit = st.sidebar.slider("Time-based Exit (minutes)", 1, 60, 5, 1)

start_button = st.sidebar.button("Start Agent")
stop_button = st.sidebar.button("Stop Agent")

# --- Dashboard ---
log_container = st.container()
log_container.header("Activity Log")
log_area = log_container.empty()

position_container = st.container()
position_container.header("Open Positions")
position_area = position_container.empty()

if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'positions' not in st.session_state:
    st.session_state.positions = []
if 'agent_running' not in st.session_state:
    st.session_state.agent_running = False

def run_trading_loop():
    """The main trading loop for the agent."""
    if not st.session_state.agent_running:
        return

    for symbol in symbols.split(','):
        try:
            # Fetch data
            now = int(pd.Timestamp.now().timestamp())
            then = int((pd.Timestamp.now() - pd.Timedelta(days=60)).timestamp())
            candles = fetch_historical_data(symbol, "D", then, now)

            # Generate signal
            signal = generate_signal(candles['c'])
            st.session_state.logs.append(f"[{symbol}] Signal: {signal}")

            if signal != "HOLD":
                # Get account info and calculate position size
                account = api.get_account()
                balance = float(account.equity)
                entry_price = candles['c'][-1]
                stop_loss_price = entry_price * (1 - 0.02) if signal == "BUY" else entry_price * (1 + 0.02)
                position_size = calculate_position_size(entry_price, stop_loss_price, balance, risk_per_trade)

                # Place order
                place_order(symbol, position_size, signal.lower(), 'market', 'gtc')
                st.session_state.logs.append(f"[{symbol}] Placed {signal} order for {position_size} shares.")

        except Exception as e:
            st.session_state.logs.append(f"[{symbol}] Error: {e}")

    # Update positions
    positions = api.list_positions()
    st.session_state.positions = [{"symbol": p.symbol, "qty": p.qty, "side": p.side, "avg_entry_price": p.avg_entry_price} for p in positions]

    # Rerun the script to update the UI
    time.sleep(60)
    st.rerun()

if start_button:
    st.session_state.agent_running = True
    st.session_state.logs.append("Agent started.")

if stop_button:
    st.session_state.agent_running = False
    st.session_state.logs.append("Agent stopped.")

log_area.text_area("Logs", "\n".join(st.session_state.logs), height=300)
position_area.dataframe(st.session_state.positions)

if st.session_state.agent_running:
    run_trading_loop()
