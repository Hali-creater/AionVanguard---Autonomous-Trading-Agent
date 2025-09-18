import pandas as pd
from abc import ABC, abstractmethod
import ta
import numpy as np
import logging
from typing import Dict, Any, Optional

class BaseTradingStrategy(ABC):
    """
    Abstract base class for defining a trading strategy.

    All trading strategies should inherit from this class and implement
    the `generate_signal` method.
    """
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generates a trading signal (BUY, SELL, or HOLD) based on input data.

        Args:
            data: A pandas DataFrame containing historical market data (e.g., OHLCV).
                  The DataFrame is expected to contain at least 'open', 'high', 'low',
                  'close', and 'volume' columns.

        Returns:
            A string representing the trading signal ('BUY', 'SELL', or 'HOLD').
        """
        pass

class CombinedStrategy(BaseTradingStrategy):
    """
    A trading strategy that combines a Moving Average (MA) Crossover with a
    Relative Strength Index (RSI) filter for confirmation. This provides a
    more robust signal than a simple crossover alone.
    """
    def __init__(self, short_window=20, long_window=50, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
        """
        Initializes the strategy with configurable parameters.
        """
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")

        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        logging.info(f"Initialized MA Crossover + RSI Strategy with params: "
                     f"Short/Long MA: {short_window}/{long_window}, RSI Window: {rsi_window}")

    def _calculate_indicators(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Calculates all necessary indicators and returns the latest values.
        """
        try:
            close_prices = data['close']
            short_sma = ta.trend.sma_indicator(close_prices, window=self.short_window)
            long_sma = ta.trend.sma_indicator(close_prices, window=self.long_window)
            rsi = ta.momentum.rsi(close_prices, window=self.rsi_window)

            if short_sma is None or long_sma is None or rsi is None:
                 logging.warning("One or more indicators returned None.")
                 return None

            indicators = {
                "latest_short_sma": short_sma.iloc[-1],
                "latest_long_sma": long_sma.iloc[-1],
                "previous_short_sma": short_sma.iloc[-2],
                "previous_long_sma": long_sma.iloc[-2],
                "latest_rsi": rsi.iloc[-1]
            }

            # Check for NaN values which can occur if data is too short
            if any(pd.isna(val) for val in indicators.values()):
                logging.info("Not enough data to compute all indicators for the latest candle. Holding.")
                return None

            return indicators

        except Exception as e:
            logging.error(f"Error calculating indicators: {e}")
            return None

    def _determine_signal_from_indicators(self, indicators: Dict[str, Any]) -> str:
        """
        Determines the trade signal based on a dictionary of pre-calculated indicator values.
        This method contains the core decision logic of the strategy.
        """
        prev_short = indicators['previous_short_sma']
        prev_long = indicators['previous_long_sma']
        latest_short = indicators['latest_short_sma']
        latest_long = indicators['latest_long_sma']
        rsi = indicators['latest_rsi']

        signal = 'HOLD'

        # Buy Condition: Bullish Crossover + RSI Confirmation
        is_bullish_crossover = prev_short <= prev_long and latest_short > latest_long
        if is_bullish_crossover:
            if rsi < self.rsi_overbought:
                signal = 'BUY'
                logging.info(f"BUY signal: Bullish crossover and RSI ({rsi:.2f}) is below {self.rsi_overbought}.")
            else:
                logging.info(f"Crossover detected, but holding: RSI ({rsi:.2f}) is in overbought territory.")

        # Sell Condition: Bearish Crossover + RSI Confirmation
        is_bearish_crossover = prev_short >= prev_long and latest_short < latest_long
        if is_bearish_crossover:
            if rsi > self.rsi_oversold:
                signal = 'SELL'
                logging.info(f"SELL signal: Bearish crossover and RSI ({rsi:.2f}) is above {self.rsi_oversold}.")
            else:
                logging.info(f"Crossover detected, but holding: RSI ({rsi:.2f}) is in oversold territory.")

        return signal

    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generates a trading signal by calculating indicators and then applying decision logic.
        """
        if data.empty or 'close' not in data.columns or len(data) < self.long_window:
            logging.warning("Input data is empty, missing 'close' column, or too short. Cannot generate signal.")
            return 'HOLD'

        indicators = self._calculate_indicators(data)

        if indicators is None:
            return 'HOLD'

        return self._determine_signal_from_indicators(indicators)
