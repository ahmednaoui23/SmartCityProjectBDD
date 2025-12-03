from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import proprietaire as sch
from app import crud

router = APIRouter()

@router.post("/", response_model=sch.ProprietaireOut, status_code=status.HTTP_201_CREATED)
def create_proprietaire(payload: sch.ProprietaireCreate, db: Session = Depends(get_db)):
    result = crud.create_proprietaire(db, payload)
    # DEBUG: afficher type et représentation courte
    print("DEBUG create_proprietaire -> type:", type(result))
    try:
        print("DEBUG create_proprietaire -> repr:", repr(result))
    except Exception:
        print("DEBUG create_proprietaire -> repr failed")
    return result
@router.get("/", response_model=list[sch.ProprietaireOut])
def list_proprietaires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_proprietaires(db, skip, limit)

@router.get("/{id_}", response_model=sch.ProprietaireOut)
def get_one(id_: int, db: Session = Depends(get_db)):
    obj = crud.get_proprietaire(db, id_)
    if not obj:
        raise HTTPException(status_code=404, detail="Proprietaire not found")
    return obj