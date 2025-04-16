import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models.auth import User
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_user():
    """
    Create a test user directly in the database.
    """
    async with async_session() as db:
        # Check if test user already exists
        from sqlalchemy.future import select
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        test_user = result.scalars().first()
        
        if not test_user:
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password="dev_hash_password123",  # This matches our simplified hash function
                full_name="Test User",
                is_active=True,
                is_superuser=False
            )
            db.add(test_user)
            await db.commit()
            logger.info("Test user created.")
        else:
            logger.info("Test user already exists.")

if __name__ == "__main__":
    asyncio.run(create_test_user())
