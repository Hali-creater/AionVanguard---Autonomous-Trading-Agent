import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from queue import Queue
import threading
from typing import Any

from autonomous_trading_agent.strategy.trading_strategy import CombinedStrategy
from autonomous_trading_agent.risk_management.risk_manager import RiskManager
from autonomous_trading_agent.broker_integration.alpaca_integration import AlpacaIntegration

class TradingAgent:
    """
    The core trading agent. It runs in a separate thread and communicates
    with the UI via a message queue.
    """
    def __init__(self, config: dict, message_queue: Queue):
        self.config = config
        self.message_queue = message_queue
        self.is_running = threading.Event()
        self.thread = None

        self.strategy = CombinedStrategy()

        if self.config['broker'] == 'Alpaca':
            # In a real app, you would pass API keys from config to the integration
            self.broker = AlpacaIntegration()
        else:
            self._send_message("log", f"Broker '{self.config['broker']}' is not yet supported.")
            raise ValueError(f"Broker '{self.config['broker']}' is not yet supported.")

        self.risk_manager = RiskManager(
            account_balance=self.config['initial_balance'],
            risk_per_trade_percentage=self.config['risk_per_trade'] / 100,
            daily_risk_limit_percentage=0.05 # This could be part of the config
        )
        self._send_message("log", "Agent initialized successfully.")

    def _send_message(self, msg_type: str, data: Any):
        """Puts a message onto the queue for the UI to process."""
        self.message_queue.put({"type": msg_type, "data": data})

    def start(self):
        """Starts the trading loop in a new background thread."""
        if self.thread and self.thread.is_alive():
            self._send_message("log", "Agent is already running.")
            return

        self._send_message("log", "Agent starting...")
        self.is_running.set()
        self.thread = threading.Thread(target=self.run_trading_loop, daemon=True)
        self.thread.start()
        self._send_message("status_update", "Running")

    def stop(self):
        """Signals the trading loop to stop."""
        if not self.is_running.is_set():
            self._send_message("log", "Agent is already stopped.")
            return

        self._send_message("log", "Agent stopping...")
        self.is_running.clear()
        self._send_message("status_update", "Stopped")

    def run_trading_loop(self):
        """The main loop where the agent fetches data, gets signals, and acts."""
        self._send_message("log", "Trading loop thread started.")

        open_positions = pd.DataFrame(columns=['Symbol', 'Quantity', 'Side', 'Entry Price', 'Current Price', 'Unrealized P/L', 'Stop Loss', 'Take Profit', 'Entry Time'])

        while self.is_running.is_set():
            for symbol in self.config['symbols']:
                if not self.is_running.is_set():
                    break

                self._send_message("log", f"--- Processing symbol: {symbol} ---")
                try:
                    # NOTE: Hardcoding the end_date to a fixed, recent date.
                    # This is a workaround for running the agent on a system with a future clock,
                    # which would cause data fetching to fail as there's no data for future dates.
                    # In a real production environment, this should be datetime.now().
                    end_date = datetime(2023, 9, 22)
                    start_date = end_date - timedelta(days=3)
                    historical_data = self.broker.fetch_historical_data(symbol, '1Min', start_date.isoformat(), end_date.isoformat())

                    if historical_data.empty:
                        self._send_message("log", f"Could not fetch historical data for {symbol}.")
                        continue

                    self._send_message("log", f"Fetched {len(historical_data)} data points for {symbol}.")
                    signal = self.strategy.generate_signal(historical_data)
                    self._send_message("log", f"Signal for {symbol}: {signal}")

                    # Simplified execution logic
                    if signal in ['BUY', 'SELL']:
                        if not self.risk_manager.check_daily_risk_limit():
                            self._send_message("log", "Daily risk limit reached. Halting trades.")
                            self.stop()
                            break

                        entry_price = historical_data['close'].iloc[-1]
                        stop_loss_price = entry_price * (1 - 0.02) if signal == 'BUY' else entry_price * (1 + 0.02)
                        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss_price)
                        take_profit_price = self.risk_manager.determine_take_profit(entry_price, stop_loss_price, self.config['risk_reward_ratio'])

                        if position_size > 0:
                            self._send_message("log", f"SIMULATING {signal} for {position_size:.2f} shares of {symbol} at {entry_price:.2f}")
                            new_position = pd.DataFrame([{'Symbol': symbol, 'Quantity': position_size, 'Side': signal, 'Entry Price': entry_price, 'Current Price': entry_price, 'Unrealized P/L': 0.0, 'Stop Loss': stop_loss_price, 'Take Profit': take_profit_price, 'Entry Time': datetime.now()}])
                            open_positions = pd.concat([open_positions, new_position], ignore_index=True)
                            self._send_message("position_update", open_positions.to_dict('records'))

                except Exception as e:
                    self._send_message("log", f"An error occurred while processing {symbol}: {e}")
                    logging.error(f"Error processing {symbol}: {e}", exc_info=True)

            # Simplified time-based exit logic
            if not open_positions.empty:
                indices_to_close = [
                    idx for idx, pos in open_positions.iterrows()
                    if (datetime.now() - pos['Entry Time']) > timedelta(minutes=self.config['time_based_exit'])
                ]
                if indices_to_close:
                    for idx in indices_to_close:
                         self._send_message("log", f"Time-based exit for {open_positions.loc[idx, 'Symbol']}.")
                    open_positions = open_positions.drop(indices_to_close).reset_index(drop=True)
                    self._send_message("position_update", open_positions.to_dict('records'))

            self._send_message("log", "Loop finished. Waiting for next 60s iteration...")
            # This sleep is non-blocking for the UI as it's in a separate thread.
            # It yields control, allowing the stop event to be checked.
            self.is_running.wait(60)

        self._send_message("log", "Trading loop has been terminated.")
