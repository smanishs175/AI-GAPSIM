import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.auth import User
from app.models.grid import Bus, Branch, Generator, Load, Substation
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

async def setup_test_data(db_session: AsyncSession):
    """Helper function to set up test grid data."""
    # Create test bus
    bus = Bus(
        name="Test Bus",
        bus_type=1,
        base_kv=138.0,
        geometry="SRID=4326;POINT(-115 40)",
        metadata_json={"number": 1, "area": 1, "zone": 1}
    )
    db_session.add(bus)
    await db_session.flush()
    
    # Create test branch
    branch = Branch(
        name="Test Branch",
        from_bus_id=bus.id,
        to_bus_id=bus.id,
        rate1=100.0,
        rate2=120.0,
        rate3=150.0,
        status=True,
        geometry="SRID=4326;LINESTRING(-115 40, -116 41)",
        metadata_json={"circuit": 1, "length": 100.0}
    )
    db_session.add(branch)
    
    # Create test generator
    generator = Generator(
        name="Test Generator",
        bus_id=bus.id,
        p_gen=100.0,
        q_gen=50.0,
        p_max=150.0,
        p_min=0.0,
        q_max=75.0,
        q_min=-75.0,
        gen_type="SolarPV",
        geometry="SRID=4326;POINT(-115 40)",
        metadata_json={"number": 1, "status": 1}
    )
    db_session.add(generator)
    
    # Create test load
    load = Load(
        name="Test Load",
        bus_id=bus.id,
        p_load=80.0,
        q_load=40.0,
        geometry="SRID=4326;POINT(-115 40)",
        metadata_json={"number": 1, "status": 1}
    )
    db_session.add(load)
    
    # Create test substation
    substation = Substation(
        name="Test Substation",
        voltage=138.0,
        geometry="SRID=4326;POINT(-115 40)",
        metadata_json={"number": 1, "area": 1}
    )
    db_session.add(substation)
    
    await db_session.commit()

@pytest.fixture(autouse=True)
async def setup(db_session: AsyncSession):
    """Set up test data."""
    await setup_test_user(db_session)
    await setup_test_data(db_session)

async def test_get_buses(client: AsyncClient):
    """Test getting all buses."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/grid/buses",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Bus"
    assert data[0]["bus_type"] == 1
    assert data[0]["base_kv"] == 138.0
    assert "geometry" in data[0]
    assert "metadata" in data[0]

async def test_get_bus_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a bus by ID."""
    token = await get_auth_token(client)
    
    # Get the first bus ID
    result = await db_session.execute("SELECT id FROM buses LIMIT 1")
    bus_id = result.scalar_one()
    
    response = await client.get(
        f"/api/grid/buses/{bus_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bus_id
    assert data["name"] == "Test Bus"
    assert data["bus_type"] == 1
    assert data["base_kv"] == 138.0
    assert "geometry" in data
    assert "metadata" in data

async def test_get_branches(client: AsyncClient):
    """Test getting all branches."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/grid/branches",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Branch"
    assert data[0]["rate1"] == 100.0
    assert data[0]["status"] is True
    assert "geometry" in data[0]
    assert "metadata" in data[0]

async def test_get_generators(client: AsyncClient):
    """Test getting all generators."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/grid/generators",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Generator"
    assert data[0]["p_gen"] == 100.0
    assert data[0]["gen_type"] == "SolarPV"
    assert "geometry" in data[0]
    assert "metadata" in data[0]

async def test_get_loads(client: AsyncClient):
    """Test getting all loads."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/grid/loads",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Load"
    assert data[0]["p_load"] == 80.0
    assert data[0]["q_load"] == 40.0
    assert "geometry" in data[0]
    assert "metadata" in data[0]

async def test_get_substations(client: AsyncClient):
    """Test getting all substations."""
    token = await get_auth_token(client)
    
    response = await client.get(
        "/api/grid/substations",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Substation"
    assert data[0]["voltage"] == 138.0
    assert "geometry" in data[0]
    assert "metadata" in data[0]
