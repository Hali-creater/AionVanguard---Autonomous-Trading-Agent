---
title: AionVanguard - Autonomous Trading Agent
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.49.0
app_file: app.py
pinned: false
---

# AionVanguard - Autonomous Trading Agent

This project is an autonomous trading agent designed to execute trades based on a robust technical analysis strategy. It features a decoupled, multi-threaded architecture and a responsive user interface built with Streamlit for easy monitoring and control.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Deployment to Hugging Face Spaces](#deployment-to-hugging-face-spaces)
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

## Deployment to Hugging Face Spaces

This application can be deployed to Hugging Face Spaces.

1.  **Create a new Space:** Go to [huggingface.co/new-space](https://huggingface.co/new-space) to create a new Space.
2.  **Configure the Space:**
    -   **Owner:** Your Hugging Face username or organization.
    -   **Space name:** A name for your project (e.g., `aionvanguard-trading-agent`).
    -   **License:** Choose a license (e.g., `Apache-2.0`).
    -   **Space SDK:** Select **Streamlit**.
    -   **Space hardware:** Choose the appropriate hardware. The free tier is likely sufficient.
    -   **Public/Private:** Choose whether your Space will be public or private.
3.  **Upload the code:** Upload the files from this repository to your new Hugging Face Space.
4.  **Add Secrets:** Once deployed, you will need to add your broker API keys as secrets in the Space settings. Go to your Space's settings (`Settings` -> `Secrets`) and add your keys (e.g., `API_KEY`, `API_SECRET`). The application will read these from the UI.

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
    streamlit run app.py
    ```

## Configuration

The agent is configured via the Streamlit UI. For local development, the UI will prompt for API keys. For Hugging Face Spaces deployment, you can store these as secrets in your Space's settings.

## Code Structure
```
.
├── README.md
├── requirements.txt
├── app.py
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
