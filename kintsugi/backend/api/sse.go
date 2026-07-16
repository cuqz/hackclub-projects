package api

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type SSEBroker struct {
	clients    map[chan string]bool
	register   chan chan string
	unregister chan chan string
	broadcast  chan string
}

func NewSSEBroker() *SSEBroker {
	b := &SSEBroker{
		clients:    make(map[chan string]bool),
		register:   make(chan chan string),
		unregister: make(chan chan string),
		broadcast:  make(chan string, 256),
	}
	go b.run()
	return b
}

func (b *SSEBroker) run() {
	for {
		select {
		case client := <-b.register:
			b.clients[client] = true
		case client := <-b.unregister:
			if _, ok := b.clients[client]; ok {
				delete(b.clients, client)
				close(client)
			}
		case msg := <-b.broadcast:
			for client := range b.clients {
				select {
				case client <- msg:
				default:
					delete(b.clients, client)
					close(client)
				}
			}
		}
	}
}

func (b *SSEBroker) Subscribe() chan string {
	ch := make(chan string, 256)
	b.register <- ch
	return ch
}

func (b *SSEBroker) Unsubscribe(ch chan string) {
	b.unregister <- ch
}

func (b *SSEBroker) Publish(event SSEEvent) {
	data, _ := json.Marshal(event)
	b.broadcast <- string(data)
}

func (b *SSEBroker) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	ch := b.Subscribe()
	defer b.Unsubscribe(ch)

	// send initial connection event
	fmt.Fprintf(w, "data: {\"type\":\"connected\",\"payload\":\"\"}\n\n")
	flusher.Flush()

	ctx := r.Context()
	for {
		select {
		case <-ctx.Done():
			return
		case msg, ok := <-ch:
			if !ok {
				return
			}
			fmt.Fprintf(w, "data: %s\n\n", msg)
			flusher.Flush()
		}
	}
}
