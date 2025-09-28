import logging
import pandas as pd
from typing import Optional, Dict

from .base_broker import BaseBroker
from ..execution.alpaca_executor import AlpacaExecutor
from alpaca_trade_api.rest import APIError

class AlpacaBroker(BaseBroker):
    """
    Broker integration for Alpaca.
    Implements the BaseBroker interface using the AlpacaExecutor.
    """
    def __init__(self, api_key: str, api_secret: str, paper_trading: bool = True):
        """
        Initializes the AlpacaBroker.
        Args:
            api_key (str): Alpaca API key.
            api_secret (str): Alpaca API secret.
            paper_trading (bool): If True, connects to the paper trading endpoint.
        """
        try:
            self.executor = AlpacaExecutor(api_key=api_key, api_secret=api_secret)
            logging.info("AlpacaBroker initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize AlpacaBroker: {e}")
            raise

    def place_order(
        self,
        symbol: str,
        order_type: str,
        quantity: float,
        side: str,
        time_in_force: str = 'gtc',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Places an order with Alpaca.
        """
        try:
            # The executor expects quantity to be signed to indicate direction.
            signed_quantity = quantity if side == 'buy' else -quantity

            order_id = self.executor.place_order(
                symbol=symbol,
                order_type=order_type,
                quantity=signed_quantity,
                price=limit_price
            )

            if order_id:
                order = self.executor.api.get_order(order_id)
                return {
                    'id': order.id, 'symbol': order.symbol, 'qty': order.qty,
                    'side': order.side, 'type': order.type, 'status': order.status
                }
            return None
        except APIError as e:
            logging.error(f"Failed to place order for {symbol} with Alpaca: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancels an open order."""
        return self.executor.cancel_order(order_id)

    def get_open_positions(self) -> pd.DataFrame:
        """Retrieves all open positions."""
        df = self.executor.get_open_positions()
        expected_cols = ['symbol', 'qty', 'side', 'avg_entry_price', 'market_value', 'unrealized_pl']
        if df.empty:
            return pd.DataFrame(columns=expected_cols)

        df = df.rename(columns={'quantity': 'qty'})

        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        return df[expected_cols]

    def get_account_summary(self) -> Optional[Dict]:
        """Retrieves a summary of the trading account."""
        try:
            account = self.executor.api.get_account()
            return {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'currency': account.currency
            }
        except APIError as e:
            logging.error(f"Failed to get account summary from Alpaca: {e}")
            return None