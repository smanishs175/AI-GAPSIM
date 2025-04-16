#!/bin/bash

# Script to update the application

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Check if Git is installed
if ! command -v git > /dev/null 2>&1; then
  echo "Git is not installed. Please install it and try again."
  exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if the application is running
if docker-compose ps | grep -q "Up"; then
  # Backup the database before updating
  echo "Backing up the database before updating..."
  ./scripts/backup.sh
  
  # Stop the application
  echo "Stopping the application..."
  docker-compose down
fi

# Pull the latest changes
echo "Pulling the latest changes from the repository..."
git pull

# Rebuild the application
echo "Rebuilding the application..."
docker-compose build

# Start the application
echo "Starting the application..."
docker-compose up -d

# Run database migrations
echo "Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "Update completed successfully."
