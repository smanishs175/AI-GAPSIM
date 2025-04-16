from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import sqlite3
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('wecc_grid.db')
    conn.row_factory = sqlite3.Row
    return conn

# Models
class User(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

# Authentication routes
@app.post("/api/auth/login", response_model=Token)
async def login(username: str = "test@example.com", password: str = "password123"):
    return {
        "access_token": "dummy_token",
        "token_type": "bearer"
    }

@app.get("/api/auth/me", response_model=User)
async def get_current_user():
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }

# Grid data routes
@app.get("/api/public/buses")
async def get_buses():
    conn = get_db_connection()
    buses = conn.execute('SELECT * FROM buses').fetchall()
    conn.close()
    
    result = []
    for bus in buses:
        bus_dict = dict(bus)
        # Convert geometry string to GeoJSON
        geometry_str = bus_dict.get('geometry', 'POINT(0 0)')
        coords = geometry_str.replace('POINT(', '').replace(')', '').split()
        bus_dict['geometry'] = {
            "type": "Point",
            "coordinates": [float(coords[0]), float(coords[1])]
        }
        # Convert metadata_json string to dict
        if 'metadata_json' in bus_dict:
            try:
                bus_dict['metadata'] = json.loads(bus_dict['metadata_json'])
                del bus_dict['metadata_json']
            except:
                bus_dict['metadata'] = {}
        
        result.append(bus_dict)
    
    return result

@app.get("/api/public/branches")
async def get_branches():
    conn = get_db_connection()
    branches = conn.execute('SELECT * FROM branches').fetchall()
    conn.close()
    
    result = []
    for branch in branches:
        branch_dict = dict(branch)
        # Convert geometry string to GeoJSON
        geometry_str = branch_dict.get('geometry', 'LINESTRING(0 0, 1 1)')
        points_str = geometry_str.replace('LINESTRING(', '').replace(')', '').split(', ')
        coordinates = []
        for point_str in points_str:
            coords = point_str.split()
            coordinates.append([float(coords[0]), float(coords[1])])
        
        branch_dict['geometry'] = {
            "type": "LineString",
            "coordinates": coordinates
        }
        
        # Convert metadata_json string to dict
        if 'metadata_json' in branch_dict:
            try:
                branch_dict['metadata'] = json.loads(branch_dict['metadata_json'])
                del branch_dict['metadata_json']
            except:
                branch_dict['metadata'] = {}
        
        result.append(branch_dict)
    
    return result

@app.get("/api/public/generators")
async def get_generators():
    conn = get_db_connection()
    generators = conn.execute('SELECT * FROM generators').fetchall()
    conn.close()
    
    result = []
    for generator in generators:
        generator_dict = dict(generator)
        # Convert geometry string to GeoJSON
        geometry_str = generator_dict.get('geometry', 'POINT(0 0)')
        coords = geometry_str.replace('POINT(', '').replace(')', '').split()
        generator_dict['geometry'] = {
            "type": "Point",
            "coordinates": [float(coords[0]), float(coords[1])]
        }
        
        # Convert metadata_json string to dict
        if 'metadata_json' in generator_dict:
            try:
                generator_dict['metadata'] = json.loads(generator_dict['metadata_json'])
                del generator_dict['metadata_json']
            except:
                generator_dict['metadata'] = {}
        
        result.append(generator_dict)
    
    return result

@app.get("/api/public/loads")
async def get_loads():
    conn = get_db_connection()
    loads = conn.execute('SELECT * FROM loads').fetchall()
    conn.close()
    
    result = []
    for load in loads:
        load_dict = dict(load)
        # Convert geometry string to GeoJSON
        geometry_str = load_dict.get('geometry', 'POINT(0 0)')
        coords = geometry_str.replace('POINT(', '').replace(')', '').split()
        load_dict['geometry'] = {
            "type": "Point",
            "coordinates": [float(coords[0]), float(coords[1])]
        }
        
        # Convert metadata_json string to dict
        if 'metadata_json' in load_dict:
            try:
                load_dict['metadata'] = json.loads(load_dict['metadata_json'])
                del load_dict['metadata_json']
            except:
                load_dict['metadata'] = {}
        
        result.append(load_dict)
    
    return result

