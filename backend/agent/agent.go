package agent

import (
	"log"
	"sync"
	"time"

	"aionvanguard/backend/broker"
	"aionvanguard/backend/data"
	"aionvanguard/backend/risk"
	"aionvanguard/backend/strategy"

	"github.com/alpacahq/alpaca-trade-api-go/v2/alpaca"
	"github.com/gorilla/websocket"
)

// TradingAgent is the core of the trading bot.
type TradingAgent struct {
	Config         *Config
	Broker         *broker.AlpacaBroker
	DataFetcher    *data.FinnhubFetcher
	Strategy       *strategy.CombinedStrategy
	RiskManager    *risk.Manager
	Conn           *websocket.Conn
	isRunning      bool
	mu             sync.Mutex
	stopChan       chan struct{}
}

// Config holds the configuration for the trading agent.
type Config struct {
	Symbols         []string
	RiskPerTrade    float64
	RiskRewardRatio float64
	TimeBasedExit   int
}

// NewTradingAgent creates and configures a new TradingAgent.
func NewTradingAgent(config *Config, conn *websocket.Conn) *TradingAgent {
	return &TradingAgent{
		Config:      config,
		Broker:      broker.NewAlpacaBroker(),
		DataFetcher: data.NewFinnhubFetcher(),
		Strategy:    strategy.NewCombinedStrategy(20, 50, 14, 70, 30),
		RiskManager: risk.NewManager(10000.0, config.RiskPerTrade/100, 0.05),
		Conn:        conn,
		stopChan:    make(chan struct{}),
	}
}

// Start begins the trading loop.
func (a *TradingAgent) Start() {
	a.mu.Lock()
	if a.isRunning {
		a.mu.Unlock()
		log.Println("Agent is already running.")
		return
	}
	a.isRunning = true
	a.mu.Unlock()

	go a.runTradingLoop()
}

// Stop halts the trading loop.
func (a *TradingAgent) Stop() {
	a.mu.Lock()
	if !a.isRunning {
		a.mu.Unlock()
		log.Println("Agent is not running.")
		return
	}
	close(a.stopChan)
	a.isRunning = false
	a.mu.Unlock()
}

func (a *TradingAgent) runTradingLoop() {
	log.Println("Trading loop started.")
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-a.stopChan:
			log.Println("Trading loop stopped.")
			return
		case <-ticker.C:
			a.trade()
		}
	}
}

func (a *TradingAgent) trade() {
	account, err := a.Broker.GetAccount()
	if err != nil {
		log.Println("Error getting account:", err)
		return
	}
	balance, _ := account.Equity.Float64()
	a.RiskManager.UpdateAccountBalance(balance)

	for _, symbol := range a.Config.Symbols {
		a.processSymbol(symbol)
	}
}

func (a *TradingAgent) processSymbol(symbol string) {
	now := time.Now()
	// Fetch more data for better indicator calculation
	then := now.AddDate(0, 0, -30)

	candles, err := a.DataFetcher.FetchHistoricalData(symbol, "D", then, now)
	if err != nil {
		log.Printf("Error fetching data for %s: %v", symbol, err)
		return
	}

	signal := a.Strategy.GenerateSignal(candles.C)
	if signal == strategy.Hold {
		return
	}

	entryPrice := candles.C[len(candles.C)-1]
	stopLossPrice := entryPrice * (1 - 0.02)
	if signal == strategy.Sell {
		stopLossPrice = entryPrice * (1 + 0.02)
	}

	positionSize := a.RiskManager.CalculatePositionSize(entryPrice, stopLossPrice)
	if positionSize > 0 {
		side := alpaca.Buy
		if signal == strategy.Sell {
			side = alpaca.Sell
		}

		_, err := a.Broker.PlaceOrder(symbol, positionSize, side, alpaca.Market, alpaca.GTC)
		if err != nil {
			log.Printf("Error placing order for %s: %v", symbol, err)
		}
	}
}
