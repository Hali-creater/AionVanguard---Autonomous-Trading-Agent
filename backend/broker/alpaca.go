package broker

import (
	"log"
	"os"

	"github.com/alpacahq/alpaca-trade-api-go/v2/alpaca"
	"github.com/shopspring/decimal"
)

// AlpacaBroker handles communication with the Alpaca API.
type AlpacaBroker struct {
	client alpaca.Client
}

// NewAlpacaBroker creates and configures a new Alpaca client.
func NewAlpacaBroker() *AlpacaBroker {
	apiKey := os.Getenv("ALPACA_API_KEY_ID")
	apiSecret := os.Getenv("ALPACA_API_SECRET_KEY")
	baseURL := "https://paper-api.alpaca.markets" // Use paper trading endpoint

	if apiKey == "" || apiSecret == "" {
		log.Fatal("Alpaca API key and secret must be set as environment variables.")
	}

	client := alpaca.NewClient(alpaca.ClientOpts{
		ApiKey:    apiKey,
		ApiSecret: apiSecret,
		BaseURL:   baseURL,
	})

	return &AlpacaBroker{client: client}
}

// PlaceOrder executes a trade on Alpaca.
func (b *AlpacaBroker) PlaceOrder(symbol string, qty float64, side alpaca.Side, orderType alpaca.OrderType, timeInForce alpaca.TimeInForce) (string, error) {
	order, err := b.client.PlaceOrder(alpaca.PlaceOrderRequest{
		Symbol:      symbol,
		Qty:         decimal.NewFromFloat(qty),
		Side:        side,
		Type:        orderType,
		TimeInForce: timeInForce,
	})

	if err != nil {
		return "", err
	}

	log.Printf("Placed %s order for %f shares of %s. Order ID: %s", side, qty, symbol, order.ID)
	return order.ID, nil
}

// GetAccount retrieves the current Alpaca account information.
func (b *AlpacaBroker) GetAccount() (*alpaca.Account, error) {
	return b.client.GetAccount()
}

// GetOpenPositions retrieves a list of all open positions.
func (b *AlpacaBroker) GetOpenPositions() ([]alpaca.Position, error) {
	return b.client.ListPositions()
}
