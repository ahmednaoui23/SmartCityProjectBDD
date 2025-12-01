from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import mesure as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.MesureOut)
def create_mesure(payload: sch.MesureCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_mesure(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[sch.MesureOut])
def list_mesures(limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_mesures(db, limit)