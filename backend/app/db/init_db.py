import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import Base, engine, async_session
from app.core.security import get_password_hash
from app.models.auth import User
from app.models.grid import Bus, Branch, Generator, Load, Substation, BalancingAuthority
from app.models.weather import WeatherData, HeatmapData, EnergyEmergencyAlert
from app.services.grid_service import load_grid_data_from_excel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """
    Initialize the database with tables and initial data.
    """
    # Create tables
    async with engine.begin() as conn:
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    # Create initial admin user
    async with async_session() as db:
        logger.info("Creating admin user...")
        await create_admin_user(db)
    
    # Load grid data from Excel files
    logger.info("Loading grid data from Excel files...")
    grid_data = load_grid_data_from_excel()
    
    if grid_data:
        async with async_session() as db:
            logger.info("Inserting grid data into database...")
            await insert_grid_data(db, grid_data)
    
    logger.info("Database initialization complete.")

async def create_admin_user(db: AsyncSession):
    """
    Create an admin user if it doesn't exist.
    """
    # Check if admin user already exists
    result = await db.execute(select(User).where(User.email == "admin@example.com"))
    admin_user = result.scalars().first()
    
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        await db.commit()
        logger.info("Admin user created.")
    else:
        logger.info("Admin user already exists.")

async def insert_grid_data(db: AsyncSession, grid_data):
    """
    Insert grid data into the database.
    """
    # Insert buses
    for _, row in grid_data['buses'].iterrows():
        bus = Bus(
            id=row['id'],
            name=row['name'],
            bus_type=row['bus_type'],
            base_kv=row['base_kv'],
            geometry=row['geometry'],
            metadata_json=row['metadata'] if 'metadata' in row else {}
        )
        db.add(bus)
    
    # Insert branches
    for _, row in grid_data['branches'].iterrows():
        branch = Branch(
            id=row['id'],
            name=row['name'],
            from_bus_id=row['from_bus_id'],
            to_bus_id=row['to_bus_id'],
            rate1=row['rate1'],
            rate2=row['rate2'] if 'rate2' in row else 0,
            rate3=row['rate3'] if 'rate3' in row else 0,
            status=row['status'] if 'status' in row else True,
            geometry=row['geometry'],
            metadata_json=row['metadata'] if 'metadata' in row else {}
        )
        db.add(branch)
    
    # Insert generators
    for _, row in grid_data['generators'].iterrows():
        generator = Generator(
            id=row['id'],
            name=row['name'],
            bus_id=row['bus_id'],
            p_gen=row['p_gen'],
            q_gen=row['q_gen'],
            p_max=row['p_max'],
            p_min=row['p_min'],
            q_max=row['q_max'] if 'q_max' in row else 0,
            q_min=row['q_min'] if 'q_min' in row else 0,
            gen_type=row['gen_type'],
            geometry=row['geometry'],
            metadata_json=row['metadata'] if 'metadata' in row else {}
        )
        db.add(generator)
    
    # Insert loads
    for _, row in grid_data['loads'].iterrows():
        load = Load(
            id=row['id'],
            name=row['name'],
            bus_id=row['bus_id'],
            p_load=row['p_load'],
            q_load=row['q_load'],
            geometry=row['geometry'],
            metadata_json=row['metadata'] if 'metadata' in row else {}
        )
        db.add(load)
    
    # Insert substations
    for _, row in grid_data['substations'].iterrows():
        substation = Substation(
            id=row['id'],
            name=row['name'],
            voltage=row['voltage'],
            geometry=row['geometry'],
            metadata_json=row['metadata'] if 'metadata' in row else {}
        )
        db.add(substation)
    
    await db.commit()
    logger.info("Grid data inserted.")

if __name__ == "__main__":
    asyncio.run(init_db())
