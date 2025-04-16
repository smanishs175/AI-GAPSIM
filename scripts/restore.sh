#!/bin/bash

# Script to restore the database and data files from a backup

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Function to display usage information
usage() {
  echo "Usage: $0 <db_backup_file> <data_backup_file>"
  echo "  db_backup_file    - Path to the database backup file"
  echo "  data_backup_file  - Path to the data backup file"
  exit 1
}

# Check if the required arguments are provided
if [ $# -ne 2 ]; then
  usage
fi

DB_BACKUP_FILE="$1"
DATA_BACKUP_FILE="$2"

# Check if the backup files exist
if [ ! -f "$DB_BACKUP_FILE" ]; then
  echo "Error: Database backup file not found: $DB_BACKUP_FILE"
  exit 1
fi

if [ ! -f "$DATA_BACKUP_FILE" ]; then
  echo "Error: Data backup file not found: $DATA_BACKUP_FILE"
  exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if the database container is running
if ! docker-compose ps | grep -q "db.*Up"; then
  echo "Database container is not running. Please start the application and try again."
  exit 1
fi

# Confirm with the user
echo "WARNING: This will overwrite the current database and data files."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Restore cancelled."
  exit 1
fi

# Stop the application
echo "Stopping the application..."
docker-compose down

# Restore the data directory
echo "Restoring the data directory..."
tar -xzf "$DATA_BACKUP_FILE"

# Start the database container
echo "Starting the database container..."
docker-compose up -d db

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
sleep 10

# Restore the database
echo "Restoring the database..."
cat "$DB_BACKUP_FILE" | docker-compose exec -T db psql -U postgres wecc_grid

# Check if the database restore was successful
if [ $? -eq 0 ]; then
  echo "Database restore completed successfully."
else
  echo "Database restore failed."
  exit 1
fi

# Start the application
echo "Starting the application..."
docker-compose up -d

echo "Restore completed successfully."
