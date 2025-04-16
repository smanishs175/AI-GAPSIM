from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.services.weather_service import (
    get_weather_data_for_point,
    get_weather_data_for_range,
    get_weather_data_for_component
)
from app.services.auth_service import get_current_active_user
from app.models.auth import User

router = APIRouter()

@router.get("/point")
async def get_weather_for_point(
    latitude: float = Query(..., description="Latitude of the point"),
    longitude: float = Query(..., description="Longitude of the point"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get weather data for a specific point and date.
    
    Args:
        latitude: Latitude of the point
        longitude: Longitude of the point
        date: Date in YYYY-MM-DD format
        
    Returns:
        Weather data for the point
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    weather_data = await get_weather_data_for_point(
        db, 
        latitude=latitude, 
        longitude=longitude, 
        date=date_obj
    )
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather data not found for the specified point and date"
        )
    
    return weather_data

@router.get("/range")
async def get_weather_for_range(
    latitude: float = Query(..., description="Latitude of the point"),
    longitude: float = Query(..., description="Longitude of the point"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get weather data for a specific point over a date range.
    
    Args:
        latitude: Latitude of the point
        longitude: Longitude of the point
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of weather data for each day in the range
    """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    if start_date_obj > end_date_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    weather_data = await get_weather_data_for_range(
        db, 
        latitude=latitude, 
        longitude=longitude, 
        start_date=start_date_obj,
        end_date=end_date_obj
    )
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather data not found for the specified point and date range"
        )
    
    return weather_data

@router.get("/component/{component_type}/{component_id}")
async def get_weather_for_component(
    component_type: str = Path(..., description="Type of component (bus, branch, generator, load, substation)"),
    component_id: int = Path(..., description="ID of the component"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get weather data and impact calculations for a specific grid component over a date range.
    
    Args:
        component_type: Type of component (bus, branch, generator, load, substation)
        component_id: ID of the component
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Weather data and impact calculations for the component
    """
    if component_type not in ["bus", "branch", "generator", "load", "substation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid component type. Must be one of: bus, branch, generator, load, substation"
        )
    
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    if start_date_obj > end_date_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    result = await get_weather_data_for_component(
        db,
        component_type=component_type,
        component_id=component_id,
        start_date=start_date_obj,
        end_date=end_date_obj
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather data not found for the specified {component_type} and date range"
        )
    
    return result
