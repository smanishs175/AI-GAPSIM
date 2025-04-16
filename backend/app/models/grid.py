from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Bus(Base):
    """
    Bus model representing electrical nodes in the power grid.
    """
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bus_type = Column(Integer)  # 1=PQ, 2=PV, 3=Slack
    base_kv = Column(Float)
    geometry = Column(String)  # Simplified from Geometry('POINT', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Branch(Base):
    """
    Branch model representing transmission lines in the power grid.
    """
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    from_bus_id = Column(Integer, ForeignKey("buses.id"))
    to_bus_id = Column(Integer, ForeignKey("buses.id"))
    rate1 = Column(Float)  # MVA rating
    rate2 = Column(Float)  # MVA rating
    rate3 = Column(Float)  # MVA rating
    status = Column(Boolean, default=True)  # 1=in-service, 0=out-of-service
    geometry = Column(String)  # Simplified from Geometry('LINESTRING', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Generator(Base):
    """
    Generator model representing power producers in the grid.
    """
    __tablename__ = "generators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    p_gen = Column(Float)  # MW
    q_gen = Column(Float)  # MVAr
    p_max = Column(Float)  # MW
    p_min = Column(Float)  # MW
    q_max = Column(Float)  # MVAr
    q_min = Column(Float)  # MVAr
    gen_type = Column(String)  # e.g., "WT-Onshore", "SolarPV", "Thermal"
    geometry = Column(String)  # Simplified from Geometry('POINT', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Load(Base):
    """
    Load model representing power consumers in the grid.
    """
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    p_load = Column(Float)  # MW
    q_load = Column(Float)  # MVAr
    geometry = Column(String)  # Simplified from Geometry('POINT', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Substation(Base):
    """
    Substation model representing physical infrastructure in the grid.
    """
    __tablename__ = "substations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    voltage = Column(Float)  # kV
    geometry = Column(String)  # Simplified from Geometry('POINT', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BalancingAuthority(Base):
    """
    Balancing Authority model representing control areas in the grid.
    """
    __tablename__ = "balancing_authorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    abbreviation = Column(String, index=True)
    geometry = Column(String)  # Simplified from Geometry('POLYGON', srid=4326)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
