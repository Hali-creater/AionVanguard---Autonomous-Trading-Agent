import streamlit as st
import pandas as pd
import time
import logging
from queue import Queue, Empty
from datetime import datetime

from autonomous_trading_agent.agent import TradingAgent
from autonomous_trading_agent.risk_management.risk_manager import RiskManager

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="AionVanguard - Autonomous Trading Agent")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Session State Initialization ---
# We store the agent instance and message queue in the session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = Queue()
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = "Stopped"
if 'logs' not in st.session_state:
    st.session_state.logs = ["Welcome to AionVanguard! Configure your agent and click Start."]
if 'positions' not in st.session_state:
    st.session_state.positions = pd.DataFrame(columns=['Symbol', 'Quantity', 'Side', 'Entry Price', 'Current Price', 'Unrealized P/L', 'Stop Loss', 'Take Profit', 'Entry Time'])
if 'account_balance' not in st.session_state:
    st.session_state.account_balance = 10000.0

# --- UI Callbacks ---
def add_log(message):
    """Adds a message to the log display in the UI."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {message}")
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop()

def start_agent_callback():
    """Callback to start the trading agent."""
    if not st.session_state.api_key or not st.session_state.api_secret:
        st.error("API Key and Secret must be provided.")
        return

    add_log("User requested to start the agent.")

    config = {
        "broker": st.session_state.broker_select,
        "api_key": st.session_state.api_key,
        "api_secret": st.session_state.api_secret,
        "symbols": [s.strip().upper() for s in st.session_state.symbols.split(',')],
        "initial_balance": st.session_state.initial_balance,
        "risk_per_trade": st.session_state.risk_per_trade,
        "risk_reward_ratio": st.session_state.risk_reward_ratio,
        "time_based_exit": st.session_state.time_based_exit,
    }

    try:
        # Create a new agent instance and start it. It will run in a background thread.
        st.session_state.agent = TradingAgent(config, st.session_state.message_queue)
        st.session_state.agent.start()
    except Exception as e:
        add_log(f"Failed to start agent: {e}")
        st.session_state.agent_status = "Stopped"

def stop_agent_callback():
    """Callback to stop the trading agent."""
    if st.session_state.agent:
        st.session_state.agent.stop()
    else:
        add_log("Agent is not running, nothing to stop.")

# --- UI Layout ---
st.title("🚀 AionVanguard - Trading Agent Dashboard")

with st.sidebar:
    # Configuration and controls are defined here as before
    st.header("Agent Configuration")
    st.selectbox('Select Broker', ('Alpaca',), key='broker_select', help="Currently only Alpaca is implemented.")
    st.text_input("Alpaca API Key", type="password", key='api_key')
    st.text_input("Alpaca API Secret", type="password", key='api_secret')
    st.info("Your API keys are stored securely in the app's memory for this session only.")
    st.text_input("Symbols (comma-separated)", value="AAPL,TSLA", key='symbols')

    st.subheader("Risk Management")
    st.number_input("Initial Account Balance", value=10000.0, step=1000.0, key='initial_balance')
    st.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0, 0.1, key='risk_per_trade')
    st.number_input("Risk/Reward Ratio (1:X)", min_value=0.1, value=3.0, step=0.1, key='risk_reward_ratio')

    st.subheader("Strategy Settings")
    st.number_input("Time-based Exit (minutes)", min_value=1, value=5, step=1, key='time_based_exit')

    st.header("Agent Controls")
    col1, col2 = st.columns(2)
    with col1:
        st.button("▶️ Start Agent", on_click=start_agent_callback, width='stretch', disabled=(st.session_state.agent_status == "Running"))
    with col2:
        st.button("⏹️ Stop Agent", on_click=stop_agent_callback, width='stretch', disabled=(st.session_state.agent_status != "Running"))

# --- Main Dashboard Area ---
status_color = "green" if st.session_state.agent_status == "Running" else "red"
st.header(f"Status: :{status_color}[{st.session_state.agent_status}]")

tab1, tab2 = st.tabs(["📊 Live Dashboard", "📝 Activity Log"])

with tab1:
    st.subheader("Account Balance")
    st.metric("Current Balance", f"${st.session_state.account_balance:,.2f}")
    st.subheader("Open Positions")
    positions_placeholder = st.empty()
    positions_placeholder.dataframe(st.session_state.positions, width='stretch')

with tab2:
    st.subheader("Activity Log")
    log_placeholder = st.empty()
    log_placeholder.text_area("Logs", value="\n".join(st.session_state.logs), height=400, key="log_output")

# --- Message Processing Loop ---
# This is the new, non-blocking way to update the UI.
# It runs on every script rerun (e.g., when a user interacts with a widget).
while not st.session_state.message_queue.empty():
    try:
        message = st.session_state.message_queue.get_nowait()
        msg_type = message.get("type")
        data = message.get("data")

        if msg_type == "log":
            add_log(data)
        elif msg_type == "status_update":
            st.session_state.agent_status = data
        elif msg_type == "position_update":
            st.session_state.positions = pd.DataFrame(data)

    except Empty:
        break # Queue is empty, exit the loop
    except Exception as e:
        logging.error(f"Error processing message from queue: {e}")

# To keep the UI live, we can use a small sleep and rerun.
# This is more efficient than the old blocking loop.
if st.session_state.agent_status == "Running":
    time.sleep(1)
    st.rerun()
