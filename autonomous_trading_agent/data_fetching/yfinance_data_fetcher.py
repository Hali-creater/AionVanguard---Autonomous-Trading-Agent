import pandas as pd
import yfinance as yf
from .base_data_fetcher import BaseDataFetcher
import logging

class YFinanceDataFetcher(BaseDataFetcher):
    """
    Data fetcher that uses the yfinance library to fetch data from Yahoo Finance.
    """
    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical bar data from Yahoo Finance.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            timeframe: The data timeframe (e.g., '1d', '1h', '15m', '1m').
            start_date: The start date for the historical data (YYYY-MM-DD).
            end_date: The end date for the historical data (YYYY-MM-DD).

        Returns:
            A pandas DataFrame containing historical data (Open, High, Low, Close, Volume),
            with the timestamp as the index. Returns an empty DataFrame on error or no data.
        """
        try:
            # yfinance uses different interval strings than Alpaca.
            # We need to map them.
            timeframe_mapping = {
                '1Min': '1m',
                '15Min': '15m',
                '1H': '1h',
                '1D': '1d',
            }
            interval = timeframe_mapping.get(timeframe)
            if not interval:
                raise ValueError(f"Unsupported timeframe for yfinance: {timeframe}")

            data = yf.download(tickers=symbol, start=start_date, end=end_date, interval=interval)

            if data.empty:
                logging.warning(f'No historical data found for {symbol} from {start_date} to {end_date} with interval {interval}.')

            # yfinance column names are capitalized ('Open', 'High', 'Low', 'Close', 'Volume'), which is what we want.
            return data
        except Exception as e:
            logging.error(f'Error fetching historical data for {symbol} using yfinance: {e}')
            return pd.DataFrame()

    def fetch_realtime_data(self, symbol: str):
        """
        Real-time data fetching is not implemented for yfinance in this agent.
        """
        logging.warning('Real-time data fetching is not supported by the YFinanceDataFetcher.')
        pass