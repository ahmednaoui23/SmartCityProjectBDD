from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import consultation as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.ConsultationOut)
def create_consultation(payload: sch.ConsultationCreate, db: Session = Depends(get_db)):
    return crud.create_consultation(db, payload)