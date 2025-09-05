import streamlit as st
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from autonomous_trading_agent.strategy.trading_strategy import CombinedStrategy
from autonomous_trading_agent.risk_management.risk_manager import RiskManager
from autonomous_trading_agent.broker_integration.alpaca_integration import AlpacaIntegration
from autonomous_trading_agent.broker_integration.binance_integration import BinanceIntegration
from autonomous_trading_agent.broker_integration.interactive_brokers_integration import InteractiveBrokersIntegration
from autonomous_trading_agent.broker_integration.oanda_integration import OandaIntegration
# Import other integrations as they are implemented

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="AionVanguard - Autonomous Trading Agent")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Session State Initialization ---
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = "Stopped"
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'positions' not in st.session_state:
    st.session_state.positions = pd.DataFrame(columns=['Symbol', 'Quantity', 'Side', 'Entry Price', 'Current Price', 'Unrealized P/L', 'Stop Loss', 'Take Profit', 'Entry Time'])
if 'account_balance' not in st.session_state:
    st.session_state.account_balance = 10000.0 # Default
if 'keys_saved' not in st.session_state:
    st.session_state.keys_saved = False

# --- Helper Functions ---
def add_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {message}")
    # Keep logs from getting too long
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop()

# --- Core Agent Logic ---
class TradingAgent:
    def __init__(self, config):
        self.config = config
        self.strategy = CombinedStrategy()
        # Initialize broker integration
        self.broker = self._get_broker_integration(config)

        # Fetch initial account balance from broker
        # For now, we'll use the user-provided initial balance
        st.session_state.account_balance = self.config['initial_balance']

        self.risk_manager = RiskManager(
            account_balance=st.session_state.account_balance,
            risk_per_trade_percentage=self.config['risk_per_trade'] / 100,
            daily_risk_limit_percentage=0.05 # Placeholder, can be added to UI
        )
        add_log("Agent initialized successfully.")

    def _get_broker_integration(self, config):
        broker_name = config['broker']
        api_key = config.get('api_key')
        api_secret = config.get('api_secret')

        if broker_name == 'Alpaca':
            if not api_key or not api_secret:
                raise ValueError("Alpaca API Key and Secret are required.")
            return AlpacaIntegration(api_key=api_key, api_secret=api_secret)
        else:
            add_log(f"Broker '{broker_name}' is not yet supported.")
            raise ValueError(f"Broker '{broker_name}' is not yet supported.")

    def run_trading_loop(self):
        add_log("Trading loop started.")

        while st.session_state.agent_status == "Running":
            for symbol in self.config['symbols']:
                add_log(f"--- Processing symbol: {symbol} ---")
                try:
                    # 1. Fetch Data
                    # For scalping, we fetch recent 1-minute data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=3) # Fetch last 3 days of 1-minute data
                    # Note: Alpaca requires dates in ISO 8601 format
                    historical_data = self.broker.fetch_historical_data(symbol, '1Min', start_date.isoformat(), end_date.isoformat())

                    if historical_data.empty:
                        add_log(f"Could not fetch historical data for {symbol}.")
                        continue

                    add_log(f"Fetched {len(historical_data)} data points for {symbol}.")

                    # 2. Generate Signal
                    signal = self.strategy.generate_signal(historical_data)
                    add_log(f"Signal for {symbol}: {signal}")

                    # 3. Act on Signal
                    # This is a simplified logic. A real agent would manage existing positions.
                    if signal == 'BUY' or signal == 'SELL':
                        if not self.risk_manager.check_daily_risk_limit():
                            add_log("Daily risk limit reached. Halting trades for the day.")
                            st.session_state.agent_status = "Stopped"
                            break

                        # Simplified execution logic
                        entry_price = historical_data['close'].iloc[-1]
                        # Example: stop loss is 2% below/above entry
                        stop_loss_price = entry_price * 0.98 if signal == 'BUY' else entry_price * 1.02

                        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss_price)
                        take_profit_price = self.risk_manager.determine_take_profit(entry_price, stop_loss_price, self.config['risk_reward_ratio'])

                        if position_size > 0:
                            add_log(f"Executing {signal} for {position_size:.2f} shares of {symbol} at {entry_price:.2f}, SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}")
                            # In a real app, you'd call self.broker.place_order(...)
                            # For this simulation, we'll just log it and add to positions
                            new_position = pd.DataFrame([{
                                'Symbol': symbol,
                                'Quantity': position_size,
                                'Side': signal,
                                'Entry Price': entry_price,
                                'Current Price': entry_price,
                                'Unrealized P/L': 0.0,
                                'Stop Loss': stop_loss_price,
                                'Take Profit': take_profit_price,
                                'Entry Time': datetime.now()
                            }])
                            st.session_state.positions = pd.concat([st.session_state.positions, new_position], ignore_index=True)

                except Exception as e:
                    add_log(f"An error occurred while processing {symbol}: {e}")

            # --- Time-based Exit Logic ---
            if not st.session_state.positions.empty:
                positions_to_close = []
                for index, position in st.session_state.positions.iterrows():
                    entry_time = position['Entry Time']
                    if (datetime.now() - entry_time) > timedelta(minutes=self.config['time_based_exit']):
                        positions_to_close.append(index)
                        add_log(f"Closing position for {position['Symbol']} due to time-based exit.")

                if positions_to_close:
                    st.session_state.positions = st.session_state.positions.drop(positions_to_close).reset_index(drop=True)


            if st.session_state.agent_status != "Running":
                break

            add_log("Loop finished. Waiting for next iteration...")
            # In a real app, you'd have a proper scheduler. Here we just sleep.
            # We also need to yield control to Streamlit to update the UI.
            for i in range(60):
                if st.session_state.agent_status != "Running": break
                time.sleep(1)

        add_log("Trading loop has been terminated.")

# --- UI Callbacks ---
def save_keys():
    if st.session_state.api_key and st.session_state.api_secret:
        st.session_state.keys_saved = True
        st.info("API keys saved for the session.")
    else:
        st.error("Please provide both API Key and Secret.")

def start_agent():
    if not st.session_state.get('keys_saved', False):
        st.error("API Keys must be saved before starting the agent.")
        return

    st.session_state.agent_status = "Running"
    add_log("User requested to start the agent.")

    # Create config from UI
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
        st.session_state.agent = TradingAgent(config)
        # This is a simplified way to run the loop. A robust app might use threading.
        st.session_state.agent.run_trading_loop()
    except Exception as e:
        add_log(f"Failed to start agent: {e}")
        st.session_state.agent_status = "Stopped"

def stop_agent():
    st.session_state.agent_status = "Stopped"
    st.session_state.agent = None
    add_log("User requested to stop the agent.")

# --- UI Layout ---
st.title("🚀 AionVanguard - Trading Agent Dashboard")

with st.sidebar:
    st.header("Agent Configuration")
    st.selectbox('Select Broker', ('Alpaca', 'Binance', 'Interactive Brokers', 'OANDA'), key='broker_select', on_change=lambda: st.session_state.update(keys_saved=False))

    selected_broker = st.session_state.broker_select

    if selected_broker != 'Alpaca':
        st.warning(f"{selected_broker} integration is not yet implemented. The agent will not work with this broker.")

    # Note on Security: API keys are handled via Streamlit's session state.
    # In a deployed Streamlit Cloud environment, this state is managed on the server-side
    # and is not exposed to the client's browser. The connection is secured with HTTPS.
    # This is a standard and secure way to handle secrets in Streamlit applications.
    st.text_input(f"{selected_broker} API Key", type="password", key='api_key', on_change=lambda: st.session_state.update(keys_saved=False))
    st.text_input(f"{selected_broker} API Secret", type="password", key='api_secret', on_change=lambda: st.session_state.update(keys_saved=False))

    st.button("Save Keys", on_click=save_keys, use_container_width=True)
    if st.session_state.get('keys_saved', False):
        st.success("API keys are saved for this session.")
    st.info("Your API keys are stored securely in the app's memory for this session only and are not saved elsewhere.")
    st.text_input("Symbols (comma-separated)", value="AAPL,TSLA", key='symbols')

    st.subheader("Risk Management")
    st.number_input("Initial Account Balance", value=10000.0, step=1000.0, key='initial_balance')
    st.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0, 0.1, key='risk_per_trade')
    st.number_input("Risk/Reward Ratio (1:X)", min_value=0.1, value=3.0, step=0.1, key='risk_reward_ratio', help="The reward part of the risk/reward ratio. E.g., 3.0 for a 1:3 ratio.")

    st.subheader("Strategy Settings")
    st.number_input("Time-based Exit (minutes)", min_value=1, value=5, step=1, key='time_based_exit', help="Close position after this many minutes if not closed by SL/TP.")

    st.subheader("Position Size Calculator")
    try:
        temp_risk_manager = RiskManager(
            account_balance=st.session_state.initial_balance,
            risk_per_trade_percentage=st.session_state.risk_per_trade / 100,
            daily_risk_limit_percentage=0.05 # This is a placeholder, not used in calculation
        )
        entry_price_calc = st.number_input("Hypothetical Entry Price", min_value=0.01, value=100.0, step=1.0, key='entry_price_calc')
        stop_loss_calc = st.number_input("Hypothetical Stop Loss Price", min_value=0.01, value=98.0, step=1.0, key='stop_loss_calc')

        calculated_size = temp_risk_manager.calculate_position_size(entry_price_calc, stop_loss_calc)

        st.metric("Calculated Position Size (shares)", f"{calculated_size:.2f}")
        st.caption(f"Based on {st.session_state.risk_per_trade}% risk on an account of ${st.session_state.initial_balance:,.2f}.")
    except Exception as e:
        st.error(f"Error in calculator: {e}")


    st.header("Agent Controls")
    col1, col2 = st.columns(2)
    with col1:
        st.button("▶️ Start Agent", on_click=start_agent, use_container_width=True, disabled=(st.session_state.agent_status == "Running" or not st.session_state.get('keys_saved', False)))
    with col2:
        st.button("⏹️ Stop Agent", on_click=stop_agent, use_container_width=True, disabled=(st.session_state.agent_status != "Running"))

status_color = "red" if st.session_state.agent_status == "Stopped" else "green"
st.header(f"Status: :{status_color}[{st.session_state.agent_status}]")

tab1, tab2 = st.tabs(["📊 Live Dashboard", "📝 Activity Log"])

with tab1:
    st.subheader("Account Balance")
    st.metric("Current Balance", f"${st.session_state.account_balance:,.2f}")

    st.subheader("Open Positions")
    st.dataframe(st.session_state.positions, use_container_width=True)

with tab2:
    st.subheader("Activity Log")
    st.text_area("Logs", value="\n".join(st.session_state.logs), height=400, key="log_output")

# This is a hack to make the log update more frequently on screen
if st.session_state.agent_status == "Running":
    time.sleep(1)
    st.rerun()
