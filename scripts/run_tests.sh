#!/bin/bash

# Script to run tests

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Function to display usage information
usage() {
  echo "Usage: $0 [backend|frontend|all]"
  echo "  backend  - Run backend tests"
  echo "  frontend - Run frontend tests"
  echo "  all      - Run both backend and frontend tests (default)"
  exit 1
}

# Parse command line arguments
TEST_TYPE="all"
if [ $# -gt 0 ]; then
  TEST_TYPE="$1"
fi

# Validate test type
if [ "$TEST_TYPE" != "backend" ] && [ "$TEST_TYPE" != "frontend" ] && [ "$TEST_TYPE" != "all" ]; then
  usage
fi

# Run backend tests
run_backend_tests() {
  echo "Running backend tests..."
  cd backend || exit
  
  # Check if Docker is running
  if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
  fi
  
  # Check if the test database container is running
  if ! docker ps | grep -q "postgres"; then
    echo "Database container is not running. Starting a test database container..."
    docker run -d --name ai-gapsim-test-db \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=test_wecc_grid \
      -p 5432:5432 \
      postgis/postgis:15-3.3
    
    # Wait for the database to be ready
    echo "Waiting for the test database to be ready..."
    sleep 10
  fi
  
  # Run the tests
  python -m pytest --cov=app tests/
  
  # Return to the project directory
  cd ..
}

# Run frontend tests
run_frontend_tests() {
  echo "Running frontend tests..."
  cd frontend || exit
  
  # Run the tests
  npm test
  
  # Return to the project directory
  cd ..
}

# Run tests based on the specified type
if [ "$TEST_TYPE" = "backend" ] || [ "$TEST_TYPE" = "all" ]; then
  run_backend_tests
fi

if [ "$TEST_TYPE" = "frontend" ] || [ "$TEST_TYPE" = "all" ]; then
  run_frontend_tests
fi

echo "All tests completed."
