from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import citoyen as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.CitoyenOut)
def create_citoyen(payload: sch.CitoyenCreate, db: Session = Depends(get_db)):
    return crud.create_citoyen(db, payload)

@router.get("/", response_model=list[sch.CitoyenOut])
def list_citoyens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_citoyens(db, skip, limit)