#!/bin/bash

BASE_URL="http://localhost:8000"

# Add transactions
echo "Adding transactions..."
curl -X POST -H "Content-Type: application/json" -d '{"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"}' $BASE_URL/add
curl -X POST -H "Content-Type: application/json" -d '{"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"}' $BASE_URL/add
curl -X POST -H "Content-Type: application/json" -d '{"payer": "DANNON", "points": -200, "timestamp": "2022-10-31T15:00:00Z"}' $BASE_URL/add
curl -X POST -H "Content-Type: application/json" -d '{"payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"}' $BASE_URL/add
curl -X POST -H "Content-Type: application/json" -d '{"payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"}' $BASE_URL/add

# Spend points
echo "Spending points..."
curl -X POST -H "Content-Type: application/json" -d '{"points": 5000}' $BASE_URL/spend

# Check balance
echo "Checking balance..."
curl -X GET $BASE_URL/balance
