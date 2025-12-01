from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import intervention as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.InterventionOut)
def create_intervention(payload: sch.InterventionCreate, db: Session = Depends(get_db)):
    return crud.create_intervention(db, payload)

@router.get("/", response_model=list[sch.InterventionOut])
def list_interventions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_interventions(db, skip, limit)

@router.post("/{id_intervention}/close", response_model=sch.InterventionOut)
def close_intervention(id_intervention: int, db: Session = Depends(get_db)):
    try:
        return crud.close_intervention(db, id_intervention)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))