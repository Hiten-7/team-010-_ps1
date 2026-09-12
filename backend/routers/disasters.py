from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import Disaster, DisasterType, SeverityLevel
from backend.schemas import DisasterCreate, DisasterUpdate, DisasterResponse

router = APIRouter()


@router.post("/", response_model=DisasterResponse, status_code=status.HTTP_201_CREATED)
def create_disaster(disaster: DisasterCreate, db: Session = Depends(get_db)):
    """Create a new disaster record"""
    db_disaster = Disaster(**disaster.model_dump())
    db.add(db_disaster)
    db.commit()
    db.refresh(db_disaster)
    return db_disaster


@router.get("/", response_model=List[DisasterResponse])
def list_disasters(
    skip: int = 0,
    limit: int = 100,
    district_id: int = None,
    disaster_type: DisasterType = None,
    severity: SeverityLevel = None,
    db: Session = Depends(get_db)
):
    """List all disasters with optional filters"""
    query = db.query(Disaster)
    
    if district_id:
        query = query.filter(Disaster.district_id == district_id)
    if disaster_type:
        query = query.filter(Disaster.disaster_type == disaster_type)
    if severity:
        query = query.filter(Disaster.severity == severity)
    
    disasters = query.order_by(Disaster.occurred_at.desc()).offset(skip).limit(limit).all()
    return disasters


@router.get("/{disaster_id}", response_model=DisasterResponse)
def get_disaster(disaster_id: int, db: Session = Depends(get_db)):
    """Get a specific disaster by ID"""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster with id {disaster_id} not found"
        )
    return disaster


@router.put("/{disaster_id}", response_model=DisasterResponse)
def update_disaster(
    disaster_id: int,
    disaster_update: DisasterUpdate,
    db: Session = Depends(get_db)
):
    """Update a disaster record"""
    db_disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not db_disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster with id {disaster_id} not found"
        )
    
    update_data = disaster_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_disaster, field, value)
    
    db_disaster.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_disaster)
    return db_disaster


@router.delete("/{disaster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disaster(disaster_id: int, db: Session = Depends(get_db)):
    """Delete a disaster record"""
    db_disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not db_disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster with id {disaster_id} not found"
        )
    
    db.delete(db_disaster)
    db.commit()
    return None
