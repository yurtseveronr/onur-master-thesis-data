package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"series-service/repository"
	"series-service/routes"
)

func main() {

	repository.InitSeriesDynamoDB()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}

	router := routes.SetupRouter()

	fmt.Println("✅ Series Service running on port", port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}
