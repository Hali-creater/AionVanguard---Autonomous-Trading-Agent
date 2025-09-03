# AionVanguard - Autonomous Trading Agent

This project is an autonomous trading agent designed to execute trades based on a combination of technical analysis strategies. It features a modular architecture and a user interface built with Streamlit for easy monitoring and control.

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Hali-creater/AionVanguard&branch=main&mainModule=streamlit_app.py)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Deployment to Streamlit Cloud](#deployment-to-streamlit-cloud)
- [Local Setup](#local-setup)
- [Configuration](#configuration)
- [Code Structure](#code-structure)
- [Testing](#testing)

## Overview

AionVanguard is a Python-based autonomous trading agent. It uses a combination of strategies to identify trading opportunities and includes modules for risk management, broker integration, and dynamic adaptation to market conditions.

## Features

- **Core Strategy:** Combines PVG (Price-Volume-Gradient), SMC (Smart Money Concepts), and TPR (Trend-Pullback-Reversal) analysis.
- **Risk Management:** Implements position sizing, stop loss, take profit, and daily risk limits.
- **Broker Flexibility:** Modular design allows for integration with brokers like Alpaca, Binance, etc.
- **Live Dashboard:** A Streamlit-based UI for real-time monitoring, control, and performance tracking.

## Deployment to Streamlit Cloud

The easiest way to deploy this application is using Streamlit Cloud, which integrates directly with your GitHub repository.

1.  **Click the Deploy Button:** Click the "Deploy to Streamlit Cloud" button at the top of this README.
2.  **Connect Your Account:** If you haven't already, you'll be prompted to connect your GitHub account to Streamlit Cloud.
3.  **Deploy:** Follow the on-screen instructions. Streamlit Cloud will automatically detect the repository and the `streamlit_app.py` file and deploy the application.
4.  **Add Secrets:** Once deployed, you will need to add your broker API keys as secrets in the Streamlit Cloud settings for your app. Go to your app's settings (`...` -> `Settings` -> `Secrets`) and add your keys (e.g., `ALPACA_API_KEY_ID`, `ALPACA_API_SECRET_KEY`).

## Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hali-creater/AionVanguard.git
    cd AionVanguard
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the Dashboard:**
    ```bash
    streamlit run streamlit_app.py
    ```

## Configuration

The agent is configured using environment variables. For local development, you can create a `.env` file in the project root. For Streamlit Cloud deployment, use the built-in Secrets management.

**Example `.env` file:**
```ini
# --- Broker Configuration ---
BROKER=Alpaca
ALPACA_API_KEY_ID=YOUR_ALPACA_API_KEY_ID
ALPACA_API_SECRET_KEY=YOUR_ALPACA_API_SECRET_KEY
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

## Code Structure
```
.
├── README.md
├── requirements.txt
├── .env.example
├── streamlit_app.py
└── autonomous_trading_agent/
    ├── __init__.py
    ├── adaptability/
    ├── broker_integration/
    ├── data_fetching/
    ├── execution/
    ├── risk_management/
    ├── strategy/
    └── tests/
```

## Testing

The project includes a `tests/` directory with unit tests. Run tests using `pytest` from the project root:
```bash
pytest
```
