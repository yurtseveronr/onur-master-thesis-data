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

// ✅ Series Struct - CSV'deki tüm kolonlar
type Series struct {
	Title        string `json:"Title"`
	ImdbID       string `json:"imdbID"`
	Year         string `json:"Year"`
	Actors       string `json:"Actors"`
	Country      string `json:"Country"`
	Director     string `json:"Director"`
	Genre        string `json:"Genre"`
	ImdbRating   string `json:"imdbRating"`
	ImdbVotes    string `json:"imdbVotes"`
	ITEM_ID      string `json:"ITEM_ID"`
	Language     string `json:"Language"`
	Plot         string `json:"Plot"`
	TotalSeasons string `json:"TotalSeasons"`
}

// ✅ Global DynamoDB Client - Interface kullan (test için)
var SeriesDynamoDB dynamodbiface.DynamoDBAPI

const SeriesTableName = "TVSeries"

// ✅ Initialize DynamoDB Connection with IAM Role
func InitSeriesDynamoDB() {
	region := os.Getenv("AWS_REGION")
	if region == "" {
		region = "us-east-1" // Default region
	}

	// ✅ IAM Role kullanarak session oluştur
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region),
		// Credentials belirtmeyin - IAM Role otomatik kullanılacak
	})

	if err != nil {
		log.Fatalf("❌ Failed to connect to DynamoDB: %v", err)
	}

	SeriesDynamoDB = dynamodb.New(sess)
	fmt.Println("✅ Connected to TVSeries DynamoDB with IAM Role!")
}

// ✅ Fetch ALL series (tüm değerleri dönsün)
func FetchAllSeries() ([]*Series, error) {
	fmt.Println("📺 FetchAllSeries called")

	input := &dynamodb.ScanInput{
		TableName: aws.String(SeriesTableName),
	}

	result, err := SeriesDynamoDB.Scan(input)
	if err != nil {
		fmt.Printf("❌ Error scanning all series: %v\n", err)
		return nil, errors.New("error fetching all series")
	}

	var seriesList []*Series
	for _, item := range result.Items {
		var series Series
		err := dynamodbattribute.UnmarshalMap(item, &series)
		if err != nil {
			fmt.Printf("❌ Error parsing series data: %v\n", err)
			continue // Skip malformed items
		}
		seriesList = append(seriesList, &series)
	}

	fmt.Printf("✅ Found %d series in total\n", len(seriesList))
	return seriesList, nil
}

// ✅ Fetch a series by IMDb ID
func FetchSeriesByID(imdbID string) (*Series, error) {
	fmt.Printf("📺 FetchSeriesByID called with IMDb ID: %s\n", imdbID)

	input := &dynamodb.GetItemInput{
		TableName: aws.String(SeriesTableName),
		Key: map[string]*dynamodb.AttributeValue{
			"imdbID": {S: aws.String(imdbID)},
		},
	}

	result, err := SeriesDynamoDB.GetItem(input)
	if err != nil {
		fmt.Printf("❌ Error fetching series from DynamoDB: %v\n", err)
		return nil, errors.New("series not found")
	}

	if result.Item == nil {
		fmt.Printf("❌ Series not found: %s\n", imdbID)
		return nil, errors.New("series not found")
	}

	var series Series
	err = dynamodbattribute.UnmarshalMap(result.Item, &series)
	if err != nil {
		fmt.Printf("❌ Error parsing series data: %v\n", err)
		return nil, errors.New("error parsing series data")
	}

	fmt.Printf("✅ Series found: %s\n", series.Title)
	return &series, nil
}

// ✅ Fetch a series by Title (Case-Insensitive)
func FetchSeriesByTitle(title string) (*Series, error) {
	fmt.Printf("📺 FetchSeriesByTitle called with title: %s\n", title)

	input := &dynamodb.ScanInput{
		TableName: aws.String(SeriesTableName),
	}

	result, err := SeriesDynamoDB.Scan(input)
	if err != nil {
		fmt.Printf("❌ Error scanning series: %v\n", err)
		return nil, errors.New("error scanning series")
	}

	for _, item := range result.Items {
		var series Series
		err := dynamodbattribute.UnmarshalMap(item, &series)
		if err != nil {
			continue // Skip malformed items
		}

		if strings.EqualFold(series.Title, title) {
			fmt.Printf("✅ Series found: %s\n", series.Title)
			return &series, nil
		}
	}

	fmt.Printf("❌ Series not found: %s\n", title)
	return nil, errors.New("series not found")
}
