from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date

from app.core.database import get_db
from app.services.grid_service import (
    get_all_buses,
    get_bus_by_id,
    get_all_branches,
    get_branch_by_id,
    get_all_generators,
    get_generator_by_id,
    get_all_loads,
    get_load_by_id,
    get_all_substations,
    get_substation_by_id
)
from app.services.auth_service import get_current_active_user
from app.models.auth import User

router = APIRouter()

@router.get("/buses")
async def read_all_buses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all buses with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of bus data
    """
    buses = await get_all_buses(db, skip=skip, limit=limit)
    return buses

@router.get("/buses/{bus_id}")
async def read_bus(
    bus_id: int = Path(..., title="The ID of the bus to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific bus by ID.

    Args:
        bus_id: ID of the bus

    Returns:
        Bus data
    """
    bus = await get_bus_by_id(db, bus_id=bus_id)
    if bus is None:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

@router.get("/branches")
async def read_all_branches(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all branches (transmission lines) with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of branch data
    """
    branches = await get_all_branches(db, skip=skip, limit=limit)
    return branches

@router.get("/branches/{branch_id}")
async def read_branch(
    branch_id: int = Path(..., title="The ID of the branch to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific branch by ID.

    Args:
        branch_id: ID of the branch

    Returns:
        Branch data
    """
    branch = await get_branch_by_id(db, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.get("/generators")
async def read_all_generators(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all generators with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of generator data
    """
    generators = await get_all_generators(db, skip=skip, limit=limit)
    return generators

@router.get("/generators/{generator_id}")
async def read_generator(
    generator_id: int = Path(..., title="The ID of the generator to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific generator by ID.

    Args:
        generator_id: ID of the generator

    Returns:
        Generator data
    """
    generator = await get_generator_by_id(db, generator_id=generator_id)
    if generator is None:
        raise HTTPException(status_code=404, detail="Generator not found")
    return generator

@router.get("/loads")
async def read_all_loads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all loads with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of load data
    """
    loads = await get_all_loads(db, skip=skip, limit=limit)
    return loads

@router.get("/loads/{load_id}")
async def read_load(
    load_id: int = Path(..., title="The ID of the load to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific load by ID.

    Args:
        load_id: ID of the load

    Returns:
        Load data
    """
    load = await get_load_by_id(db, load_id=load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")
    return load

@router.get("/substations")
async def read_all_substations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all substations with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of substation data
    """
    substations = await get_all_substations(db, skip=skip, limit=limit)
    return substations

@router.get("/substations/{substation_id}")
async def read_substation(
    substation_id: int = Path(..., title="The ID of the substation to get"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific substation by ID.

    Args:
        substation_id: ID of the substation

    Returns:
        Substation data
    """
    substation = await get_substation_by_id(db, substation_id=substation_id)
    if substation is None:
        raise HTTPException(status_code=404, detail="Substation not found")
    return substation
