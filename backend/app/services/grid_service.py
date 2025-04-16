from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
import json

from app.models.grid import Bus, Branch, Generator, Load, Substation, BalancingAuthority
from app.core.config import settings

async def get_all_buses(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all buses with pagination.
    """
    query = select(Bus).offset(skip).limit(limit)
    result = await db.execute(query)
    buses = result.scalars().all()

    # Convert to GeoJSON format
    bus_list = []
    for bus in buses:
        bus_dict = {
            "id": bus.id,
            "name": bus.name,
            "bus_type": bus.bus_type,
            "base_kv": bus.base_kv,
            "geometry": {"type": "Point", "coordinates": [float(x) for x in bus.geometry.replace("POINT(", "").replace(")", "").split()]},
            "metadata": bus.metadata_json
        }
        bus_list.append(bus_dict)

    return bus_list

async def get_bus_by_id(db: AsyncSession, bus_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific bus by ID.
    """
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalars().first()

    if bus is None:
        return None

    # Convert to GeoJSON format
    bus_dict = {
        "id": bus.id,
        "name": bus.name,
        "bus_type": bus.bus_type,
        "base_kv": bus.base_kv,
        "geometry": {"type": "Point", "coordinates": [float(x) for x in bus.geometry.replace("POINT(", "").replace(")", "").split()]},
        "metadata": bus.metadata_json
    }

    return bus_dict

async def get_all_branches(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all branches with pagination.
    """
    query = select(Branch).offset(skip).limit(limit)
    result = await db.execute(query)
    branches = result.scalars().all()

    # Convert to GeoJSON format
    branch_list = []
    for branch in branches:
        branch_dict = {
            "id": branch.id,
            "name": branch.name,
            "from_bus_id": branch.from_bus_id,
            "to_bus_id": branch.to_bus_id,
            "rate1": branch.rate1,
            "rate2": branch.rate2,
            "rate3": branch.rate3,
            "status": branch.status,
            "geometry": {"type": "LineString", "coordinates": [[float(x) for x in point.split()] for point in branch.geometry.replace("LINESTRING(", "").replace(")", "").split(", ")]},
            "metadata": branch.metadata_json
        }
        branch_list.append(branch_dict)

    return branch_list

async def get_branch_by_id(db: AsyncSession, branch_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific branch by ID.
    """
    query = select(Branch).where(Branch.id == branch_id)
    result = await db.execute(query)
    branch = result.scalars().first()

    if branch is None:
        return None

    # Convert to GeoJSON format
    branch_dict = {
        "id": branch.id,
        "name": branch.name,
        "from_bus_id": branch.from_bus_id,
        "to_bus_id": branch.to_bus_id,
        "rate1": branch.rate1,
        "rate2": branch.rate2,
        "rate3": branch.rate3,
        "status": branch.status,
        "geometry": {"type": "LineString", "coordinates": [[float(x) for x in point.split()] for point in branch.geometry.replace("LINESTRING(", "").replace(")", "").split(", ")]},
        "metadata": branch.metadata_json
    }

    return branch_dict

async def get_all_generators(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all generators with pagination.
    """
    query = select(Generator).offset(skip).limit(limit)
    result = await db.execute(query)
    generators = result.scalars().all()

    # Convert to GeoJSON format
    generator_list = []
    for generator in generators:
        generator_dict = {
            "id": generator.id,
            "name": generator.name,
            "bus_id": generator.bus_id,
            "p_gen": generator.p_gen,
            "q_gen": generator.q_gen,
            "p_max": generator.p_max,
            "p_min": generator.p_min,
            "q_max": generator.q_max,
            "q_min": generator.q_min,
            "gen_type": generator.gen_type,
            "geometry": {"type": "Point", "coordinates": [float(x) for x in generator.geometry.replace("POINT(", "").replace(")", "").split()]},
            "metadata": generator.metadata_json
        }
        generator_list.append(generator_dict)

    return generator_list

async def get_generator_by_id(db: AsyncSession, generator_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific generator by ID.
    """
    query = select(Generator).where(Generator.id == generator_id)
    result = await db.execute(query)
    generator = result.scalars().first()

    if generator is None:
        return None

    # Convert to GeoJSON format
    generator_dict = {
        "id": generator.id,
        "name": generator.name,
        "bus_id": generator.bus_id,
        "p_gen": generator.p_gen,
        "q_gen": generator.q_gen,
        "p_max": generator.p_max,
        "p_min": generator.p_min,
        "q_max": generator.q_max,
        "q_min": generator.q_min,
        "gen_type": generator.gen_type,
        "geometry": {"type": "Point", "coordinates": [float(x) for x in generator.geometry.replace("POINT(", "").replace(")", "").split()]},
        "metadata": generator.metadata_json
    }

    return generator_dict

async def get_all_loads(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all loads with pagination.
    """
    query = select(Load).offset(skip).limit(limit)
    result = await db.execute(query)
    loads = result.scalars().all()

    # Convert to GeoJSON format
    load_list = []
    for load in loads:
        load_dict = {
            "id": load.id,
            "name": load.name,
            "bus_id": load.bus_id,
            "p_load": load.p_load,
            "q_load": load.q_load,
            "geometry": {"type": "Point", "coordinates": [float(x) for x in load.geometry.replace("POINT(", "").replace(")", "").split()]},
            "metadata": load.metadata_json
        }
        load_list.append(load_dict)

    return load_list

async def get_load_by_id(db: AsyncSession, load_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific load by ID.
    """
    query = select(Load).where(Load.id == load_id)
    result = await db.execute(query)
    load = result.scalars().first()

    if load is None:
        return None

    # Convert to GeoJSON format
    load_dict = {
        "id": load.id,
        "name": load.name,
        "bus_id": load.bus_id,
        "p_load": load.p_load,
        "q_load": load.q_load,
        "geometry": {"type": "Point", "coordinates": [float(x) for x in load.geometry.replace("POINT(", "").replace(")", "").split()]},
        "metadata": load.metadata_json
    }

    return load_dict

async def get_all_substations(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all substations with pagination.
    """
    query = select(Substation).offset(skip).limit(limit)
    result = await db.execute(query)
    substations = result.scalars().all()

    # Convert to GeoJSON format
    substation_list = []
    for substation in substations:
        substation_dict = {
            "id": substation.id,
            "name": substation.name,
            "voltage": substation.voltage,
            "geometry": {"type": "Point", "coordinates": [float(x) for x in substation.geometry.replace("POINT(", "").replace(")", "").split()]},
            "metadata": substation.metadata_json
        }
        substation_list.append(substation_dict)

    return substation_list

async def get_substation_by_id(db: AsyncSession, substation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific substation by ID.
    """
    query = select(Substation).where(Substation.id == substation_id)
    result = await db.execute(query)
    substation = result.scalars().first()

    if substation is None:
        return None

    # Convert to GeoJSON format
    substation_dict = {
        "id": substation.id,
        "name": substation.name,
        "voltage": substation.voltage,
        "geometry": {"type": "Point", "coordinates": [float(x) for x in substation.geometry.replace("POINT(", "").replace(")", "").split()]},
        "metadata": substation.metadata_json
    }

    return substation_dict

# Function to load data from Excel files
def load_grid_data_from_excel():
    """
    Load grid data from Excel files.
    This function would be used for initial data loading or updates.
    """
    # Example implementation (would need to be adapted to actual file structure)
    try:
        # Load buses
        bus_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_bus_data.xlsx")
        bus_gdf = gpd.GeoDataFrame(bus_df, geometry=bus_df['geometry'].apply(loads))
        bus_gdf.crs = 'epsg:4326'

        # Load branches
        branch_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_branch_data.xlsx")
        branch_gdf = gpd.GeoDataFrame(branch_df, geometry=branch_df['geometry'].apply(loads))
        branch_gdf.crs = 'epsg:4326'

        # Load generators
        gen_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_gen_data.xlsx")
        gen_gdf = gpd.GeoDataFrame(gen_df, geometry=gen_df['geometry'].apply(loads))
        gen_gdf.crs = 'epsg:4326'

        # Load loads
        load_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_load_data.xlsx")
        load_gdf = gpd.GeoDataFrame(load_df, geometry=load_df['geometry'].apply(loads))
        load_gdf.crs = 'epsg:4326'

        # Load substations
        substation_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_substation_data.xlsx")
        substation_gdf = gpd.GeoDataFrame(substation_df, geometry=substation_df['geometry'].apply(loads))
        substation_gdf.crs = 'epsg:4326'

        # Load balancing authorities
        try:
            ba_df = pd.read_excel(f"{settings.DATA_DIR}/WECC data/merged_ba_data.xlsx")
        except Exception as ba_error:
            print(f"Warning: Could not load balancing authorities: {ba_error}")
            ba_df = pd.DataFrame(columns=['id', 'name', 'short_name', 'metadata_json'])

        return {
            'buses': bus_gdf,
            'branches': branch_gdf,
            'generators': gen_gdf,
            'loads': load_gdf,
            'substations': substation_gdf,
            'balancing_authorities': ba_df
        }
    except Exception as e:
        print(f"Error loading grid data: {e}")
        return None

async def get_all_balancing_authorities(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all balancing authorities with pagination.
    """
    query = select(BalancingAuthority).offset(skip).limit(limit)
    result = await db.execute(query)
    bas = result.scalars().all()

    # Convert to dictionary format
    ba_list = []
    for ba in bas:
        ba_dict = {
            "id": ba.id,
            "name": ba.name,
            "short_name": ba.short_name,
            "metadata": ba.metadata_json
        }
        ba_list.append(ba_dict)

    return ba_list

async def get_balancing_authority_by_id(db: AsyncSession, ba_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific balancing authority by ID.
    """
    query = select(BalancingAuthority).where(BalancingAuthority.id == ba_id)
    result = await db.execute(query)
    ba = result.scalars().first()

    if ba is None:
        return None

    # Convert to dictionary format
    ba_dict = {
        "id": ba.id,
        "name": ba.name,
        "short_name": ba.short_name,
        "metadata": ba.metadata_json
    }

    return ba_dict
