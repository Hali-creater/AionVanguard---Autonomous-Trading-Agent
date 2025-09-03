import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RiskManager:
    """
    Manages trading risk based on predefined rules.

    Includes functionality for position sizing, setting stop losses and take profits,
    trailing stops, and enforcing daily risk limits.
    """
    def __init__(self, account_balance: float, risk_per_trade_percentage: float, daily_risk_limit_percentage: float):
        """
        Initializes the RiskManager with account details and risk parameters.

        Args:
            account_balance: The initial account balance.
            risk_per_trade_percentage: The maximum percentage of the account balance
                                       to risk on a single trade (e.g., 0.01 for 1%).
                                       Must be between 0 and 1.
            daily_risk_limit_percentage: The maximum percentage of the initial daily
                                         balance that can be lost in a single day (e.g., 0.05 for 5%).
                                         Must be between 0 and 1.

        Raises:
            ValueError: If input percentages are out of range or account_balance is non-positive.
        """
        if not (0 < risk_per_trade_percentage <= 1.0):
            raise ValueError('risk_per_trade_percentage must be between 0 and 1 (inclusive).')
        if not (0 < daily_risk_limit_percentage <= 1.0):
            raise ValueError('daily_risk_limit_percentage must be between 0 and 1 (inclusive).')
        if account_balance <= 0:
            raise ValueError('account_balance must be positive.')


        self.account_balance = account_balance
        self.initial_balance = account_balance # Store initial balance for daily limit calculation
        self.risk_per_trade_percentage = risk_per_trade_percentage
        self.daily_risk_limit_percentage = daily_risk_limit_percentage
        self.daily_loss_incurred = 0.0
        logging.info(f'RiskManager initialized with account balance: {account_balance}, risk per trade: {risk_per_trade_percentage*100}%, daily risk limit: {daily_risk_limit_percentage*100}%')

    def calculate_position_size(self, entry_price: float, stop_loss_price: float, asset_multiplier: float = 1.0) -> float:
        """
        Calculates the appropriate position size (quantity of asset) based on the
        account balance, risk per trade, distance to stop loss, and asset multiplier.

        Args:
            entry_price: The planned entry price for the trade.
            stop_loss_price: The planned stop loss price for the trade.
            asset_multiplier: A multiplier for the asset's price (e.g., 1 for stocks,
                              contract size for futures/forex). Defaults to 1.0.

        Returns:
            The calculated position size (quantity). Returns 0.0 if calculation is
            not possible (e.g., zero price difference, invalid prices).
        """
        if stop_loss_price <= 0 or entry_price <= 0:
            logging.error('Entry price and stop loss price must be positive for position sizing.')
            return 0.0

        risk_per_trade_dollars = self.account_balance * self.risk_per_trade_percentage
        price_difference = abs(entry_price - stop_loss_price)

        if price_difference == 0:
            logging.warning('Entry price equals stop loss price. Cannot calculate position size.')
            return 0.0

        # Position size = (Risk per trade) / (Distance to stop loss * Asset Multiplier)
        position_size = risk_per_trade_dollars / (price_difference * asset_multiplier)
        logging.info(f'Calculated position size: {position_size:.2f} for entry {entry_price}, stop loss {stop_loss_price}')
        return position_size

    def determine_stop_loss(self, entry_price: float, stop_loss_distance_percentage: float = None, volatility: float = None) -> float:
        """
        Determines the stop loss price based on the entry price and either a
        percentage distance or a volatility measure.

        Args:
            entry_price: The entry price.
            stop_loss_distance_percentage: Optional. The percentage below the entry price
                                           for a long position, or above for a short
                                           position (e.g., 0.02 for 2%). Must be between 0 and 1.
            volatility: Optional. A measure of volatility (e.g., ATR value). The stop loss
                        will be set a multiple of this value away from the entry price.

        Returns:
            The calculated stop loss price, or np.nan if calculation is not possible
            (e.g., invalid inputs, no method specified).
        """
        if entry_price <= 0:
            logging.error('Entry price must be positive to determine stop loss.')
            return np.nan

        if stop_loss_distance_percentage is not None:
            if not (0 < stop_loss_distance_percentage < 1.0):
                logging.error('stop_loss_distance_percentage must be between 0 and 1.')
                return np.nan
            stop_loss_price = entry_price * (1 - stop_loss_distance_percentage)
            logging.info(f'Determined stop loss at: {stop_loss_price:.4f} based on percentage.')
            return stop_loss_price
        elif volatility is not None:
            # Example using volatility (e.g., multiples of ATR or standard deviation)
            # This is a simplified example; real implementation would need current volatility measure
            stop_loss_price = entry_price - (volatility * 1.5) # Example: 1.5 times volatility below entry
            if stop_loss_price <= 0:
                 logging.warning('Calculated stop loss is non-positive, setting to a small value above zero.')
                 stop_loss_price = entry_price * 0.95 # Arbitrary small value
            logging.info(f'Determined stop loss at: {stop_loss_price:.4f} based on volatility.')
            return stop_loss_price
        else:
            logging.warning('Neither stop_loss_distance_percentage nor volatility provided to determine stop loss.')
            return np.nan

    def determine_take_profit(self, entry_price: float, stop_loss_price: float, risk_reward_ratio: float) -> float:
        """
        Determines the take profit price based on the entry price, stop loss price,
        and desired risk/reward ratio.

        Args:
            entry_price: The entry price.
            stop_loss_price: The stop loss price.
            risk_reward_ratio: The desired risk/reward ratio (e.g., 2.0 for 1:2). Must be positive.

        Returns:
            The calculated take profit price, or np.nan if calculation is not possible
            (e.g., zero price difference, invalid inputs).
        """
        if entry_price <= 0 or stop_loss_price <= 0 or risk_reward_ratio <= 0:
            logging.error('Entry price, stop loss price, and risk_reward_ratio must be positive to determine take profit.')
            return np.nan

        price_difference = abs(entry_price - stop_loss_price)
        # Take profit distance = Risk distance * Risk/Reward Ratio
        take_profit_distance = price_difference * risk_reward_ratio

        if entry_price > stop_loss_price: # Long position
            take_profit_price = entry_price + take_profit_distance
        elif entry_price < stop_loss_price: # Short position
            take_profit_price = entry_price - take_profit_distance
            if take_profit_price < 0:
                 logging.warning('Calculated take profit for short is non-positive, setting to a small value above zero.')
                 take_profit_price = entry_price * 0.05 # Arbitrary small value
        else:
            logging.warning('Entry price equals stop loss price. Cannot determine take profit.')
            return np.nan

        logging.info(f'Determined take profit at: {take_profit_price:.4f} for entry {entry_price}, stop loss {stop_loss_price}, R:R {risk_reward_ratio}')
        return take_profit_price

    def update_trailing_stop(self, current_price: float, trailing_stop_level: float, long_position: bool) -> float:
        """
        Updates the trailing stop level based on the current price.

        This is a placeholder implementation using a simple percentage trail.
        More sophisticated trailing stop logic (e.g., based on volatility,
        moving averages) can be implemented here.

        Args:
            current_price: The current market price of the asset.
            trailing_stop_level: The current active trailing stop level.
            long_position: True if it's a long position, False if short.

        Returns:
            The new trailing stop level. Returns the original level if no update
            is triggered by the current price.
        """
        # This method would be called periodically with the latest price
        # The trailing_stop_level is the current stop level that needs potential adjustment
        if long_position:
            # For a long position, the stop moves up as price increases
            new_trailing_stop = max(trailing_stop_level, current_price * 0.98) # Example: Trail by 2% below current price
            if new_trailing_stop > trailing_stop_level:
                logging.info(f'Trailing stop for long updated from {trailing_stop_level:.4f} to {new_trailing_stop:.4f}')
                return new_trailing_stop
        else: # Short position
            # For a short position, the stop moves down as price decreases
            new_trailing_stop = min(trailing_stop_level, current_price * 1.02) # Example: Trail by 2% above current price
            if new_trailing_stop < trailing_stop_level:
                 logging.info(f'Trailing stop for short updated from {trailing_stop_level:.4f} to {new_trailing_stop:.4f}')
                 return new_trailing_stop

        # If no update, return the original trailing stop level
        return trailing_stop_level


    def check_daily_risk_limit(self) -> bool:
        """
        Checks if the daily maximum loss limit has been reached.

        Returns:
            True if the daily loss is within the limit, False otherwise.
        """
        daily_risk_limit_dollars = self.initial_balance * self.daily_risk_limit_percentage
        if self.daily_loss_incurred >= daily_risk_limit_dollars:
            logging.warning(f'Daily risk limit reached. Total daily loss: {self.daily_loss_incurred:.2f}, Limit: {daily_risk_limit_dollars:.2f}')
            return False # Limit reached, trading should stop
        logging.info(f'Daily risk limit not reached. Total daily loss: {self.daily_loss_incurred:.2f}, Limit: {daily_risk_limit_dollars:.2f}')
        return True # Limit not reached, trading can continue

    def update_daily_loss(self, loss_amount: float):
        """
        Updates the total daily loss incurred.

        This method should be called after a losing trade is closed.

        Args:
            loss_amount: The amount of loss from the closed trade (should be positive).
        """
        if loss_amount > 0:
            self.daily_loss_incurred += loss_amount
            self.account_balance -= loss_amount # Update account balance after a loss
            logging.info(f'Daily loss updated by {loss_amount:.2f}. Total daily loss incurred: {self.daily_loss_incurred:.2f}')
            logging.info(f'Account balance updated to: {self.account_balance:.2f}')
        elif loss_amount < 0:
            logging.warning('Loss amount should be positive. Use update_daily_profit for gains.')


    def reset_daily_loss(self):
        """
        Resets the daily loss counter and updates the initial balance for the day.

        This method should be called at the beginning of each new trading day.
        """
        self.daily_loss_incurred = 0.0
        # Note: Account balance is not reset here, it reflects the current balance
        # You might want to reset initial_balance if account_balance changes significantly day-to-day
        self.initial_balance = self.account_balance # Reset initial balance for next day's limit calculation
        logging.info('Daily loss reset.')
