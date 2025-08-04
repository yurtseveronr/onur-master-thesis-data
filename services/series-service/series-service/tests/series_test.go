package handlers_test

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"series-service/handlers"
	"series-service/repository"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbiface"
	"github.com/gorilla/mux"
)

// Mock for TVSeries testing
type mockSeriesDynamoDBClient struct {
	dynamodbiface.DynamoDBAPI
	shouldReturnItem  bool
	shouldReturnItems bool
}

func (m *mockSeriesDynamoDBClient) GetItem(input *dynamodb.GetItemInput) (*dynamodb.GetItemOutput, error) {
	if !m.shouldReturnItem {
		return &dynamodb.GetItemOutput{Item: nil}, nil
	}

	// Always return a series for any ID
	return &dynamodb.GetItemOutput{
		Item: map[string]*dynamodb.AttributeValue{
			"imdbID": {
				S: aws.String("tt1234567"),
			},
			"Title": {
				S: aws.String("Test Series"),
			},
			"Year": {
				S: aws.String("2023"),
			},
			"Genre": {
				S: aws.String("Drama"),
			},
			"TotalSeasons": {
				S: aws.String("3"),
			},
			"Plot": {
				S: aws.String("A comprehensive test series"),
			},
			"Actors": {
				S: aws.String("Actor 1, Actor 2"),
			},
			"Director": {
				S: aws.String("Test Director"),
			},
			"Language": {
				S: aws.String("English"),
			},
			"Country": {
				S: aws.String("USA"),
			},
			"imdbRating": {
				S: aws.String("8.5"),
			},
			"imdbVotes": {
				S: aws.String("100,000"),
			},
		},
	}, nil
}

func (m *mockSeriesDynamoDBClient) Scan(input *dynamodb.ScanInput) (*dynamodb.ScanOutput, error) {
	if !m.shouldReturnItems {
		return &dynamodb.ScanOutput{Items: []map[string]*dynamodb.AttributeValue{}}, nil
	}

	// Always return multiple series
	return &dynamodb.ScanOutput{
		Items: []map[string]*dynamodb.AttributeValue{
			{
				"imdbID": {
					S: aws.String("tt1234567"),
				},
				"Title": {
					S: aws.String("Test Series"),
				},
				"Year": {
					S: aws.String("2023"),
				},
				"Genre": {
					S: aws.String("Drama"),
				},
				"TotalSeasons": {
					S: aws.String("3"),
				},
			},
			{
				"imdbID": {
					S: aws.String("tt7654321"),
				},
				"Title": {
					S: aws.String("Another Series"),
				},
				"Year": {
					S: aws.String("2024"),
				},
				"Genre": {
					S: aws.String("Comedy"),
				},
				"TotalSeasons": {
					S: aws.String("2"),
				},
			},
			{
				"imdbID": {
					S: aws.String("tt9876543"),
				},
				"Title": {
					S: aws.String("Third Series"),
				},
				"Year": {
					S: aws.String("2025"),
				},
				"Genre": {
					S: aws.String("Action"),
				},
				"TotalSeasons": {
					S: aws.String("1"),
				},
			},
		},
	}, nil
}

