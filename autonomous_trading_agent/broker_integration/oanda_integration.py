import logging
import pandas as pd
from autonomous_trading_agent.data_fetching.oanda_data_fetcher import OandaDataFetcher
from autonomous_trading_agent.execution.oanda_executor import OandaExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OandaIntegration:
    """
    Integrates data fetching and execution for OANDA.

    This class acts as a facade, providing a single point of interaction
    for the trading agent with this specific broker's functionalities.
    It initializes and holds instances of the broker's DataFetcher and Executor.
    """
    def __init__(self):
        """
        Initializes the integration by creating instances of the broker's
        specific DataFetcher and Executor classes.
        """
        try:
            self.data_fetcher = OandaDataFetcher()
            self.executor = OandaExecutor()
            logging.info('OandaIntegration initialized.')
        except Exception as e:
            logging.error(f'Error initializing OandaIntegration: {e}')
            self.data_fetcher = None
            self.executor = None


    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Delegates the historical data fetching request to the data fetcher.

        Args:
            symbol: The trading symbol.
            timeframe: The data timeframe.
            start_date: The start date.
            end_date: The end date.

        Returns:
            A pandas DataFrame containing historical data, or an empty DataFrame.
        """
        if self.data_fetcher:
            return self.data_fetcher.fetch_historical_data(symbol, timeframe, start_date, end_date)
        logging.warning('Data fetcher not initialized.')
        return pd.DataFrame()


    def fetch_realtime_data(self, symbol: str):
        """
        Delegates the real-time data fetching setup to the data fetcher.

        Args:
            symbol: The trading symbol.
        """
        if self.data_fetcher:
            self.data_fetcher.fetch_realtime_data(symbol)
        else:
            logging.warning('Data fetcher not initialized.')


    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None, stop_loss: float = None, take_profit: float = None):
        """
        Delegates the order placement request to the executor.

        Args:
            symbol: The trading symbol.
            order_type: The type of order.
            quantity: The quantity.
            price: Optional. The price.
            stop_loss: Optional. The stop loss price.
            take_profit: Optional. The take profit price.

        Returns:
            A unique order ID if successful, None otherwise.
        """
        if self.executor:
            return self.executor.place_order(symbol, order_type, quantity, price, stop_loss, take_profit)
        logging.warning('Executor not initialized.')
        return None

    def modify_order(self, order_id: str, new_quantity: float = None, new_price: float = None, new_stop_loss: float = None, new_take_profit: float = None):
        """
        Delegates the order modification request to the executor.

        Args:
            order_id: The ID of the order to modify.
            new_quantity: Optional. The new quantity.
            new_price: Optional. The new price.
            new_stop_loss: Optional. The new stop loss price.
            new_take_profit: Optional. The new take profit price.

        Returns:
            True if successful, False otherwise.
        """
        if self.executor:
            return self.executor.modify_order(order_id, new_quantity, new_price, new_stop_loss, new_take_profit)
        logging.warning('Executor not initialized.')
        return False

    def cancel_order(self, order_id: str):
        """
        Delegates the order cancellation request to the executor.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            True if successful, False otherwise.
        """
        if self.executor:
            return self.executor.cancel_order(order_id)
        logging.warning('Executor not initialized.')
        return False

    def get_account_balance(self) -> float:
        """
        Delegates the account balance request to the executor.

        Returns:
            The account balance, or 0.0 if fetching fails.
        """
        if self.executor:
            return self.executor.get_account_balance()
        logging.warning('Executor not initialized.')
        return 0.0

    def get_open_positions(self) -> pd.DataFrame:
        """
        Delegates the open positions request to the executor.

        Returns:
            A pandas DataFrame with open positions, or an empty DataFrame.
        """
        if self.executor:
            return self.executor.get_open_positions()
        logging.warning('Executor not initialized.')
        return pd.DataFrame()
