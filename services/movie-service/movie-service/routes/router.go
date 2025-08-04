package routes

import (
	"fmt"
	"movie-service/handlers"
	"net/http"

	"github.com/gorilla/mux"
)

// ✅ Logging Middleware (Gelen request'leri loglamak için)
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("🔥 Incoming Request:", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

// ✅ SetupRouter initializes API routes
func SetupRouter() *mux.Router {
	r := mux.NewRouter()

	// ✅ Middleware ekleyelim
	r.Use(loggingMiddleware)

	// ✅ Root check
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte(`{"message": "Movie Service is running"}`))
	}).Methods("GET")

	// ✅ Movie routes
	r.HandleFunc("/api/movies/id/{id}", handlers.GetMovieByID).Methods("GET")
	r.HandleFunc("/api/movies/title/{title}", handlers.GetMovieByTitle).Methods("GET")

	fmt.Println("✅ Routes registered successfully!")
	return r
}
