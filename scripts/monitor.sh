#!/bin/bash

# Script to monitor the application

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Function to display usage information
usage() {
  echo "Usage: $0 [logs|status|stats]"
  echo "  logs   - Show logs from all containers"
  echo "  status - Show status of all containers"
  echo "  stats  - Show resource usage statistics"
  exit 1
}

# Parse command line arguments
ACTION="status"
if [ $# -gt 0 ]; then
  ACTION="$1"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Perform the requested action
case "$ACTION" in
  logs)
    echo "Showing logs from all containers..."
    docker-compose logs -f
    ;;
  status)
    echo "Showing status of all containers..."
    docker-compose ps
    ;;
  stats)
    echo "Showing resource usage statistics..."
    docker stats $(docker-compose ps -q)
    ;;
  *)
    usage
    ;;
esac
