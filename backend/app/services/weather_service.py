from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import math
import json
import redis
import pandas as pd
import numpy as np

from app.models.weather import WeatherData
from app.models.grid import Bus, Branch, Generator, Load, Substation
from app.core.config import settings
from app.services.grid_service import (
    get_bus_by_id,
    get_branch_by_id,
    get_generator_by_id,
    get_load_by_id,
    get_substation_by_id
)

# Initialize Redis client for caching
redis_client = redis.Redis.from_url(settings.REDIS_URL)
CACHE_EXPIRATION = 60 * 60 * 24  # 24 hours in seconds

async def get_weather_data_for_point(
    db: AsyncSession, 
    latitude: float, 
    longitude: float, 
    date: date
) -> Optional[Dict[str, Any]]:
    """
    Get weather data for a specific point and date.
    
    Args:
        db: Database session
        latitude: Latitude of the point
        longitude: Longitude of the point
        date: Date to get weather data for
        
    Returns:
        Weather data for the point
    """
    # Check cache first
    cache_key = f"weather:{latitude}:{longitude}:{date.isoformat()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query database
    query = select(WeatherData).where(
        and_(
            func.ST_DWithin(
                WeatherData.geometry, 
                func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
                0.1  # Approximately 11km at the equator
            ),
            WeatherData.date == date
        )
    ).order_by(
        func.ST_Distance(
            WeatherData.geometry, 
            func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        )
    ).limit(1)
    
    result = await db.execute(query)
    weather_data = result.scalars().first()
    
    if not weather_data:
        # If not in database, fetch from external source
        # This is a placeholder for the actual implementation
        # In a real implementation, you would call an external weather API
        weather_data = await fetch_weather_data_from_external_source(latitude, longitude, date)
        
        if not weather_data:
            return None
    
    # Convert to dictionary
    data = {
        "date": weather_data.date.isoformat(),
        "latitude": weather_data.latitude,
        "longitude": weather_data.longitude,
        "max_temperature": weather_data.max_temperature,
        "avg_temperature": weather_data.avg_temperature,
        "min_temperature": weather_data.min_temperature,
        "relative_humidity": weather_data.relative_humidity,
        "specific_humidity": weather_data.specific_humidity,
        "longwave_radiation": weather_data.longwave_radiation,
        "shortwave_radiation": weather_data.shortwave_radiation,
        "precipitation": weather_data.precipitation,
        "wind_speed": weather_data.wind_speed
    }
    
    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(data))
    
    return data

async def get_weather_data_for_range(
    db: AsyncSession, 
    latitude: float, 
    longitude: float, 
    start_date: date,
    end_date: date
) -> List[Dict[str, Any]]:
    """
    Get weather data for a specific point over a date range.
    
    Args:
        db: Database session
        latitude: Latitude of the point
        longitude: Longitude of the point
        start_date: Start date
        end_date: End date
        
    Returns:
        List of weather data for each day in the range
    """
    result = []
    current_date = start_date
    
    while current_date <= end_date:
        weather_data = await get_weather_data_for_point(db, latitude, longitude, current_date)
        if weather_data:
            result.append(weather_data)
        current_date += timedelta(days=1)
    
    return result

