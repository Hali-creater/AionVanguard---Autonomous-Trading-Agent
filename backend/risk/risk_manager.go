package risk

import (
	"log"
	"math"
)

// Manager handles trading risk based on predefined rules.
type Manager struct {
	AccountBalance          float64
	RiskPerTradePercentage  float64
	DailyRiskLimitPercentage float64
	DailyLossIncurred       float64
}

// NewManager creates and configures a new RiskManager.
func NewManager(accountBalance, riskPerTradePercentage, dailyRiskLimitPercentage float64) *Manager {
	return &Manager{
		AccountBalance:          accountBalance,
		RiskPerTradePercentage:  riskPerTradePercentage,
		DailyRiskLimitPercentage: dailyRiskLimitPercentage,
	}
}

// CalculatePositionSize determines the appropriate position size for a trade.
func (m *Manager) CalculatePositionSize(entryPrice, stopLossPrice float64) float64 {
	if entryPrice <= 0 || stopLossPrice <= 0 {
		log.Println("Entry and stop-loss prices must be positive.")
		return 0
	}

	riskAmount := m.AccountBalance * m.RiskPerTradePercentage
	priceDifference := math.Abs(entryPrice - stopLossPrice)

	if priceDifference == 0 {
		log.Println("Entry and stop-loss prices cannot be the same.")
		return 0
	}

	return riskAmount / priceDifference
}

// DetermineTakeProfit calculates the take-profit price for a trade.
func (m *Manager) DetermineTakeProfit(entryPrice, stopLossPrice, riskRewardRatio float64) float64 {
	priceDifference := math.Abs(entryPrice - stopLossPrice)
	takeProfitDistance := priceDifference * riskRewardRatio

	if entryPrice > stopLossPrice { // Long position
		return entryPrice + takeProfitDistance
	}
	return entryPrice - takeProfitDistance
}

// UpdateAccountBalance sets the account balance to a new value.
func (m *Manager) UpdateAccountBalance(newBalance float64) {
	if newBalance > 0 {
		m.AccountBalance = newBalance
		log.Printf("Account balance updated to: %.2f", m.AccountBalance)
	} else {
		log.Println("Attempted to update account balance with a non-positive value.")
	}
}
