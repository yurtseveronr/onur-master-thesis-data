package handlers

import (
	"encoding/json"
	"net/http"
	"series-service/repository"

	"github.com/gorilla/mux"
)

// Get Series by IMDb ID
func GetSeriesByID(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	imdbID := vars["imdbID"]

	series, err := repository.FetchSeriesByID(imdbID)
	if err != nil {
		http.Error(w, `{"error": "series not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(series)
}

// 📺 Get Series by Title
func GetSeriesByTitle(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	title := vars["title"]

	series, err := repository.FetchSeriesByTitle(title)
	if err != nil {
		http.Error(w, `{"error": "series not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(series)
}
