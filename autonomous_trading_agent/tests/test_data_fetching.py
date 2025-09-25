import unittest
import pandas as pd
from datetime import datetime, timedelta
from autonomous_trading_agent.data_fetching.yfinance_data_fetcher import YFinanceDataFetcher

class TestDataFetching(unittest.TestCase):
    """
    Tests for the data_fetching module.
    """
    def setUp(self):
        """
        Set up the test case.
        """
        self.fetcher = YFinanceDataFetcher()

    def test_yfinance_fetch_historical_data_success(self):
        """
        Test that the YFinanceDataFetcher can successfully fetch historical data.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)

        # Use a well-known symbol that is unlikely to be delisted.
        symbol = "AAPL"
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty, "The fetched data should not be empty.")
        self.assertIn('Close', data.columns, "DataFrame should have a 'Close' column.")

    def test_yfinance_fetch_historical_data_invalid_symbol(self):
        """
        Test fetching data for a symbol that does not exist.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)

        # Use a symbol that is highly unlikely to exist.
        symbol = "INVALID_SYMBOL_XYZ"
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        self.assertTrue(data.empty, "The fetched data should be empty for an invalid symbol.")
