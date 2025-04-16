import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.core.database import Base, engine, get_db
from app.core.security import get_password_hash
from app.models.auth import User
from app.models.grid import Bus, Branch, Generator, Load, Substation, BalancingAuthority
from app.utils.data_importer import import_grid_data, import_ba_data, import_eea_data
from app.utils.generate_weather_data import generate_synthetic_weather_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables() -> None:
    """Create database tables."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")

async def create_initial_admin() -> None:
    """Create initial admin user if it doesn't exist."""
    async for db in get_db():
        try:
            # Check if admin user already exists
            result = await db.execute(select(User).where(User.email == "admin@example.com"))
            admin_user = result.scalars().first()

            if admin_user:
                logger.info("Admin user already exists.")
            else:
                # Create admin user
                admin = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    full_name="System Administrator",
                    is_active=True,
                    is_superuser=True
                )
                db.add(admin)
                logger.info("Admin user created successfully.")

            # Check if demo user already exists
            result = await db.execute(select(User).where(User.email == "demo@example.com"))
            demo_user = result.scalars().first()

            if demo_user:
                logger.info("Demo user already exists.")
            else:
                # Create demo user
                demo = User(
                    email="demo@example.com",
                    username="demo",
                    hashed_password=get_password_hash("demo123"),
                    full_name="Demo User",
                    is_active=True,
                    is_superuser=False
                )
                db.add(demo)
                logger.info("Demo user created successfully.")
            
            await db.commit()

        except IntegrityError:
            await db.rollback()
            logger.warning("User creation failed due to integrity error.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating users: {e}")

async def import_all_data(db: AsyncSession) -> None:
    """Import all data from Excel files."""
    logger.info("Importing grid data...")
    await import_grid_data(db)

    logger.info("Importing balancing authority data...")
    await import_ba_data(db)

    logger.info("Importing EEA data...")
    await import_eea_data(db)

    # Generate synthetic weather data for a 10-day period
    logger.info("Generating synthetic weather data...")
    start_date = datetime(2020, 7, 21)
    end_date = datetime(2020, 7, 30)
    await generate_synthetic_weather_data(db, start_date, end_date)

    logger.info("All data imported successfully.")

async def init_db() -> None:
    """Initialize database with tables and initial data."""
    await create_tables()
    await create_initial_admin()

    # Import data
    async for db in get_db():
        await import_all_data(db)

if __name__ == "__main__":
    asyncio.run(init_db())
