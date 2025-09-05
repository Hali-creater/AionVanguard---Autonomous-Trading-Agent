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
    Requires API_KEY, API_SECRET, and optionally
    BASE_URL.
    """
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://paper-api.alpaca.markets'):
        """
        Initializes the AlpacaDataFetcher by taking API credentials and
        establishing a REST API connection.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        if not self.api_key or not self.api_secret:
            raise ValueError('Alpaca API key and secret must be provided.')
        self.api = REST(self.api_key, self.api_secret, self.base_url)

    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical bar data from Alpaca for a given symbol and timeframe.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            timeframe: The data timeframe (e.g., '1D', '1H', '15Min', '1Min').
                       Must be one of the timeframes supported by Alpaca and mapped
                       in this method.
            start_date: The start date for the historical data (ISO 8601 format string or datetime object).
            end_date: The end date for the historical data (ISO 8601 format string or datetime object).

        Returns:
            A pandas DataFrame containing historical data (Open, High, Low, Close, Volume),
            with the timestamp as the index. Returns an empty DataFrame on error or no data.
        """
        try:
            # Map string timeframe to Alpaca TimeFrame object
            if timeframe == '1D':
                tf = TimeFrame.Day
            elif timeframe == '1H':
                tf = TimeFrame.Hour
            elif timeframe == '15Min':
                tf = TimeFrame.Minute15
            elif timeframe == '1Min':
                tf = TimeFrame.Minute
            else:
                raise ValueError(f'Unsupported timeframe: {timeframe}')

            data = self.api.get_bars(symbol, tf, start_date, end_date).df
            if data.empty:
                logging.info(f'No historical data found for {symbol} in the specified range.')
            return data
        except Exception as e:
            logging.error(f'Error fetching historical data for {symbol}: {e}')
            return pd.DataFrame()

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
