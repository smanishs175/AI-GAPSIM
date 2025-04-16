import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.auth import User
from app.main import app

pytestmark = pytest.mark.asyncio

async def test_register_user(db_session: AsyncSession, client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "is_active" in data
    
    # Check that the user was created in the database
    user = await db_session.get(User, data["id"])
    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.is_active is True

async def test_login_user(db_session: AsyncSession, client: AsyncClient):
    """Test user login."""
    # Create a user
    user = User(
        email="login@example.com",
        username="loginuser",
        hashed_password=get_password_hash("password123"),
        full_name="Login User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_login_wrong_password(db_session: AsyncSession, client: AsyncClient):
    """Test login with wrong password."""
    # Create a user
    user = User(
        email="wrong@example.com",
        username="wronguser",
        hashed_password=get_password_hash("password123"),
        full_name="Wrong User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login with wrong password
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect username or password"

async def test_get_current_user(db_session: AsyncSession, client: AsyncClient):
    """Test getting current user."""
    # Create a user
    user = User(
        email="current@example.com",
        username="currentuser",
        hashed_password=get_password_hash("password123"),
        full_name="Current User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login to get token
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": "current@example.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["username"] == "currentuser"
    assert data["full_name"] == "Current User"
