import os
import logging
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings
from app.models.grid import Bus, Branch, Generator, Load, Substation, BalancingAuthority
from app.models.weather import EnergyEmergencyAlert
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to safely load WKT strings
def safe_loads(wkt_str):
    if not wkt_str or not isinstance(wkt_str, str):
        return None
    try:
        return loads(wkt_str)
    except Exception as e:
        logger.error(f"Error loading geometry: {e}")
        return None

# Helper function to read Excel files
def read_excel_file(file_path: str) -> Optional[pd.DataFrame]:
    """Read Excel file and return DataFrame."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

async def import_grid_data(db: AsyncSession) -> None:
    """Import grid data from Excel files."""
    data_dir = settings.DATA_DIR
    
    # Import buses
    logger.info("Importing buses...")
    bus_file = os.path.join(data_dir, "WECC data", "merged_bus_data.xlsx")
    if os.path.exists(bus_file):
        df = read_excel_file(bus_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    geometry = safe_loads(row.get('geometry'))
                    if geometry:
                        bus = Bus(
                            name=row.get('NAME', f"Bus {row.get('NUMBER', 'Unknown')}"),
                            bus_type=row.get('TYPE', 1),
                            base_kv=row.get('BASE KV', 0.0),
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'number': row.get('NUMBER'),
                                'area': row.get('AREA'),
                                'zone': row.get('ZONE'),
                                'owner': row.get('OWNER')
                            }
                        )
                        db.add(bus)
                except Exception as e:
                    logger.error(f"Error importing bus: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} buses.")
    
    # Import branches (transmission lines)
    logger.info("Importing branches...")
    branch_file = os.path.join(data_dir, "WECC data", "merged_branch_data.xlsx")
    if os.path.exists(branch_file):
        df = read_excel_file(branch_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    geometry = safe_loads(row.get('geometry'))
                    if geometry:
                        branch = Branch(
                            name=row.get('NAME', f"Branch {row.get('I BUS', 'Unknown')}-{row.get('J BUS', 'Unknown')}"),
                            from_bus_id=row.get('I BUS'),
                            to_bus_id=row.get('J BUS'),
                            rate1=row.get('RATE1', 0.0),
                            rate2=row.get('RATE2', 0.0),
                            rate3=row.get('RATE3', 0.0),
                            status=row.get('Line Status', 1) == 1,
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'circuit': row.get('CIRCUIT'),
                                'length': row.get('LENGTH'),
                                'r': row.get('R'),
                                'x': row.get('X'),
                                'b': row.get('B')
                            }
                        )
                        db.add(branch)
                except Exception as e:
                    logger.error(f"Error importing branch: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} branches.")
    
    # Import generators
    logger.info("Importing generators...")
    gen_file = os.path.join(data_dir, "WECC data", "merged_gen_data.xlsx")
    if os.path.exists(gen_file):
        df = read_excel_file(gen_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    geometry = safe_loads(row.get('geometry'))
                    if geometry:
                        generator = Generator(
                            name=row.get('NAME', f"Generator {row.get('NUMBER', 'Unknown')}"),
                            bus_id=row.get('BUS'),
                            p_gen=row.get('PGEN', 0.0),
                            q_gen=row.get('QGEN', 0.0),
                            p_max=row.get('PMAX', 0.0),
                            p_min=row.get('PMIN', 0.0),
                            q_max=row.get('QMAX', 0.0),
                            q_min=row.get('QMIN', 0.0),
                            gen_type=row.get('TYPE', 'Unknown'),
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'number': row.get('NUMBER'),
                                'status': row.get('STATUS'),
                                'mbase': row.get('MBASE'),
                                'zr': row.get('ZR'),
                                'zx': row.get('ZX')
                            }
                        )
                        db.add(generator)
                except Exception as e:
                    logger.error(f"Error importing generator: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} generators.")
    
    # Import loads
    logger.info("Importing loads...")
    load_file = os.path.join(data_dir, "WECC data", "merged_load_data.xlsx")
    if os.path.exists(load_file):
        df = read_excel_file(load_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    geometry = safe_loads(row.get('geometry'))
                    if geometry:
                        load = Load(
                            name=row.get('NAME', f"Load {row.get('NUMBER', 'Unknown')}"),
                            bus_id=row.get('BUS'),
                            p_load=row.get('PL', 0.0),
                            q_load=row.get('QL', 0.0),
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'number': row.get('NUMBER'),
                                'status': row.get('STATUS'),
                                'area': row.get('AREA'),
                                'zone': row.get('ZONE')
                            }
                        )
                        db.add(load)
                except Exception as e:
                    logger.error(f"Error importing load: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} loads.")
    
    # Import substations
    logger.info("Importing substations...")
    substation_file = os.path.join(data_dir, "WECC data", "merged_substation_data.xlsx")
    if os.path.exists(substation_file):
        df = read_excel_file(substation_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    geometry = safe_loads(row.get('geometry'))
                    if geometry:
                        substation = Substation(
                            name=row.get('NAME', f"Substation {row.get('NUMBER', 'Unknown')}"),
                            voltage=row.get('VOLTAGE', 0.0),
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'number': row.get('NUMBER'),
                                'area': row.get('AREA'),
                                'zone': row.get('ZONE'),
                                'owner': row.get('OWNER')
                            }
                        )
                        db.add(substation)
                except Exception as e:
                    logger.error(f"Error importing substation: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} substations.")

async def import_ba_data(db: AsyncSession) -> None:
    """Import Balancing Authority data."""
    data_dir = settings.DATA_DIR
    ba_file = os.path.join(data_dir, "BA_GPS_Data.xlsx")
    
    if os.path.exists(ba_file):
        logger.info(f"Importing BA data from {ba_file}...")
        df = read_excel_file(ba_file)
        if df is not None:
            for _, row in df.iterrows():
                try:
                    # Check if geometry column exists, otherwise create from coordinates
                    if 'geometry' in row and row['geometry']:
                        geometry = safe_loads(row['geometry'])
                    elif all(x in row for x in ['LATITUDE', 'LONGITUDE']):
                        # Create a simple polygon around the point
                        lat, lon = row['LATITUDE'], row['LONGITUDE']
                        size = 0.5  # Approximately 50km
                        wkt = f"POLYGON(({lon-size} {lat-size}, {lon+size} {lat-size}, {lon+size} {lat+size}, {lon-size} {lat+size}, {lon-size} {lat-size}))"
                        geometry = loads(wkt)
                    else:
                        logger.warning(f"No geometry or coordinates found for BA {row.get('NAME', 'Unknown')}")
                        continue
                    
                    if geometry:
                        ba = BalancingAuthority(
                            name=row.get('NAME', 'Unknown BA'),
                            abbreviation=row.get('ABBREVIATION', row.get('NAME', 'Unknown')[:4]),
                            geometry=f"SRID=4326;{geometry.wkt}",
                            metadata_json={
                                'country': row.get('COUNTRY', 'USA'),
                                'region': row.get('REGION', 'WECC')
                            }
                        )
                        db.add(ba)
                except Exception as e:
                    logger.error(f"Error importing BA: {e}")
            
            await db.commit()
            logger.info(f"Imported {len(df)} Balancing Authorities.")

async def import_eea_data(db: AsyncSession) -> None:
    """Import Energy Emergency Alert data."""
    data_dir = settings.DATA_DIR
    
    # List of EEA files
    eea_files = [
        os.path.join(data_dir, "EEA-AESO.xlsx"),
        os.path.join(data_dir, "EEA-CIPV.xlsx")
    ]
    
    for eea_file in eea_files:
        if os.path.exists(eea_file):
            logger.info(f"Importing EEA data from {eea_file}...")
            df = read_excel_file(eea_file)
            if df is not None:
                ba_name = os.path.basename(eea_file).split('-')[1].split('.')[0]
                
                # Get BA ID
                result = await db.execute(select(BalancingAuthority).where(
                    func.lower(BalancingAuthority.abbreviation) == func.lower(ba_name)
                ))
                ba = result.scalars().first()
                
                if not ba:
                    logger.warning(f"BA with abbreviation {ba_name} not found. Skipping EEA import.")
                    continue
                
                for _, row in df.iterrows():
                    try:
                        # Parse date
                        if 'DATE' in row:
                            date_str = row['DATE']
                            if isinstance(date_str, str):
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            elif isinstance(date_str, datetime):
                                date_obj = date_str
                            else:
                                logger.warning(f"Invalid date format: {date_str}")
                                continue
                        else:
                            logger.warning("No DATE column found in EEA file.")
                            continue
                        
                        eea = EnergyEmergencyAlert(
                            ba_id=ba.id,
                            date=date_obj,
                            level=row.get('LEVEL', 1),
                            description=row.get('DESCRIPTION', ''),
                            metadata_json={
                                'duration_hours': row.get('DURATION_HOURS', 0),
                                'affected_mw': row.get('AFFECTED_MW', 0)
                            }
                        )
                        db.add(eea)
                    except Exception as e:
                        logger.error(f"Error importing EEA: {e}")
                
                await db.commit()
                logger.info(f"Imported {len(df)} EEA events for {ba_name}.")

if __name__ == "__main__":
    # This can be used for testing the import functions directly
    import asyncio
    from app.core.database import get_db
    
    async def test_import():
        async for db in get_db():
            await import_grid_data(db)
            await import_ba_data(db)
            await import_eea_data(db)
    
    asyncio.run(test_import())
