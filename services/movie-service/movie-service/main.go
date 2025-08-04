package main

import (
	"fmt"
	"log"
	"movie-service/repository"
	"movie-service/routes"
	"net/http"
)

func main() {
	// ✅ DynamoDB bağlantısını başlat
	repository.InitDynamoDB()

	r := routes.SetupRouter()

	// ✅ Start API
	fmt.Println("🚀 Movie service is running on port 8081")
	log.Fatal(http.ListenAndServe(":8081", r))
}
