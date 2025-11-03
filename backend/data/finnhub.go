package data

import (
	"context"
	"log"
	"os"
	"time"

	finnhub "github.com/Finnhub-Stock-API/finnhub-go/v2"
)

// FinnhubFetcher handles communication with the Finnhub API.
type FinnhubFetcher struct {
	client *finnhub.DefaultApiService
}

// NewFinnhubFetcher creates and configures a new Finnhub client.
func NewFinnhubFetcher() *FinnhubFetcher {
	apiKey := os.Getenv("FINNHUB_API_KEY")
	if apiKey == "" {
		log.Fatal("Finnhub API key must be set as an environment variable.")
	}

	cfg := finnhub.NewConfiguration()
	cfg.AddDefaultHeader("X-Finnhub-Token", apiKey)
	client := finnhub.NewAPIClient(cfg).DefaultApi

	return &FinnhubFetcher{client: client}
}

// FetchHistoricalData retrieves historical candle data for a given symbol.
func (f *FinnhubFetcher) FetchHistoricalData(symbol, resolution string, from, to time.Time) (finnhub.StockCandles, error) {
	candles, _, err := f.client.StockCandles(context.Background(), symbol, resolution, from.Unix(), to.Unix())
	if err != nil {
		return finnhub.StockCandles{}, err
	}
	return candles, nil
}
