package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"hivemind/agents"
	"hivemind/api"
	"hivemind/db"
	"hivemind/featherless"
)

func main() {
	apiKey := os.Getenv("FEATHERLESS_API_KEY")

	model := os.Getenv("FEATHERLESS_MODEL")
	if model == "" {
		model = "Qwen/Qwen3-32B"
	}

	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":8080"
	}

	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "hivemind.db"
	}

	store, err := db.New(dbPath)
	if err != nil {
		log.Fatalf("db init: %v", err)
	}

	client := featherless.New(apiKey, model)
	orch := agents.NewOrchestrator(client)
	broker := api.NewSSEBroker()
	handler := api.NewHandler(store, orch, broker)
	router := api.NewRouter(handler)

	mode := "live"
	if client.Mock() {
		mode = "DEMO (mock data)"
	}

	fmt.Printf("HiveMind running on %s\n", addr)
	fmt.Printf("Model: %s\n", model)
	fmt.Printf("Mode: %s\n", mode)
	log.Fatal(http.ListenAndServe(addr, router))
}
