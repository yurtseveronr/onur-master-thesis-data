package main

import (
	"fmt"
	"log"
	"movie-service/repository"
	"movie-service/routes"
	"net/http"
)

func main() {

	repository.InitDynamoDB()

	r := routes.SetupRouter()

	fmt.Println("🚀 Movie service is running on port 8081")
	log.Fatal(http.ListenAndServe(":8081", r))
}
