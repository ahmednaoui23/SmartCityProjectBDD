from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import participer_a as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.ParticiperAOut)
def create_participation(payload: sch.ParticiperACreate, db: Session = Depends(get_db)):
    try:
        return crud.create_participation(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))