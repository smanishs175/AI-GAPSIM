from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from datetime import date
import json
import redis
import numpy as np

from app.models.weather import HeatmapData
from app.core.config import settings

# Initialize Redis client for caching
redis_client = redis.Redis.from_url(settings.REDIS_URL)
CACHE_EXPIRATION = 60 * 60 * 24  # 24 hours in seconds

async def get_available_heatmap_parameters(db: AsyncSession) -> List[str]:
    """
    Get available heatmap parameters.
    
    Args:
        db: Database session
        
    Returns:
        List of available parameters
    """
    # Check cache first
    cache_key = "heatmap:parameters"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query database
    query = select(HeatmapData.parameter).distinct()
    result = await db.execute(query)
    parameters = [row[0] for row in result.all()]
    
    # If no parameters in database, return default list
    if not parameters:
        parameters = [
            "temperature",
            "humidity",
            "wind_speed",
            "precipitation",
            "radiation"
        ]
    
    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(parameters))
    
    return parameters

async def get_heatmap_bounds(
    db: AsyncSession, 
    parameter: str, 
    date: date
) -> Optional[Dict[str, Any]]:
    """
    Get bounds for a heatmap.
    
    Args:
        db: Database session
        parameter: Heatmap parameter
        date: Date
        
    Returns:
        Bounds for the heatmap
    """
    # Check cache first
    cache_key = f"heatmap:bounds:{parameter}:{date.isoformat()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query database
    query = select(HeatmapData).where(
        and_(
            HeatmapData.parameter == parameter,
            HeatmapData.date == date
        )
    )
    result = await db.execute(query)
    heatmap_data = result.scalars().first()
    
    if not heatmap_data or not heatmap_data.bounds_json:
        # If not in database, generate default bounds
        bounds = {
            "min_lat": 30,
            "max_lat": 58,
            "min_lon": -130,
            "max_lon": -100,
            "min_value": 0,
            "max_value": 100
        }
    else:
        bounds = heatmap_data.bounds_json
    
    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(bounds))
    
    return bounds

async def get_heatmap_data(
    db: AsyncSession, 
    parameter: str, 
    date: date
) -> Optional[Dict[str, Any]]:
    """
    Get heatmap data.
    
    Args:
        db: Database session
        parameter: Heatmap parameter
        date: Date
        
    Returns:
        Heatmap data
    """
    # Check cache first
    cache_key = f"heatmap:data:{parameter}:{date.isoformat()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query database
    query = select(HeatmapData).where(
        and_(
            HeatmapData.parameter == parameter,
            HeatmapData.date == date
        )
    )
    result = await db.execute(query)
    heatmap_data = result.scalars().first()
    
    if not heatmap_data:
        # If not in database, generate dummy data
        bounds = await get_heatmap_bounds(db, parameter, date)
        data = generate_dummy_heatmap_data(parameter, bounds)
    else:
        data = {
            "parameter": heatmap_data.parameter,
            "date": heatmap_data.date.isoformat(),
            "data": heatmap_data.data_json,
            "bounds": heatmap_data.bounds_json
        }
    
    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(data))
    
    return data

def generate_dummy_heatmap_data(parameter: str, bounds: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate dummy heatmap data.
    
    Args:
        parameter: Heatmap parameter
        bounds: Heatmap bounds
        
    Returns:
        Dummy heatmap data
    """
    min_lat = bounds["min_lat"]
    max_lat = bounds["max_lat"]
    min_lon = bounds["min_lon"]
    max_lon = bounds["max_lon"]
    min_value = bounds["min_value"]
    max_value = bounds["max_value"]
    
    # Create a grid of points
    lat_step = 1.0
    lon_step = 1.0
    
    lat_range = np.arange(min_lat, max_lat + lat_step, lat_step)
    lon_range = np.arange(min_lon, max_lon + lon_step, lon_step)
    
    # Generate random values for each point
    np.random.seed(42)  # For reproducibility
    
    grid_data = []
    for lat in lat_range:
        for lon in lon_range:
            # Generate a value based on parameter and location
            if parameter == "temperature":
                # Temperature decreases with latitude and increases with longitude
                value = max_value - (lat - min_lat) / (max_lat - min_lat) * (max_value - min_value) * 0.7 + \
                        (lon - min_lon) / (max_lon - min_lon) * (max_value - min_value) * 0.3 + \
                        np.random.normal(0, 5)
            elif parameter == "humidity":
                # Humidity increases with latitude and decreases with longitude
                value = min_value + (lat - min_lat) / (max_lat - min_lat) * (max_value - min_value) * 0.6 - \
                        (lon - min_lon) / (max_lon - min_lon) * (max_value - min_value) * 0.4 + \
                        np.random.normal(0, 10)
            elif parameter == "wind_speed":
                # Wind speed varies more randomly
                value = min_value + np.random.uniform(0, max_value - min_value)
            elif parameter == "precipitation":
                # Precipitation is mostly low with occasional high values
                value = min_value + np.random.exponential(5)
            elif parameter == "radiation":
                # Radiation decreases with latitude
                value = max_value - (lat - min_lat) / (max_lat - min_lat) * (max_value - min_value) * 0.8 + \
                        np.random.normal(0, 10)
            else:
                value = np.random.uniform(min_value, max_value)
            
            # Ensure value is within bounds
            value = max(min_value, min(max_value, value))
            
            grid_data.append([lat, lon, value])
    
    return {
        "parameter": parameter,
        "date": "2020-07-21",  # Example date
        "data": grid_data,
        "bounds": bounds
    }
