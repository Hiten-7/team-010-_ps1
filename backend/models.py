from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class DisasterType(str, enum.Enum):
    """Disaster type enumeration"""
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    CYCLONE = "cyclone"
    DROUGHT = "drought"
    LANDSLIDE = "landslide"
    FIRE = "fire"
    TSUNAMI = "tsunami"
    OTHER = "other"


class SeverityLevel(str, enum.Enum):
    """Severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"


class District(Base):
    """District model for Indian districts"""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    population = Column(Integer)
    area_sq_km = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    disasters = relationship("Disaster", back_populates="district", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="district", cascade="all, delete-orphan")


class Disaster(Base):
    """Disaster event model"""
    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    disaster_type = Column(Enum(DisasterType), nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    affected_population = Column(Integer, default=0)
    casualties = Column(Integer, default=0)
    damage_estimate = Column(Float, default=0.0)
    location_details = Column(Text)
    occurred_at = Column(DateTime, nullable=False, index=True)
    reported_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    district = relationship("District", back_populates="disasters")


class Alert(Base):
    """Alert/Warning model for predictive intelligence"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    disaster_type = Column(Enum(DisasterType), nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    predicted_impact = Column(Text)
    recommended_actions = Column(Text)
    confidence_score = Column(Float, default=0.0)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    district = relationship("District", back_populates="alerts")
