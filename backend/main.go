package main

import (
	"encoding/json"
	"log"
	"net/http"

	"aionvanguard/backend/agent"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// In production, you should check the origin to prevent CSRF attacks.
		// For this project, we'll allow any origin.
		return true
	},
}

// Message represents the structure of messages sent over the WebSocket.
type Message struct {
	Type    string          `json:"type"`
	Payload json.RawMessage `json:"payload"`
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer ws.Close()
	log.Println("Client connected")

	var tradingAgent *agent.TradingAgent

	for {
		// Read message from the client
		_, msgBytes, err := ws.ReadMessage()
		if err != nil {
			log.Println("Read error:", err)
			if tradingAgent != nil {
				tradingAgent.Stop() // Stop the agent if the client disconnects
			}
			break
		}

		var msg Message
		if err := json.Unmarshal(msgBytes, &msg); err != nil {
			log.Println("Unmarshal error:", err)
			continue
		}

		// Handle the message based on its type
		switch msg.Type {
		case "start":
			var config agent.Config
			if err := json.Unmarshal(msg.Payload, &config); err != nil {
				log.Println("Error unmarshalling config:", err)
				continue
			}
			tradingAgent = agent.NewTradingAgent(&config, ws)
			tradingAgent.Start()
			log.Println("Agent started with config:", config)

		case "stop":
			if tradingAgent != nil {
				tradingAgent.Stop()
				log.Println("Agent stopped")
			}
		}
	}
}

func main() {
	http.HandleFunc("/ws", handleConnections)

	log.Println("HTTP server started on :8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
