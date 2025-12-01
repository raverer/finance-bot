from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=schemas.AppointmentResponse)
def create_appointment(
    payload: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    # check lead exists
    lead = db.query(models.Lead).filter(models.Lead.id == payload.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    appointment = models.Appointment(
        lead_id=payload.lead_id,
        service=payload.service,
        date=payload.date,
        time=payload.time,
        notes=payload.notes,
        status="confirmed",  # for now auto-confirm
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/", response_model=List[schemas.AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    appts = db.query(models.Appointment).order_by(models.Appointment.created_at.desc()).all()
    return appts
