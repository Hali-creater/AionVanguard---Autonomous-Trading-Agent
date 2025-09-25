import unittest
import pandas as pd
from datetime import datetime, timedelta
import os
from autonomous_trading_agent.data_fetching.alpha_vantage_data_fetcher import AlphaVantageDataFetcher

# This decorator will skip the test if the ALPHA_VANTAGE_API_KEY is not set
@unittest.skipIf(not os.getenv('ALPHA_VANTAGE_API_KEY'), "ALPHA_VANTAGE_API_KEY environment variable not set")
class TestAlphaVantageDataFetcher(unittest.TestCase):
    """
    Tests for the AlphaVantageDataFetcher.
    """
    def setUp(self):
        """
        Set up the test case.
        """
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fetcher = AlphaVantageDataFetcher(api_key=self.api_key)

    def test_alpha_vantage_fetch_historical_data_success(self):
        """
        Test that the AlphaVantageDataFetcher can successfully fetch historical data.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)

        symbol = "IBM" # Use a standard, well-known symbol
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty, "The fetched data should not be empty.")
        self.assertIn('Close', data.columns, "DataFrame should have a 'Close' column.")
        self.assertIn('Open', data.columns, "DataFrame should have an 'Open' column.")
        self.assertIn('High', data.columns, "DataFrame should have a 'High' column.")
        self.assertIn('Low', data.columns, "DataFrame should have a 'Low' column.")
        self.assertIn('Volume', data.columns, "DataFrame should have a 'Volume' column.")

    def test_alpha_vantage_fetch_historical_data_invalid_symbol(self):
        """
        Test fetching data for a symbol that does not exist.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)

        symbol = "INVALID_SYMBOL_XYZ"
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        self.assertTrue(data.empty, "The fetched data should be empty for an invalid symbol.")
