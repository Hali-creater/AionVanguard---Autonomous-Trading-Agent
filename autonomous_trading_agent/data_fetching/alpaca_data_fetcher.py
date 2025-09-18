import pandas as pd
from .base_data_fetcher import BaseDataFetcher
from alpaca_trade_api.rest import REST, TimeFrame
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class AlpacaDataFetcher(BaseDataFetcher):
    """
    Data fetcher specifically for the Alpaca trading platform.

    Implements the BaseDataFetcher interface using the Alpaca API.
    Requires ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY, and optionally
    ALPACA_BASE_URL environment variables.
    """
    def __init__(self):
        """
        Initializes the AlpacaDataFetcher by loading API credentials from
        environment variables and establishing a REST API connection.
        """
        self.api_key = os.getenv('ALPACA_API_KEY_ID')
        self.api_secret = os.getenv('ALPACA_API_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets') # Default to paper trading URL
        if not self.api_key or not self.api_secret:
            raise ValueError('Alpaca API key and secret must be set in environment variables.')
        self.api = REST(self.api_key, self.api_secret, self.base_url)

    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> tuple[pd.DataFrame, str | None]:
        """
        Fetches historical bar data from Alpaca for a given symbol and timeframe.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            timeframe: The data timeframe (e.g., '1D', '1H', '15Min', '1Min').
            start_date: The start date for the historical data (ISO 8601 format).
            end_date: The end date for the historical data (ISO 8601 format).

        Returns:
            A tuple containing:
            - A pandas DataFrame with historical data.
            - A string with an error message if an error occurred, otherwise None.
        """
        try:
            if timeframe == '1D':
                tf = TimeFrame.Day
            elif timeframe == '1H':
                tf = TimeFrame.Hour
            elif timeframe == '15Min':
                tf = TimeFrame.Minute15
            elif timeframe == '1Min':
                tf = TimeFrame.Minute
            else:
                # This error is for developers, so raising it is fine.
                raise ValueError(f'Unsupported timeframe: {timeframe}')

            data = self.api.get_bars(symbol, tf, start_date, end_date).df

            if data.empty:
                # This is not a hard error, but useful info.
                return pd.DataFrame(), f'No historical data found for {symbol} in the specified range.'

            return data, None

        except Exception as e:
            # This is a hard error (e.g., API key issue, invalid symbol).
            error_msg = f'Failed to fetch data for {symbol} from Alpaca: {e}'
            logging.error(error_msg)
            return pd.DataFrame(), error_msg

    def fetch_realtime_data(self, symbol: str):
        """
        Placeholder for real-time data fetching via Alpaca websockets.

        Args:
            symbol: The trading symbol.
        """
        # Alpaca's real-time data is typically via websockets.
        # This is a placeholder for a more complex real-time implementation.
        logging.info(f'Real-time data fetching for {symbol} not fully implemented yet for Alpaca.')
        # A real implementation would involve setting up a websocket connection
        # and handling incoming data streams.
        pass
