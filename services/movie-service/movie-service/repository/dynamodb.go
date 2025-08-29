package repository

import (
	"errors"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbiface"
)

// Movie Struct
type Movie struct {
	Title      string `json:"Title"`
	ImdbID     string `json:"imdbID"`
	Year       string `json:"Year"`
	Rated      string `json:"Rated"`
	Released   string `json:"Released"`
	Runtime    string `json:"Runtime"`
	Genre      string `json:"Genre"`
	Director   string `json:"Director"`
	Writer     string `json:"Writer"`
	Actors     string `json:"Actors"`
	Plot       string `json:"Plot"`
	Language   string `json:"Language"`
	Country    string `json:"Country"`
	Awards     string `json:"Awards"`
	Poster     string `json:"Poster"`
	Metascore  string `json:"Metascore"`
	IMDBRating string `json:"imdbRating"`
	IMDBVotes  string `json:"imdbVotes"`
	Type       string `json:"Type"`
	DVD        string `json:"DVD"`
	BoxOffice  string `json:"BoxOffice"`
	Production string `json:"Production"`
	Website    string `json:"Website"`
}

// ✅ Global DynamoDB Client
var DynamoDB dynamodbiface.DynamoDBAPI

const TableName = "movies"

func InitDynamoDB() {
	region := os.Getenv("AWS_REGION")
	if region == "" {
		region = "us-east-1"
	}

	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region),
	})

	if err != nil {
		log.Fatalf("❌ Failed to connect to DynamoDB: %v", err)
	}

	DynamoDB = dynamodb.New(sess)
	fmt.Println("✅ Connected to DynamoDB with IAM Role!")
}

// ✅ DEBUG: Fetch a movie by IMDb ID
func FetchMovieByID(imdbID string) (*Movie, error) {
	fmt.Printf("🔍 Searching for imdbID: %s\n", imdbID)

	// CSV'de imdbID var, table'da da imdbID olmalı
	input := &dynamodb.GetItemInput{
		TableName: aws.String(TableName),
		Key: map[string]*dynamodb.AttributeValue{
			"imdbID": {S: aws.String(imdbID)}, // Primary key name kontrol et!
		},
	}

	result, err := DynamoDB.GetItem(input)
	if err != nil {
		fmt.Printf("❌ DynamoDB GetItem Error: %v\n", err)
		return nil, errors.New("database error")
	}

	if result.Item == nil {
		fmt.Printf("❌ No item found for imdbID: %s\n", imdbID)

		// Debug: İlk 5 item'ı göster
		fmt.Println("🔍 Let's see what's in the table...")
		scanInput := &dynamodb.ScanInput{
			TableName: aws.String(TableName),
			Limit:     aws.Int64(5),
		}
		scanResult, scanErr := DynamoDB.Scan(scanInput)
		if scanErr == nil && len(scanResult.Items) > 0 {
			fmt.Printf("📋 Sample items in table:\n")
			for i, item := range scanResult.Items {
				fmt.Printf("  Item %d: %v\n", i+1, item)
			}
		}

		return nil, errors.New("movie not found")
	}

	fmt.Printf("✅ Found item: %v\n", result.Item)

	var movie Movie
	err = dynamodbattribute.UnmarshalMap(result.Item, &movie)
	if err != nil {
		fmt.Printf("❌ Unmarshal Error: %v\n", err)
		return nil, errors.New("error parsing movie data")
	}

	fmt.Printf("✅ Parsed movie: %+v\n", movie)
	return &movie, nil
}

// ✅ DEBUG: Fetch a movie by Title
func FetchMovieByTitle(title string) (*Movie, error) {
	fmt.Printf("🔍 Searching for title: %s\n", title)

	input := &dynamodb.ScanInput{
		TableName: aws.String(TableName),
		Limit:     aws.Int64(50), // İlk 50 item'ı tara
	}

	result, err := DynamoDB.Scan(input)
	if err != nil {
		fmt.Printf("❌ DynamoDB Scan Error: %v\n", err)
		return nil, errors.New("error scanning movies")
	}

	fmt.Printf("🔍 Scanned %d items\n", len(result.Items))

	for i, item := range result.Items {
		var movie Movie
		err := dynamodbattribute.UnmarshalMap(item, &movie)
		if err != nil {
			fmt.Printf("❌ Unmarshal error for item %d: %v\n", i, err)
			continue
		}

		fmt.Printf("🔍 Item %d - Title: '%s', ImdbID: '%s'\n", i, movie.Title, movie.ImdbID)

		if strings.EqualFold(movie.Title, title) {
			fmt.Printf("✅ Found matching movie: %+v\n", movie)
			return &movie, nil
		}
	}

	fmt.Printf("❌ No movie found with title: %s\n", title)
	return nil, errors.New("movie not found")
}
