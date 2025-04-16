import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from app.models.weather import WeatherData, HeatmapData
from app.utils.weather_data_processor import generate_heatmap_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_synthetic_weather_data(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    min_lat: float = 30.0,
    max_lat: float = 58.0,
    min_lon: float = -130.0,
    max_lon: float = -100.0,
    grid_resolution: float = 2.0
) -> None:
    """
    Generate synthetic weather data for a grid of points and date range.
    
    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        min_lat: Minimum latitude
        max_lat: Maximum latitude
        min_lon: Minimum longitude
        max_lon: Maximum longitude
        grid_resolution: Grid resolution in degrees
    """
    logger.info(f"Generating synthetic weather data from {start_date} to {end_date}...")
    
    # Create a grid of points
    lat_range = np.arange(min_lat, max_lat + grid_resolution, grid_resolution)
    lon_range = np.arange(min_lon, max_lon + grid_resolution, grid_resolution)
    
    # Generate data for each day
    current_date = start_date
    while current_date <= end_date:
        logger.info(f"Generating data for {current_date.strftime('%Y-%m-%d')}...")
        
        # Generate weather data for each point
        for lat in lat_range:
            for lon in lon_range:
                # Generate random weather data with some spatial and temporal correlation
                # Base values
                base_temp = 30 - (lat - min_lat) / (max_lat - min_lat) * 30  # Cooler at higher latitudes
                
                # Seasonal variation (northern hemisphere)
                month = current_date.month
                seasonal_factor = np.cos((month - 1) / 12 * 2 * np.pi)
                seasonal_temp = 15 * seasonal_factor
                
                # Longitude variation (cooler near coast)
                lon_factor = (lon - min_lon) / (max_lon - min_lon)
                lon_temp = 5 * lon_factor
                
                # Random variation
                random_seed = int(lat * 100 + lon * 100 + current_date.toordinal())
                np.random.seed(random_seed)
                daily_variation = np.random.normal(0, 3)
                
                # Calculate temperatures
                avg_temp = base_temp + seasonal_temp + lon_temp + daily_variation
                max_temp = avg_temp + np.random.uniform(3, 8)
                min_temp = avg_temp - np.random.uniform(3, 8)
                
                # Calculate other weather parameters
                rel_humidity = 50 + np.random.normal(0, 15)
                rel_humidity = max(0, min(100, rel_humidity))
                
                spec_humidity = rel_humidity * 0.1 + np.random.normal(0, 0.5)
                spec_humidity = max(0, spec_humidity)
                
                # Radiation depends on latitude and season
                radiation_factor = np.cos((lat - 40) / 50 * np.pi / 2) * (1 + seasonal_factor) / 2
                longwave_rad = 200 + 100 * radiation_factor + np.random.normal(0, 20)
                shortwave_rad = 600 * radiation_factor + np.random.normal(0, 100)
                
                # Precipitation (mostly zero with occasional rain)
                precip_rand = np.random.random()
                if precip_rand > 0.7:
                    precipitation = np.random.exponential(2)
                else:
                    precipitation = 0
                
                # Wind speed
                wind_speed = np.random.gamma(2, 2)
                
                # Create weather data record
                weather_data = WeatherData(
                    date=current_date,
                    latitude=lat,
                    longitude=lon,
                    geometry=f"SRID=4326;POINT({lon} {lat})",
                    max_temperature=max_temp,
                    avg_temperature=avg_temp,
                    min_temperature=min_temp,
                    relative_humidity=rel_humidity,
                    specific_humidity=spec_humidity,
                    longwave_radiation=longwave_rad,
                    shortwave_radiation=shortwave_rad,
                    precipitation=precipitation,
                    wind_speed=wind_speed,
                    source="synthetic"
                )
                
                db.add(weather_data)
        
        # Generate heatmap data for this date
        await generate_heatmaps_for_date(db, current_date.date())
        
        # Commit the transaction for this day
        await db.commit()
        
        # Move to next day
        current_date += timedelta(days=1)
    
    logger.info("Synthetic weather data generation completed.")

async def generate_heatmaps_for_date(db: AsyncSession, date_obj: datetime.date) -> None:
    """
    Generate heatmap data for a specific date.
    
    Args:
        db: Database session
        date_obj: Date
    """
    parameters = ["temperature", "humidity", "wind_speed", "precipitation", "radiation"]
    
    for parameter in parameters:
        # Generate heatmap data
        heatmap_data, bounds = generate_heatmap_data(parameter, date_obj)
        
        # Create heatmap data record
        heatmap = HeatmapData(
            date=date_obj,
            parameter=parameter,
            data_json=heatmap_data,
            bounds_json=bounds
        )
        
        db.add(heatmap)
    
    logger.info(f"Generated heatmaps for {date_obj}")

if __name__ == "__main__":
    # This can be used for testing the weather data generation directly
    import asyncio
    from app.core.database import get_db
    
    async def test_generate():
        start_date = datetime(2020, 7, 21)
        end_date = datetime(2020, 7, 30)
        
        async for db in get_db():
            await generate_synthetic_weather_data(db, start_date, end_date)
    
    asyncio.run(test_generate())
