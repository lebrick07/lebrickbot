package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

type HealthResponse struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
}

type RootResponse struct {
	Message     string `json:"message"`
	Environment string `json:"environment"`
	Version     string `json:"version"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	env := os.Getenv("ENVIRONMENT")
	if env == "" {
		env = "development"
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(RootResponse{
		Message:     "Hello from {{CUSTOMER_NAME}}!",
		Environment: env,
		Version:     "1.0.0",
	})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/healthz", healthHandler)
	http.HandleFunc("/", rootHandler)

	env := os.Getenv("ENVIRONMENT")
	if env == "" {
		env = "development"
	}

	fmt.Printf("Starting server on port %s\n", port)
	fmt.Printf("Environment: %s\n", env)

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
