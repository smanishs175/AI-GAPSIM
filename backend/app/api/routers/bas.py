from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date

from app.core.database import get_db
from app.services.ba_service import (
    get_all_bas,
    get_ba_by_id,
    get_ba_events,
    get_ba_demand,
    get_ba_generation
)
from app.services.auth_service import get_current_active_user
from app.models.auth import User

router = APIRouter()

@router.get("")
async def read_all_bas(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all Balancing Authorities.

    Returns:
        List of Balancing Authority data
    """
    bas = await get_all_bas(db)
    return bas

@router.get("/{ba_id}")
async def read_ba(
    ba_id: int = Path(..., title="The ID of the Balancing Authority to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific Balancing Authority by ID.

    Args:
        ba_id: ID of the Balancing Authority

    Returns:
        Balancing Authority data
    """
    ba = await get_ba_by_id(db, ba_id=ba_id)
    if ba is None:
        raise HTTPException(status_code=404, detail="Balancing Authority not found")
    return ba

@router.get("/{ba_id}/events")
async def read_ba_events(
    ba_id: int = Path(..., title="The ID of the Balancing Authority"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get Energy Emergency Alert events for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of EEA events
    """
    # Convert date strings to date objects if provided
    start_date_obj = None
    end_date_obj = None

    if start_date:
        try:
            start_date_obj = date.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )

    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    events = await get_ba_events(db, ba_id=ba_id, start_date=start_date_obj, end_date=end_date_obj)
    return events

@router.get("/{ba_id}/demand")
async def read_ba_demand(
    ba_id: int = Path(..., title="The ID of the Balancing Authority"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get demand data for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Demand data for the Balancing Authority
    """
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    demand_data = await get_ba_demand(db, ba_id=ba_id, start_date=start_date_obj, end_date=end_date_obj)

    if not demand_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand data not found for the specified Balancing Authority and date range"
        )

    return demand_data

@router.get("/{ba_id}/generation")
async def read_ba_generation(
    ba_id: int = Path(..., title="The ID of the Balancing Authority"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get generation data for a Balancing Authority.

    Args:
        ba_id: ID of the Balancing Authority
        start_date: Start date
        end_date: End date

    Returns:
        Generation data for the Balancing Authority
    """
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    generation_data = await get_ba_generation(db, ba_id=ba_id, start_date=start_date_obj, end_date=end_date_obj)

    if not generation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation data not found for the specified Balancing Authority and date range"
        )

    return generation_data
