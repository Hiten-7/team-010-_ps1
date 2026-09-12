from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import Alert, DisasterType, SeverityLevel, AlertStatus
from backend.schemas import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter()


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    district_id: int = None,
    disaster_type: DisasterType = None,
    severity: SeverityLevel = None,
    status_filter: AlertStatus = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all alerts with optional filters"""
    query = db.query(Alert)
    
    if district_id:
        query = query.filter(Alert.district_id == district_id)
    if disaster_type:
        query = query.filter(Alert.disaster_type == disaster_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    if active_only:
        query = query.filter(Alert.status == AlertStatus.ACTIVE)
        query = query.filter(Alert.valid_until >= datetime.utcnow())
    
    alerts = query.order_by(Alert.issued_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    
    update_data = alert_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db_alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    
    db_alert.status = AlertStatus.RESOLVED
    db_alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    
    db.delete(db_alert)
    db.commit()
    return None
