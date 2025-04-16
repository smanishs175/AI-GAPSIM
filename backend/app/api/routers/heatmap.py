from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.services.heatmap_service import (
    get_heatmap_data,
    get_available_heatmap_parameters,
    get_heatmap_bounds
)
from app.services.auth_service import get_current_active_user
from app.models.auth import User

router = APIRouter()

@router.get("/parameters")
async def read_available_parameters(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[str]:
    """
    Get available heatmap parameters.
    
    Returns:
        List of available parameters
    """
    parameters = await get_available_heatmap_parameters(db)
    return parameters

@router.get("/bounds")
async def read_heatmap_bounds(
    parameter: str = Query(..., description="Heatmap parameter"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get bounds for a heatmap.
    
    Args:
        parameter: Heatmap parameter
        date: Date in YYYY-MM-DD format
        
    Returns:
        Bounds for the heatmap
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    bounds = await get_heatmap_bounds(db, parameter=parameter, date=date_obj)
    
    if not bounds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heatmap bounds not found for the specified parameter and date"
        )
    
    return bounds

@router.get("")
async def read_heatmap_data(
    parameter: str = Query(..., description="Heatmap parameter"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get heatmap data.
    
    Args:
        parameter: Heatmap parameter
        date: Date in YYYY-MM-DD format
        
    Returns:
        Heatmap data
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    heatmap_data = await get_heatmap_data(db, parameter=parameter, date=date_obj)
    
    if not heatmap_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heatmap data not found for the specified parameter and date"
        )
    
    return heatmap_data
