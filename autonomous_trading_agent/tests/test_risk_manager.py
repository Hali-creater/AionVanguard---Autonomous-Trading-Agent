import unittest
import pandas as pd
import numpy as np
from autonomous_trading_agent.risk_management.risk_manager import RiskManager

import logging
logging.basicConfig(level=logging.CRITICAL)

class TestRiskManager(unittest.TestCase):
    """
    Unit tests for the RiskManager class.
    """
    def setUp(self):
        """
        Set up test environment before each test method.
        Initializes the RiskManager with standard parameters.
        """
        self.initial_balance = 10000.0
        self.risk_per_trade = 0.01 # 1%
        self.daily_risk_limit = 0.05 # 5%
        self.risk_manager = RiskManager(
            account_balance=self.initial_balance,
            risk_per_trade_percentage=self.risk_per_trade,
            daily_risk_limit_percentage=self.daily_risk_limit
        )

    def test_initialization(self):
        """
        Tests if the RiskManager is initialized with the correct parameters.
        """
        self.assertEqual(self.risk_manager.account_balance, self.initial_balance)
        self.assertEqual(self.risk_manager.initial_balance, self.initial_balance)
        self.assertEqual(self.risk_manager.risk_per_trade_percentage, self.risk_per_trade)
        self.assertEqual(self.risk_manager.daily_risk_limit_percentage, self.daily_risk_limit)
        self.assertEqual(self.risk_manager.daily_loss_incurred, 0.0)

    def test_initialization_invalid_risk_per_trade(self):
        """
        Tests if ValueError is raised for invalid risk_per_trade_percentage during initialization.
        """
        with self.assertRaises(ValueError):
            RiskManager(account_balance=10000.0, risk_per_trade_percentage=1.5, daily_risk_limit_percentage=0.05)
        with self.assertRaises(ValueError):
            RiskManager(account_balance=10000.0, risk_per_trade_percentage=0.0, daily_risk_limit_percentage=0.05)

    def test_initialization_invalid_daily_risk_limit(self):
        """
        Tests if ValueError is raised for invalid daily_risk_limit_percentage during initialization.
        """
        with self.assertRaises(ValueError):
            RiskManager(account_balance=10000.0, risk_per_trade_percentage=0.01, daily_risk_limit_percentage=1.2)
        with self.assertRaises(ValueError):
            RiskManager(account_balance=10000.0, risk_per_trade_percentage=0.01, daily_risk_limit_percentage=0.0)

    def test_initialization_invalid_account_balance(self):
        """
        Tests if ValueError is raised for invalid account_balance during initialization.
        """
        with self.assertRaises(ValueError):
            RiskManager(account_balance=0.0, risk_per_trade_percentage=0.01, daily_risk_limit_percentage=0.05)
        with self.assertRaises(ValueError):
            RiskManager(account_balance=-1000.0, risk_per_trade_percentage=0.01, daily_risk_limit_percentage=0.05)


    def test_calculate_position_size(self):
        """
        Tests the calculation of position size for a long trade.
        """
        entry_price = 100.0
        stop_loss_price = 99.0
        expected_risk_dollars = self.initial_balance * self.risk_per_trade
        price_difference = entry_price - stop_loss_price
        expected_position_size = expected_risk_dollars / price_difference
        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss_price)
        self.assertAlmostEqual(position_size, expected_position_size)

    def test_calculate_position_size_short(self):
        """
        Tests the calculation of position size for a short trade.
        """
        entry_price = 100.0
        stop_loss_price = 101.0
        expected_risk_dollars = self.initial_balance * self.risk_per_trade
        price_difference = stop_loss_price - entry_price
        expected_position_size = expected_risk_dollars / price_difference
        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss_price)
        self.assertAlmostEqual(position_size, expected_position_size)

    def test_calculate_position_size_zero_price_difference(self):
        """
        Tests position size calculation when entry and stop loss prices are the same.
        Should return 0.
        """
        position_size = self.risk_manager.calculate_position_size(100.0, 100.0)
        self.assertEqual(position_size, 0.0)

    def test_calculate_position_size_zero_prices(self):
        """
        Tests position size calculation with zero or negative entry/stop loss prices.
        Should return 0.
        """
        position_size = self.risk_manager.calculate_position_size(0.0, 10.0)
        self.assertEqual(position_size, 0.0)
        position_size = self.risk_manager.calculate_position_size(10.0, 0.0)
        self.assertEqual(position_size, 0.0)
        position_size = self.risk_manager.calculate_position_size(-10.0, -5.0)
        self.assertEqual(position_size, 0.0)


    def test_determine_stop_loss_percentage(self):
        """
        Tests stop loss determination based on a percentage from the entry price.
        """
        entry_price = 100.0
        stop_loss_percentage = 0.02
        expected_stop_loss = entry_price * (1 - stop_loss_percentage)
        stop_loss = self.risk_manager.determine_stop_loss(entry_price, stop_loss_distance_percentage=stop_loss_percentage)
        self.assertAlmostEqual(stop_loss, expected_stop_loss)

    def test_determine_stop_loss_percentage_invalid(self):
        """
        Tests stop loss determination with an invalid percentage (<= 0 or >= 1).
        Should return NaN.
        """
        stop_loss = self.risk_manager.determine_stop_loss(100.0, stop_loss_distance_percentage=1.5)
        self.assertTrue(np.isnan(stop_loss))
        stop_loss = self.risk_manager.determine_stop_loss(100.0, stop_loss_distance_percentage=0.0)
        self.assertTrue(np.isnan(stop_loss))


    def test_determine_stop_loss_volatility(self):
        """
        Tests stop loss determination based on a volatility measure (using placeholder logic).
        """
        entry_price = 100.0
        volatility = 2.0
        expected_stop_loss = entry_price - (volatility * 1.5)
        stop_loss = self.risk_manager.determine_stop_loss(entry_price, volatility=volatility)
        self.assertAlmostEqual(stop_loss, expected_stop_loss)

    def test_determine_stop_loss_volatility_non_positive(self):
        """
        Tests stop loss determination based on volatility when the calculated SL is non-positive.
        Should return a small positive value based on the fallback logic.
        """
        entry_price = 10.0
        volatility = 10.0
        stop_loss = self.risk_manager.determine_stop_loss(entry_price, volatility=volatility)
        self.assertTrue(stop_loss > 0)
        self.assertAlmostEqual(stop_loss, entry_price * 0.95)


    def test_determine_stop_loss_no_params(self):
        """
        Tests stop loss determination when no method (percentage or volatility) is specified.
        Should return NaN.
        """
        stop_loss = self.risk_manager.determine_stop_loss(100.0)
        self.assertTrue(np.isnan(stop_loss))

    def test_determine_stop_loss_zero_entry_price(self):
        """
        Tests stop loss determination with a zero entry price.
        Should return NaN.
        """
        stop_loss = self.risk_manager.determine_stop_loss(0.0, stop_loss_distance_percentage=0.01)
        self.assertTrue(np.isnan(stop_loss))


    def test_determine_take_profit_long(self):
        """
        Tests take profit determination for a long trade.
        """
        entry_price = 100.0
        stop_loss_price = 99.0
        risk_reward_ratio = 2.0
        risk_distance = entry_price - stop_loss_price
        expected_take_profit = entry_price + (risk_distance * risk_reward_ratio)
        take_profit = self.risk_manager.determine_take_profit(entry_price, stop_loss_price, risk_reward_ratio)
        self.assertAlmostEqual(take_profit, expected_take_profit)

    def test_determine_take_profit_short(self):
        """
        Tests take profit determination for a short trade.
        """
        entry_price = 100.0
        stop_loss_price = 101.0
        risk_reward_ratio = 2.0
        risk_distance = stop_loss_price - entry_price
        expected_take_profit = entry_price - (risk_distance * risk_reward_ratio)
        take_profit = self.risk_manager.determine_take_profit(entry_price, stop_loss_price, risk_reward_ratio)
        self.assertAlmostEqual(take_profit, expected_take_profit)


    def test_determine_take_profit_short_non_positive(self):
        """
        Tests take profit determination for a short trade when the calculated TP is non-positive.
        Should return a small positive value based on the fallback logic.
        """
        entry_price = 10.0
        stop_loss_price = 12.0
        risk_reward_ratio = 10.0
        take_profit = self.risk_manager.determine_take_profit(entry_price, stop_loss_price, risk_reward_ratio)
        self.assertTrue(take_profit > 0)
        self.assertAlmostEqual(take_profit, entry_price * 0.05)


    def test_determine_take_profit_zero_prices_or_ratio(self):
        """
        Tests take profit determination with zero or invalid inputs (prices, ratio, or zero price difference).
        Should return NaN.
        """
        take_profit = self.risk_manager.determine_take_profit(0.0, 99.0, 2.0)
        self.assertTrue(np.isnan(take_profit))
        take_profit = self.risk_manager.determine_take_profit(100.0, 0.0, 2.0)
        self.assertTrue(np.isnan(take_profit))
        take_profit = self.risk_manager.determine_take_profit(100.0, 99.0, 0.0)
        self.assertTrue(np.isnan(take_profit))
        take_profit = self.risk_manager.determine_take_profit(100.0, 100.0, 2.0)
        self.assertTrue(np.isnan(take_profit))


    def test_update_trailing_stop_long(self):
        """
        Tests trailing stop update logic for a long position.
        """
        current_stop = 98.0
        current_price_higher = 105.0
        expected_new_stop = 102.9
        new_stop = self.risk_manager.update_trailing_stop(current_price_higher, current_stop, long_position=True)
        self.assertAlmostEqual(new_stop, expected_new_stop)

        current_price_lower = 100.0
        expected_new_stop = 98.0
        new_stop = self.risk_manager.update_trailing_stop(current_price_lower, current_stop, long_position=True)
        self.assertAlmostEqual(new_stop, expected_new_stop)


    def test_update_trailing_stop_short(self):
        """
        Tests trailing stop update logic for a short position.
        """
        current_stop = 102.0
        current_price_lower = 95.0
        expected_new_stop = 96.9
        new_stop = self.risk_manager.update_trailing_stop(current_price_lower, current_stop, long_position=False)
        self.assertAlmostEqual(new_stop, expected_new_stop)

        current_price_higher = 100.0
        expected_new_stop = 102.0
        new_stop = self.risk_manager.update_trailing_stop(current_price_higher, current_stop, long_position=False)
        self.assertAlmostEqual(new_stop, expected_new_stop)


    def test_check_daily_risk_limit_not_reached(self):
        """
        Tests if the daily risk limit check returns True when the limit is not reached.
        """
        self.risk_manager.daily_loss_incurred = self.initial_balance * (self.daily_risk_limit - 0.01)
        self.assertTrue(self.risk_manager.check_daily_risk_limit())

    def test_check_daily_risk_limit_reached(self):
        """
        Tests if the daily risk limit check returns False when the limit is reached or exceeded.
        """
        self.risk_manager.daily_loss_incurred = self.initial_balance * self.daily_risk_limit
        self.assertFalse(self.risk_manager.check_daily_risk_limit())

        self.risk_manager.daily_loss_incurred = self.initial_balance * (self.daily_risk_limit + 0.01)
        self.assertFalse(self.risk_manager.check_daily_risk_limit())


    def test_update_daily_loss(self):
        """
        Tests updating the daily loss incurred and account balance.
        """
        initial_balance = self.risk_manager.account_balance
        loss1 = 50.0
        self.risk_manager.update_daily_loss(loss1)
        self.assertAlmostEqual(self.risk_manager.daily_loss_incurred, loss1)
        self.assertAlmostEqual(self.risk_manager.account_balance, initial_balance - loss1)

        loss2 = 30.0
        self.risk_manager.update_daily_loss(loss2)
        self.assertAlmostEqual(self.risk_manager.daily_loss_incurred, loss1 + loss2)
        self.assertAlmostEqual(self.risk_manager.account_balance, initial_balance - loss1 - loss2)

    def test_update_daily_loss_zero_or_negative(self):
        """
        Tests updating daily loss with zero or negative values (should not increase loss).
        """
        initial_loss = self.risk_manager.daily_loss_incurred
        initial_balance = self.risk_manager.account_balance
        self.risk_manager.update_daily_loss(0.0)
        self.assertAlmostEqual(self.risk_manager.daily_loss_incurred, initial_loss)
        self.assertAlmostEqual(self.risk_manager.account_balance, initial_balance)
        self.risk_manager.update_daily_loss(-10.0)
        self.assertAlmostEqual(self.risk_manager.daily_loss_incurred, initial_loss)
        self.assertAlmostEqual(self.risk_manager.account_balance, initial_balance)


    def test_reset_daily_loss(self):
        """
        Tests resetting the daily loss counter and updating the initial balance for the day.
        """
        self.risk_manager.daily_loss_incurred = 100.0
        self.risk_manager.account_balance -= 100.0
        current_balance = self.risk_manager.account_balance
        self.risk_manager.reset_daily_loss()
        self.assertEqual(self.risk_manager.daily_loss_incurred, 0.0)
        self.assertEqual(self.risk_manager.initial_balance, current_balance)
