from .base_executor import BaseExecutor
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv
import logging
import pandas as pd

load_dotenv()

class AlpacaExecutor(BaseExecutor):
    """
    Order executor specifically for the Alpaca trading platform.

    Implements the BaseExecutor interface using the Alpaca REST API.
    Requires API_KEY, API_SECRET, and optionally
    BASE_URL.
    """
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://paper-api.alpaca.markets'):
        """
        Initializes the AlpacaExecutor by taking API credentials and
        establishing a REST API connection.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        if not self.api_key or not self.api_secret:
            raise ValueError('Alpaca API key and secret must be provided.')
        try:
            self.api = REST(self.api_key, self.api_secret, self.base_url)
            logging.info('AlpacaExecutor initialized successfully.')
        except Exception as e:
            logging.error(f'Failed to initialize Alpaca REST API: {e}')
            raise

    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None, stop_loss: float = None, take_profit: float = None):
        """
        Places a trade order with Alpaca. Supports market and limit orders,
        and bracket orders with stop loss and take profit.

        Args:
            symbol: The trading symbol.
            order_type: The type of order ('market' or 'limit'). Case-insensitive.
            quantity: The quantity of shares/contracts. Positive for buy, negative for sell.
            price: Optional. The limit price for 'limit' orders. Ignored for 'market' orders.
            stop_loss: Optional. The stop loss price. Can be included in a bracket order.
            take_profit: Optional. The take profit price. Can be included in a bracket order.

        Returns:
            The Alpaca order object ID (a string) if successful, None otherwise.
        """
        try:
            # Basic validation
            if quantity == 0:
                logging.warning(f'Invalid quantity {quantity} for order on {symbol}.')
                return None

            side = 'buy' if quantity > 0 else 'sell'
            qty = abs(quantity)

            order_params = {
                'symbol': symbol,
                'qty': qty,
                'type': order_type.lower(),
                'side': side,
                'time_in_force': 'gtc' # Good 'Til Cancelled
            }

            if order_type.lower() == 'limit' and price is not None:
                 order_params['limit_price'] = price
            elif order_type.lower() == 'market' and price is not None:
                 logging.warning('Price specified for market order, ignoring.')
            elif order_type.lower() == 'limit' and price is None:
                 logging.error('Limit order requires a price.')
                 return None


            # Add stop loss and take profit if provided (as OTO or OCO - depends on broker support)
            # Alpaca supports bracket orders (OTOCO: One Triggers OCO (One Cancels Other))
            if stop_loss is not None or take_profit is not None:
                 order_params['order_class'] = 'bracket'
                 if take_profit is not None:
                      order_params['take_profit'] = {'limit_price': take_profit}
                 if stop_loss is not None:
                      order_params['stop_loss'] = {'stop_price': stop_loss}


            order = self.api.submit_order(**order_params)
            logging.info(f'Placed {order_type} order for {quantity} shares of {symbol}. Order ID: {order.id}')
            return order.id
        except Exception as e:
            logging.error(f'Error placing order for {symbol}: {e}')
            return None

    def modify_order(self, order_id: str, new_quantity: float = None, new_price: float = None, new_stop_loss: float = None, new_take_profit: float = None):
        """
        Modifies an existing open order on Alpaca.

        Args:
            order_id: The ID of the order to modify.
            new_quantity: Optional. The new quantity.
            new_price: Optional. The new limit price (for limit orders).
            new_stop_loss: Optional. The new stop loss price (for bracket orders).
            new_take_profit: Optional. The new take profit price (for bracket orders).

        Returns:
            True if the modification request was successful, False otherwise.
        """
        try:
            update_params = {}
            if new_quantity is not None: update_params['qty'] = new_quantity
            if new_price is not None: update_params['limit_price'] = new_price
            if new_stop_loss is not None: update_params['stop_loss'] = {'stop_price': new_stop_loss}
            if new_take_profit is not None: update_params['take_profit'] = {'limit_price': new_take_profit}

            if not update_params:
                logging.warning(f'No valid parameters provided to modify order {order_id}.')
                return False

            self.api.replace_order(order_id, **update_params)
            logging.info(f'Modified order {order_id} with updates: {update_params}')
            return True
        except Exception as e:
            logging.error(f'Error modifying order {order_id}: {e}')
            return False

    def cancel_order(self, order_id: str):
        """
        Cancels an existing open order on Alpaca.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            True if the cancellation request was successful, False otherwise.
        """
        try:
            self.api.cancel_order(order_id)
            logging.info(f'Cancelled order {order_id}.')
            return True
        except Exception as e:
            logging.error(f'Error cancelling order {order_id}: {e}')
            return False

    def get_account_balance(self) -> float:
        """
        Retrieves the current account equity from Alpaca.

        Returns:
            The account equity as a float, or 0.0 if fetching fails.
        """
        try:
            account = self.api.get_account()
            balance = float(account.equity)
            logging.info(f'Fetched account balance: {balance:.2f}')
            return balance
        except Exception as e:
            logging.error(f'Error fetching account balance: {e}')
            return 0.0

    def get_open_positions(self) -> pd.DataFrame:
        """
        Retrieves a list of currently open positions from Alpaca.

        Returns:
            A pandas DataFrame with details of open positions (symbol, quantity,
            side, average entry price, market value, unrealized P/L), or an empty
            DataFrame if fetching fails or no positions are open.
        """
        try:
            positions = self.api.list_positions()
            if not positions:
                logging.info('No open positions found.')
                return pd.DataFrame()

            positions_data = []
            for pos in positions:
                positions_data.append({
                    'symbol': pos.symbol,
                    'quantity': float(pos.qty),
                    'side': pos.side,
                    'avg_entry_price': float(pos.avg_entry_price),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                })

            df = pd.DataFrame(positions_data)
            logging.info(f'Fetched {len(positions)} open positions.')
            return df
        except Exception as e:
            logging.error(f'Error fetching open positions: {e}')
            return pd.DataFrame()
