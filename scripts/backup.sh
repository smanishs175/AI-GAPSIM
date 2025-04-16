#!/bin/bash

# Script to backup the database and data files

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Set backup directory
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Set backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
DATA_BACKUP_FILE="$BACKUP_DIR/data_backup_$TIMESTAMP.tar.gz"

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

# Backup the database
echo "Backing up the database..."
docker-compose exec -T db pg_dump -U postgres wecc_grid > "$DB_BACKUP_FILE"

# Check if the database backup was successful
if [ $? -eq 0 ]; then
  echo "Database backup completed successfully: $DB_BACKUP_FILE"
else
  echo "Database backup failed."
  exit 1
fi

# Backup the data directory
echo "Backing up the data directory..."
tar -czf "$DATA_BACKUP_FILE" data/

# Check if the data backup was successful
if [ $? -eq 0 ]; then
  echo "Data backup completed successfully: $DATA_BACKUP_FILE"
else
  echo "Data backup failed."
  exit 1
fi

# Cleanup old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "db_backup_*.sql" -type f -mtime +7 -delete
find "$BACKUP_DIR" -name "data_backup_*.tar.gz" -type f -mtime +7 -delete

echo "Backup completed successfully."
