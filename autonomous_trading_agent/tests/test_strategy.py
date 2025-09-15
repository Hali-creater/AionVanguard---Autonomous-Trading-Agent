import pytest
import pandas as pd
import numpy as np
from autonomous_trading_agent.strategy.trading_strategy import CombinedStrategy

@pytest.fixture
def strategy():
    """Provides a default CombinedStrategy instance for testing."""
    return CombinedStrategy(short_window=5, long_window=10, rsi_window=14, rsi_overbought=70, rsi_oversold=30)

def generate_test_data(prices, volumes=None):
    """Helper function to create a pandas DataFrame for testing."""
    count = len(prices)
    if volumes is None:
        volumes = np.full(count, 100)
    safe_prices = [p if p > 0 else 0.01 for p in prices]
    return pd.DataFrame({
        'open': np.array(safe_prices) - 0.5,
        'high': np.array(safe_prices) + 0.5,
        'low': np.array(safe_prices) - 1.0,
        'close': np.array(safe_prices),
        'volume': volumes
    })

class TestCombinedStrategy:
    """
    Unit tests for the CombinedStrategy class.
    Tests are separated into core logic tests and integration tests.
    """

    # --- Core Logic Tests (testing _determine_signal_from_indicators directly) ---

    def test_logic_buy_signal(self, strategy):
        """Tests the core decision logic for a clean BUY signal."""
        indicators = {
            "previous_short_sma": 99.8, "latest_short_sma": 100.2,
            "previous_long_sma": 100.0, "latest_long_sma": 100.0,
            "latest_rsi": 55.0
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'BUY'

    def test_logic_sell_signal(self, strategy):
        """Tests the core decision logic for a clean SELL signal."""
        indicators = {
            "previous_short_sma": 100.2, "latest_short_sma": 99.8,
            "previous_long_sma": 100.0, "latest_long_sma": 100.0,
            "latest_rsi": 45.0
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'SELL'

    def test_logic_hold_on_buy_due_to_rsi(self, strategy):
        """Tests the RSI filter preventing a BUY signal when overbought."""
        indicators = {
            "previous_short_sma": 99.8, "latest_short_sma": 100.2,
            "previous_long_sma": 100.0, "latest_long_sma": 100.0,
            "latest_rsi": 75.0  # Overbought
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'HOLD'

    def test_logic_hold_on_sell_due_to_rsi(self, strategy):
        """Tests the RSI filter preventing a SELL signal when oversold."""
        indicators = {
            "previous_short_sma": 100.2, "latest_short_sma": 99.8,
            "previous_long_sma": 100.0, "latest_long_sma": 100.0,
            "latest_rsi": 25.0  # Oversold
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'HOLD'

    def test_logic_hold_no_crossover(self, strategy):
        """Tests that no signal is generated when SMAs do not cross."""
        # Case 1: Both moving up, no cross
        indicators = {
            "previous_short_sma": 101.0, "latest_short_sma": 102.0,
            "previous_long_sma": 100.0, "latest_long_sma": 101.0,
            "latest_rsi": 60.0
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'HOLD'

        # Case 2: Both moving down, no cross
        indicators = {
            "previous_short_sma": 99.0, "latest_short_sma": 98.0,
            "previous_long_sma": 100.0, "latest_long_sma": 99.0,
            "latest_rsi": 40.0
        }
        signal = strategy._determine_signal_from_indicators(indicators)
        assert signal == 'HOLD'


    # --- Integration Tests (testing generate_signal with real data) ---

    def test_initialization_error(self):
        """Tests that initializing with short_window >= long_window raises a ValueError."""
        with pytest.raises(ValueError, match="short_window must be less than long_window"):
            CombinedStrategy(short_window=10, long_window=5)

    def test_integration_hold_due_to_overbought_rsi(self, strategy):
        """
        Tests HOLD on a real bullish crossover because RSI is too high.
        """
        prices = list(range(100, 95, -1)) + list(range(96, 180, 4))
        data = generate_test_data(prices)
        signal = strategy.generate_signal(data)
        assert signal == 'HOLD'

    def test_integration_hold_due_to_oversold_rsi(self, strategy):
        """
        Tests HOLD on a real bearish crossover because RSI is too low.
        """
        prices = list(range(150, 155, 1)) + list(range(154, 50, -4))
        data = generate_test_data(prices)
        signal = strategy.generate_signal(data)
        assert signal == 'HOLD'

    def test_integration_empty_data(self, strategy):
        """Tests that empty input data gracefully returns HOLD."""
        data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        signal = strategy.generate_signal(data)
        assert signal == 'HOLD'

    def test_integration_insufficient_data(self, strategy):
        """Tests that data shorter than the long window returns HOLD."""
        prices = [100, 101, 102, 103, 104]
        data = generate_test_data(prices)
        signal = strategy.generate_signal(data)
        assert signal == 'HOLD'

    def test_integration_data_with_nans(self, strategy):
        """
        Tests that data with NaNs that affect the latest indicators returns HOLD.
        """
        prices = list(range(100, 130))
        prices[-2] = np.nan
        data = generate_test_data(prices)
        signal = strategy.generate_signal(data)
        assert signal == 'HOLD'
