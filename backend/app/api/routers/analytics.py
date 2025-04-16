from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, between, desc
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.services.auth_service import get_current_active_user
from app.models.auth import User
from app.models.grid import Bus, Branch, Generator, Load, Substation, BalancingAuthority
from app.models.weather import WeatherData, EnergyEmergencyAlert

router = APIRouter()

@router.get("/weather-summary")
async def get_weather_summary(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of weather data for a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Summary of weather data
    """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get average temperature by day
    avg_temp_query = select(
        func.date_trunc('day', WeatherData.date).label('day'),
        func.avg(WeatherData.avg_temperature).label('avg_temp')
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj
        )
    ).group_by(
        func.date_trunc('day', WeatherData.date)
    ).order_by(
        func.date_trunc('day', WeatherData.date)
    )
    
    avg_temp_result = await db.execute(avg_temp_query)
    avg_temp_data = [{"date": row.day.strftime("%Y-%m-%d"), "value": row.avg_temp} for row in avg_temp_result]
    
    # Get average precipitation by day
    avg_precip_query = select(
        func.date_trunc('day', WeatherData.date).label('day'),
        func.avg(WeatherData.precipitation).label('avg_precip')
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj
        )
    ).group_by(
        func.date_trunc('day', WeatherData.date)
    ).order_by(
        func.date_trunc('day', WeatherData.date)
    )
    
    avg_precip_result = await db.execute(avg_precip_query)
    avg_precip_data = [{"date": row.day.strftime("%Y-%m-%d"), "value": row.avg_precip} for row in avg_precip_result]
    
    # Get average wind speed by day
    avg_wind_query = select(
        func.date_trunc('day', WeatherData.date).label('day'),
        func.avg(WeatherData.wind_speed).label('avg_wind')
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj
        )
    ).group_by(
        func.date_trunc('day', WeatherData.date)
    ).order_by(
        func.date_trunc('day', WeatherData.date)
    )
    
    avg_wind_result = await db.execute(avg_wind_query)
    avg_wind_data = [{"date": row.day.strftime("%Y-%m-%d"), "value": row.avg_wind} for row in avg_wind_result]
    
    # Get extreme weather events (high temperature, high wind, high precipitation)
    extreme_temp_query = select(
        WeatherData
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj,
            WeatherData.max_temperature > 35  # Threshold for extreme temperature
        )
    ).order_by(
        desc(WeatherData.max_temperature)
    ).limit(5)
    
    extreme_temp_result = await db.execute(extreme_temp_query)
    extreme_temp_data = [{
        "date": row.date.strftime("%Y-%m-%d"),
        "latitude": row.latitude,
        "longitude": row.longitude,
        "max_temperature": row.max_temperature
    } for row in extreme_temp_result.scalars()]
    
    extreme_wind_query = select(
        WeatherData
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj,
            WeatherData.wind_speed > 15  # Threshold for extreme wind
        )
    ).order_by(
        desc(WeatherData.wind_speed)
    ).limit(5)
    
    extreme_wind_result = await db.execute(extreme_wind_query)
    extreme_wind_data = [{
        "date": row.date.strftime("%Y-%m-%d"),
        "latitude": row.latitude,
        "longitude": row.longitude,
        "wind_speed": row.wind_speed
    } for row in extreme_wind_result.scalars()]
    
    extreme_precip_query = select(
        WeatherData
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj,
            WeatherData.precipitation > 20  # Threshold for extreme precipitation
        )
    ).order_by(
        desc(WeatherData.precipitation)
    ).limit(5)
    
    extreme_precip_result = await db.execute(extreme_precip_query)
    extreme_precip_data = [{
        "date": row.date.strftime("%Y-%m-%d"),
        "latitude": row.latitude,
        "longitude": row.longitude,
        "precipitation": row.precipitation
    } for row in extreme_precip_result.scalars()]
    
    return {
        "temperature_trend": avg_temp_data,
        "precipitation_trend": avg_precip_data,
        "wind_speed_trend": avg_wind_data,
        "extreme_events": {
            "high_temperature": extreme_temp_data,
            "high_wind": extreme_wind_data,
            "high_precipitation": extreme_precip_data
        }
    }

@router.get("/grid-statistics")
async def get_grid_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get statistics about the power grid.
    
    Returns:
        Grid statistics
    """
    # Count components by type
    bus_count_query = select(func.count(Bus.id))
    branch_count_query = select(func.count(Branch.id))
    generator_count_query = select(func.count(Generator.id))
    load_count_query = select(func.count(Load.id))
    substation_count_query = select(func.count(Substation.id))
    ba_count_query = select(func.count(BalancingAuthority.id))
    
    bus_count = await db.scalar(bus_count_query)
    branch_count = await db.scalar(branch_count_query)
    generator_count = await db.scalar(generator_count_query)
    load_count = await db.scalar(load_count_query)
    substation_count = await db.scalar(substation_count_query)
    ba_count = await db.scalar(ba_count_query)
    
    # Get generator statistics by type
    generator_by_type_query = select(
        Generator.gen_type,
        func.count(Generator.id).label('count'),
        func.sum(Generator.p_max).label('total_capacity')
    ).group_by(
        Generator.gen_type
    )
    
    generator_by_type_result = await db.execute(generator_by_type_query)
    generator_by_type_data = [{
        "type": row.gen_type or "Unknown",
        "count": row.count,
        "total_capacity": row.total_capacity
    } for row in generator_by_type_result]
    
    # Get total load
    total_load_query = select(func.sum(Load.p_load))
    total_load = await db.scalar(total_load_query) or 0
    
    # Get total generation capacity
    total_capacity_query = select(func.sum(Generator.p_max))
    total_capacity = await db.scalar(total_capacity_query) or 0
    
    return {
        "component_counts": {
            "buses": bus_count,
            "branches": branch_count,
            "generators": generator_count,
            "loads": load_count,
            "substations": substation_count,
            "balancing_authorities": ba_count
        },
        "generation": {
            "by_type": generator_by_type_data,
            "total_capacity": total_capacity
        },
        "load": {
            "total_load": total_load
        },
        "system_metrics": {
            "generation_to_load_ratio": total_capacity / total_load if total_load > 0 else 0
        }
    }

@router.get("/eea-analysis")
async def get_eea_analysis(
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analysis of Energy Emergency Alert (EEA) events.
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Analysis of EEA events
    """
    # Build query
    query = select(
        EnergyEmergencyAlert,
        BalancingAuthority.name.label('ba_name'),
        BalancingAuthority.abbreviation.label('ba_abbreviation')
    ).join(
        BalancingAuthority,
        EnergyEmergencyAlert.ba_id == BalancingAuthority.id
    )
    
    # Apply date filters if provided
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.where(EnergyEmergencyAlert.date >= start_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.where(EnergyEmergencyAlert.date <= end_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    # Execute query
    result = await db.execute(query)
    
    # Process results
    events = []
    for row in result:
        event = {
            "id": row.EnergyEmergencyAlert.id,
            "date": row.EnergyEmergencyAlert.date.strftime("%Y-%m-%d"),
            "level": row.EnergyEmergencyAlert.level,
            "description": row.EnergyEmergencyAlert.description,
            "ba_name": row.ba_name,
            "ba_abbreviation": row.ba_abbreviation,
            "metadata": row.EnergyEmergencyAlert.metadata_json
        }
        events.append(event)
    
    # Count events by level
    level_counts = {1: 0, 2: 0, 3: 0}
    for event in events:
        level = event["level"]
        if level in level_counts:
            level_counts[level] += 1
    
    # Count events by BA
    ba_counts = {}
    for event in events:
        ba = event["ba_abbreviation"]
        if ba not in ba_counts:
            ba_counts[ba] = 0
        ba_counts[ba] += 1
    
    # Count events by month
    month_counts = {}
    for event in events:
        month = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%Y-%m")
        if month not in month_counts:
            month_counts[month] = 0
        month_counts[month] += 1
    
    return {
        "events": events,
        "summary": {
            "total_events": len(events),
            "by_level": level_counts,
            "by_ba": ba_counts,
            "by_month": month_counts
        }
    }

@router.get("/weather-impact-correlation")
async def get_weather_impact_correlation(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get correlation between weather events and EEA events.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Correlation analysis
    """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get EEA events in the date range
    eea_query = select(
        EnergyEmergencyAlert,
        BalancingAuthority.name.label('ba_name'),
        BalancingAuthority.abbreviation.label('ba_abbreviation'),
        BalancingAuthority.geometry.label('ba_geometry')
    ).join(
        BalancingAuthority,
        EnergyEmergencyAlert.ba_id == BalancingAuthority.id
    ).where(
        and_(
            EnergyEmergencyAlert.date >= start_date_obj,
            EnergyEmergencyAlert.date <= end_date_obj
        )
    )
    
    eea_result = await db.execute(eea_query)
    
    # Process EEA events
    eea_events = []
    for row in eea_result:
        event = {
            "id": row.EnergyEmergencyAlert.id,
            "date": row.EnergyEmergencyAlert.date.strftime("%Y-%m-%d"),
            "level": row.EnergyEmergencyAlert.level,
            "ba_name": row.ba_name,
            "ba_abbreviation": row.ba_abbreviation
        }
        eea_events.append(event)
    
    # For each EEA event, get the weather data for the BA on that day
    correlation_data = []
    
    for event in eea_events:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        
        # Get average weather data for the BA region on the event date
        # This is a simplified approach - in a real implementation, you would use
        # the BA geometry to find weather data points within the BA boundary
        weather_query = select(
            func.avg(WeatherData.max_temperature).label('avg_max_temp'),
            func.avg(WeatherData.wind_speed).label('avg_wind_speed'),
            func.avg(WeatherData.precipitation).label('avg_precipitation')
        ).where(
            WeatherData.date == event_date
        )
        
        weather_result = await db.execute(weather_query)
        weather_row = weather_result.first()
        
        if weather_row:
            correlation_data.append({
                "eea_event": event,
                "weather_data": {
                    "avg_max_temperature": weather_row.avg_max_temp,
                    "avg_wind_speed": weather_row.avg_wind_speed,
                    "avg_precipitation": weather_row.avg_precipitation
                }
            })
    
    # Calculate average weather metrics for days with EEA events
    eea_days_weather = {
        "avg_max_temperature": 0,
        "avg_wind_speed": 0,
        "avg_precipitation": 0
    }
    
    if correlation_data:
        for item in correlation_data:
            eea_days_weather["avg_max_temperature"] += item["weather_data"]["avg_max_temperature"] or 0
            eea_days_weather["avg_wind_speed"] += item["weather_data"]["avg_wind_speed"] or 0
            eea_days_weather["avg_precipitation"] += item["weather_data"]["avg_precipitation"] or 0
        
        eea_days_weather["avg_max_temperature"] /= len(correlation_data)
        eea_days_weather["avg_wind_speed"] /= len(correlation_data)
        eea_days_weather["avg_precipitation"] /= len(correlation_data)
    
    # Get average weather metrics for all days in the range
    all_days_query = select(
        func.avg(WeatherData.max_temperature).label('avg_max_temp'),
        func.avg(WeatherData.wind_speed).label('avg_wind_speed'),
        func.avg(WeatherData.precipitation).label('avg_precipitation')
    ).where(
        and_(
            WeatherData.date >= start_date_obj,
            WeatherData.date <= end_date_obj
        )
    )
    
    all_days_result = await db.execute(all_days_query)
    all_days_row = all_days_result.first()
    
    all_days_weather = {
        "avg_max_temperature": all_days_row.avg_max_temp if all_days_row else 0,
        "avg_wind_speed": all_days_row.avg_wind_speed if all_days_row else 0,
        "avg_precipitation": all_days_row.avg_precipitation if all_days_row else 0
    }
    
    # Calculate percentage difference
    percentage_diff = {
        "max_temperature": (
            ((eea_days_weather["avg_max_temperature"] - all_days_weather["avg_max_temperature"]) / 
             all_days_weather["avg_max_temperature"]) * 100
            if all_days_weather["avg_max_temperature"] else 0
        ),
        "wind_speed": (
            ((eea_days_weather["avg_wind_speed"] - all_days_weather["avg_wind_speed"]) / 
             all_days_weather["avg_wind_speed"]) * 100
            if all_days_weather["avg_wind_speed"] else 0
        ),
        "precipitation": (
            ((eea_days_weather["avg_precipitation"] - all_days_weather["avg_precipitation"]) / 
             all_days_weather["avg_precipitation"]) * 100
            if all_days_weather["avg_precipitation"] else 0
        )
    }
    
    return {
        "correlation_data": correlation_data,
        "summary": {
            "eea_days_weather": eea_days_weather,
            "all_days_weather": all_days_weather,
            "percentage_difference": percentage_diff
        },
        "conclusion": {
            "temperature_correlation": "High" if abs(percentage_diff["max_temperature"]) > 10 else "Low",
            "wind_correlation": "High" if abs(percentage_diff["wind_speed"]) > 10 else "Low",
            "precipitation_correlation": "High" if abs(percentage_diff["precipitation"]) > 10 else "Low"
        }
    }
