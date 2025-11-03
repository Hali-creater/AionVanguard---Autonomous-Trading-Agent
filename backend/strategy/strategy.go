package strategy

import (
	"log"

	"github.com/markcheno/go-talib"
)

// Signal represents a trading signal.
type Signal string

const (
	// Buy represents a buy signal.
	Buy Signal = "BUY"
	// Sell represents a sell signal.
	Sell Signal = "SELL"
	// Hold represents a hold signal.
	Hold Signal = "HOLD"
)

// CombinedStrategy implements a trading strategy that combines a Moving Average
// Crossover with an RSI filter for confirmation.
type CombinedStrategy struct {
	ShortWindow    int
	LongWindow     int
	RSIWindow      int
	RSIOverbought  float64
	RSIOversold    float64
}

// NewCombinedStrategy creates and configures a new CombinedStrategy.
func NewCombinedStrategy(shortWindow, longWindow, rsiWindow int, rsiOverbought, rsiOversold float64) *CombinedStrategy {
	return &CombinedStrategy{
		ShortWindow:    shortWindow,
		LongWindow:     longWindow,
		RSIWindow:      rsiWindow,
		RSIOverbought:  rsiOverbought,
		RSIOversold:    rsiOversold,
	}
}

// GenerateSignal generates a trading signal based on the provided historical data.
func (s *CombinedStrategy) GenerateSignal(closePrices []float64) Signal {
	if len(closePrices) < s.LongWindow {
		log.Println("Not enough data to generate a signal.")
		return Hold
	}

	// Calculate indicators
	shortSMA := talib.Sma(closePrices, s.ShortWindow)
	longSMA := talib.Sma(closePrices, s.LongWindow)
	rsi := talib.Rsi(closePrices, s.RSIWindow)

	// Get the latest values
	latestShortSMA := shortSMA[len(shortSMA)-1]
	previousShortSMA := shortSMA[len(shortSMA)-2]
	latestLongSMA := longSMA[len(longSMA)-1]
	previousLongSMA := longSMA[len(longSMA)-2]
	latestRSI := rsi[len(rsi)-1]

	// Buy Condition: Bullish Crossover + RSI Confirmation
	isBullishCrossover := previousShortSMA <= previousLongSMA && latestShortSMA > latestLongSMA
	if isBullishCrossover && latestRSI < s.RSIOverbought {
		log.Printf("BUY signal: Bullish crossover and RSI (%.2f) is below %.2f.", latestRSI, s.RSIOverbought)
		return Buy
	}

	// Sell Condition: Bearish Crossover + RSI Confirmation
	isBearishCrossover := previousShortSMA >= previousLongSMA && latestShortSMA < latestLongSMA
	if isBearishCrossover && latestRSI > s.RSIOversold {
		log.Printf("SELL signal: Bearish crossover and RSI (%.2f) is above %.2f.", latestRSI, s.RSIOversold)
		return Sell
	}

	return Hold
}
