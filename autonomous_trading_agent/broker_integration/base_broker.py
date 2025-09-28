from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict

class BaseBroker(ABC):
    """
    Abstract base class for all broker integrations.
    Defines the standard interface for executing trades and managing the account.
    """

    @abstractmethod
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
        Places an order with the broker.

        Args:
            symbol (str): The trading symbol.
            order_type (str): Type of order (e.g., 'market', 'limit').
            quantity (float): The number of shares.
            side (str): 'buy' or 'sell'.
            time_in_force (str): Time in force for the order.
            limit_price (Optional[float]): Price for a limit order.
            stop_price (Optional[float]): Price for a stop/stop-limit order.

        Returns:
            A dictionary with order details from the broker, or None if failed.
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancels an open order.

        Args:
            order_id (str): The unique ID of the order to cancel.

        Returns:
            True if cancellation was successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_open_positions(self) -> pd.DataFrame:
        """
        Retrieves all open positions.

        Returns:
            A pandas DataFrame with details of open positions.
            Expected columns: ['symbol', 'qty', 'side', 'avg_entry_price', 'market_value', 'unrealized_pl']
        """
        pass

    @abstractmethod
    def get_account_summary(self) -> Optional[Dict]:
        """
        Retrieves a summary of the trading account.

        Returns:
            A dictionary containing account details like equity, buying power, etc.
        """
        pass