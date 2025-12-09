from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import participer_a as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.ParticiperAOut)
def create_participation(payload: sch.ParticiperACreate, db: Session = Depends(get_db)):
    c = db.get(models.Citoyen, payload.id_citoyen)
    con = db.get(models.Consultation, payload.id_consultation)
    if not c or not con:
        raise HTTPException(status_code=400, detail="Citoyen or Consultation not found")
    obj = models.ParticiperA(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj