from abc import ABC, abstractmethod
import pandas as pd

class BaseExecutor(ABC):
    """
    Abstract base class for order execution against different brokers.

    Defines the standard interface for placing, modifying, and canceling orders,
    and fetching account information.
    """
    @abstractmethod
    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None, stop_loss: float = None, take_profit: float = None):
        """
        Places a trade order with the broker.

        Args:
            symbol: The trading symbol.
            order_type: The type of order (e.g., 'market', 'limit').
            quantity: The quantity of the asset to trade. Positive for buy, negative for sell.
            price: Optional. The limit price for 'limit' orders.
            stop_loss: Optional. The stop loss price for the order/position.
            take_profit: Optional. The take profit price for the order/position.

        Returns:
            A unique order ID if the order was placed successfully, None otherwise.
        """
        pass

    @abstractmethod
    def modify_order(self, order_id: str, new_quantity: float = None, new_price: float = None, new_stop_loss: float = None, new_take_profit: float = None):
        """
        Modifies an existing open order.

        Args:
            order_id: The ID of the order to modify.
            new_quantity: Optional. The new quantity.
            new_price: Optional. The new price (for limit orders).
            new_stop_loss: Optional. The new stop loss price.
            new_take_profit: Optional. The new take profit price.

        Returns:
            True if the modification was successful, False otherwise.
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str):
        """
        Cancels an existing open order.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            True if the cancellation was successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_account_balance(self) -> float:
        """
        Retrieves the current account equity or balance.

        Returns:
            The account balance as a float, or 0.0 if fetching fails.
        """
        pass

    @abstractmethod
    def get_open_positions(self) -> pd.DataFrame:
        """
        Retrieves a list of currently open trading positions.

        Returns:
            A pandas DataFrame with details of open positions, or an empty
            DataFrame if fetching fails or no positions are open.
        """
        pass
