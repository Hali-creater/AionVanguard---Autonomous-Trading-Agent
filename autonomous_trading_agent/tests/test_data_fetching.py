import unittest
import pandas as pd
from datetime import datetime, timedelta
import os
import finnhub
from autonomous_trading_agent.data_fetching.finnhub_data_fetcher import FinnhubDataFetcher
from autonomous_trading_agent.data_fetching.yfinance_data_fetcher import YFinanceDataFetcher

# This decorator will skip the test if the FINNHUB_API_KEY is not set
@unittest.skipIf(not os.getenv('FINNHUB_API_KEY'), "FINNHUB_API_KEY environment variable not set")
class TestFinnhubDataFetcher(unittest.TestCase):
    """
    Tests for the FinnhubDataFetcher.
    """
    def setUp(self):
        """
        Set up the test case.
        """
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.fetcher = FinnhubDataFetcher(api_key=self.api_key)

    def test_finnhub_fetch_historical_data_success(self):
        """
        Test that the FinnhubDataFetcher can successfully fetch historical data.
        This test will be skipped if the API key lacks permissions.
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)

            symbol = "AAPL" # Use a standard, well-known symbol
            timeframe = "1D"

            data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.isoformat(), end_date.isoformat())

            self.assertIsInstance(data, pd.DataFrame)
            self.assertFalse(data.empty, "The fetched data should not be empty.")
            self.assertIn('Close', data.columns, "DataFrame should have a 'Close' column.")
            self.assertIn('Open', data.columns, "DataFrame should have an 'Open' column.")
            self.assertIn('High', data.columns, "DataFrame should have a 'High' column.")
            self.assertIn('Low', data.columns, "DataFrame should have a 'Low' column.")
            self.assertIn('Volume', data.columns, "DataFrame should have a 'Volume' column.")
        except finnhub.FinnhubAPIException as e:
            if e.status_code == 403:
                self.skipTest("Skipping test: API key does not have permission for this resource.")
            else:
                raise e

class TestYFinanceDataFetcher(unittest.TestCase):
    """
    Tests for the YFinanceDataFetcher.
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

        symbol = "AAPL"
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.isoformat(), end_date.isoformat())

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty, "The fetched data should not be empty.")
        self.assertIn('Close', data.columns, "DataFrame should have a 'Close' column.")

    def test_yfinance_fetch_historical_data_invalid_symbol(self):
        """
        Test fetching data for a symbol that does not exist.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)

        symbol = "INVALID_SYMBOL_XYZ"
        timeframe = "1D"

        data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.isoformat(), end_date.isoformat())

        self.assertTrue(data.empty, "The fetched data should be empty for an invalid symbol.")

    def test_finnhub_fetch_historical_data_invalid_symbol(self):
        """
        Test fetching data for a symbol that does not exist.
        This test will be skipped if the API key lacks permissions.
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)

            symbol = "INVALID_SYMBOL_XYZ"
            timeframe = "1D"

            data = self.fetcher.fetch_historical_data(symbol, timeframe, start_date.isoformat(), end_date.isoformat())

            self.assertTrue(data.empty, "The fetched data should be empty for an invalid symbol.")
        except finnhub.FinnhubAPIException as e:
            if e.status_code == 403:
                self.skipTest("Skipping test: API key does not have permission for this resource.")
            else:
                raise e
