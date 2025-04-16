import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.security import get_password_hash
from app.models.auth import User
from app.models.weather import WeatherData
from app.main import app

pytestmark = pytest.mark.asyncio

async def get_auth_token(client: AsyncClient) -> str:
    """Helper function to get auth token."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

async def setup_test_user(db_session: AsyncSession):
    """Helper function to set up test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

async def setup_test_weather_data(db_session: AsyncSession):
    """Helper function to set up test weather data."""
    # Create test weather data
    weather_data = WeatherData(
        date=datetime(2020, 7, 21),
        latitude=40.0,
        longitude=-115.0,
        geometry="SRID=4326;POINT(-115 40)",
        max_temperature=30.0,
        avg_temperature=25.0,
        min_temperature=20.0,
        relative_humidity=60.0,
        specific_humidity=10.0,
        longwave_radiation=200.0,
        shortwave_radiation=800.0,
        precipitation=0.0,
        wind_speed=5.0,
        source="test"
    )
    db_session.add(weather_data)
    
    # Create another weather data point for range testing
    weather_data2 = WeatherData(
        date=datetime(2020, 7, 22),
        latitude=40.0,
        longitude=-115.0,
        geometry="SRID=4326;POINT(-115 40)",
        max_temperature=32.0,
        avg_temperature=27.0,
        min_temperature=22.0,
        relative_humidity=55.0,
        specific_humidity=9.0,
        longwave_radiation=210.0,
        shortwave_radiation=820.0,
        precipitation=2.0,
        wind_speed=6.0,
        source="test"
    )
    db_session.add(weather_data2)
    
    await db_session.commit()

@pytest.fixture(autouse=True)
async def setup(db_session: AsyncSession):
    """Set up test data."""
    await setup_test_user(db_session)
    await setup_test_weather_data(db_session)

async def test_get_weather_for_point(client: AsyncClient):
    """Test getting weather data for a point."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/weather/point",
        params={
            "latitude": 40.0,
            "longitude": -115.0,
            "date": "2020-07-21"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2020-07-21T00:00:00"
    assert data["latitude"] == 40.0
    assert data["longitude"] == -115.0
    assert data["max_temperature"] == 30.0
    assert data["avg_temperature"] == 25.0
    assert data["min_temperature"] == 20.0
    assert data["relative_humidity"] == 60.0
    assert data["wind_speed"] == 5.0

async def test_get_weather_for_range(client: AsyncClient):
    """Test getting weather data for a range of dates."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/weather/range",
        params={
            "latitude": 40.0,
            "longitude": -115.0,
            "start_date": "2020-07-21",
            "end_date": "2020-07-22"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["date"] == "2020-07-21T00:00:00"
    assert data[1]["date"] == "2020-07-22T00:00:00"
    assert data[0]["max_temperature"] == 30.0
    assert data[1]["max_temperature"] == 32.0

async def test_get_weather_for_component(client: AsyncClient, db_session: AsyncSession):
    """Test getting weather data for a component."""
    token = await get_auth_token(client)
    
    # Get the first bus ID
    result = await db_session.execute("SELECT id FROM buses LIMIT 1")
    bus_id = result.scalar_one()
    
    response = await client.get(
        f"/api/weather/component/bus/{bus_id}",
        params={
            "start_date": "2020-07-21",
            "end_date": "2020-07-22"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "component" in data
    assert "weather_data" in data
    assert "impacts" in data
    assert len(data["weather_data"]) > 0
    assert "daily_impacts" in data["impacts"]
    assert "summary" in data["impacts"]
