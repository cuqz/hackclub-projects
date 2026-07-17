package api

import (
	"net/http"
	"strings"
)

func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(200)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func NewRouter(h *Handler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/api/submit", h.HandleSubmit)
	mux.HandleFunc("/api/problems", h.HandleProblems)
	mux.HandleFunc("/api/solutions", h.HandleSolutions)
	mux.HandleFunc("/api/stats", h.HandleStats)
	mux.HandleFunc("/api/events", h.HandleSSE)

	// catch-all for SPA
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if strings.HasPrefix(r.URL.Path, "/api/") {
			http.Error(w, "not found", 404)
			return
		}
		// serve from embedded frontend or proxy
		w.Header().Set("Content-Type", "text/html")
		w.Write([]byte(`<html><body><h1>HiveMind API</h1><p>Frontend not embedded. Run frontend separately.</p></body></html>`))
	})

	return CORSMiddleware(mux)
}
