package routes

import (
	"log"
	"net/http"
	"series-service/handlers"

	"github.com/gorilla/mux"
)

// ✅ Setup Router
func SetupRouter() *mux.Router {
	router := mux.NewRouter()

	// 📺 Series Endpoints
	router.HandleFunc("/api/series/id/{imdbID}", handlers.GetSeriesByID).Methods("GET")
	router.HandleFunc("/api/series/title/{title}", handlers.GetSeriesByTitle).Methods("GET")

	// 🔥 Middleware for Logging
	router.Use(loggingMiddleware)

	return router
}

// ✅ Middleware for Logging Requests
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("🔥 Incoming Request: %s %s\n", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}
