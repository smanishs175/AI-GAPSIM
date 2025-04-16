#!/bin/bash

# Script to clean up the environment

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Function to display usage information
usage() {
  echo "Usage: $0 [--all]"
  echo "  --all  - Remove all containers, volumes, and data (WARNING: This will delete all data)"
  exit 1
}

# Parse command line arguments
REMOVE_ALL=false
if [ $# -gt 0 ]; then
  if [ "$1" = "--all" ]; then
    REMOVE_ALL=true
  else
    usage
  fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Stop the application
echo "Stopping the application..."
docker-compose down

# Remove containers and networks
echo "Removing containers and networks..."
docker-compose rm -f

if [ "$REMOVE_ALL" = true ]; then
  # Confirm with the user
  echo "WARNING: This will remove all volumes and data. This action cannot be undone."
  read -p "Are you sure you want to continue? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
  fi
  
  # Remove volumes
  echo "Removing volumes..."
  docker volume rm $(docker volume ls -q -f name=ai-gapsim) 2>/dev/null || true
  
  # Remove data directory
  echo "Removing data directory..."
  rm -rf data/*
  
  echo "All containers, volumes, and data have been removed."
else
  echo "Containers and networks have been removed. Volumes and data are preserved."
fi

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".pytest_cache" -type d -exec rm -rf {} +
find . -name ".coverage" -delete
find . -name "htmlcov" -type d -exec rm -rf {} +
find . -name "node_modules" -type d -exec rm -rf {} +
find . -name "dist" -type d -exec rm -rf {} +

echo "Cleanup completed successfully."
