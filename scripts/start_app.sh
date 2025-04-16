#!/bin/bash

# Script to start the application

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Function to display usage information
usage() {
  echo "Usage: $0 [dev|prod]"
  echo "  dev  - Start the application in development mode (default)"
  echo "  prod - Start the application in production mode"
  exit 1
}

# Parse command line arguments
MODE="dev"
if [ $# -gt 0 ]; then
  MODE="$1"
fi

# Validate mode
if [ "$MODE" != "dev" ] && [ "$MODE" != "prod" ]; then
  usage
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Start the application
if [ "$MODE" = "dev" ]; then
  echo "Starting the application in development mode..."
  docker-compose up -d
  
  # Wait for services to start
  echo "Waiting for services to start..."
  sleep 5
  
  # Check if the database is initialized
  echo "Checking if the database is initialized..."
  if ! docker-compose exec db psql -U postgres -d wecc_grid -c "SELECT COUNT(*) FROM users" > /dev/null 2>&1; then
    echo "Database is not initialized. Running initialization script..."
    ./scripts/init_db.sh
  else
    echo "Database is already initialized."
  fi
  
  # Show logs
  echo "Application started in development mode. Showing logs..."
  docker-compose logs -f
else
  echo "Starting the application in production mode..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
  
  # Wait for services to start
  echo "Waiting for services to start..."
  sleep 5
  
  # Check if the database is initialized
  echo "Checking if the database is initialized..."
  if ! docker-compose exec db psql -U postgres -d wecc_grid -c "SELECT COUNT(*) FROM users" > /dev/null 2>&1; then
    echo "Database is not initialized. Running initialization script..."
    ./scripts/init_db.sh
  else
    echo "Database is already initialized."
  fi
  
  echo "Application started in production mode."
fi
