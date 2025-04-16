from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class WeatherData(Base):
    """
    Weather data model for storing historical and forecasted weather data.
    """
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    geometry = Column(String)  # Simplified from Geometry('POINT', srid=4326)

    # Weather parameters
    max_temperature = Column(Float)  # °C
    avg_temperature = Column(Float)  # °C
    min_temperature = Column(Float)  # °C
    relative_humidity = Column(Float)  # %
    specific_humidity = Column(Float)  # g/kg
    longwave_radiation = Column(Float)  # W/m²
    shortwave_radiation = Column(Float)  # W/m²
    precipitation = Column(Float)  # mm
    wind_speed = Column(Float)  # m/s

    # Metadata
    source = Column(String)  # e.g., "NSDF", "NOAA"
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class HeatmapData(Base):
    """
    Heatmap data model for storing pre-generated heatmap data.
    """
    __tablename__ = "heatmap_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    parameter = Column(String, index=True)  # e.g., "temperature", "humidity"
    data_json = Column(JSON)  # Contains the heatmap data as a grid
    bounds_json = Column(JSON)  # Contains the bounds of the heatmap
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EnergyEmergencyAlert(Base):
    """
    Energy Emergency Alert (EEA) model for storing alert data.
    """
    __tablename__ = "energy_emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    ba_id = Column(Integer, ForeignKey("balancing_authorities.id"))
    date = Column(DateTime, index=True)
    level = Column(Integer)  # 1, 2, or 3
    description = Column(String)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
