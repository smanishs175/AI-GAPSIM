import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import date, datetime, timedelta

def get_weather_data(year: int, month: int, day: int, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get weather data for a specific point and date.
    This is a placeholder for the original weather_data_extractor.py functionality.
    
    Args:
        year: Year
        month: Month
        day: Day
        latitude: Latitude of the point
        longitude: Longitude of the point
        
    Returns:
        Weather data for the point
    """
    # Generate dummy data based on location and date
    # In a real implementation, this would fetch data from a weather API or database
    
    # Seed random number generator based on inputs for reproducibility
    seed = int(year * 10000 + month * 100 + day + latitude * 100 + longitude * 100)
    np.random.seed(seed)
    
    # Base temperature varies by latitude (colder at higher latitudes)
    base_temp = 30 - (latitude - 30) * 0.8
    
    # Seasonal variation (northern hemisphere)
    month_factor = math.cos((month - 1) / 12 * 2 * math.pi)
    seasonal_temp = 15 * month_factor
    
    # Daily random variation
    daily_variation = np.random.normal(0, 3)
    
    # Calculate temperatures
    avg_temp = base_temp + seasonal_temp + daily_variation
    max_temp = avg_temp + np.random.uniform(3, 8)
    min_temp = avg_temp - np.random.uniform(3, 8)
    
    # Calculate other weather parameters
    rel_humidity = 50 + np.random.normal(0, 15)
    rel_humidity = max(0, min(100, rel_humidity))
    
    spec_humidity = rel_humidity * 0.1 + np.random.normal(0, 0.5)
    spec_humidity = max(0, spec_humidity)
    
    # Radiation depends on latitude and season
    radiation_factor = math.cos((latitude - 40) / 50 * math.pi / 2) * (1 + month_factor) / 2
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
    
    return {
        "tasmax": {"value": max_temp, "unit": "°C"},
        "tas": {"value": avg_temp, "unit": "°C"},
        "tasmin": {"value": min_temp, "unit": "°C"},
        "hurs": {"value": rel_humidity, "unit": "%"},
        "huss": {"value": spec_humidity, "unit": "g/kg"},
        "rlds": {"value": longwave_rad, "unit": "W/m²"},
        "rsds": {"value": shortwave_rad, "unit": "W/m²"},
        "pr": {"value": precipitation, "unit": "mm"},
        "sfcWind": {"value": wind_speed, "unit": "m/s"}
    }

def get_weather_data_BA(year: int, month: int, day: int, ba_name: str) -> Dict[str, Any]:
    """
    Get weather data for a Balancing Authority and date.
    This is a placeholder for the original weather_data_extractor_BA.py functionality.
    
    Args:
        year: Year
        month: Month
        day: Day
        ba_name: Name of the Balancing Authority
        
    Returns:
        Weather data for the Balancing Authority
    """
    # Map BA name to approximate center coordinates
    ba_coordinates = {
        "AESO": (53.0, -113.0),
        "AZPS": (34.0, -112.0),
        "AVA": (47.5, -117.5),
        "BANC": (38.5, -121.5),
        "BPA": (46.0, -122.0),
        "BCHA": (50.0, -123.0),
        "CISO": (37.0, -120.0),
        "TPWR": (47.2, -122.5),
        "EPE": (31.8, -106.5),
        "IPCO": (43.5, -116.0),
        "IID": (33.0, -115.5),
        "LDWP": (34.0, -118.2),
        "GWA": (48.5, -109.0),
        "NEVP": (36.0, -115.0),
        "NWMT": (46.5, -112.0),
        "PACE": (41.0, -111.0),
        "PACW": (45.0, -123.0),
        "PGE": (45.5, -122.5),
        "PSCO": (39.5, -105.0),
        "PNM": (35.0, -106.5),
        "PSE": (47.5, -122.0),
        "SRP": (33.5, -112.0),
        "SCL": (47.6, -122.3),
        "SPPC": (39.5, -119.5),
        "TEPC": (32.2, -110.9),
        "TID": (37.5, -120.8),
        "WACM": (39.0, -107.0),
        "WALC": (35.0, -114.0)
    }
    
    # Get coordinates for the BA
    if ba_name in ba_coordinates:
        latitude, longitude = ba_coordinates[ba_name]
    else:
        # Default to center of WECC region if BA not found
        latitude, longitude = (40.0, -115.0)
    
    # Get weather data for the BA's center point
    return get_weather_data(year, month, day, latitude, longitude)

def fill_nan_values(data: np.ndarray) -> np.ndarray:
    """
    Fill NaN values in a 2D array by interpolating from nearby valid values.
    
    Args:
        data: 2D array with NaN values
        
    Returns:
        2D array with NaN values filled
    """
    n = len(data)
    for i in range(n):
        # Check if current value is NaN
        if np.isnan(data[i, 2]):
            # Search for the nearest valid value
            prev_valid = next((j for j in range(i-1, -1, -1) if not np.isnan(data[j, 2])), None)
            next_valid = next((j for j in range(i+1, n) if not np.isnan(data[j, 2])), None)
            
            if prev_valid is not None and next_valid is not None:
                data[i, 2] = (data[prev_valid, 2] + data[next_valid, 2]) / 2
            elif prev_valid is not None:
                data[i, 2] = data[prev_valid, 2]
            elif next_valid is not None:
                data[i, 2] = data[next_valid, 2]
    
    return data

def generate_heatmap_data(
    parameter: str,
    date_obj: date,
    min_lat: float = 30.0,
    max_lat: float = 58.0,
    min_lon: float = -130.0,
    max_lon: float = -100.0,
    resolution: float = 1.0
) -> Tuple[List[List[float]], Dict[str, float]]:
    """
    Generate heatmap data for a specific parameter and date.
    
    Args:
        parameter: Weather parameter (temperature, humidity, wind_speed, precipitation, radiation)
        date_obj: Date
        min_lat: Minimum latitude
        max_lat: Maximum latitude
        min_lon: Minimum longitude
        max_lon: Maximum longitude
        resolution: Grid resolution in degrees
        
    Returns:
        Tuple of (heatmap data, bounds)
    """
    # Define latitude and longitude ranges with the specified resolution
    lat_range = np.arange(min_lat, max_lat + resolution, resolution)
    lon_range = np.arange(min_lon, max_lon + resolution, resolution)
    
    # Create a list of coordinates within the specified range
    coordinates = [(lat, lon) for lat in lat_range for lon in lon_range]
    
    # Generate weather data for each coordinate
    heatmap_data = []
    values = []
    
    for lat, lon in coordinates:
        weather_data = get_weather_data(
            date_obj.year, 
            date_obj.month, 
            date_obj.day, 
            lat, 
            lon
        )
        
        # Extract the relevant parameter
        if parameter == "temperature":
            value = weather_data["tas"]["value"]
        elif parameter == "humidity":
            value = weather_data["hurs"]["value"]
        elif parameter == "wind_speed":
            value = weather_data["sfcWind"]["value"]
        elif parameter == "precipitation":
            value = weather_data["pr"]["value"]
        elif parameter == "radiation":
            value = weather_data["rsds"]["value"]
        else:
            value = 0
        
        heatmap_data.append([lat, lon, value])
        values.append(value)
    
    # Calculate bounds
    bounds = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
        "min_value": min(values) if values else 0,
        "max_value": max(values) if values else 100
    }
    
    return heatmap_data, bounds
