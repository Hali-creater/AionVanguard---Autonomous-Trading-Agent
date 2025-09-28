---
title: AionVanguard - Autonomous Trading Agent
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.30.0"
app_file: streamlit_app.py
pinned: false
---

# AionVanguard - Autonomous Trading Agent

This project is an autonomous trading agent designed to execute trades based on a robust technical analysis strategy. It features a decoupled, multi-threaded architecture and a responsive user interface built with Streamlit for easy monitoring and control.

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Hali-creater/AionVanguard&branch=main&mainModule=streamlit_app.py)

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Deployment to Streamlit Cloud](#deployment-to-streamlit-cloud)
- [Local Setup](#local-setup)
- [Configuration](#configuration)
- [Code Structure](#code-structure)
- [Testing](#testing)

## Overview

AionVanguard is a Python-based autonomous trading agent. It uses a **Moving Average (MA) Crossover strategy combined with a Relative Strength Index (RSI) filter** to identify trading opportunities. The agent is designed for robustness and maintainability, with a clear separation between its core logic and the user interface.

## Architecture

The agent is built with a modern, decoupled architecture to ensure stability and responsiveness:
- **Multi-Threaded Design:** The core `TradingAgent` runs in a separate background thread from the Streamlit UI. This ensures that the agent's long-running tasks (like fetching data and checking for signals) do not block or freeze the user interface.
- **Message Queue Communication:** The background agent communicates with the front-end via a thread-safe message queue (`queue.Queue`). This allows the agent to send logs, status updates, and position changes to the UI in a safe and organized manner.
- **Decoupled Logic:** The agent's core logic (`agent.py`) is completely independent of the Streamlit framework, making it easier to test, maintain, and potentially reuse in other applications.

## Features

- **Core Strategy:** A classic and effective **Moving Average Crossover with RSI Filter**.
    - A "BUY" signal is generated when the short-term MA crosses above the long-term MA, provided the RSI is not in overbought territory.
    - A "SELL" signal is generated when the short-term MA crosses below the long-term MA, provided the RSI is not in oversold territory.
- **Risk Management:** Implements position sizing, stop loss, take profit, and daily risk limits.
- **Broker Flexibility:** Modular design allows for integration with brokers like Alpaca, Binance, etc. (Currently, Alpaca is implemented).
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
├── streamlit_app.py
└── autonomous_trading_agent/
    ├── __init__.py
    ├── agent.py                 <-- Core agent logic
    ├── adaptability/
    ├── broker_integration/
    ├── data_fetching/
    ├── execution/
    ├── risk_management/
    ├── strategy/
    └── tests/
```

## Testing

The project includes a `tests/` directory with robust unit and integration tests. Run tests using `pytest` from the project root. It is recommended to run it as a Python module to ensure it uses the correct environment.
```bash
python3 -m pytest
```
