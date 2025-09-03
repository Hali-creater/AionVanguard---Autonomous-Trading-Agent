import pandas as pd
from abc import ABC, abstractmethod

class BaseDataFetcher(ABC):
    """
    Abstract base class for data fetching from different brokers.

    Defines the standard interface for fetching historical and real-time data.
    """
    @abstractmethod
    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical data for a given symbol and timeframe.

        Args:
            symbol: The trading symbol (e.g., 'AAPL', 'BTCUSD').
            timeframe: The data timeframe (e.g., '1D', '1H', '15Min', '1Min').
            start_date: The start date for the historical data (format dependent on broker API).
            end_date: The end date for the historical data (format dependent on broker API).

        Returns:
            A pandas DataFrame containing historical data (Open, High, Low, Close, Volume),
            or an empty DataFrame if data fetching fails or no data is found.
        """
        pass

    @abstractmethod
    def fetch_realtime_data(self, symbol: str):
        """
        Sets up real-time data streaming for a given symbol.

        Note: Real-time data fetching is typically asynchronous and broker-specific
        (e.g., using websockets). This method initiates the process.

        Args:
            symbol: The trading symbol for real-time data.
        """
        pass
