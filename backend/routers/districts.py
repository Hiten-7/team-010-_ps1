from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import District
from backend.schemas import DistrictCreate, DistrictUpdate, DistrictResponse

router = APIRouter()


@router.post("/", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED)
def create_district(district: DistrictCreate, db: Session = Depends(get_db)):
    """Create a new district"""
    # Check if district code already exists
    existing = db.query(District).filter(District.code == district.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District with code {district.code} already exists"
        )
    
    db_district = District(**district.model_dump())
    db.add(db_district)
    db.commit()
    db.refresh(db_district)
    return db_district


@router.get("/", response_model=List[DistrictResponse])
def list_districts(
    skip: int = 0,
    limit: int = 100,
    state: str = None,
    db: Session = Depends(get_db)
):
    """List all districts with optional state filter"""
    query = db.query(District)
    
    if state:
        query = query.filter(District.state == state)
    
    districts = query.order_by(District.name).offset(skip).limit(limit).all()
    return districts


@router.get("/{district_id}", response_model=DistrictResponse)
def get_district(district_id: int, db: Session = Depends(get_db)):
    """Get a specific district by ID"""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    return district


@router.get("/code/{district_code}", response_model=DistrictResponse)
def get_district_by_code(district_code: str, db: Session = Depends(get_db)):
    """Get a specific district by code"""
    district = db.query(District).filter(District.code == district_code).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with code {district_code} not found"
        )
    return district


@router.put("/{district_id}", response_model=DistrictResponse)
def update_district(
    district_id: int,
    district_update: DistrictUpdate,
    db: Session = Depends(get_db)
):
    """Update a district"""
    db_district = db.query(District).filter(District.id == district_id).first()
    if not db_district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    
    update_data = district_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_district, field, value)
    
    db_district.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_district)
    return db_district


@router.delete("/{district_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_district(district_id: int, db: Session = Depends(get_db)):
    """Delete a district"""
    db_district = db.query(District).filter(District.id == district_id).first()
    if not db_district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    
    db.delete(db_district)
    db.commit()
    return None
