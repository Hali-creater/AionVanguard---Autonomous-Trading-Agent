import pandas as pd
import ta
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdaptabilityManager:
    """
    Manages the adaptability of the trading strategy based on market conditions.

    Analyzes current market data to identify regimes (e.g., trending, ranging,
    high/low volatility) and suggests adjustments to strategy parameters
    and risk management settings.
    """
    def __init__(self, volatility_threshold: float = 0.02, trend_strength_threshold: float = 20):
        """
        Initializes the AdaptabilityManager with thresholds for market analysis.

        Args:
            volatility_threshold: A threshold for determining high vs low volatility
                                  (e.g., based on ATR percentage).
            trend_strength_threshold: A threshold for determining trending vs ranging
                                      markets (e.g., based on ADX value).
        """
        self.volatility_threshold = volatility_threshold
        self.trend_strength_threshold = trend_strength_threshold
        logging.info('AdaptabilityManager initialized with volatility_threshold={} and trend_strength_threshold={}.'.format(self.volatility_threshold, self.trend_strength_threshold))


    def analyze_market_conditions(self, data: pd.DataFrame) -> dict:
        """
        Analyzes the provided market data to determine current market conditions and regime.

        Uses indicators like ATR for volatility and ADX for trend strength.
        Requires 'high', 'low', 'close', and 'volume' columns in the input data.

        Args:
            data: A pandas DataFrame containing historical market data (OHLCV).
                  Should contain enough data points for indicator calculations.

        Returns:
            A dictionary containing analyzed market conditions, including volatility
            ('high', 'low', 'unknown'), trend ('trending', 'ranging', 'unknown'),
            and an overall 'regime' ('TRENDING_HIGH_VOL', 'RANGING_LOW_VOL', etc.,
            or 'UNKNOWN', 'UNCERTAIN').
        """
        logging.info('Analyzing market conditions...')
        market_conditions = {}

        if data.empty:
            logging.warning('Input data is empty. Cannot analyze market conditions.')
            return {'regime': 'UNKNOWN'}

        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
             missing = [col for col in required_cols if col not in data.columns]
             logging.error(f'Missing required data columns for analysis: {missing}')
             return {'regime': 'UNKNOWN'}

        try:
            data['ATR'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], window=14)
            latest_atr = data['ATR'].iloc[-1] if not data['ATR'].empty else np.nan
            latest_close = data['close'].iloc[-1] if not data['close'].empty else np.nan

            if not np.isnan(latest_atr) and not np.isnan(latest_close) and latest_close != 0:
                volatility_percentage = (latest_atr / latest_close)
                market_conditions['volatility'] = 'high' if volatility_percentage > self.volatility_threshold else 'low'
            else:
                market_conditions['volatility'] = 'unknown'

            adx_indicator = ta.trend.ADXIndicator(data['high'], data['low'], data['close'], window=14)
            data['ADX'] = adx_indicator.adx()
            latest_adx = data['ADX'].iloc[-1] if not data['ADX'].empty else np.nan

            if not np.isnan(latest_adx):
                market_conditions['trend'] = 'trending' if latest_adx > self.trend_strength_threshold else 'ranging'
            else:
                market_conditions['trend'] = 'unknown'

            if market_conditions.get('trend') == 'trending' and market_conditions.get('volatility') == 'high':
                market_conditions['regime'] = 'TRENDING_HIGH_VOL'
            elif market_conditions.get('trend') == 'trending' and market_conditions.get('volatility') == 'low':
                 market_conditions['regime'] = 'TRENDING_LOW_VOL'
            elif market_conditions.get('trend') == 'ranging' and market_conditions.get('volatility') == 'high':
                 market_conditions['regime'] = 'RANGING_HIGH_VOL'
            elif market_conditions.get('trend') == 'ranging' and market_conditions.get('volatility') == 'low':
                 market_conditions['regime'] = 'RANGING_LOW_VOL'
            else:
                 market_conditions['regime'] = 'UNCERTAIN'

        except Exception as e:
            logging.error(f"Error during market condition analysis: {e}")
            return {'regime': 'UNKNOWN', 'volatility': 'unknown', 'trend': 'unknown'}

        logging.info(f'Market conditions analyzed: {market_conditions}')
        return market_conditions


    def suggest_strategy_adjustment(self, market_conditions: dict) -> dict:
        """
        Suggests adjustments to strategy parameters and risk management settings
        based on the identified market conditions.

        This is a placeholder logic. A real implementation would map market
        regimes to specific adjustments for the trading strategy and risk manager.

        Args:
            market_conditions: A dictionary containing the analyzed market conditions
                               as returned by `analyze_market_conditions`.

        Returns:
            A dictionary containing suggested adjustments (e.g., 'strategy_type',
            'risk_per_trade_multiplier', 'stop_loss_multiplier', 'take_profit_multiplier').
            Returns an empty dictionary or default adjustments if conditions are unknown
            or no specific adjustments are defined for the regime.
        """
        logging.info(f'Suggesting strategy adjustments based on conditions: {market_conditions}')
        suggested_adjustments = {}
        current_regime = market_conditions.get('regime', 'UNKNOWN')
        volatility_level = market_conditions.get('volatility', 'unknown')

        if current_regime == 'TRENDING_HIGH_VOL':
            suggested_adjustments['strategy_type'] = 'trend_following'
            suggested_adjustments['risk_per_trade_multiplier'] = 0.8
            suggested_adjustments['stop_loss_multiplier'] = 1.5
            suggested_adjustments['take_profit_multiplier'] = 2.0
        elif current_regime == 'TRENDING_LOW_VOL':
            suggested_adjustments['strategy_type'] = 'trend_following'
            suggested_adjustments['risk_per_trade_multiplier'] = 1.0
            suggested_adjustments['stop_loss_multiplier'] = 1.0
            suggested_adjustments['take_profit_multiplier'] = 1.5
        elif current_regime == 'RANGING_HIGH_VOL':
            suggested_adjustments['strategy_type'] = 'range_bound'
            suggested_adjustments['risk_per_trade_multiplier'] = 0.6
            suggested_adjustments['stop_loss_multiplier'] = 1.8
            suggested_adjustments['take_profit_multiplier'] = 1.2
        elif current_regime == 'RANGING_LOW_VOL':
            suggested_adjustments['strategy_type'] = 'range_bound'
            suggested_adjustments['risk_per_trade_multiplier'] = 1.0
            suggested_adjustments['stop_loss_multiplier'] = 1.0
            suggested_adjustments['take_profit_multiplier'] = 1.0
        else: # UNKNOWN or UNCERTAIN regime
            suggested_adjustments['strategy_type'] = 'hold'
            suggested_adjustments['risk_per_trade_multiplier'] = 0.5
            suggested_adjustments['stop_loss_multiplier'] = 1.0
            suggested_adjustments['take_profit_multiplier'] = 1.0

        if volatility_level == 'high' and 'stop_loss_multiplier' in suggested_adjustments:
             suggested_adjustments['stop_loss_multiplier'] *= 1.2
        elif volatility_level == 'low' and 'stop_loss_multiplier' in suggested_adjustments:
             suggested_adjustments['stop_loss_multiplier'] *= 0.8

        logging.info(f'Suggested strategy adjustments: {suggested_adjustments}')
        return suggested_adjustments
