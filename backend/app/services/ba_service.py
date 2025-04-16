from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, between
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import json
import redis
import pandas as pd
import numpy as np
import random

from app.models.grid import BalancingAuthority, Generator, Load
from app.models.weather import EnergyEmergencyAlert
from app.core.config import settings

# Initialize Redis client for caching
redis_client = redis.Redis.from_url(settings.REDIS_URL)
CACHE_EXPIRATION = 60 * 60 * 24  # 24 hours in seconds

async def get_all_bas(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Get all Balancing Authorities.

    Args:
        db: Database session

    Returns:
        List of Balancing Authority data
    """
    # Check cache first
    cache_key = "bas:all"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Query database
    query = select(BalancingAuthority)
    result = await db.execute(query)
    bas = result.scalars().all()

    # If no BAs in database, generate dummy data
    if not bas:
        ba_data = generate_dummy_bas()
    else:
        # Convert to GeoJSON format
        ba_data = []
        for ba in bas:
            ba_dict = {
                "id": ba.id,
                "name": ba.name,
                "abbreviation": ba.abbreviation,
                "geometry": {"type": "Polygon", "coordinates": [[[float(x) for x in point.split()] for point in ba.geometry.replace("POLYGON((", "").replace("))", "").split(", ")]]},
                "metadata": ba.metadata_json
            }
            ba_data.append(ba_dict)

    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(ba_data))

    return ba_data

async def get_ba_by_id(db: AsyncSession, ba_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific Balancing Authority by ID.

    Args:
        db: Database session
        ba_id: ID of the Balancing Authority

    Returns:
        Balancing Authority data
    """
    # Check cache first
    cache_key = f"bas:{ba_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Query database
    query = select(BalancingAuthority).where(BalancingAuthority.id == ba_id)
    result = await db.execute(query)
    ba = result.scalars().first()

    if not ba:
        # If not in database, check if it's in the dummy data
        all_bas = await get_all_bas(db)
        ba_dict = next((b for b in all_bas if b["id"] == ba_id), None)
    else:
        # Convert to GeoJSON format
        ba_dict = {
            "id": ba.id,
            "name": ba.name,
            "abbreviation": ba.abbreviation,
            "geometry": {"type": "Polygon", "coordinates": [[[float(x) for x in point.split()] for point in ba.geometry.replace("POLYGON((", "").replace("))", "").split(", ")]]},
            "metadata": ba.metadata_json
        }

    if not ba_dict:
        return None

    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(ba_dict))

    return ba_dict

async def get_ba_events(
    db: AsyncSession,
    ba_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Get Energy Emergency Alert events for a Balancing Authority.

    Args:
        db: Database session
        ba_id: ID of the Balancing Authority
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of EEA events
    """
    # Build cache key
    cache_key = f"bas:{ba_id}:events"
    if start_date:
        cache_key += f":{start_date.isoformat()}"
    if end_date:
        cache_key += f":{end_date.isoformat()}"

    # Check cache first
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Query database
    query = select(EnergyEmergencyAlert).where(EnergyEmergencyAlert.ba_id == ba_id)

    if start_date:
        query = query.where(EnergyEmergencyAlert.date >= start_date)

    if end_date:
        query = query.where(EnergyEmergencyAlert.date <= end_date)

    result = await db.execute(query)
    events = result.scalars().all()

    # If no events in database, generate dummy data
    if not events:
        event_data = generate_dummy_ba_events(ba_id, start_date, end_date)
    else:
        # Convert to dictionary format
        event_data = []
        for event in events:
            event_dict = {
                "id": event.id,
                "ba_id": event.ba_id,
                "date": event.date.isoformat(),
                "level": event.level,
                "description": event.description,
                "metadata": event.metadata_json
            }
            event_data.append(event_dict)

    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(event_data))

    return event_data

async def get_ba_demand(
    db: AsyncSession,
    ba_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Get demand data for a Balancing Authority.

    Args:
        db: Database session
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Demand data for the Balancing Authority
    """
    # Build cache key
    cache_key = f"bas:{ba_id}:demand:{start_date.isoformat()}:{end_date.isoformat()}"

    # Check cache first
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Query database to get all loads in the BA
    # This would require a spatial query to find loads within the BA polygon
    # For simplicity, we'll generate dummy data
    demand_data = generate_dummy_ba_demand(ba_id, start_date, end_date)

    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(demand_data))

    return demand_data