async def get_weather_data_for_component(
    db: AsyncSession,
    component_type: str,
    component_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Get weather data and impact calculations for a specific grid component over a date range.
    
    Args:
        db: Database session
        component_type: Type of component (bus, branch, generator, load, substation)
        component_id: ID of the component
        start_date: Start date
        end_date: End date
        
    Returns:
        Weather data and impact calculations for the component
    """
    # Get component data
    component = None
    if component_type == "bus":
        component = await get_bus_by_id(db, component_id)
    elif component_type == "branch":
        component = await get_branch_by_id(db, component_id)
    elif component_type == "generator":
        component = await get_generator_by_id(db, component_id)
    elif component_type == "load":
        component = await get_load_by_id(db, component_id)
    elif component_type == "substation":
        component = await get_substation_by_id(db, component_id)
    
    if not component:
        return None
    
    # Extract coordinates from component geometry
    coordinates = extract_coordinates_from_geometry(component["geometry"])
    
    if not coordinates:
        return None
    
    # Get weather data for the component's location
    weather_data = await get_weather_data_for_range(
        db, 
        latitude=coordinates[1], 
        longitude=coordinates[0], 
        start_date=start_date,
        end_date=end_date
    )
    
    if not weather_data:
        return None
    
    # Calculate impacts based on component type
    impacts = calculate_impacts(component_type, component, weather_data)
    
    return {
        "component": component,
        "weather_data": weather_data,
        "impacts": impacts
    }

def extract_coordinates_from_geometry(geometry: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """
    Extract coordinates from a GeoJSON geometry.
    
    Args:
        geometry: GeoJSON geometry
        
    Returns:
        Tuple of (longitude, latitude) or None if not a point
    """
    if geometry["type"] == "Point":
        return geometry["coordinates"]
    elif geometry["type"] == "LineString":
        # For lines, return the midpoint
        coords = geometry["coordinates"]
        mid_idx = len(coords) // 2
        return coords[mid_idx]
    elif geometry["type"] == "Polygon":
        # For polygons, return the centroid (simplified)
        coords = geometry["coordinates"][0]  # Outer ring
        x = sum(p[0] for p in coords) / len(coords)
        y = sum(p[1] for p in coords) / len(coords)
        return (x, y)
    
    return None

def calculate_impacts(
    component_type: str, 
    component: Dict[str, Any], 
    weather_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate weather impacts on a component.
    
    Args:
        component_type: Type of component
        component: Component data
        weather_data: Weather data for the component's location
        
    Returns:
        Impact calculations
    """
    if not weather_data:
        return {}
    
    # Get the first day's data as reference
    day_one_data = weather_data[0]
    day_one_max_temp = day_one_data["max_temperature"]
    
    impacts = {
        "daily_impacts": []
    }
    
    for day_data in weather_data:
        daily_impact = {
            "date": day_data["date"],
            "weather": {
                "max_temperature": day_data["max_temperature"],
                "avg_temperature": day_data["avg_temperature"],
                "min_temperature": day_data["min_temperature"],
                "relative_humidity": day_data["relative_humidity"],
                "specific_humidity": day_data["specific_humidity"],
                "longwave_radiation": day_data["longwave_radiation"],
                "shortwave_radiation": day_data["shortwave_radiation"],
                "precipitation": day_data["precipitation"],
                "wind_speed": day_data["wind_speed"]
            }
        }
        
        # Calculate component-specific impacts
        if component_type == "load":
            p_load = component["p_load"]
            q_load = component["q_load"]
            longitude = component["geometry"]["coordinates"][0]
            
            # Calculate PL_day and QL_day for the current day
            max_temp_current = day_data["max_temperature"]
            PL_day_current = p_load * (1 + 0.01 * (5.33 - 0.067 * longitude) * (max_temp_current - day_one_max_temp))
            PL_day_current = max(0, PL_day_current)  # Ensure PL_day_current is not negative
            
            QL_day_current = q_load * (1 + 0.01 * (5.33 - 0.067 * longitude) * (max_temp_current - day_one_max_temp))
            
            daily_impact["load_impact"] = {
                "PL_day": PL_day_current,
                "QL_day": QL_day_current
            }
            
        elif component_type == "generator":
            p_gen = component["p_gen"]
            q_gen = component["q_gen"]
            gen_type = component["gen_type"]
            
            max_temp_current = day_data["max_temperature"]
            wind_speed_current = day_data["wind_speed"]
            
            # Default values
            V_cutin = 3
            V_cutout = 25
            V_rated = 12
            T_th_PV = 35
            ro_sf = 0.02
            T_th_gen = 40
            ro_th = 0.031
            eff_no = 0.6
            
            # Calculate generator impacts based on type
            if gen_type == "WT-Onshore":
                if wind_speed_current < V_cutin or wind_speed_current > V_cutout:
                    p_gen_day_current = 0
                elif V_cutin <= wind_speed_current < V_rated:
                    p_gen_day_current = p_gen * ((wind_speed_current - V_cutin) / (V_rated - V_cutin))
                else:
                    p_gen_day_current = p_gen
                
                eff = 1
                q_gen_day_current = q_gen
                
            elif gen_type in ["SolarPV-Tracking", "SolarPV-NonTracking"]:
                if max_temp_current <= T_th_PV:
                    eff = 1
                else:
                    eff = eff_no * (1 - ro_sf * (max_temp_current - T_th_PV))
                
                p_gen_day_current = p_gen * eff
                q_gen_day_current = q_gen
                
            else:  # Thermal generators
                if max_temp_current <= T_th_gen:
                    eff = 1
                else:
                    eff = 1 - ro_th * (max_temp_current - T_th_gen)
                
                p_gen_day_current = p_gen * eff
                q_gen_day_current = q_gen * eff
            
            daily_impact["generator_impact"] = {
                "Pgen_day": p_gen_day_current,
                "Qgen_day": q_gen_day_current,
                "Efficiency": eff
            }
            
        elif component_type == "branch":
            rate1 = component["rate1"]
            
            max_temp_current = day_data["max_temperature"]
            alpha_l = 1
            T_RL = 35
            
            # Calculate line capacity for the current day
            CL_day_current = rate1 * alpha_l * math.sqrt(T_RL / max_temp_current)
            
            # Check the conditions and adjust CL_day_current if necessary
            if CL_day_current > rate1 or CL_day_current < 0:
                CL_day_current = rate1
            
            daily_impact["branch_impact"] = {
                "CL_day": CL_day_current
            }
        
        impacts["daily_impacts"].append(daily_impact)
    
    # Calculate min/max values and corresponding dates
    if impacts["daily_impacts"]:
        impacts["summary"] = calculate_summary(impacts["daily_impacts"], component_type)
    
    return impacts

def calculate_summary(daily_impacts: List[Dict[str, Any]], component_type: str) -> Dict[str, Any]:
    """
    Calculate summary statistics from daily impacts.
    
    Args:
        daily_impacts: List of daily impact data
        component_type: Type of component
        
    Returns:
        Summary statistics
    """
    summary = {
        "weather": {
            "max_temperature": {"min": None, "min_date": None, "max": None, "max_date": None},
            "avg_temperature": {"min": None, "min_date": None, "max": None, "max_date": None},
            "min_temperature": {"min": None, "min_date": None, "max": None, "max_date": None},
            "relative_humidity": {"min": None, "min_date": None, "max": None, "max_date": None},
            "specific_humidity": {"min": None, "min_date": None, "max": None, "max_date": None},
            "longwave_radiation": {"min": None, "min_date": None, "max": None, "max_date": None},
            "shortwave_radiation": {"min": None, "min_date": None, "max": None, "max_date": None},
            "precipitation": {"min": None, "min_date": None, "max": None, "max_date": None},
            "wind_speed": {"min": None, "min_date": None, "max": None, "max_date": None}
        }
    }
    
    # Add component-specific summary fields
    if component_type == "load":
        summary["load_impact"] = {
            "PL_day": {"min": None, "min_date": None, "max": None, "max_date": None},
            "QL_day": {"min": None, "min_date": None, "max": None, "max_date": None}
        }
    elif component_type == "generator":
        summary["generator_impact"] = {
            "Pgen_day": {"min": None, "min_date": None, "max": None, "max_date": None},
            "Qgen_day": {"min": None, "min_date": None, "max": None, "max_date": None},
            "Efficiency": {"min": None, "min_date": None, "max": None, "max_date": None}
        }
    elif component_type == "branch":
        summary["branch_impact"] = {
            "CL_day": {"min": None, "min_date": None, "max": None, "max_date": None}
        }
    
    # Calculate min/max for each parameter
    for impact in daily_impacts:
        date = impact["date"]
        
        # Weather parameters
        for param in summary["weather"]:
            value = impact["weather"][param]
            
            if summary["weather"][param]["min"] is None or value < summary["weather"][param]["min"]:
                summary["weather"][param]["min"] = value
                summary["weather"][param]["min_date"] = date
            
            if summary["weather"][param]["max"] is None or value > summary["weather"][param]["max"]:
                summary["weather"][param]["max"] = value
                summary["weather"][param]["max_date"] = date
        
        # Component-specific parameters
        if component_type == "load" and "load_impact" in impact:
            for param in summary["load_impact"]:
                value = impact["load_impact"][param]
                
                if summary["load_impact"][param]["min"] is None or value < summary["load_impact"][param]["min"]:
                    summary["load_impact"][param]["min"] = value
                    summary["load_impact"][param]["min_date"] = date
                
                if summary["load_impact"][param]["max"] is None or value > summary["load_impact"][param]["max"]:
                    summary["load_impact"][param]["max"] = value
                    summary["load_impact"][param]["max_date"] = date
        
        elif component_type == "generator" and "generator_impact" in impact:
            for param in summary["generator_impact"]:
                value = impact["generator_impact"][param]
                
                if summary["generator_impact"][param]["min"] is None or value < summary["generator_impact"][param]["min"]:
                    summary["generator_impact"][param]["min"] = value
                    summary["generator_impact"][param]["min_date"] = date
                
                if summary["generator_impact"][param]["max"] is None or value > summary["generator_impact"][param]["max"]:
                    summary["generator_impact"][param]["max"] = value
                    summary["generator_impact"][param]["max_date"] = date
        
        elif component_type == "branch" and "branch_impact" in impact:
            for param in summary["branch_impact"]:
                value = impact["branch_impact"][param]
                
                if summary["branch_impact"][param]["min"] is None or value < summary["branch_impact"][param]["min"]:
                    summary["branch_impact"][param]["min"] = value
                    summary["branch_impact"][param]["min_date"] = date
                
                if summary["branch_impact"][param]["max"] is None or value > summary["branch_impact"][param]["max"]:
                    summary["branch_impact"][param]["max"] = value
                    summary["branch_impact"][param]["max_date"] = date
    
    return summary

async def fetch_weather_data_from_external_source(
    latitude: float, 
    longitude: float, 
    date: date
) -> Optional[WeatherData]:
    """
    Fetch weather data from an external source.
    This is a placeholder for the actual implementation.
    
    Args:
        latitude: Latitude of the point
        longitude: Longitude of the point
        date: Date to get weather data for
        
    Returns:
        Weather data for the point
    """
    # In a real implementation, you would call an external weather API
    # For now, we'll return some dummy data
    weather_data = WeatherData(
        date=date,
        latitude=latitude,
        longitude=longitude,
        max_temperature=25.0,
        avg_temperature=20.0,
        min_temperature=15.0,
        relative_humidity=60.0,
        specific_humidity=10.0,
        longwave_radiation=200.0,
        shortwave_radiation=800.0,
        precipitation=0.0,
        wind_speed=5.0,
        source="dummy"
    )
    
    return weather_data