@app.get("/api/public/substations")
async def get_substations():
    conn = get_db_connection()
    substations = conn.execute('SELECT * FROM substations').fetchall()
    conn.close()
    
    result = []
    for substation in substations:
        substation_dict = dict(substation)
        # Convert geometry string to GeoJSON
        geometry_str = substation_dict.get('geometry', 'POINT(0 0)')
        coords = geometry_str.replace('POINT(', '').replace(')', '').split()
        substation_dict['geometry'] = {
            "type": "Point",
            "coordinates": [float(coords[0]), float(coords[1])]
        }
        
        # Convert metadata_json string to dict
        if 'metadata_json' in substation_dict:
            try:
                substation_dict['metadata'] = json.loads(substation_dict['metadata_json'])
                del substation_dict['metadata_json']
            except:
                substation_dict['metadata'] = {}
        
        result.append(substation_dict)
    
    return result

@app.get("/api/public/bas")
async def get_bas():
    conn = get_db_connection()
    bas = conn.execute('SELECT * FROM balancing_authorities').fetchall()
    conn.close()
    
    result = []
    for ba in bas:
        ba_dict = dict(ba)
        # Convert geometry string to GeoJSON if it exists
        if 'geometry' in ba_dict and ba_dict['geometry']:
            geometry_str = ba_dict['geometry']
            if geometry_str.startswith('POLYGON'):
                # Simple polygon parsing
                points_str = geometry_str.replace('POLYGON((', '').replace('))', '').split(', ')
                coordinates = []
                for point_str in points_str:
                    coords = point_str.split()
                    coordinates.append([float(coords[0]), float(coords[1])])
                
                ba_dict['geometry'] = {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                }
            else:
                # Default empty polygon
                ba_dict['geometry'] = {
                    "type": "Polygon",
                    "coordinates": [[[-120, 40], [-119, 40], [-119, 41], [-120, 41], [-120, 40]]]
                }
        else:
            # Default empty polygon
            ba_dict['geometry'] = {
                "type": "Polygon",
                "coordinates": [[[-120, 40], [-119, 40], [-119, 41], [-120, 41], [-120, 40]]]
            }
        
        # Convert metadata_json string to dict
        if 'metadata_json' in ba_dict:
            try:
                ba_dict['metadata'] = json.loads(ba_dict['metadata_json'])
                del ba_dict['metadata_json']
            except:
                ba_dict['metadata'] = {}
        
        result.append(ba_dict)
    
    return result

@app.get("/api/public/heatmap")
async def get_heatmap(parameter: str, date: str):
    # Generate dummy heatmap data
    min_lat, max_lat = 30, 50
    min_lon, max_lon = -125, -100
    
    # Create a grid of points
    lat_step, lon_step = 2.0, 2.0
    
    data = []
    for lat in range(int(min_lat), int(max_lat) + 1, int(lat_step)):
        for lon in range(int(min_lon), int(max_lon) + 1, int(lon_step)):
            # Generate a value based on parameter
            if parameter == "temperature":
                value = 70 - (lat - min_lat) / (max_lat - min_lat) * 40
            elif parameter == "humidity":
                value = 30 + (lat - min_lat) / (max_lat - min_lat) * 40
            elif parameter == "wind_speed":
                value = 5 + (lon - min_lon) / (max_lon - min_lon) * 15
            else:
                value = 50
            
            data.append([float(lat), float(lon), float(value)])
    
    return {
        "parameter": parameter,
        "date": date,
        "data": data,
        "bounds": {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
            "min_value": 0,
            "max_value": 100
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
