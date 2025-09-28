import logging
from typing import Optional, Dict

from .base_broker import BaseBroker
from .alpaca_integration import AlpacaBroker

def create_broker(config: Dict) -> Optional[BaseBroker]:
    """
    Factory function to create a broker instance based on configuration.

    Args:
        config (Dict): The configuration dictionary. Must contain 'broker' key
                       and the necessary API keys.

    Returns:
        An instance of a class that implements BaseBroker, or None if the
        broker is not supported or configuration is missing.
    """
    broker_name = config.get("broker")
    if not broker_name:
        logging.error("Broker name not specified in configuration.")
        return None

    logging.info(f"Creating broker for: {broker_name}")

    if broker_name.lower() == "alpaca":
        api_key = config.get("alpaca_api_key")
        api_secret = config.get("alpaca_api_secret")
        paper_trading = config.get("paper_trading", True)

        if not api_key or not api_secret:
            logging.error("Alpaca API key or secret not provided in configuration.")
            return None

        try:
            return AlpacaBroker(api_key=api_key, api_secret=api_secret, paper_trading=paper_trading)
        except Exception as e:
            logging.error(f"Failed to instantiate AlpacaBroker: {e}")
            return None

    # Placeholder for other brokers
    # elif broker_name.lower() == "binance":
    #     # ... implementation for Binance
    #     pass

    else:
        logging.error(f"Broker '{broker_name}' is not supported.")
        return None