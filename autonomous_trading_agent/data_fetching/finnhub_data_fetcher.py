import pandas as pd
import finnhub
from .base_data_fetcher import BaseDataFetcher
import logging
from datetime import datetime

class FinnhubDataFetcher(BaseDataFetcher):
    """
    Data fetcher that uses the Finnhub API.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Finnhub API key must be provided.")
        self.api_key = api_key
        self.finnhub_client = finnhub.Client(api_key=self.api_key)

    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical bar data from Finnhub.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            timeframe: The data timeframe (e.g., '1Min', '15Min', '1H', '1D').
            start_date: The start date for the data (ISO 8601 format string).
            end_date: The end date for the data (ISO 8601 format string).

        Returns:
            A pandas DataFrame containing historical data.
        """
        try:
            # Map our timeframe to Finnhub's resolution strings
            timeframe_mapping = {
                '1Min': '1',
                '15Min': '15',
                '1H': '60',
                '1D': 'D',
            }
            resolution = timeframe_mapping.get(timeframe)
            if not resolution:
                raise ValueError(f"Unsupported timeframe for Finnhub: {timeframe}")

            logging.info(f"Fetching {resolution} data for {symbol} from Finnhub.")

            # Convert dates to unix timestamps
            start_timestamp = int(datetime.fromisoformat(start_date).timestamp())
            end_timestamp = int(datetime.fromisoformat(end_date).timestamp())

            # Fetch data
            res = self.finnhub_client.stock_candles(symbol, resolution, start_timestamp, end_timestamp)

            if res.get('s') != 'ok':
                logging.warning(f"Finnhub API did not return 'ok' status for {symbol}. Response: {res}")
                return pd.DataFrame()

            if 't' not in res or not res['t']:
                 logging.warning(f'No historical data found for {symbol} from Finnhub.')
                 return pd.DataFrame()

            # Convert to pandas DataFrame
            df = pd.DataFrame({
                'Open': res['o'],
                'High': res['h'],
                'Low': res['l'],
                'Close': res['c'],
                'Volume': res['v']
            }, index=pd.to_datetime(res['t'], unit='s'))

            # Ensure the columns have the correct case, as expected by the agent
            df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            }, inplace=True)

            return df

        except finnhub.FinnhubAPIException as e:
            logging.error(f'Finnhub API error for {symbol}: {e}')
            raise e  # Re-raise for the caller to handle (e.g., tests)
        except Exception as e:
            logging.error(f'A general error occurred while fetching data for {symbol} using Finnhub: {e}')
            return pd.DataFrame()

    def fetch_realtime_data(self, symbol: str):
        logging.warning('Real-time data fetching is not supported by the FinnhubDataFetcher in this implementation.')
        pass