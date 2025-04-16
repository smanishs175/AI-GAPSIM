#!/bin/bash

# Script to generate sample data for testing

# Change to the project directory
cd "$(dirname "$0")/.." || exit

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if the application is running
if ! docker-compose ps | grep -q "backend.*Up"; then
  echo "Application is not running. Please start the application and try again."
  exit 1
fi

# Generate sample data
echo "Generating sample weather data..."
docker-compose exec backend python -c "
import asyncio
from datetime import datetime
from app.core.database import get_db
from app.utils.generate_weather_data import generate_synthetic_weather_data

async def generate_data():
    start_date = datetime(2020, 7, 21)
    end_date = datetime(2020, 7, 30)
    
    async for db in get_db():
        await generate_synthetic_weather_data(db, start_date, end_date)

asyncio.run(generate_data())
"

# Check if the data generation was successful
if [ $? -eq 0 ]; then
  echo "Sample weather data generated successfully."
else
  echo "Sample weather data generation failed."
  exit 1
fi

echo "Sample data generation completed successfully."
