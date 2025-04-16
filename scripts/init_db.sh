#!/bin/bash

# Script to initialize the database

# Change to the backend directory
cd "$(dirname "$0")/../backend" || exit

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if the database container is running
if ! docker ps | grep -q "ai-gapsim_db"; then
  echo "Database container is not running. Starting services with Docker Compose..."
  cd ..
  docker-compose up -d db redis
  cd backend
  
  # Wait for the database to be ready
  echo "Waiting for the database to be ready..."
  sleep 10
fi

# Run the database initialization script
echo "Initializing database..."
python init_db.py

echo "Database initialization completed."
