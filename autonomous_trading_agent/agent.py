import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from queue import Queue
import threading
from typing import Any

from autonomous_trading_agent.strategy.trading_strategy import CombinedStrategy
from autonomous_trading_agent.risk_management.risk_manager import RiskManager
import finnhub
from autonomous_trading_agent.data_fetching.finnhub_data_fetcher import FinnhubDataFetcher
from autonomous_trading_agent.data_fetching.yfinance_data_fetcher import YFinanceDataFetcher
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

        # The data fetcher is now separate from the broker for execution
        self.primary_data_fetcher = FinnhubDataFetcher(api_key=self.config.get('finnhub_api_key'))
        self.fallback_data_fetcher = YFinanceDataFetcher()

        if self.config['broker'] == 'Alpaca':
            # The broker is still used for trade execution
            self.broker = AlpacaIntegration(
                api_key=self.config.get('alpaca_api_key'),
                api_secret=self.config.get('alpaca_api_secret')
            )
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

        while self.is_running.is_set():
            # Fetch account details at the start of each loop
            account_balance = self.broker.get_account_balance()
            if account_balance is not None:
                self.risk_manager.update_account_balance(account_balance)
                self._send_message("account_balance_update", account_balance)

            open_positions = self.broker.get_open_positions()
            self._send_message("position_update", open_positions.to_dict('records'))
            for symbol in self.config['symbols']:
                if not self.is_running.is_set():
                    break

                self._send_message("log", f"--- Processing symbol: {symbol} ---")
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30) # Fetch more data for better indicator calculation

                    try:
                        historical_data = self.primary_data_fetcher.fetch_historical_data(symbol, '1Min', start_date.isoformat(), end_date.isoformat())
                    except finnhub.FinnhubAPIException as e:
                        if e.status_code == 403:
                            self._send_message("log", f"Finnhub API key lacks permissions for {symbol}. Falling back to yfinance.")
                            historical_data = self.fallback_data_fetcher.fetch_historical_data(symbol, '1Min', start_date.isoformat(), end_date.isoformat())
                        else:
                            raise e # Re-raise other API errors

                    if historical_data.empty:
                        self._send_message("log", f"Could not fetch historical data for {symbol} from any source.")
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
                            quantity = position_size if signal == 'BUY' else -position_size
                            order_id = self.broker.place_order(
                                symbol=symbol,
                                order_type='market',
                                quantity=quantity,
                                stop_loss=stop_loss_price,
                                take_profit=take_profit_price
                            )
                            if order_id:
                                self._send_message("log", f"Successfully placed {signal} order for {position_size:.2f} shares of {symbol}. Order ID: {order_id}")
                                # Immediately fetch and send updated positions to the UI for responsiveness
                                self._send_message("log", "Fetching updated positions after order placement...")
                                updated_positions = self.broker.get_open_positions()
                                self._send_message("position_update", updated_positions.to_dict('records'))
                            else:
                                self._send_message("log", f"Failed to place {signal} order for {symbol}.")

                except Exception as e:
                    self._send_message("log", f"An error occurred while processing {symbol}: {e}")
                    logging.error(f"Error processing {symbol}: {e}", exc_info=True)

            # Re-implement time-based exit logic with live broker data
            if not open_positions.empty:
                # Ensure 'entry_time' column is in datetime format
                open_positions['entry_time'] = pd.to_datetime(open_positions['entry_time'], utc=True)

                positions_to_close = open_positions[
                    (datetime.now(pd.Timestamp.utcnow().tz) - open_positions['entry_time']) > timedelta(minutes=self.config['time_based_exit'])
                ]

                for _, position in positions_to_close.iterrows():
                    symbol_to_close = position['symbol']
                    self._send_message("log", f"Time-based exit for {symbol_to_close}. Closing position.")
                    self.broker.close_position(symbol_to_close)

            self._send_message("log", "Loop finished. Waiting for next 60s iteration...")
            # This sleep is non-blocking for the UI as it's in a separate thread.
            # It yields control, allowing the stop event to be checked.
            self.is_running.wait(60)

        self._send_message("log", "Trading loop has been terminated.")
