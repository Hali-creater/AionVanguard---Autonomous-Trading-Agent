import logging
import pandas as pd
from autonomous_trading_agent.data_fetching.alpaca_data_fetcher import AlpacaDataFetcher
from autonomous_trading_agent.execution.alpaca_executor import AlpacaExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlpacaIntegration:
    """
    Integrates data fetching and execution for Alpaca.
    """
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://paper-api.alpaca.markets'):
        """
        Initializes the integration by creating instances of the broker's
        specific DataFetcher and Executor classes.
        """
        try:
            self.data_fetcher = AlpacaDataFetcher(api_key, api_secret, base_url)
            self.executor = AlpacaExecutor(api_key, api_secret, base_url)
            logging.info('AlpacaIntegration initialized.')
        except Exception as e:
            logging.error(f'Error initializing AlpacaIntegration: {e}')
            self.data_fetcher = None
            self.executor = None


    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        if self.data_fetcher:
            return self.data_fetcher.fetch_historical_data(symbol, timeframe, start_date, end_date)
        logging.warning('Data fetcher not initialized.')
        return pd.DataFrame()


    def fetch_realtime_data(self, symbol: str):
        if self.data_fetcher:
            self.data_fetcher.fetch_realtime_data(symbol)
        else:
            logging.warning('Data fetcher not initialized.')


    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None, stop_loss: float = None, take_profit: float = None):
        if self.executor:
            return self.executor.place_order(symbol, order_type, quantity, price, stop_loss, take_profit)
        logging.warning('Executor not initialized.')
        return None

    def modify_order(self, order_id: str, new_quantity: float = None, new_price: float = None, new_stop_loss: float = None, new_take_profit: float = None):
        if self.executor:
            return self.executor.modify_order(order_id, new_quantity, new_price, new_stop_loss, new_take_profit)
        logging.warning('Executor not initialized.')
        return False

    def cancel_order(self, order_id: str):
        if self.executor:
            return self.executor.cancel_order(order_id)
        logging.warning('Executor not initialized.')
        return False

    def get_account_balance(self) -> float:
        if self.executor:
            return self.executor.get_account_balance()
        logging.warning('Executor not initialized.')
        return 0.0

    def get_open_positions(self) -> pd.DataFrame:
        if self.executor:
            return self.executor.get_open_positions()
        logging.warning('Executor not initialized.')
        return pd.DataFrame()
