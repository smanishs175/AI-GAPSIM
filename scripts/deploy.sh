#!/bin/bash

# Script to deploy the application to production

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Check if .env.prod file exists
if [ ! -f .env.prod ]; then
  echo "Error: .env.prod file not found. Please create it based on .env.prod.example."
  exit 1
fi

# Load environment variables
set -a
source .env.prod
set +a

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose > /dev/null 2>&1; then
  echo "Docker Compose is not installed. Please install it and try again."
  exit 1
fi

# Check if SSL certificates exist
if [ ! -f nginx/ssl/fullchain.pem ] || [ ! -f nginx/ssl/privkey.pem ]; then
  echo "SSL certificates not found. Creating self-signed certificates for development..."
  mkdir -p nginx/ssl
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/CN=${DOMAIN_NAME}" \
    -addext "subjectAltName=DNS:${DOMAIN_NAME},DNS:www.${DOMAIN_NAME}"
  
  echo "Self-signed certificates created. Replace them with real certificates for production."
fi

# Create www directory if it doesn't exist
mkdir -p nginx/www/static

# Build and start the application in production mode
echo "Building and starting the application in production mode..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if the database is initialized
echo "Checking if the database is initialized..."
if ! docker-compose exec db psql -U postgres -d wecc_grid -c "SELECT COUNT(*) FROM users" > /dev/null 2>&1; then
  echo "Database is not initialized. Running initialization script..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec backend python init_db.py
else
  echo "Database is already initialized."
fi

echo "Deployment completed successfully."
echo "The application is now running at https://${DOMAIN_NAME}"