async def get_ba_generation(
    db: AsyncSession,
    ba_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Get generation data for a Balancing Authority.

    Args:
        db: Database session
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Generation data for the Balancing Authority
    """
    # Build cache key
    cache_key = f"bas:{ba_id}:generation:{start_date.isoformat()}:{end_date.isoformat()}"

    # Check cache first
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Query database to get all generators in the BA
    # This would require a spatial query to find generators within the BA polygon
    # For simplicity, we'll generate dummy data
    generation_data = generate_dummy_ba_generation(ba_id, start_date, end_date)

    # Cache the result
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(generation_data))

    return generation_data

def generate_dummy_bas() -> List[Dict[str, Any]]:
    """
    Generate dummy Balancing Authority data.

    Returns:
        List of dummy Balancing Authority data
    """
    # WECC Balancing Authorities
    ba_list = [
        {"id": 1, "name": "Alberta Electric System Operator", "abbreviation": "AESO"},
        {"id": 2, "name": "Arizona Public Service Company", "abbreviation": "AZPS"},
        {"id": 3, "name": "Avista Corporation", "abbreviation": "AVA"},
        {"id": 4, "name": "Balancing Authority of Northern California", "abbreviation": "BANC"},
        {"id": 5, "name": "Bonneville Power Administration", "abbreviation": "BPA"},
        {"id": 6, "name": "British Columbia Hydro and Power Authority", "abbreviation": "BCHA"},
        {"id": 7, "name": "California Independent System Operator", "abbreviation": "CISO"},
        {"id": 8, "name": "City of Tacoma", "abbreviation": "TPWR"},
        {"id": 9, "name": "El Paso Electric Company", "abbreviation": "EPE"},
        {"id": 10, "name": "Idaho Power Company", "abbreviation": "IPCO"},
        {"id": 11, "name": "Imperial Irrigation District", "abbreviation": "IID"},
        {"id": 12, "name": "Los Angeles Department of Water and Power", "abbreviation": "LDWP"},
        {"id": 13, "name": "NaturEner Power Watch", "abbreviation": "GWA"},
        {"id": 14, "name": "Nevada Power Company", "abbreviation": "NEVP"},
        {"id": 15, "name": "NorthWestern Energy", "abbreviation": "NWMT"},
        {"id": 16, "name": "PacifiCorp East", "abbreviation": "PACE"},
        {"id": 17, "name": "PacifiCorp West", "abbreviation": "PACW"},
        {"id": 18, "name": "Portland General Electric Company", "abbreviation": "PGE"},
        {"id": 19, "name": "Public Service Company of Colorado", "abbreviation": "PSCO"},
        {"id": 20, "name": "Public Service Company of New Mexico", "abbreviation": "PNM"},
        {"id": 21, "name": "Puget Sound Energy", "abbreviation": "PSE"},
        {"id": 22, "name": "Salt River Project", "abbreviation": "SRP"},
        {"id": 23, "name": "Seattle City Light", "abbreviation": "SCL"},
        {"id": 24, "name": "Sierra Pacific Power Company", "abbreviation": "SPPC"},
        {"id": 25, "name": "Tucson Electric Power Company", "abbreviation": "TEPC"},
        {"id": 26, "name": "Turlock Irrigation District", "abbreviation": "TID"},
        {"id": 27, "name": "Western Area Power Administration - Colorado-Missouri", "abbreviation": "WACM"},
        {"id": 28, "name": "Western Area Power Administration - Lower Colorado", "abbreviation": "WALC"}
    ]

    # Generate dummy polygon for each BA
    for ba in ba_list:
        # Generate a simple polygon (this is just a placeholder)
        # In a real implementation, you would use actual BA boundaries
        center_lat = 40 + (ba["id"] - 1) % 7 * 2
        center_lon = -120 + (ba["id"] - 1) // 7 * 5

        # Create a simple square polygon
        size = 1.0
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [center_lon - size, center_lat - size],
                [center_lon + size, center_lat - size],
                [center_lon + size, center_lat + size],
                [center_lon - size, center_lat + size],
                [center_lon - size, center_lat - size]
            ]]
        }

        ba["geometry"] = polygon
        ba["metadata"] = {
            "region": "WECC",
            "country": "USA" if ba["id"] not in [1, 6] else "Canada"
        }

    return ba_list

def generate_dummy_ba_events(
    ba_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Generate dummy Energy Emergency Alert events for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of dummy EEA events
    """
    # Set default date range if not provided
    if not start_date:
        start_date = date(2020, 1, 1)

    if not end_date:
        end_date = date(2020, 12, 31)

    # Seed random number generator for reproducibility
    random.seed(ba_id)

    # Generate random number of events (0-10)
    num_events = random.randint(0, 10)

    events = []
    for i in range(num_events):
        # Generate random date within range
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        event_date = start_date + timedelta(days=random_days)

        # Generate random level (1-3)
        level = random.randint(1, 3)

        # Generate description based on level
        if level == 1:
            description = "All available resources in use."
        elif level == 2:
            description = "Load management procedures in effect."
        else:  # level == 3
            description = "Firm load interruption imminent or in progress."

        events.append({
            "id": i + 1,
            "ba_id": ba_id,
            "date": event_date.isoformat(),
            "level": level,
            "description": description,
            "metadata": {
                "duration_hours": random.randint(1, 24),
                "affected_mw": random.randint(100, 1000)
            }
        })

    return events

def generate_dummy_ba_demand(
    ba_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Generate dummy demand data for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Dummy demand data
    """
    # Seed random number generator for reproducibility
    random.seed(ba_id)

    # Generate base demand values
    base_p_load = random.uniform(1000, 5000)  # MW
    base_q_load = base_p_load * random.uniform(0.1, 0.3)  # MVAr

    # Generate daily demand data
    dates = []
    p_loads = []
    q_loads = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.isoformat())

        # Add daily variation (higher on weekdays, lower on weekends)
        day_of_week = current_date.weekday()
        weekday_factor = 1.0 if day_of_week < 5 else 0.8

        # Add seasonal variation (higher in summer and winter)
        month = current_date.month
        if month in [6, 7, 8]:  # Summer
            seasonal_factor = 1.2
        elif month in [12, 1, 2]:  # Winter
            seasonal_factor = 1.1
        else:  # Spring/Fall
            seasonal_factor = 0.9

        # Add random variation
        random_factor = random.uniform(0.9, 1.1)

        # Calculate daily demand
        daily_p_load = base_p_load * weekday_factor * seasonal_factor * random_factor
        daily_q_load = base_q_load * weekday_factor * seasonal_factor * random_factor

        p_loads.append(daily_p_load)
        q_loads.append(daily_q_load)

        current_date += timedelta(days=1)

    return {
        "ba_id": ba_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "dates": dates,
        "p_load": p_loads,
        "q_load": q_loads
    }

def generate_dummy_ba_generation(
    ba_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Generate dummy generation data for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Dummy generation data
    """
    # Seed random number generator for reproducibility
    random.seed(ba_id + 100)  # Different seed than demand

    # Define generation mix for the BA
    gen_types = ["Hydro", "Natural Gas", "Coal", "Nuclear", "Wind", "Solar", "Geothermal", "Biomass"]

    # Assign random capacity to each type
    total_capacity = random.uniform(1500, 6000)  # MW

    gen_capacities = {}
    remaining_capacity = total_capacity

    for i, gen_type in enumerate(gen_types[:-1]):  # All except the last one
        if i == len(gen_types) - 2:  # Second to last
            capacity = remaining_capacity
        else:
            capacity = remaining_capacity * random.uniform(0.1, 0.4)

        gen_capacities[gen_type] = capacity
        remaining_capacity -= capacity

    gen_capacities[gen_types[-1]] = remaining_capacity  # Assign remaining to last type

    # Generate daily generation data
    dates = []
    generation_by_type = {gen_type: [] for gen_type in gen_types}

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.isoformat())

        # Add daily variation for each type
        for gen_type in gen_types:
            capacity = gen_capacities[gen_type]

            # Different factors based on generation type
            if gen_type == "Solar":
                # Solar varies by season and is zero at night (daily average)
                month = current_date.month
                if month in [5, 6, 7, 8, 9]:  # Summer
                    factor = random.uniform(0.4, 0.6)
                else:  # Winter
                    factor = random.uniform(0.2, 0.4)
            elif gen_type == "Wind":
                # Wind is more variable
                factor = random.uniform(0.1, 0.7)
            elif gen_type in ["Hydro", "Natural Gas"]:
                # These can be dispatched to meet demand
                factor = random.uniform(0.5, 0.9)
            else:
                # Baseload generation
                factor = random.uniform(0.7, 0.95)

            daily_generation = capacity * factor
            generation_by_type[gen_type].append(daily_generation)

        current_date += timedelta(days=1)

    return {
        "ba_id": ba_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "dates": dates,
        "generation_by_type": generation_by_type,
        "capacities": gen_capacities
    }
