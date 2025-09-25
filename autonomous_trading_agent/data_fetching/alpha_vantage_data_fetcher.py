import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from .base_data_fetcher import BaseDataFetcher
import logging
import time

class AlphaVantageDataFetcher(BaseDataFetcher):
    """
    Data fetcher that uses the Alpha Vantage API.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Alpha Vantage API key must be provided.")
        self.api_key = api_key
        # Note: The `alpha_vantage` library handles the output format (pandas)
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')

    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical bar data from Alpha Vantage.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            timeframe: The data timeframe (e.g., '1min', '15min', '60min').
            start_date: The start date for the data (not directly used by AV interval calls).
            end_date: The end date for the data (not directly used by AV interval calls).

        Returns:
            A pandas DataFrame containing historical data.
        """
        try:
            # Map our timeframe to Alpha Vantage's interval strings
            timeframe_mapping = {
                '1Min': '1min',
                '15Min': '15min',
                '1H': '60min',
                '1D': 'daily',
            }
            interval = timeframe_mapping.get(timeframe)
            if not interval:
                raise ValueError(f"Unsupported timeframe for Alpha Vantage: {timeframe}")

            logging.info(f"Fetching {interval} data for {symbol} from Alpha Vantage.")

            # Alpha Vantage free tier has a limit of 5 calls per minute.
            # A more robust implementation would use a rate limiter.
            # For now, a simple sleep will do.
            time.sleep(12)

            if interval == 'daily':
                data, meta_data = self.ts.get_daily(symbol=symbol, outputsize='full')
            else:
                data, meta_data = self.ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')

            # The library returns data with descending index. We reverse it.
            data = data.iloc[::-1]

            # Rename columns to match our agent's expected format
            data.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }, inplace=True)

            # The column names for daily data are different
            if interval == 'daily':
                 data.rename(columns={
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                }, inplace=True)


            # Filter by date range
            data.index = pd.to_datetime(data.index)
            data = data[(data.index >= start_date) & (data.index <= end_date)]

            if data.empty:
                logging.warning(f'No historical data found for {symbol} from Alpha Vantage.')

            return data

        except Exception as e:
            # The alpha_vantage library can sometimes raise a ValueError on API limit or bad symbol
            logging.error(f'Error fetching historical data for {symbol} using Alpha Vantage: {e}')
            return pd.DataFrame()

    def fetch_realtime_data(self, symbol: str):
        logging.warning('Real-time data fetching is not supported by the AlphaVantageDataFetcher.')
        pass