from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/leads", tags=["Leads"])


def qualify_lead(income: float | None, selected_service: str | None) -> str:
    """
    Very simple rule-based qualification.
    You can improve this later.
    """
    if income is None:
        return "unqualified"

    if income >= 100000:
        return "high"
    elif income >= 50000:
        return "medium"
    else:
        return "low"


@router.post("/", response_model=schemas.LeadResponse)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    qualification_level = qualify_lead(lead.income, lead.selected_service)

    db_lead = models.Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        selected_service=lead.selected_service,
        income=lead.income,
        financial_goal=lead.financial_goal,
        qualification_level=qualification_level,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/{lead_id}", response_model=schemas.LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/", response_model=List[schemas.LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).all()
    return leads
