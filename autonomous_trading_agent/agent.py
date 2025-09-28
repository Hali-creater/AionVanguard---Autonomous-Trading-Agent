import time
import logging
from datetime import datetime, timedelta
from queue import Queue
import threading
from typing import Any

from autonomous_trading_agent.strategy.trading_strategy import BaseTradingStrategy
from autonomous_trading_agent.risk_management.risk_manager import RiskManager
from autonomous_trading_agent.data_fetching.data_manager import DataManager
from autonomous_trading_agent.broker_integration.broker_factory import create_broker
from autonomous_trading_agent.portfolio.portfolio_manager import PortfolioManager

class TradingAgent:
    """
    The core trading agent, which acts as a controller to orchestrate the
    different components of the trading system. It runs in a separate thread.
    """
    def __init__(self, config: dict, message_queue: Queue, strategy: BaseTradingStrategy):
        self.config = config
        self.message_queue = message_queue
        self.strategy = strategy
        self.is_running = threading.Event()
        self.thread = None

        self._send_message("log", "Initializing agent components...")

        # Initialize all the core components
        self.data_manager = DataManager(config)
        self.broker = create_broker(config)
        if not self.broker:
            self._send_message("log", "Failed to initialize broker. Agent cannot start.")
            raise ValueError("Broker initialization failed.")

        self.risk_manager = RiskManager(
            account_balance=self.config.get('initial_balance', 100000),
            risk_per_trade_percentage=self.config.get('risk_per_trade', 1.0) / 100
        )

        self.portfolio_manager = PortfolioManager(
            config=self.config,
            broker=self.broker,
            risk_manager=self.risk_manager,
            message_queue=self.message_queue
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
        self.thread = threading.Thread(target=self._trading_loop, daemon=True)
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

    def _trading_loop(self):
        """
        The main loop where the agent orchestrates fetching data, generating
        signals, and managing the portfolio.
        """
        self._send_message("log", "Trading loop thread started.")

        while self.is_running.is_set():
            try:
                self._send_message("log", "--- Starting new trading cycle ---")

                # 1. Process signals for each symbol
                for symbol in self.config['symbols']:
                    if not self.is_running.is_set(): break

                    self._send_message("log", f"Processing symbol: {symbol}")

                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30) # Lookback for indicators

                    historical_data = self.data_manager.fetch_historical_data(
                        symbol, '1Min', start_date.isoformat(), end_date.isoformat()
                    )

                    if historical_data.empty:
                        self._send_message("log", f"No data for {symbol}, skipping.")
                        continue

                    signal = self.strategy.generate_signal(historical_data)
                    self._send_message("log", f"Signal for {symbol}: {signal}")

                    # Let the portfolio manager handle the signal
                    continue_trading = self.portfolio_manager.process_signal(signal, symbol, historical_data)

                    if not continue_trading:
                        self._send_message("log", "A risk limit was hit. Stopping agent.")
                        self.stop()
                        break

                # 2. Manage all open positions (e.g., check for exits)
                if self.is_running.is_set():
                    self.portfolio_manager.manage_open_positions()

                self._send_message("log", "Cycle finished. Waiting for next iteration...")
                self.is_running.wait(self.config.get("trading_interval", 60))

            except Exception as e:
                self._send_message("log", f"An unexpected error occurred in the trading loop: {e}")
                logging.error(f"Trading loop error: {e}", exc_info=True)
                self.is_running.wait(60) # Wait before retrying

        self._send_message("log", "Trading loop has been terminated.")