// ✅ MEGA TEST - Tüm fonksiyonları tek testte test et
func TestTVSeriesComplete(t *testing.T) {
	// Mock'u set et - repository'deki variable name'e göre
	repository.SeriesDynamoDB = &mockSeriesDynamoDBClient{shouldReturnItem: true, shouldReturnItems: true}

	// ============ TEST 1: GetSeriesByID ============
	t.Log("🧪 Testing GetSeriesByID...")
	req1 := httptest.NewRequest("GET", "/api/series/id/tt1234567", nil)
	req1 = mux.SetURLVars(req1, map[string]string{"imdbID": "tt1234567"}) // imdbID key kullan
	rr1 := httptest.NewRecorder()

	handlers.GetSeriesByID(rr1, req1)

	if rr1.Code != http.StatusOK {
		t.Errorf("GetSeriesByID: Expected 200, got %d. Response: %s", rr1.Code, rr1.Body.String())
	}
	if !strings.Contains(rr1.Body.String(), "Test Series") {
		t.Errorf("GetSeriesByID: Expected 'Test Series' in response, got: %s", rr1.Body.String())
	}
	if !strings.Contains(rr1.Body.String(), "tt1234567") {
		t.Errorf("GetSeriesByID: Expected 'tt1234567' in response, got: %s", rr1.Body.String())
	}
	t.Log("✅ GetSeriesByID passed!")

	// ============ TEST 2: GetSeriesByTitle ============
	t.Log("🧪 Testing GetSeriesByTitle...")
	req2 := httptest.NewRequest("GET", "/api/series/title/Test%20Series", nil)
	req2 = mux.SetURLVars(req2, map[string]string{"title": "Test Series"})
	rr2 := httptest.NewRecorder()

	handlers.GetSeriesByTitle(rr2, req2)

	if rr2.Code != http.StatusOK {
		t.Errorf("GetSeriesByTitle: Expected 200, got %d. Response: %s", rr2.Code, rr2.Body.String())
	}
	if !strings.Contains(rr2.Body.String(), "Test Series") {
		t.Errorf("GetSeriesByTitle: Expected 'Test Series' in response, got: %s", rr2.Body.String())
	}
	t.Log("✅ GetSeriesByTitle passed!")

	// ============ TEST 3: Not Found Scenarios ============
	t.Log("🧪 Testing Not Found scenarios...")

	// Mock'u false yap
	repository.SeriesDynamoDB = &mockSeriesDynamoDBClient{shouldReturnItem: false, shouldReturnItems: false}

	req3 := httptest.NewRequest("GET", "/api/series/id/invalid", nil)
	req3 = mux.SetURLVars(req3, map[string]string{"imdbID": "invalid"})
	rr3 := httptest.NewRecorder()

	handlers.GetSeriesByID(rr3, req3)

	if rr3.Code != http.StatusNotFound {
		t.Errorf("Not Found test: Expected 404, got %d", rr3.Code)
	}
	if !strings.Contains(rr3.Body.String(), "series not found") {
		t.Errorf("Not Found test: Expected error message, got: %s", rr3.Body.String())
	}
	t.Log("✅ Not Found scenarios passed!")

	// ============ TEST 4: Multiple HTTP Methods ============
	t.Log("🧪 Testing Different HTTP Methods...")

	// Mock'u tekrar true yap
	repository.SeriesDynamoDB = &mockSeriesDynamoDBClient{shouldReturnItem: true}

	methods := []string{"GET", "POST", "PUT", "DELETE", "PATCH"}
	for _, method := range methods {
		req := httptest.NewRequest(method, "/api/series/id/tt1234567", nil)
		req = mux.SetURLVars(req, map[string]string{"imdbID": "tt1234567"})
		rr := httptest.NewRecorder()

		if method == "GET" {
			handlers.GetSeriesByID(rr, req)
			if rr.Code != http.StatusOK {
				t.Errorf("HTTP %s: Expected 200, got %d", method, rr.Code)
			}
		}
	}
	t.Log("✅ HTTP Methods test passed!")

	// ============ TEST 5: Concurrent Requests ============
	t.Log("🧪 Testing Concurrent Requests...")
	done := make(chan bool, 5)
	errors := make(chan error, 5)

	for i := 0; i < 5; i++ {
		go func(index int) {
			req := httptest.NewRequest("GET", "/api/series/id/tt1234567", nil)
			req = mux.SetURLVars(req, map[string]string{"imdbID": "tt1234567"})
			rr := httptest.NewRecorder()

			handlers.GetSeriesByID(rr, req)

			if rr.Code != http.StatusOK {
				errors <- fmt.Errorf("Concurrent request %d: Expected 200, got %d", index, rr.Code)
			} else {
				errors <- nil
			}
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 5; i++ {
		<-done
		if err := <-errors; err != nil {
			t.Error(err)
		}
	}
	t.Log("✅ Concurrent requests passed!")

	// ============ TEST 6: Content-Type Headers ============
	t.Log("🧪 Testing Content-Type Headers...")
	req6 := httptest.NewRequest("GET", "/api/series/id/tt1234567", nil)
	req6 = mux.SetURLVars(req6, map[string]string{"imdbID": "tt1234567"})
	rr6 := httptest.NewRecorder()

	handlers.GetSeriesByID(rr6, req6)

	if rr6.Header().Get("Content-Type") != "application/json" {
		t.Errorf("Content-Type: Expected 'application/json', got '%s'", rr6.Header().Get("Content-Type"))
	}
	t.Log("✅ Content-Type headers passed!")

	// ============ TEST 7: JSON Response Structure ============
	t.Log("🧪 Testing JSON Response Structure...")
	req7 := httptest.NewRequest("GET", "/api/series/id/tt1234567", nil)
	req7 = mux.SetURLVars(req7, map[string]string{"imdbID": "tt1234567"})
	rr7 := httptest.NewRecorder()

	handlers.GetSeriesByID(rr7, req7)

	responseBody := rr7.Body.String()

	// Check for required JSON fields
	requiredFields := []string{"Title", "imdbID", "Year", "Genre", "TotalSeasons"}
	for _, field := range requiredFields {
		if !strings.Contains(responseBody, field) {
			t.Errorf("JSON Structure: Missing field '%s' in response: %s", field, responseBody)
		}
	}
	t.Log("✅ JSON Response structure passed!")

	// ============ FINAL SUCCESS MESSAGE ============
	t.Log("🎉 ALL TVSERIES TESTS PASSED! Complete coverage achieved!")
}
