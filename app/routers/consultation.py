from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import consultation as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.ConsultationOut)
def create_consultation(payload: sch.ConsultationCreate, db: Session = Depends(get_db)):
    obj = models.Consultation(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj