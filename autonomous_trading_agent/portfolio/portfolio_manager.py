import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from queue import Queue

from ..broker_integration.base_broker import BaseBroker
from ..risk_management.risk_manager import RiskManager

class PortfolioManager:
    """
    Manages the portfolio, including executing trades based on signals
    and managing open positions.
    """
    def __init__(self, config: Dict, broker: BaseBroker, risk_manager: RiskManager, message_queue: Queue):
        self.config = config
        self.broker = broker
        self.risk_manager = risk_manager
        self.message_queue = message_queue
        self._send_message("log", "PortfolioManager initialized.")

    def _send_message(self, msg_type: str, data: Any):
        """Puts a message onto the queue for the UI to process."""
        self.message_queue.put({"type": msg_type, "data": data})

    def process_signal(self, signal: str, symbol: str, historical_data: pd.DataFrame) -> bool:
        """
        Processes a trading signal and executes a trade if conditions are met.
        Returns False if a risk limit is hit and trading should stop.
        """
        if signal not in ['BUY', 'SELL']:
            return True # Not a signal to act on, continue processing

        open_positions = self.broker.get_open_positions()
        if not open_positions[open_positions['symbol'] == symbol].empty:
            self._send_message("log", f"Position for {symbol} already exists. Skipping new entry signal.")
            return True

        if not self.risk_manager.check_daily_risk_limit():
            self._send_message("log", "Daily risk limit reached. Halting new trades for the day.")
            return False

        entry_price = historical_data['close'].iloc[-1]
        # This stop-loss logic is simplistic; a real strategy should provide this.
        stop_loss_price = entry_price * (1 - 0.02) if signal == 'BUY' else entry_price * (1 + 0.02)

        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss_price)

        if position_size <= 0:
            self._send_message("log", "Calculated position size is zero or less. No trade will be placed.")
            return True

        self._send_message("log", f"Attempting to place {signal} order for {position_size:.4f} of {symbol}.")

        order_details = self.broker.place_order(
            symbol=symbol,
            order_type='market',
            quantity=position_size,
            side=signal.lower(),
        )

        if order_details:
            self._send_message("log", f"Successfully placed order for {symbol}. Order ID: {order_details.get('id')}")
            trade_risk = abs(entry_price - stop_loss_price) * position_size
            self.risk_manager.add_trade_risk(trade_risk)
        else:
            self._send_message("log", f"Failed to place order for {symbol}.")

        return True

    def manage_open_positions(self):
        """
        Periodically checks and updates the status of open positions from the broker.
        """
        try:
            positions = self.broker.get_open_positions()
            if not positions.empty:
                self._send_message("position_update", positions.to_dict('records'))
            else:
                # Send an empty list to clear the UI if there are no positions
                self._send_message("position_update", [])
        except Exception as e:
            self._send_message("log", f"Error fetching open positions: {e}")