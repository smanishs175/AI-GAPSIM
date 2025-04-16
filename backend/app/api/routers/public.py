from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.services.grid_service import (
    get_all_buses,
    get_all_branches,
    get_all_generators,
    get_all_loads,
    get_all_substations
)
from app.services.ba_service import get_all_bas
from app.services.heatmap_service import get_heatmap_data

router = APIRouter()

@router.get("/buses")
async def read_all_buses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all buses with pagination (public endpoint).
    """
    buses = await get_all_buses(db, skip=skip, limit=limit)
    return buses

@router.get("/branches")
async def read_all_branches(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all branches with pagination (public endpoint).
    """
    branches = await get_all_branches(db, skip=skip, limit=limit)
    return branches

@router.get("/generators")
async def read_all_generators(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all generators with pagination (public endpoint).
    """
    generators = await get_all_generators(db, skip=skip, limit=limit)
    return generators

@router.get("/loads")
async def read_all_loads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all loads with pagination (public endpoint).
    """
    loads = await get_all_loads(db, skip=skip, limit=limit)
    return loads

@router.get("/substations")
async def read_all_substations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all substations with pagination (public endpoint).
    """
    substations = await get_all_substations(db, skip=skip, limit=limit)
    return substations

@router.get("/bas")
async def read_all_bas(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all balancing authorities (public endpoint).
    """
    bas = await get_all_bas(db)
    return bas

@router.get("/heatmap")
async def read_heatmap_data(
    parameter: str = Query(..., description="Weather parameter to visualize"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get heatmap data for a specific parameter and date (public endpoint).
    """
    heatmap_data = await get_heatmap_data(db, parameter, date)
    return heatmap_data
