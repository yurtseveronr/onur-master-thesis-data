package handlers

import (
	"encoding/json"
	"fmt"
	"movie-service/repository"
	"net/http"

	"github.com/gorilla/mux"
)

// ✅ Fetch movie by IMDb ID
func GetMovieByID(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	imdbID := vars["id"]

	fmt.Println("🔥 Incoming Request: GET /api/movies/id/", imdbID)

	movie, err := repository.FetchMovieByID(imdbID)
	if err != nil {
		http.Error(w, `{"error": "Movie not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(movie)
}

// ✅ Fetch movie by Title
func GetMovieByTitle(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	title := vars["title"]

	fmt.Println("🔥 Incoming Request: GET /api/movies/title/", title)

	movie, err := repository.FetchMovieByTitle(title)
	if err != nil {
		http.Error(w, `{"error": "Movie not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(movie)
}
