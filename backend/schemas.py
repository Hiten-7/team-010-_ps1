from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from backend.models import DisasterType, SeverityLevel, AlertStatus


# District Schemas
class DistrictBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    population: Optional[int] = None
    area_sq_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DistrictCreate(DistrictBase):
    pass


class DistrictUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    population: Optional[int] = None
    area_sq_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DistrictResponse(DistrictBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Disaster Schemas
class DisasterBase(BaseModel):
    district_id: int
    disaster_type: DisasterType
    severity: SeverityLevel
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    affected_population: Optional[int] = 0
    casualties: Optional[int] = 0
    damage_estimate: Optional[float] = 0.0
    location_details: Optional[str] = None
    occurred_at: datetime


class DisasterCreate(DisasterBase):
    pass


class DisasterUpdate(BaseModel):
    disaster_type: Optional[DisasterType] = None
    severity: Optional[SeverityLevel] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    affected_population: Optional[int] = None
    casualties: Optional[int] = None
    damage_estimate: Optional[float] = None
    location_details: Optional[str] = None
    occurred_at: Optional[datetime] = None


class DisasterResponse(DisasterBase):
    id: int
    reported_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Alert Schemas
class AlertBase(BaseModel):
    district_id: int
    disaster_type: DisasterType
    severity: SeverityLevel
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    predicted_impact: Optional[str] = None
    recommended_actions: Optional[str] = None
    confidence_score: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    valid_from: datetime
    valid_until: datetime


class AlertCreate(AlertBase):
    status: Optional[AlertStatus] = AlertStatus.ACTIVE


class AlertUpdate(BaseModel):
    disaster_type: Optional[DisasterType] = None
    severity: Optional[SeverityLevel] = None
    status: Optional[AlertStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1)
    predicted_impact: Optional[str] = None
    recommended_actions: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AlertResponse(AlertBase):
    id: int
    status: AlertStatus
    issued_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
