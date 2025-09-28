import logging
import pandas as pd
from typing import List, Dict, Optional

from .base_data_fetcher import BaseDataFetcher
from .finnhub_data_fetcher import FinnhubDataFetcher
from .yfinance_data_fetcher import YFinanceDataFetcher

class DataManager:
    """
    Manages one or more data fetchers to provide a resilient way to get market data.
    It can be configured with a primary and multiple fallback fetchers.
    """
    def __init__(self, config: Dict):
        """
        Initializes the DataManager with a configuration.

        Args:
            config (Dict): A configuration dictionary that should contain
                           keys for data sources and their respective API keys.
                           Example:
                           {
                               "data_sources": ["finnhub", "yfinance"],
                               "finnhub_api_key": "YOUR_KEY"
                           }
        """
        self.fetchers: List[BaseDataFetcher] = []
        data_sources = config.get("data_sources", ["yfinance"]) # Default to yfinance

        for source in data_sources:
            fetcher = self._create_fetcher(source, config)
            if fetcher:
                self.fetchers.append(fetcher)

        if not self.fetchers:
            raise ValueError("Could not initialize any data fetchers from the provided config.")

    def _create_fetcher(self, source_name: str, config: Dict) -> Optional[BaseDataFetcher]:
        """Factory method to create a data fetcher instance."""
        if source_name == "finnhub":
            api_key = config.get("finnhub_api_key")
            if not api_key:
                logging.warning("Finnhub selected as a data source, but no API key was provided.")
                return None
            return FinnhubDataFetcher(api_key=api_key)
        elif source_name == "yfinance":
            return YFinanceDataFetcher()
        else:
            logging.warning(f"Data source '{source_name}' is not supported.")
            return None

    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Tries to fetch historical data from the configured fetchers in order.

        It will try the first fetcher, and if it fails or returns empty data,
        it will proceed to the next one in the list.

        Args:
            symbol: The trading symbol.
            timeframe: The data timeframe (e.g., '1D', '1H', '1Min').
            start_date: The start date for the data.
            end_date: The end date for the data.

        Returns:
            A pandas DataFrame with the historical data, or an empty DataFrame if
            all fetchers fail.
        """
        for fetcher in self.fetchers:
            try:
                logging.info(f"Attempting to fetch data for {symbol} using {fetcher.__class__.__name__}.")
                data = fetcher.fetch_historical_data(symbol, timeframe, start_date, end_date)
                if not data.empty:
                    logging.info(f"Successfully fetched data using {fetcher.__class__.__name__}.")
                    return data
                logging.warning(f"{fetcher.__class__.__name__} returned no data for {symbol}.")
            except Exception as e:
                logging.error(f"Failed to fetch data using {fetcher.__class__.__name__}: {e}", exc_info=True)

        logging.error(f"All configured data fetchers failed to retrieve data for {symbol}.")
        return pd.DataFrame()